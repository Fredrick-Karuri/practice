# Caching Strategies

## TTL Strategy by Data Type

| Data Type | Cache Layer | TTL | Reason |
|-----------|-------------|-----|--------|
| User profiles | Redis | 5 min | Changes rarely, read often |
| Post content | Redis | 1 min | Likes/comments change frequently |
| Feed data | Redis | 30-60s | Needs freshness, high read volume |
| Session data | Redis | 24 hours | Fast access, expires naturally |
| Database queries | DB query cache | auto | Repeated identical queries |

---

## Cache Patterns

### 1. Cache-Aside (Lazy Loading)

✅ Most common pattern  
✅ Cache populated on demand  
❌ Initial request is slow (cache miss)

**Flow:**
- **Read:** Check cache → Miss → Fetch DB → Store cache → Return
- **Write:** Update DB → Invalidate cache

**Implementation:**

```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_decorator(ttl_seconds: int, key_prefix: str):
    """Cache-aside pattern decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{args[0]}"
            
            # Try cache first
            cached = redis_client.get(cache_key)
            if cached:
                print(f"Cache HIT: {cache_key}")
                return json.loads(cached)
            
            # Cache miss - fetch from source
            print(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(cache_key, ttl_seconds, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage
@cache_decorator(ttl_seconds=300, key_prefix="user")
def get_user_profile(user_id: int):
    # This would hit the database
    return {
        "id": user_id,
        "username": "johndoe",
        "follower_count": 1500
    }
```

---

### 2. Write-Through

✅ Cache always in sync  
❌ Every write hits cache + DB (slower writes)

**Flow:**
- **Read:** Check cache → Hit → Return
- **Write:** Update DB → Update cache

**When to use:** Data that must always be consistent

---

### 3. Write-Behind (Write-Back)

✅ Fastest writes  
❌ Risk of data loss (cache ahead of DB)

**Flow:**
- **Read:** Check cache → Hit → Return
- **Write:** Update cache → Queue DB write (async)

**When to use:** High-write workloads where eventual consistency is acceptable

---

### 4. Refresh-Ahead

✅ Proactively refresh hot data  
❌ Complex to implement

**Flow:** Background job refreshes cache before expiry

**When to use:** Predictable access patterns with expensive queries

---

## Cache Invalidation

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
    def update_counter(key: str, delta: int):
        """
        Update cached counters atomically
        Pattern: Write-through for counters
        """
        redis_client.incrby(key, delta)
        # Also update in database
        # db.execute("UPDATE posts SET like_count = like_count + %s", delta)
```

---

## Cache Key Design

### Best Practices

**Hierarchical keys:**
```
user:123
user:123:posts
user:123:followers
post:456
post:456:comments
```

**Include version in key for schema changes:**
```
user:v2:123
post:v1:456
```

**Use consistent separators:**
- Use `:` as delimiter
- Keep keys under 200 characters
- Make keys human-readable for debugging

---

## Cache Hit Rate Optimization

### 90/10 Rule
90% of requests hit 10% of data - focus caching effort here

### Strategies

1. **Identify hot data:**
   - Track access frequency
   - Cache top 10% most accessed items
   - Use longer TTLs for hot data

2. **Monitor hit rates:**
   ```python
   hits = redis_client.info('stats')['keyspace_hits']
   misses = redis_client.info('stats')['keyspace_misses']
   hit_rate = hits / (hits + misses)
   # Target: > 80% for hot data
   ```

3. **Preload cache:**
   - Warm cache after deployment
   - Background job for predictable data

4. **Layered caching:**
   - L1: In-memory (fastest, smallest)
   - L2: Redis (fast, medium)
   - L3: Database (slow, complete)

---

## When to Use What

### Redis
- Session storage
- Real-time counters (likes, views)
- Leaderboards (sorted sets)
- Rate limiting
- Hot user profiles
- Recent activity feeds

### Memcached
- Simple key-value caching
- Lighter than Redis
- No persistence needed

### Application Cache (In-Memory)
- Configuration data
- Rarely changing reference data
- Small datasets

---

## Common Pitfalls

❌ **Cache stampede:** Multiple requests for expired key hit DB simultaneously
- **Solution:** Use mutex/lock when refreshing cache

❌ **Stale data:** Cache serves old data after DB update
- **Solution:** Proper invalidation strategy

❌ **Memory bloat:** Cache grows unbounded
- **Solution:** Set maxmemory policy (LRU eviction)

❌ **Over-caching:** Caching data that's rarely accessed
- **Solution:** Monitor hit rates, only cache hot data

---

## Rule of Thumb

- Cache data that's **read often** but **changes rarely**
- Use TTLs appropriate to data freshness requirements
- Always have an invalidation strategy
- Monitor cache hit rates (target: > 80%)
- Start simple (cache-aside), optimize later