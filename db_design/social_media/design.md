# Social Media Platform - Design Documentation

## Core Design Decisions

### 1. Denormalized Counts in Posts Table

**Decision:** Store `like_count` and `comment_count` directly in `posts`.

**Rationale:**
- Feed display requires counts for every post
- `COUNT(*)` queries on every post load = expensive at scale
- Read-heavy workload (feeds viewed much more than likes added)

**Implementation:**
```sql
-- Increment on like
UPDATE posts SET like_count = like_count + 1 WHERE id = ?;

-- Or use triggers
CREATE TRIGGER increment_like_count
AFTER INSERT ON likes
FOR EACH ROW
EXECUTE FUNCTION update_like_count();
```

**Trade-off:** Write complexity vs read performance (critical for feeds)

---

### 2. Separate Follows Table

**Decision:** Use dedicated `follows` table, not followers array in users.

**Rationale:**
- Efficient bidirectional queries (followers AND following)
- Easy pagination of large follower lists
- Simplified feed generation (just JOIN on follows)

**Query examples:**
```sql
-- Get followers
SELECT follower_id FROM follows WHERE followed_id = ?;

-- Get following
SELECT followed_id FROM follows WHERE follower_id = ?;

-- Get feed (posts from users I follow)
SELECT p.* FROM posts p
JOIN follows f ON p.user_id = f.followed_id
WHERE f.follower_id = ?
ORDER BY p.created_at DESC;
```

---

### 3. Composite Index on (user_id, created_at)

**Decision:** Index posts on `(user_id, created_at)`.

**Rationale:**
- Feed queries filter by user AND sort by date
- PostgreSQL can use composite index for both operations
- Critical for feed generation performance

**Trade-off:** Increased index size and slower inserts (minimal impact for read-heavy workload)

---

### 4. CASCADE Deletes

**Decision:** CASCADE on user deletion to posts/likes/comments/follows.

**Rationale:**
- Account deletion removes all user content
- Maintains referential integrity automatically
- Prevents orphaned records

**Alternative:** Soft deletes (`deleted_at`) for audit trail and recovery

**Implementation:**
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

---

### 5. Content Length Constraints

**Decision:** Enforce length limits at database level.

**Example:**
```sql
content VARCHAR(280) CHECK (length(content) > 0)
bio VARCHAR(500)
```

**Rationale:**
- Prevents abuse and storage bloat
- Enforces business rules consistently
- Database-level validation catches app bugs

**Trade-off:** Schema changes needed for limit adjustments

---

## Query Performance

### Fast Queries

| Operation | Index/Optimization |
|-----------|-------------------|
| User feed | `(user_id, created_at)` composite |
| User's posts | `(user_id, created_at)` |
| Follower count | Denormalized counter |
| Like count | Denormalized counter |
| Check if following | Unique index on `(follower_id, followed_id)` |

### Slow Queries

| Operation | Issue | Solution |
|-----------|-------|----------|
| Content search | Full table scan | Add GIN full-text search index |
| Trending posts | Complex aggregation | Materialized view, updated hourly |
| Explore feed | Random sampling | Precompute hot posts in cache |

---

## Scaling Improvements

### 1. Full-Text Search

```sql
CREATE INDEX idx_posts_content_search 
ON posts USING GIN (to_tsvector('english', content));
```

Enables fast content search without ILIKE.

---

### 2. Partition Posts Table

**Strategy:** Partition by date for large datasets (100M+ posts).

```sql
CREATE TABLE posts_2024_q1 PARTITION OF posts
FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

**Benefit:** Query only relevant partitions

---

### 3. Read Replicas

**Setup:** Separate read/write database instances.

- **Writes:** User posts, likes, follows → Primary
- **Reads:** Feed generation, search → Replicas

**Benefit:** Reduces load on primary database

---

### 4. Caching Layer (Redis)

**Cache strategy:**
- User feeds (TTL: 5 minutes)
- Hot posts (trending content)
- User profiles
- Follower/following counts

**Invalidation:** On new post, like, or follow action

---

### 5. Soft Deletes

**Add column:**
```sql
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;
```

**Benefits:**
- Account recovery
- Audit trail
- Analytics on deleted accounts

**Queries must filter:**
```sql
WHERE deleted_at IS NULL
```

---

## Transaction Boundaries

### Create Post with Media
```sql
BEGIN;
  -- Insert post
  -- Upload media to S3
  -- Insert media references
  -- Update user post_count
COMMIT;
```

### Like Post
```sql
BEGIN;
  -- Insert like record
  -- Increment post like_count
  -- Create notification
COMMIT;
```

### Follow User
```sql
BEGIN;
  -- Insert follow record
  -- Increment followed_user follower_count
  -- Increment follower_user following_count
  -- Create notification
COMMIT;
```

---

## Feed Generation Strategies

### Option 1: Pull Model (Query on Load)

```sql
SELECT p.* FROM posts p
JOIN follows f ON p.user_id = f.followed_id
WHERE f.follower_id = ? AND p.created_at > ?
ORDER BY p.created_at DESC
LIMIT 20;
```

**Pros:** Always fresh, simple  
**Cons:** Slow for users following many accounts

---

### Option 2: Push Model (Precompute)

On post creation, write to all followers' feeds:
```sql
INSERT INTO feed_cache (user_id, post_id, created_at)
SELECT follower_id, ?, ? FROM follows WHERE followed_id = ?;
```

**Pros:** Fast read  
**Cons:** High write amplification (celebrity with 10M followers)

---

### Option 3: Hybrid Model (Recommended)

- **Regular users (<10K followers):** Push to feed cache
- **Celebrities (>10K followers):** Pull on demand
- Cache results for 5 minutes

**Best of both:** Fast for most users, scales for celebrities

---

## Monitoring Metrics

| Metric | Target | Alert |
|--------|--------|-------|
| Feed load time | <200ms | >1s |
| Post creation time | <100ms | >500ms |
| Like/follow latency | <50ms | >200ms |
| Cache hit rate | >90% | <70% |
| Database CPU | <60% | >80% |

---

## Common Pitfalls

### 1. Not Updating Denormalized Counts
Use triggers or ensure atomic updates in application.

### 2. N+1 Query Problem
Load post authors in single query:
```sql
SELECT * FROM posts WHERE id IN (...)
JOIN users ON posts.user_id = users.id;
```

### 3. Missing Unique Constraint
Prevent duplicate follows/likes:
```sql
UNIQUE (follower_id, followed_id)
UNIQUE (user_id, post_id)  -- for likes
```

### 4. Unbounded Feed Queries
Always use LIMIT and pagination:
```sql
LIMIT 20 OFFSET ?  -- or cursor-based
```

### 5. Not Indexing Foreign Keys
Slow JOINs and CASCADE operations.

---

## Future Enhancements

**Phase 2:**
- Direct messaging
- Hashtags and mentions
- Post editing with edit history
- Polls and rich media

**Phase 3:**
- Stories/ephemeral content
- Verification badges
- Advanced search
- Content recommendations (ML)

**Phase 4:**
- Live streaming
- Spaces/audio rooms
- Analytics dashboard
- API for third-party apps

---

## Summary

This schema provides a scalable social media platform with:

✅ Fast feed generation via composite indexes  
✅ Efficient follower/following queries  
✅ Denormalized counts for performance  
✅ Clean CASCADE deletion behavior  
✅ Database-level constraints  

**Performance:** Sub-200ms feed loads with proper caching

**Scaling path:** Read replicas → Caching → Sharding/partitioning