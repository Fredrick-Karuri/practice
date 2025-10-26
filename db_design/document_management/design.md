# Document Management System - Design Documentation

## Overview

This document outlines the design decisions, trade-offs, and implementation considerations for a production-ready document management system similar to Google Drive, Dropbox, or OneDrive.

**Target Scale:**
- 10M+ users
- 1B+ files
- 100K concurrent users
- Sub-100ms response times for common operations

---

## Core Design Decisions

### 1. Unified Items Table (Files + Folders)

**Decision:** Store both files and folders in a single `items` table.

**Rationale:**
- Simplifies hierarchy queries (no JOIN between separate tables)
- Consistent permission model for both types
- Polymorphic pattern enables easy addition of new types
- Reduced code complexity

**Trade-offs:**
- Some columns only apply to files (e.g., `current_version_id`)
- Slight storage overhead for NULL values

**Alternative Considered:** Separate `files` and `folders` tables (rejected due to complex JOINs and duplicate permission logic)

---

### 2. Hybrid Hierarchy: Adjacency List + Materialized Path

**Decision:** Combine adjacency list (`parent_id`) with materialized path (`full_path`).

**Rationale:**
- **Adjacency list** (`parent_id`): Simple inserts, updates, and deletes
- **Materialized path** (`full_path`): Instant path lookups without recursive queries
- Best of both worlds for read-heavy workloads

**Trade-offs:**
- Must update `full_path` when folders are moved/renamed
- Requires maintaining consistency between both representations

**Performance:**
- Path lookup: O(1) index scan
- Move operation: Update current item + all descendants

**Alternatives Considered:**
- **Pure adjacency list:** Slow for deep hierarchies (recursive CTEs)
- **Closure table:** O(N²) storage, complex updates
- **Nested sets:** Extremely complex updates (renumbering)

---

### 3. Content-Addressable Blob Storage with Deduplication

**Decision:** Store file content once per unique content, using SHA-256 checksums.

**Rationale:**
- Same file uploaded multiple times = stored once
- Typical storage savings: 40-70%
- Reference counting prevents premature deletion
- Storage layer (S3) separate from metadata (PostgreSQL)

**Implementation:**
```
blob_storage table:
- checksum (SHA-256, primary key)
- storage_key (S3 bucket + object path)
- reference_count (number of versions using this blob)
- size_bytes
```

**Trade-offs:**
- Complexity in managing reference counts
- Requires atomic increment/decrement operations
- Need periodic reconciliation to detect drift

---

### 4. Version History Without Full Duplication

**Decision:** Each version references `blob_storage` table.

**Rationale:**
- Multiple versions with same content = same blob reference
- Only store metadata per version (timestamp, user, version number)
- Minimal storage overhead

**Example:**
```
Version 1: "Hello" → blob_abc123
Version 2: "Hello World" → blob_def456
Version 3: "Hello" → blob_abc123 (reuses first blob)
```

**Trade-offs:**
- Deleting items requires careful reference counting
- Must handle race conditions in concurrent operations

---

### 5. Materialized View for Effective Permissions

**Decision:** Precompute inherited permissions in a materialized view.

**Rationale:**
- Permission checks are read-heavy (every file access)
- Recursive CTE on every check = slow at scale
- Materialized view = simple index lookup

**Performance Impact:**
- Without materialized view: 500ms+ for deep hierarchies
- With materialized view: <10ms (index lookup)

**Trade-offs:**
- Eventual consistency (refresh needed after permission changes)
- Refresh overhead (mitigated by CONCURRENTLY option)

**Refresh Strategy:**
- On permission change: `REFRESH MATERIALIZED VIEW CONCURRENTLY`
- Scheduled: Every 5 minutes (background job)
- Requires unique index on `(item_id, user_id)` for concurrent refresh

---

### 6. Owner Always Has Admin Permission

**Decision:** File/folder owners always have implicit admin permission.

**Rationale:**
- Owners shouldn't be locked out of their own content
- Matches user expectations (industry standard behavior)
- Simplifies permission logic

**Implementation:** Materialized view includes owner permissions automatically

---

### 7. Soft Deletes with Trash/Recycle Bin

**Decision:** Use `deleted_at` timestamp instead of hard deletes.

**Rationale:**
- 30-day recovery period (user expectation)
- Accidental deletes are common
- Regulatory/compliance requirements

**Implementation:**
```sql
-- All queries must include:
WHERE deleted_at IS NULL

-- Or use a view:
CREATE VIEW active_items AS 
SELECT * FROM items WHERE deleted_at IS NULL;
```

**Trade-offs:**
- Queries must always filter deleted items
- Storage overhead for deleted items (until permanent deletion)

---

### 8. Normalized Tags Table

**Decision:** Separate `tag_names` and `item_tags` tables.

**Rationale:**
- Tag name stored once, not per file
- Enables tag autocomplete
- Prevents typos (Important vs important vs IMPORTANT)
- Track tag popularity

**Storage Savings:** ~90% vs storing tag names with each item

---

### 9. Share Links with Tokens

**Decision:** UUID-based tokens for public sharing.

**Rationale:**
- Public sharing without user accounts
- Unguessable tokens (not sequential IDs)
- Optional password protection and expiration
- Access tracking for analytics

**Security:**
- Use `gen_random_uuid()` (cryptographically secure)
- Never use sequential IDs
- Rate limit access attempts

---

### 10. Audit Log for Compliance

**Decision:** Store all actions in `audit_log` table.

**Rationale:**
- Track who did what, when
- Regulatory requirements (GDPR, HIPAA)
- Security investigations
- User activity analytics

**Implementation:**
- Use JSONB for flexible metadata
- Partition by date (monthly/yearly)
- Append-only (no UPDATEs allowed)

**Trade-offs:**
- High write volume
- Large table growth (requires archival strategy)

---

### 11. Storage Quotas Per User

**Decision:** Track `storage_used_bytes` per user.

**Rationale:**
- Prevent abuse
- Monetization (paid tiers)
- Resource management

**Consistency:**
- Update atomically with file operations
- Periodic reconciliation (weekly background job)
- Handle edge cases (concurrent uploads)

---

### 12. Permission Types: Read, Write, Admin

**Decision:** Three permission levels.

**Definitions:**
- **read:** View and download
- **write:** Edit, upload new versions
- **admin:** Delete, manage permissions

**Owner:** Always has implicit admin permission

**Trade-offs:**
- Less granular than some systems (e.g., no separate "download" permission)
- Covers 99% of use cases with simpler model

---

## Query Performance

### Fast Queries (with proper indexing)

| Operation | Expected Latency | Index Used |
|-----------|-----------------|------------|
| List folder contents (50 items) | <50ms | `(parent_id, item_name)` |
| Check permission | <10ms | Materialized view |
| Get current version | <5ms | Direct pointer |
| Search by name | <100ms | GIN index |
| Get user's files | <50ms | `owner_id` |
| Access share link | <10ms | `token` |

### Slow Queries

| Operation | Issue | Mitigation |
|-----------|-------|------------|
| Deep path calculation | Recursive CTE | Use `full_path` column |
| Folder size calculation | Sum all descendants | Cache result, update incrementally |
| Complex searches | Multiple OR conditions | Use full-text search |
| Audit log queries | High volume | Partition by date |
| Permission inheritance | Recursive | Materialized view |

---

## Scaling Considerations

### What Would Break at Scale

#### 1. Deep Folder Nesting (100+ levels)

**Problem:** Recursive CTEs become exponentially slow.

**Solutions:**
- Limit max depth to 20 levels (UI enforcement)
- Use materialized path exclusively
- Show warning when approaching limit

---

#### 2. Permission Check Latency

**Problem:** Every file access = database query.

**Solutions:**
- Cache permissions in Redis (5 min TTL)
- Include permission info in JWT token
- Batch permission checks

---

#### 3. Large Folders (100K+ files)

**Problem:** Listing folder contents = huge result set.

**Solutions:**
- Cursor-based pagination (not OFFSET)
- Index on `(parent_id, created_at)`
- Virtual scrolling in UI

---

#### 4. Version Accumulation (1000+ versions per file)

**Problem:** `file_versions` table grows huge.

**Solutions:**
- Limit to last 50 versions
- Auto-delete versions >1 year old (configurable)
- Archive older versions to cheaper storage

---

#### 5. Materialized View Refresh

**Problem:** Large refreshes can cause latency spikes.

**Solutions:**
- Use triggers for incremental updates
- Accept 5-minute delay (eventual consistency)
- Refresh during low-traffic periods

---

#### 6. Blob Storage Reference Counting

**Problem:** Race conditions in concurrent operations.

**Solutions:**
- Use database transactions for all operations
- Optimistic locking with version numbers
- Row-level locks during count updates

---

#### 7. Orphaned Blobs in S3

**Problem:** PostgreSQL knows blob exists, but S3 file deleted.

**Solutions:**
- Regular reconciliation job (compare DB vs S3)
- Store checksum in S3 metadata
- Validate on access

---

#### 8. Audit Log Growth

**Problem:** Billions of rows after a few years.

**Solutions:**
- Partition by month/year
- Archive to data warehouse after 90 days
- Use separate database for audit logs
- Retention policy (delete after 7 years)

---

#### 9. Share Link Abuse

**Problem:** Public links getting crawled/scraped.

**Solutions:**
- Rate limiting per token
- CAPTCHA after N failed password attempts
- Auto-expire after 30 days of no use
- Suspicious pattern detection

---

#### 10. Storage Quota Drift

**Problem:** `storage_used_bytes` out of sync with reality.

**Solutions:**
- Database triggers on version create/delete
- Background reconciliation job (weekly)
- Alert on >5% drift

---

## Transaction Boundaries

Operations that must be atomic:

### 1. Upload File
```sql
BEGIN;
  -- Insert/update blob_storage (increment reference count)
  -- Insert item (if new) or new version (if existing)
  -- Update current_version_id pointer
  -- Update user storage_used_bytes
  -- Insert audit log entry
COMMIT;
```

### 2. Delete File Permanently
```sql
BEGIN;
  -- Decrement blob_storage.reference_count
  -- Delete blob from S3 if reference_count = 0
  -- Delete item (CASCADE handles versions, permissions)
  -- Update user storage_used_bytes
  -- Insert audit log entry
COMMIT;
```

### 3. Move Item
```sql
BEGIN;
  -- Update parent_id
  -- Update full_path (this item + all descendants)
  -- Insert audit log entry
COMMIT;
```

### 4. Share with User
```sql
BEGIN;
  -- Insert permissions record
  -- Mark materialized view for refresh
  -- Send notification (external system)
  -- Insert audit log entry
COMMIT;
```

---

## Permission Inheritance Strategy

### Option 1: Recursive Query

**How it works:** Walk up folder tree to find permission.

**Pros:**
- Always accurate
- No cache invalidation

**Cons:**
- Slow (N queries for N-deep path)

---

### Option 2: Materialized View (Implemented)

**How it works:** Precompute all effective permissions.

**Pros:**
- Fast lookups (O(1) index scan)
- Scales well

**Cons:**
- Eventual consistency
- Refresh overhead

---

### Option 3: Denormalized Cache Table (Production Recommendation)

**How it works:** Triggers update cache on changes.

**Pros:**
- Fast + always accurate
- Best of both worlds

**Cons:**
- Complex trigger logic
- Harder to debug

---

### Option 4: Application-Level Cache (Redis)

**How it works:** Cache permission checks in Redis.

**Pros:**
- Extremely fast
- Reduces DB load

**Cons:**
- Requires Redis infrastructure
- Cache invalidation complexity

---

## Storage Backend

### S3 / Blob Storage

- Store actual file content (not in PostgreSQL)
- `storage_key` = S3 bucket + object key
- Use presigned URLs for downloads (avoid proxying)
- Enable S3 versioning as backup
- S3 lifecycle policies for archival

### Content Delivery Network (CDN)

- Serve popular files through CloudFront/CloudFlare
- Reduce latency for global users
- Cache based on `storage_key` + version
- Invalidate cache when version changes

### File Processing

- Generate thumbnails for images (async job)
- Extract text for search (async job)
- Scan for viruses (before allowing access)
- Convert documents to web formats

---

## Indexing Strategy

### 1. Composite Index: `(parent_id, item_name)`

**Used for:** List folder contents query

**Why composite:** Filter by `parent_id` AND sort by `item_name`

PostgreSQL can use this for both operations efficiently.

---

### 2. Partial Index: `WHERE deleted_at IS NULL`

**Benefit:** Only indexes non-deleted items (95%+ of data)

**Result:**
- Smaller index = faster queries
- Deleted items rarely queried

---

### 3. GIN Index for Full-Text Search

**Enables:**
```sql
WHERE to_tsvector('english', item_name) @@ query
```

**Benefits:**
- Much faster than ILIKE for search
- Supports advanced search features

**Trade-offs:**
- Larger index
- Slower inserts

---

### 4. Unique Index on Materialized View

**Enables:** `REFRESH MATERIALIZED VIEW CONCURRENTLY`

**Requirement:** Unique index on `(item_id, user_id)`

**Benefit:** Non-blocking refresh (production requirement)

---

## Caching Strategy

### Layer 1: Application Cache (Redis)

**Cache for 5 minutes:**
- User's effective permissions
- Recent folder listings
- Popular file metadata

**Invalidate on:**
- Permission changes
- Item moves
- Deletes

**Key format:** `"perms:user:123:item:456"` → `"read"`

---

### Layer 2: CDN Cache

**Cache:**
- File content from edge locations
- Cache-Control headers based on file type

**Invalidate on:**
- New version uploaded

**Security:**
- Presigned URLs expire after 1 hour

---

### Layer 3: Database Query Cache

**PostgreSQL:**
- `shared_buffers` for hot indexes
- `pg_stat_statements` to identify slow queries
- `EXPLAIN ANALYZE` for query optimization

---

## Migration Strategy

For existing systems converting to this schema:

### Phase 1: Migrate Users and Folder Structure
- Convert to adjacency list
- Build `full_path` column
- Validate hierarchy (no cycles)

### Phase 2: Migrate Files and Versions
- Calculate checksums for existing files
- Upload to blob storage
- Create `file_versions` records
- Update `current_version_id` pointers

### Phase 3: Deduplicate Content
- Find files with identical content
- Merge to single `blob_storage` entry
- Update reference counts
- Delete duplicate blobs from S3

### Phase 4: Migrate Permissions
- Convert old permission model
- Build `effective_permissions` materialized view
- Validate permissions work correctly

### Phase 5: Add New Features
- Share links
- Tags
- Audit log (from this point forward)

---

## Backup Strategy

### Database Backups
- Daily full backup
- Continuous WAL archiving (point-in-time recovery)
- Test restores monthly

### Blob Storage Backups
- S3 versioning enabled
- Cross-region replication
- Lifecycle policy: Archive to Glacier after 90 days

### Disaster Recovery
- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 15 minutes
- Automated failover to secondary region

---

## Monitoring & Alerting

### Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Permission check latency | <50ms p95 | >100ms |
| Folder listing latency | <200ms p95 | >500ms |
| Upload success rate | >99.9% | <99% |
| Storage quota accuracy | ±2% | >5% drift |
| Materialized view freshness | <5 min | >10 min |
| Blob reference count accuracy | 100% | Any discrepancy |

### Alerts

- Slow queries (>1 second)
- Failed uploads
- Storage quota exceeded
- Orphaned blobs detected
- Permission check failures
- Materialized view refresh failures

---

## Security Considerations

### 1. SQL Injection
- Always use parameterized queries
- Never concatenate user input into SQL

### 2. Path Traversal
- Validate `item_name` doesn't contain `../`
- Check permission before returning item

### 3. Permission Bypass
- Always check permissions in queries
- Don't trust client-side permission claims
- Use `effective_permissions` view consistently

### 4. Share Link Security
- Use cryptographically random tokens (`gen_random_uuid`)
- Never use sequential IDs as share tokens
- Rate limit access attempts
- Optional password protection for sensitive files

### 5. Storage Key Exposure
- Never return `storage_key` to client
- Use presigned URLs with short expiration
- Validate checksum on download (prevent tampering)

### 6. Audit Log Integrity
- Append-only table (no UPDATEs allowed)
- Use database triggers to prevent tampering
- Regular backups to immutable storage

---

## Performance Benchmarks

**Expected with proper indexing:**

| Operation | Latency | Notes |
|-----------|---------|-------|
| List folder (50 items) | <50ms | |
| Check permission | <10ms | With materialized view |
| Search by name | <100ms | With GIN index |
| Upload file (10MB) | <2s | S3 latency dominant |
| Get version history | <20ms | |
| Calculate folder size (1000 files) | <500ms | |

**Scaling targets:**
- 10M users
- 1B files
- 100K concurrent users
- 10K uploads/second
- 100K permission checks/second

---

## Cost Optimization

### 1. Storage
- Deduplication saves 40-70% storage costs
- S3 Intelligent Tiering for automatic archival
- Delete orphaned blobs (`reference_count = 0`)

### 2. Database
- Use read replicas for queries
- Partition `audit_log` table by date
- Archive old data to data warehouse

### 3. Bandwidth
- Use CDN to reduce egress from S3
- Compress files before storage
- Delta encoding for document versions

---

## Future Enhancements

### Phase 2
- Real-time collaboration (WebSocket, operational transforms)
- Comments and annotations
- Activity feed (recent changes)
- Favorites/starred items
- Recent files list

### Phase 3
- File preview generation (thumbnails, PDFs)
- Full-text content search (Elasticsearch)
- Advanced sharing (expiring links, view-only)
- Team workspaces (shared folders)

### Phase 4
- File encryption at rest (client-side)
- Compliance features (retention policies)
- Advanced analytics (storage reports, access patterns)
- Integrations (Slack, email)

---

## Testing Strategy

### Unit Tests
- Permission inheritance logic
- Checksum calculation
- Reference counting
- Path calculation

### Integration Tests
- Upload → version → download flow
- Share link access
- Permission changes
- Soft delete → restore

### Performance Tests
- Load test: 10K concurrent users
- Stress test: Permission checks
- Endurance test: 24-hour continuous uploads

### Data Integrity Tests
- Reference count accuracy
- Storage quota accuracy
- No orphaned blobs
- No permission bypass

---

## Deployment Checklist

### Before Launch
- [ ] Load test with production-like data volume
- [ ] Set up monitoring and alerts
- [ ] Configure database backups
- [ ] Enable S3 versioning
- [ ] Set up CDN
- [ ] Security audit (penetration testing)
- [ ] Disaster recovery drill
- [ ] Document runbooks for common issues

### Post-Launch Monitoring
- [ ] Query performance (slow query log)
- [ ] Error rates (upload failures)
- [ ] Storage growth rate
- [ ] Permission check latency
- [ ] Materialized view freshness

---

## Common Pitfalls to Avoid

### 1. Forgetting `deleted_at` Filter
**Always add:** `WHERE deleted_at IS NULL`

**Or create view:**
```sql
CREATE VIEW active_items AS 
SELECT * FROM items WHERE deleted_at IS NULL;
```

### 2. Not Refreshing Materialized View
After permission changes, must refresh or set up trigger/background job.

### 3. Reference Count Bugs
Always increment/decrement in same transaction. Run periodic reconciliation.

### 4. Path Traversal Attacks
Validate `item_name`: no `../` or absolute paths. Check permissions before returning.

### 5. Exposing `storage_key` to Clients
Always use presigned URLs. Never return raw S3 paths.

### 6. Not Handling S3 Eventual Consistency
After upload, S3 may not immediately return file. Add retry logic with exponential backoff.

### 7. Infinite Loops in Hierarchy
Prevent with: `CHECK (id != parent_id)`. Validate on update: not ancestor of self.

---

## Summary

This schema provides a production-ready document management system with:

✅ Hierarchical folder structure (self-referencing)  
✅ Version history with deduplication  
✅ Permission inheritance (with caching)  
✅ Soft deletes (30-day trash)  
✅ Share links with expiration  
✅ Audit logging for compliance  
✅ Storage quotas per user  
✅ Full-text search  
✅ Tag-based organization  
✅ Blob storage integration (S3)  

**Performance Characteristics:**
- Optimized for read-heavy workload (90% reads, 10% writes)
- Supports 10M+ users, 1B+ files
- Sub-100ms response times for common operations
- Horizontal scaling via read replicas

**Trade-offs Made:**
- Complexity of reference counting for deduplication
- Eventual consistency for permission cache
- Storage overhead for materialized paths
- Recursive queries for deep hierarchies (mitigated)

This design mirrors how real-world systems like **Google Drive**, **Dropbox**, and **OneDrive** handle document management at scale, balancing performance, data integrity, and feature richness while remaining maintainable.