# Case Study: Scaling Social Media Feed

## The Problem

**Requirement:** Show users a feed of posts from people they follow, sorted by recency.

**Scale:**
- 10 million users
- Average 500 people followed per user
- 100 posts/second created
- Each user checks feed 20 times/day

**Total:** 200 million feed requests/day

---

## Naive Approach (Doesn't Scale)

```sql
SELECT posts.* 
FROM posts
WHERE user_id IN (
    SELECT following_id 
    FROM follows 
    WHERE follower_id = ?
)
ORDER BY created_at DESC
LIMIT 50
```

### Why It Fails

**For a user following 500 people:**
1. Fetch 500 user IDs from follows table
2. Scan posts table for all posts from those 500 users
3. Sort potentially millions of posts
4. Return top 50

**Result:**
- Query scans millions of rows
- Takes 5-10 seconds
- Database CPU at 100%
- Can't handle 200M requests/day

---

## Solution 1: Fan-Out on Write (Push Model)

**Strategy:** Pre-compute each user's feed when posts are created.

### Architecture

```
User creates post
    ↓
Insert into posts table
    ↓
Queue background job
    ↓
Copy post_id to EACH follower's feed (Redis)
    ↓
Follower reads pre-computed feed (instant!)
```

### Implementation

```python
# ===== WRITE PATH =====

@app.route('/posts', methods=['POST'])
def create_post():
    """Create post and queue fan-out"""
    post = {
        'id': generate_id(),
        'user_id': current_user.id,
        'content': request.json['content'],
        'created_at': datetime.now()
    }
    
    # Insert into database
    db.execute(
        "INSERT INTO posts (id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
        post['id'], post['user_id'], post['content'], post['created_at']
    )
    
    # Queue fan-out job (background)
    fanout_post_to_followers.delay(post['id'], post['user_id'])
    
    return {'status': 'created', 'post_id': post['id']}, 201


@app.task
def fanout_post_to_followers(post_id, author_id):
    """Background job: Copy post to all followers' feeds"""
    
    # Get all followers (could be millions!)
    followers = db.execute(
        "SELECT follower_id FROM follows WHERE following_id = ?",
        author_id
    )
    
    # Batch Redis operations
    pipe = redis_client.pipeline()
    
    for follower in followers:
        # Add to follower's feed (sorted set by timestamp)
        pipe.zadd(
            f"feed:{follower['follower_id']}", 
            {post_id: time.time()}
        )
        # Keep only latest 1000 posts
        pipe.zremrangebyrank(f"feed:{follower['follower_id']}", 0, -1001)
    
    # Execute all operations at once
    pipe.execute()
    
    logger.info(f"Fanned out post {post_id} to {len(followers)} followers")


# ===== READ PATH =====

@app.route('/feed')
def get_feed():
    """Read pre-computed feed (FAST)"""
    user_id = current_user.id
    
    # Get post IDs from Redis sorted set (O(log n))
    post_ids = redis_client.zrevrange(
        f"feed:{user_id}",
        0, 49,  # Top 50 posts
        withscores=False
    )
    
    # Batch fetch full post data from cache or DB
    posts = get_posts_by_ids(post_ids)
    
    return {'posts': posts}, 200


def get_posts_by_ids(post_ids):
    """Efficiently fetch multiple posts"""
    # Try cache first
    pipe = redis_client.pipeline()
    for post_id in post_ids:
        pipe.get(f"post:{post_id}")
    cached_posts = pipe.execute()
    
    # Fetch missing from database
    missing_ids = [
        post_ids[i] for i, cached in enumerate(cached_posts) 
        if cached is None
    ]
    
    if missing_ids:
        db_posts = db.execute(
            f"SELECT * FROM posts WHERE id IN ({','.join(['?'] * len(missing_ids))})",
            *missing_ids
        )
        # Cache for next time
        for post in db_posts:
            redis_client.setex(f"post:{post['id']}", 300, json.dumps(post))
    
    # Combine cached + db posts
    all_posts = [json.loads(p) for p in cached_posts if p] + db_posts
    return all_posts
```

### Performance

**Write:**
- User with 1000 followers: 1000 Redis writes (~100ms)
- User with 1M followers: 1M Redis writes (~10 seconds)

**Read:**
- Single Redis query: 1-5ms
- Batch fetch posts: 10-20ms
- **Total: 15-25ms** ✅

### Pros & Cons

✅ **Reads are instant** (just fetch from Redis)  
✅ Scales to billions of reads  
✅ Feed is always up-to-date  

❌ **Writes expensive** for users with many followers  
❌ Storage intensive (duplicate post_ids across feeds)  
❌ Celebrities (1M+ followers) can't use this

**Use when:** Most users have < 10,000 followers

---

## Solution 2: Fan-Out on Read (Pull Model)

**Strategy:** Compute feed when user requests it.

### Implementation

```python
# ===== WRITE PATH =====

@app.route('/posts', methods=['POST'])
def create_post():
    """Just insert post - no fan-out"""
    post = {
        'id': generate_id(),
        'user_id': current_user.id,
        'content': request.json['content'],
        'created_at': datetime.now()
    }
    
    db.execute(
        "INSERT INTO posts (id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
        post['id'], post['user_id'], post['content'], post['created_at']
    )
    
    # Cache user's recent posts
    redis_client.zadd(
        f"user_posts:{current_user.id}",
        {post['id']: time.time()}
    )
    
    return {'status': 'created'}, 201


# ===== READ PATH =====

@app.route('/feed')
def get_feed():
    """Compute feed on demand"""
    user_id = current_user.id
    
    # Check cache first
    cached_feed = redis_client.get(f"feed_cache:{user_id}")
    if cached_feed:
        return {'posts': json.loads(cached_feed)}, 200
    
    # Get list of people user follows
    following = db.execute(
        "SELECT following_id FROM follows WHERE follower_id = ? LIMIT 500",
        user_id
    )
    following_ids = [f['following_id'] for f in following]
    
    # Fetch recent posts from each (from cache)
    all_posts = []
    for following_id in following_ids:
        # Get from Redis cache
        recent_post_ids = redis_client.zrevrange(
            f"user_posts:{following_id}",
            0, 9  # Last 10 posts
        )
        posts = get_posts_by_ids(recent_post_ids)
        all_posts.extend(posts)
    
    # Merge and sort by timestamp
    all_posts.sort(key=lambda p: p['created_at'], reverse=True)
    feed = all_posts[:50]
    
    # Cache result for 30 seconds
    redis_client.setex(
        f"feed_cache:{user_id}",
        30,
        json.dumps(feed)
    )
    
    return {'posts': feed}, 200
```

### Performance

**Write:**
- Single database insert: 5ms
- Update user's post cache: 1ms
- **Total: 6ms** ✅

**Read:**
- Fetch 500 following IDs: 10ms
- Fetch recent posts for each (cached): 100ms
- Merge and sort: 20ms
- **Total: 130ms**

### Pros & Cons

✅ **Writes are instant**  
✅ No storage overhead  
✅ Works for celebrities  

❌ **Reads require computation** (100-200ms)  
❌ Complex merge logic  
❌ Doesn't scale to users following 10k+ people

**Use when:** Users follow many people (> 1000)

---

## Solution 3: Hybrid Approach (Twitter/Instagram)

**Strategy:** Use fan-out on write for most users, fan-out on read for celebrities.

### Architecture

```
User creates post
    ↓
Check follower count
    ↓
  < 10k followers?
    ↓            ↓
   YES          NO
    ↓            ↓
Fan-out      Mark as
on write     "celebrity"
    ↓            ↓
            Pull on read
```

### Implementation

```python
# ===== Configuration =====

CELEBRITY_THRESHOLD = 10_000  # Followers

def is_celebrity(user_id):
    """Check if user has many followers"""
    follower_count = redis_client.get(f"follower_count:{user_id}")
    if not follower_count:
        follower_count = db.execute(
            "SELECT COUNT(*) FROM follows WHERE following_id = ?",
            user_id
        )[0]['count']
        redis_client.setex(f"follower_count:{user_id}", 3600, follower_count)
    
    return int(follower_count) > CELEBRITY_THRESHOLD


# ===== WRITE PATH =====

@app.route('/posts', methods=['POST'])
def create_post():
    """Smart fan-out based on follower count"""
    post = create_post_in_db(request.json)
    
    if is_celebrity(current_user.id):
        # Celebrity: Just cache recent posts
        redis_client.zadd(
            f"user_posts:{current_user.id}",
            {post['id']: time.time()}
        )
        logger.info(f"Celebrity post {post['id']} - no fan-out")
    else:
        # Regular user: Fan-out on write
        fanout_post_to_followers.delay(post['id'], current_user.id)
        logger.info(f"Regular post {post['id']} - fan-out queued")
    
    return {'status': 'created'}, 201


# ===== READ PATH =====

@app.route('/feed')
def get_feed():
    """Hybrid feed generation"""
    user_id = current_user.id
    
    # Get following list
    following = get_following(user_id)
    
    # Separate into regular users and celebrities
    regular_users = []
    celebrities = []
    
    for user in following:
        if is_celebrity(user['id']):
            celebrities.append(user['id'])
        else:
            regular_users.append(user['id'])
    
    # Get pre-computed feed (from fan-out on write)
    regular_posts = redis_client.zrevrange(f"feed:{user_id}", 0, 49)
    regular_posts = get_posts_by_ids(regular_posts)
    
    # Fetch celebrity posts on-demand (fan-out on read)
    celebrity_posts = []
    for celeb_id in celebrities:
        recent = redis_client.zrevrange(f"user_posts:{celeb_id}", 0, 9)
        celebrity_posts.extend(get_posts_by_ids(recent))
    
    # Merge both
    all_posts = regular_posts + celebrity_posts
    all_posts.sort(key=lambda p: p['created_at'], reverse=True)
    feed = all_posts[:50]
    
    return {'posts': feed}, 200
```

### Performance

**Write:**
- Regular user (1k followers): Fan-out in 100ms
- Celebrity (1M followers): No fan-out, instant

**Read:**
- User following 490 regular + 10 celebrities
- Pre-computed feed: 10ms
- Fetch 10 celebrity posts: 20ms
- Merge: 5ms
- **Total: 35ms** ✅

### Pros & Cons

✅ **Best of both worlds**  
✅ Writes fast for everyone  
✅ Reads fast for everyone  
✅ Scales to billions of users  

❌ More complex implementation  
❌ Need to track "celebrity" status

**Use when:** Large-scale social platform (1M+ users)

---

## Optimization Techniques

### 1. Batch Operations

```python
# Bad: N queries
for follower in followers:
    redis_client.zadd(f"feed:{follower}", {post_id: timestamp})

# Good: Pipeline (1 round-trip)
pipe = redis_client.pipeline()
for follower in followers:
    pipe.zadd(f"feed:{follower}", {post_id: timestamp})
pipe.execute()
```

**Speedup:** 100x faster

---

### 2. Cache User Posts

```python
# When user creates post, add to their recent posts cache
redis_client.zadd(f"user_posts:{user_id}", {post_id: timestamp})
redis_client.zremrangebyrank(f"user_posts:{user_id}", 0, -101)  # Keep 100

# When building feed, fetch from cache
recent_posts = redis_client.zrevrange(f"user_posts:{user_id}", 0, 9)
```

**Avoids:** Database queries for recent posts

---

### 3. Pagination

```python
@app.route('/feed')
def get_feed():
    page = request.args.get('page', 1)
    per_page = 50
    start = (page - 1) * per_page
    end = start + per_page - 1
    
    post_ids = redis_client.zrevrange(f"feed:{user_id}", start, end)
    return {'posts': get_posts_by_ids(post_ids)}
```

**Benefit:** Don't load entire feed at once

---

### 4. Feed Trimming

```python
# Keep only latest 1000 posts in feed
redis_client.zremrangebyrank(f"feed:{user_id}", 0, -1001)
```

**Benefit:** Limit memory usage

---

## Comparison

| Approach | Write Speed | Read Speed | Storage | Best For |
|----------|-------------|------------|---------|----------|
| Fan-out on Write | Slow (O(N followers)) | Fast (O(1)) | High | < 10k followers |
| Fan-out on Read | Fast (O(1)) | Slow (O(N following)) | Low | > 1k following |
| Hybrid | Fast | Fast | Medium | Any scale |

---

## Rule of Thumb

- **< 100k users:** Start with fan-out on read (simpler)
- **100k - 1M users:** Implement fan-out on write
- **1M+ users:** Hybrid approach mandatory
- **Always:** Cache aggressively, batch operations, trim feeds
- **Monitor:** Feed generation time (target: < 100ms)