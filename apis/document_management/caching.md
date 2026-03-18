# Caching & Scaling Strategies for Backend Systems

**Pattern**: Multi-layer caching with appropriate TTLs  
**Key Insight**: Cache at the right layer for the right data

---

## Caching Strategy by Data Type

| Data Type | Cache Layer | TTL | Reason |
|-----------|-------------|-----|--------|
| User profiles | Redis | 5 min | Changes rarely, read often |
| Post content | Redis | 1 min | Likes/comments change frequently |
| Feed data | Redis | 30-60s | Needs freshness, high read volume |
| Static assets | CDN | 1 year | Immutable (versioned URLs) |
| API responses | Browser/CDN | varies | Cache-Control headers |
| Session data | Redis | 24 hours | Fast access, expires |
| Database queries | DB query cache | auto | Repeated identical queries |

---

## Redis Caching Patterns

### Cache-Aside Decorator Pattern

```python
import redis
import json
from typing import Optional
from functools import wraps

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_decorator(ttl_seconds: int, key_prefix: str):
    """
    Decorator for caching function results
    
    Pattern: Cache-aside (lazy loading)
    - Check cache first
    - If miss, fetch from DB and populate cache
    - Return cached result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function args
            cache_key = f"{key_prefix}:{args[0]}"  # Simplified
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                print(f"Cache HIT: {cache_key}")
                return json.loads(cached)
            
            # Cache miss - fetch from source
            print(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

# Example usage
@cache_decorator(ttl_seconds=300, key_prefix="user")
def get_user_profile(user_id: int):
    """Fetch user from database (simulated)"""
    return {
        "id": user_id,
        "username": "johndoe",
        "follower_count": 1500
    }
```

---

## Cache Invalidation Patterns

> *The two hard problems in computer science:*  
> *1. Cache invalidation*  
> *2. Naming things*  
> *3. Off-by-one errors*

### Centralized Cache Manager

```python
class CacheManager:
    """Centralized cache invalidation"""
    
    @staticmethod
    def invalidate_user(user_id: int):
        """When user data changes"""
        keys_to_delete = [
            f"user:{user_id}",
            f"user:{user_id}:posts",
            f"user:{user_id}:followers",
            f"user:{user_id}:following"
        ]
        redis_client.delete(*keys_to_delete)
    
    @staticmethod
    def invalidate_post(post_id: int, author_id: int):
        """When post changes (new comment, like, etc)"""
        keys_to_delete = [
            f"post:{post_id}",
            f"user:{author_id}:posts",
            f"feed:*"  # Nuclear option: clear all feeds
        ]
        redis_client.delete(*keys_to_delete)
    
    @staticmethod
    def update_denormalized_count(key: str, delta: int):
        """
        Update cached counters atomically
        Pattern: Write-through cache
        """
        # Increment in cache
        redis_client.incrby(key, delta)
        # Also update in database
        # db.execute("UPDATE posts SET like_count = like_count + %s WHERE id = %s", delta, post_id)
```

---

## Cache Patterns Comparison

### 1. Cache-Aside (Lazy Loading)

✅ Most common  
✅ Cache populated on demand  
❌ Initial request is slow (cache miss)

**Flow:**
- **Read:** Check cache → Miss → Fetch DB → Store cache → Return
- **Write:** Update DB → Invalidate cache

### 2. Write-Through

✅ Cache always in sync  
❌ Every write hits cache + DB (slower writes)

**Flow:**
- **Read:** Check cache → Hit → Return
- **Write:** Update DB → Update cache

### 3. Write-Behind (Write-back)

✅ Fastest writes  
❌ Risk of data loss (cache ahead of DB)

**Flow:**
- **Read:** Check cache → Hit → Return
- **Write:** Update cache → Queue DB write (async)

### 4. Refresh-Ahead

✅ Proactively refresh hot data  
❌ Complex to implement

**Flow:** Background job refreshes cache before expiry

---

## Scaling Strategies

### Vertical Scaling (Scale Up)

Add more resources to single server:
- More CPU cores
- More RAM
- Faster disk (SSD → NVMe)

**Pros:**
- Simple (no code changes)
- No distributed system complexity

**Cons:**
- Physical limits (can't add infinite RAM)
- Single point of failure
- Expensive at high end

**Use when:**
- Early stage (< 10k users)
- Database is bottleneck
- Quick fix needed

---

### Horizontal Scaling (Scale Out)

Add more servers:
- Load balancer distributes requests
- Stateless application servers
- Shared database or distributed data

**Pros:**
- Unlimited scaling potential
- Redundancy (no single point of failure)
- Cost effective (commodity hardware)

**Cons:**
- Code must be stateless
- Distributed system complexity
- Data consistency challenges

**Use when:**
- Growing past single server capacity
- Need high availability
- Long-term scalability

---

## Database Scaling Strategies

### 1. Read Replicas

- Master handles writes
- Replicas handle reads
- Eventual consistency (slight lag)

**Use for:** Read-heavy workloads (90%+ reads)  
**Example:** Social media feeds, product catalogs

### 2. Sharding (Horizontal Partitioning)

- Split data across multiple databases
- Each shard has subset of data
- Route queries to correct shard

**Shard by:** user_id, region, date range

**Use for:** Massive datasets (billions of rows)  
**Example:** Chat messages, time-series data

**⚠️ Challenges:**
- Cross-shard queries are expensive
- Rebalancing shards is complex
- Choose shard key carefully!

### 3. Caching Layer

- Redis/Memcached in front of DB
- Cache hot data (90/10 rule: 90% of requests hit 10% of data)

**Use for:** Everything! Always add caching.

### 4. Denormalization

- Store redundant data for speed
- Example: `like_count` in posts table

**Trade-off:** Faster reads, complex writes

---

## Async Processing Patterns

*Don't make users wait for slow operations!*

### 1. Message Queues (RabbitMQ, AWS SQS)

**Example:** User uploads image
1. API returns 202 Accepted immediately
2. Background worker processes image
3. Webhook notifies when done

**Use for:** Image processing, video encoding, email sending

### 2. Background Jobs (Celery, Sidekiq)

**Example:** User creates post
1. Insert into database (fast)
2. Queue job to fan-out to followers' feeds
3. API returns success

**Use for:** Feed updates, notifications, analytics

### 3. Webhooks

**Example:** Payment processed
1. Payment service calls your webhook
2. You update order status
3. Notify user

**Use for:** External integrations, event-driven architecture

---

## Example: Scaling Social Media Feed

### Problem

Generating feed is slow at scale.

**Naive approach (TOO SLOW):**
```sql
SELECT * FROM posts 
WHERE user_id IN (SELECT following_id FROM follows WHERE follower_id = ?)
ORDER BY created_at DESC 
LIMIT 50
```

At 1M users following 1000 people each:
- Must scan 1000 users' posts
- Sort millions of posts
- Query takes 5+ seconds 😱

---

### Solution 1: Fan-out on Write (Push Model)

**When user creates post:**
1. Insert post into database
2. Background job: Copy post ID to each follower's feed cache
3. Each user's feed is pre-computed in Redis

**Read feed (FAST):**
```redis
LRANGE user:123:feed 0 49  # Redis sorted list
```

✅ **Pros:** Reads are O(1) - just fetch from Redis  
❌ **Cons:** Writes are expensive (N copies for N followers)

**Use when:** Most users have < 10k followers

---

### Solution 2: Fan-out on Read (Pull Model)

**When user requests feed:**
1. Fetch list of people they follow
2. Get recent posts from each (from cache if possible)
3. Merge and sort
4. Cache result for 30 seconds

✅ **Pros:** Writes are fast (just insert post)  
❌ **Cons:** Reads require work (merge N lists)

**Use when:** Users follow many people

---

### Solution 3: Hybrid (Twitter's Approach)

- **Small accounts (< 10k followers):** Fan-out on write
- **Large accounts (celebrities):** Fan-out on read
- Combine both at read time

**When Beyoncé posts:**
- Don't copy to 100M feeds (too slow)
- Fetch her recent posts at read time for her followers

**When I post:**
- Copy to my 300 followers' feeds (fast)
- Their feeds are pre-computed

**Best of both worlds!**

---

## Load Balancing Strategies

### Round Robin
- Request 1 → Server A
- Request 2 → Server B
- Request 3 → Server C
- Repeat

✅ Simple, fair distribution  
❌ Doesn't account for server load

### Least Connections
- Send to server with fewest active connections

✅ Adapts to varying request durations

### IP Hash
- Hash user IP → always route to same server

✅ Sticky sessions (useful for stateful apps)  
❌ Uneven distribution if users clustered

### Weighted
- Server A gets 50% of traffic
- Server B gets 30%
- Server C gets 20%

✅ Useful during deployments or testing

---

## CDN Strategy

### What to Put on CDN

✅ Static assets (JS, CSS, images)  
✅ User-uploaded content (profile pics, posts)  
✅ API responses for public data (cached at edge)

### How It Works

1. User requests image from CDN
2. CDN checks: Do I have this? (cache hit/miss)
3. If miss: Fetch from origin server, cache it, return
4. If hit: Return cached version (FAST - served from nearby location)

### Configuration

```http
Cache-Control: public, max-age=31536000  # 1 year for immutable assets
```

- Use versioned URLs: `/assets/app.v123.js` (cache forever, change URL to bust cache)
- ETag for conditional requests (304 Not Modified)

### Cost Savings

- Reduce origin server load by 80-90%
- Faster for users (served from edge location)

---

## Monitoring & Alerting

### What to Measure

#### 1. Request Rate
- Requests per second (RPS)
- Alert if > expected traffic (DDoS?) or < expected (outage?)

#### 2. Latency
- p50, p95, p99 response times
- Alert if p99 > 1 second

#### 3. Error Rate
- 4xx errors (client bugs)
- 5xx errors (server bugs)
- Alert if > 1% error rate

#### 4. Cache Hit Rate
- Percentage of requests served from cache
- Target: > 80% for hot data
- Low hit rate = caching not working

#### 5. Database Performance
- Query execution time
- Connection pool usage
- Slow query log

### Tools

- **Application:** New Relic, Datadog, Prometheus
- **Logs:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing:** Jaeger, Zipkin (distributed tracing)

---

## Design Decisions Summary

### When to Use What

**Cache Layer:**
- **Redis:** Hot data, session storage, counters, real-time leaderboards
- **CDN:** Static assets, public content, images/videos
- **Memcached:** Simple key-value caching (lighter than Redis)
- **Browser cache:** API responses, static assets (via headers)

**Scaling Strategy:**
- **< 10k users:** Single server (vertical scaling)
- **10k - 100k users:** Add Redis, read replicas
- **100k - 1M users:** Horizontal scaling, load balancer, CDN
- **1M+ users:** Sharding, microservices, distributed cache

**Async Processing:**
- **Use for:** Anything that takes > 500ms
- **Examples:** Email, image processing, analytics, feed updates
- **Don't use for:** Critical path operations that user needs immediately

**Database Scaling:**
1. **First:** Add indexes, optimize queries
2. **Then:** Add Redis caching layer
3. **Then:** Read replicas for read-heavy workloads
4. **Last resort:** Sharding (complex, avoid if possible)

### Rule of Thumb

- Cache data that's read often but changes rarely
- Use async for operations users don't need to wait for
- Scale horizontally for compute, vertically for databases (until you can't)
- Monitor everything, optimize the bottlenecks (not everything)