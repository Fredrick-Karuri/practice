# Social Media API - Design Documentation

## Core Design Decisions

### 1. Nested User Data in Responses

**Decision:** Include user objects within post responses.

**Example:**
```json
{
  "id": "post_123",
  "content": "Hello world",
  "user": {
    "id": "user_456",
    "username": "johndoe",
    "avatar_url": "..."
  }
}
```

**Rationale:**
- Avoids N+1 query problem
- Feed with 20 posts would require 20 additional API calls without nesting
- Single request loads all necessary data

**Trade-off:** Larger response payloads vs fewer HTTP requests (better overall)

**Alternative:** Separate `/users/:id` endpoint (rejected due to performance)

---

### 2. Denormalized Counts

**Decision:** Store counts in main entities (`like_count`, `follower_count`).

**Rationale:**
- Displayed on every post/profile view
- `COUNT(*)` on large tables is slow
- Read optimization for read-heavy workload

**Trade-off:** Increased write complexity and eventual consistency

**Alternative:** Calculate on read (too slow at scale)

---

### 3. Pagination on All List Endpoints

**Decision:** Require `page` and `page_size` parameters.

**Standard format:**
```json
{
  "data": [...],
  "page": 2,
  "page_size": 20,
  "has_more": true
}
```

**Rationale:**
- Prevents returning millions of records
- Predictable response times
- Protects against accidental DDoS

**Alternative:** Cursor-based pagination (better for real-time feeds, recommended for production)

---

### 4. POST /users/:id/follow (Not PUT)

**Decision:** Use POST verb for follow action.

**Rationale:**
- POST semantically represents creating a relationship
- Idempotent behavior: return 400 if already following
- Industry standard pattern

**Alternative considered:**
```http
PUT /users/:id/relationships
{ "type": "follow" }
```
Rejected as less intuitive.

---

### 5. Separate Like/Unlike Endpoints

**Decision:** Distinct endpoints instead of toggle.

**Endpoints:**
```http
POST /posts/:id/like
DELETE /posts/:id/like
```

**Rationale:**
- Explicit intent (client knows desired state)
- Avoids race conditions (double-click scenarios)
- Clearer semantics

**Trade-off:** Client must track like state

**Alternative:** Single toggle endpoint (simpler client, more complex server logic)

---

### 6. No Total Count in Pagination

**Decision:** Omit `total_count` from paginated responses.

**Response structure:**
```json
{
  "data": [...],
  "has_more": true
}
```

**Rationale:**
- `COUNT(*)` on complex feed queries is expensive
- Users don't need exact count (just "has more" indicator)
- Common pattern in modern APIs (Twitter, Instagram)

**Trade-off:** Cannot display "Page X of Y"

**Alternative:** Estimate total or calculate asynchronously

---

### 7. Version in URL Path

**Decision:** Include API version in URL: `/v1/...`

**Rationale:**
- Breaking changes inevitable over time
- Gradual client migration path
- Explicit and visible to developers

**Trade-off:** Maintaining multiple versions simultaneously

**Alternative:** Version in header (less discoverable)

---

### 8. Bearer Token Authentication

**Decision:** JWT-based stateless authentication.

**Header format:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Rationale:**
- Stateless (no session storage required)
- Works with mobile apps and SPAs
- Horizontal scaling friendly
- Standard pattern with expiry

**Trade-off:** Token size in every request

**Alternative:** Session cookies (stateful, harder to scale)

---

## API Endpoints Overview

### Authentication
```http
POST /v1/auth/register
POST /v1/auth/login
POST /v1/auth/refresh
POST /v1/auth/logout
```

### Users
```http
GET    /v1/users/:id
PUT    /v1/users/:id
GET    /v1/users/:id/posts
GET    /v1/users/:id/followers
GET    /v1/users/:id/following
POST   /v1/users/:id/follow
DELETE /v1/users/:id/follow
```

### Posts
```http
GET    /v1/posts/:id
POST   /v1/posts
DELETE /v1/posts/:id
POST   /v1/posts/:id/like
DELETE /v1/posts/:id/like
GET    /v1/posts/:id/comments
```

### Feed
```http
GET /v1/feed?page=1&page_size=20
```

---

## Scaling Challenges

### 1. Feed Generation

**Problem:** 100M users following 1000 people each.

**Solutions:**
- **Pre-compute feeds:** Fan-out on write for regular users
- **Redis caching:** Store hot feeds in memory
- **Hybrid approach:** Pull for celebrities, push for regular users
- **Async processing:** Background jobs for feed updates

---

### 2. Like Counter Race Conditions

**Problem:** High-traffic posts receive thousands of likes per second.

**Solutions:**
- **Queue-based updates:** Buffer likes, batch updates
- **Eventual consistency:** Accept slight delays in counts
- **Redis counters:** Atomic increments, sync to DB periodically
- **Sharding:** Distribute counter updates

---

### 3. Deep Pagination

**Problem:** `OFFSET 10000 LIMIT 20` scans entire dataset.

**Solution:** Cursor-based pagination
```http
GET /v1/feed?cursor=post_abc123&limit=20

Response:
{
  "data": [...],
  "next_cursor": "post_xyz789"
}
```

**Implementation:**
```sql
SELECT * FROM posts 
WHERE created_at < ? 
ORDER BY created_at DESC 
LIMIT 20;
```

---

### 4. Real-Time Updates

**Problem:** Feed should update live without manual refresh.

**Solutions:**
- **WebSockets:** Real-time push for new posts
- **Server-Sent Events (SSE):** One-way updates
- **Long polling:** Fallback for older clients
- **Hybrid:** WebSocket for primary, polling for fallback

---

## Caching Strategy

### Cache Duration by Resource

| Resource | TTL | Rationale |
|----------|-----|-----------|
| User profiles | 5 minutes | Rarely change |
| Posts | 30 seconds | Likes/comments change frequently |
| Feeds | 1 minute | Balance freshness vs load |
| Static assets | 1 year | Immutable with cache busting |

### HTTP Caching Headers

```http
Cache-Control: public, max-age=300
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

**Benefits:**
- `304 Not Modified` responses reduce bandwidth
- CDN caching for public content
- Client-side caching reduces requests

---

## Error Handling

### Standard Error Format

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Content cannot be empty",
    "field": "content"
  }
}
```

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (delete success) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid token) |
| 403 | Forbidden (permission denied) |
| 404 | Not Found |
| 429 | Too Many Requests (rate limit) |
| 500 | Internal Server Error |

---

## Rate Limiting

### Strategy

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

**Limits by endpoint type:**
- **Read endpoints:** 1000 requests/hour
- **Write endpoints:** 100 requests/hour
- **Authentication:** 10 requests/hour

**Implementation:** Redis with sliding window algorithm

---

## Monitoring & Observability

### Key Metrics

| Metric | Target | Alert |
|--------|--------|-------|
| API response time (p95) | <200ms | >500ms |
| Error rate | <1% | >5% |
| Cache hit rate | >80% | <60% |
| Feed generation time | <500ms | >2s |
| Authentication latency | <50ms | >200ms |

### Logging

**Log levels:**
- **INFO:** Successful operations
- **WARN:** Rate limits hit, slow queries
- **ERROR:** Failures, exceptions

**Structured logging format:**
```json
{
  "timestamp": "2025-10-26T10:30:00Z",
  "level": "INFO",
  "endpoint": "/v1/posts",
  "method": "POST",
  "user_id": "user_123",
  "duration_ms": 45
}
```

---

## Security Considerations

### 1. Input Validation
- Sanitize all user input
- Enforce length limits
- Validate content types

### 2. Authentication
- JWT with short expiry (15 minutes)
- Refresh tokens for renewal
- Rotate secrets regularly

### 3. Authorization
- Check permissions on every request
- Use middleware for consistent enforcement
- Never trust client-side validation

### 4. Rate Limiting
- Per-user and per-IP limits
- Exponential backoff for repeated violations
- Whitelist for internal services

### 5. CORS Configuration
```python
CORS(
    origins=["https://app.example.com"],
    allow_credentials=True,
    max_age=3600
)
```

---

## Testing Strategy

### Unit Tests
- Request/response validation
- Business logic
- Error handling

### Integration Tests
- End-to-end API flows
- Database interactions
- Authentication/authorization

### Load Tests
- Feed generation under load
- Concurrent like operations
- Rate limit effectiveness

---

## API Versioning Strategy

### When to Create v2

Breaking changes requiring new version:
- Removing fields from responses
- Changing field types
- Modifying authentication mechanism
- Restructuring endpoint hierarchy

Non-breaking changes (no new version):
- Adding optional fields
- Adding new endpoints
- Expanding enum values
- Bug fixes

### Deprecation Process

1. Announce deprecation 6 months ahead
2. Add `Deprecation` header to v1 responses
3. Document migration guide
4. Monitor v1 usage metrics
5. Sunset v1 after 12 months

---

## Common Pitfalls

### 1. Not Paginating Results
Always paginate. Even "small" lists grow over time.

### 2. Exposing Database IDs
Use UUIDs or opaque identifiers to prevent enumeration attacks.

### 3. Missing Idempotency
POST endpoints should be idempotent when possible (duplicate follow/like handling).

### 4. No Rate Limiting
Protects against abuse and accidental DDoS.

### 5. Inconsistent Error Responses
Use standard error format across all endpoints.

### 6. Not Using HTTP Status Codes Correctly
200 for errors with `{"error": "..."}` is an anti-pattern.

---

## Future Enhancements

**Phase 2:**
- GraphQL endpoint (flexible queries)
- Webhooks for integrations
- Batch operations API

**Phase 3:**
- Media upload with preprocessing
- Advanced search with filters
- Analytics API

**Phase 4:**
- WebSocket API for real-time
- Admin API (separate from public API)
- Public API for third-party developers

---

## Summary

This API design provides a scalable, maintainable REST API with:

✅ **Performance:** Nested data avoids N+1 queries  
✅ **Scalability:** Cursor pagination, caching, denormalized counts  
✅ **Security:** JWT auth, rate limiting, input validation  
✅ **Developer Experience:** Clear semantics, versioning, error handling  
✅ **Observability:** Structured logging, metrics, monitoring  

**Architecture:** Stateless, horizontally scalable, cache-friendly  
**Performance targets:** Sub-200ms p95 response times with caching