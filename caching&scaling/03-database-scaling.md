# Database Scaling

## Scaling Progression

1. **Optimize queries** (add indexes, fix N+1 problems)
2. **Add caching layer** (Redis in front of DB)
3. **Read replicas** (for read-heavy workloads)
4. **Sharding** (last resort - adds complexity)

---

## Read Replicas

### Architecture

```
┌─────────────┐
│   Master    │ ← All writes go here
│  (Primary)  │
└──────┬──────┘
       │ Replication (async)
       ├───────────┬───────────┐
       ▼           ▼           ▼
   ┌───────┐  ┌───────┐  ┌───────┐
   │Replica│  │Replica│  │Replica│ ← Reads load balanced
   │   1   │  │   2   │  │   3   │
   └───────┘  └───────┘  └───────┘
```

### How It Works

- Master handles all writes
- Changes replicate to read replicas (async)
- Read queries load-balanced across replicas
- Slight lag (eventual consistency)

### Implementation

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Master (writes)
master_engine = create_engine('postgresql://master:5432/db')

# Replicas (reads)
replica_engines = [
    create_engine('postgresql://replica1:5432/db'),
    create_engine('postgresql://replica2:5432/db'),
]

class Database:
    def write(self, query):
        """All writes to master"""
        session = sessionmaker(bind=master_engine)()
        return session.execute(query)
    
    def read(self, query):
        """Reads from random replica"""
        import random
        replica = random.choice(replica_engines)
        session = sessionmaker(bind=replica)()
        return session.execute(query)
```

### Pros & Cons

✅ **Use for:** Read-heavy workloads (90%+ reads)  
✅ Horizontal scaling for reads  
✅ No application logic changes  

❌ Eventual consistency (replication lag ~100ms)  
❌ Can't scale writes  
❌ "Read your writes" problem

### Handling Replication Lag

```python
def create_post(user_id, content):
    # Write to master
    post_id = db.master.insert("INSERT INTO posts ...")
    
    # Immediately read from master (not replica)
    # to avoid "post not found" due to lag
    post = db.master.select(f"SELECT * FROM posts WHERE id = {post_id}")
    
    return post
```

---

## Sharding (Horizontal Partitioning)

Split data across multiple databases by a shard key.

### Shard Key Selection

**Critical decision - hard to change later!**

#### Good Shard Keys

✅ **User ID:** Even distribution, queries usually scoped to one user
```python
shard = user_id % num_shards
```

✅ **Geographic region:** Data locality, compliance
```python
shard = lookup_region(user_id)  # "us-east", "eu-west"
```

✅ **Date range:** For time-series data
```python
shard = post_created_at.year  # Yearly shards
```

#### Bad Shard Keys

❌ **Status field:** Uneven distribution (most posts are "active")  
❌ **Boolean:** Only 2 shards possible  
❌ **Category:** Hot categories overload shards

---

### Sharding Strategies

#### 1. Range-Based Sharding

```python
# User IDs 1-1M → Shard 0
# User IDs 1M-2M → Shard 1
# User IDs 2M-3M → Shard 2

def get_shard(user_id):
    return user_id // 1_000_000
```

✅ Simple  
❌ Uneven distribution (newer users more active)  
❌ Rebalancing requires data migration

---

#### 2. Hash-Based Sharding

```python
def get_shard(user_id):
    return hash(user_id) % num_shards
```

✅ Even distribution  
❌ Hard to add shards (requires rehashing all data)  
❌ Range queries impossible

---

#### 3. Directory-Based Sharding

```python
# Lookup table: user_id → shard_id
shard_mapping = {
    123: "shard_0",
    456: "shard_2",
    789: "shard_1",
}

def get_shard(user_id):
    return shard_mapping.get(user_id)
```

✅ Flexible (can move users between shards)  
✅ Can handle hot users differently  
❌ Extra lookup required  
❌ Directory becomes bottleneck

---

### Sharding Implementation

```python
class ShardedDatabase:
    def __init__(self):
        self.shards = {
            0: create_engine('postgresql://shard0:5432/db'),
            1: create_engine('postgresql://shard1:5432/db'),
            2: create_engine('postgresql://shard2:5432/db'),
        }
    
    def get_shard(self, user_id):
        shard_id = user_id % len(self.shards)
        return self.shards[shard_id]
    
    def get_user(self, user_id):
        """Query specific shard"""
        shard = self.get_shard(user_id)
        return shard.execute(f"SELECT * FROM users WHERE id = {user_id}")
    
    def get_all_users(self):
        """Cross-shard query (expensive!)"""
        results = []
        for shard in self.shards.values():
            results.extend(shard.execute("SELECT * FROM users"))
        return results
```

---

### Challenges

❌ **Cross-shard queries:** Expensive and complex
```sql
-- Can't do this efficiently across shards:
SELECT * FROM posts WHERE created_at > '2024-01-01' ORDER BY likes DESC
```

❌ **Foreign keys:** Don't work across databases
```sql
-- If user and posts are in different shards, FK fails
ALTER TABLE posts ADD FOREIGN KEY (user_id) REFERENCES users(id)
```

❌ **Transactions:** Can't have ACID across shards  
❌ **Rebalancing:** Moving data between shards is complex  
❌ **Joins:** Must happen at application layer

---

### When to Shard

✅ **Shard when:**
- Database > 1TB
- Write throughput exceeds single DB
- Other optimization exhausted

❌ **Don't shard if:**
- Database < 500GB
- Can add read replicas instead
- Can optimize queries/indexes
- Can vertically scale DB

---

## Denormalization

Store redundant data to avoid expensive joins.

### Example

**Normalized:**
```sql
SELECT posts.*, COUNT(likes.id) as like_count
FROM posts
LEFT JOIN likes ON likes.post_id = posts.id
WHERE posts.user_id = 123
GROUP BY posts.id
-- Slow: joins + aggregation
```

**Denormalized:**
```sql
-- Add like_count column to posts table
SELECT * FROM posts WHERE user_id = 123
-- Fast: single table scan, no joins
```

### Maintaining Consistency

```python
def like_post(post_id, user_id):
    # Insert like
    db.execute("INSERT INTO likes (post_id, user_id) VALUES (?, ?)", post_id, user_id)
    
    # Update denormalized count
    db.execute("UPDATE posts SET like_count = like_count + 1 WHERE id = ?", post_id)
    
    # Also invalidate cache
    cache.delete(f"post:{post_id}")
```

### Trade-offs

✅ Much faster reads  
❌ Slower writes (update multiple places)  
❌ Risk of inconsistency  
❌ More storage

**Use for:** Read-heavy data (like counts, follower counts, ratings)

---

## Connection Pooling

Reuse database connections instead of creating new ones.

```python
from sqlalchemy import create_engine

engine = create_engine(
    'postgresql://localhost/db',
    pool_size=20,          # 20 connections in pool
    max_overflow=10,       # Allow 10 extra if pool exhausted
    pool_timeout=30,       # Wait 30s for available connection
    pool_recycle=3600,     # Recycle connections after 1 hour
)
```

### Why It Matters

- Creating DB connection: ~50-100ms
- Using pooled connection: ~1ms
- 100 requests/sec = 5-10 seconds wasted without pooling!

---

## Query Optimization

### 1. Add Indexes

```sql
-- Slow: Full table scan
SELECT * FROM posts WHERE user_id = 123;

-- Fast: Index lookup
CREATE INDEX idx_posts_user_id ON posts(user_id);
```

**Rule:** Index foreign keys and frequently queried columns

---

### 2. Fix N+1 Queries

**Bad:**
```python
# 1 query for posts
posts = db.query("SELECT * FROM posts LIMIT 10")

# N queries for authors (10 more queries!)
for post in posts:
    author = db.query(f"SELECT * FROM users WHERE id = {post.user_id}")
```

**Good:**
```python
# 2 queries total
posts = db.query("SELECT * FROM posts LIMIT 10")
user_ids = [p.user_id for p in posts]
authors = db.query(f"SELECT * FROM users WHERE id IN ({','.join(user_ids)})")
```

---

### 3. Use EXPLAIN

```sql
EXPLAIN ANALYZE SELECT * FROM posts WHERE user_id = 123;

-- Output shows:
-- - Seq Scan vs Index Scan
-- - Rows scanned
-- - Execution time
```

---

## Rule of Thumb

- Start with **single database** + good indexes
- Add **caching layer** (Redis) before scaling DB
- Use **read replicas** for read-heavy workloads
- **Shard only as last resort** (adds massive complexity)
- **Denormalize** selectively for hot paths
- Always use **connection pooling**