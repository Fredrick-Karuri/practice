"""
Document Management System REST API Design

Pattern: RESTful with hierarchical resources (Google Drive-like)
Key Insights:
- Content-addressable storage for deduplication
- Soft deletes for trash/restore functionality
- Version history tracking
- Granular permission system
"""


# ============================================
# API ENDPOINTS SPECIFICATION
# ============================================

"""
BASE URL: https://api.docmgmt.com/v1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USER ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /users/me
Description: Get current user profile and storage quota
Response: UserResponse
Status: 200 OK
Headers Required: Authorization: Bearer <token>
Caching: No cache (always current data)

Example Response:
{
  "id": 123,
  "email": "user@example.com",
  "display_name": "John Doe",
  "storage_quota_bytes": 10737418240,
  "storage_used_bytes": 5368709120,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-10-26T09:15:00Z"
}

---

PATCH /users/me
Description: Update user profile
Request Body: { "display_name": "New Name" }
Response: UserResponse
Status: 200 OK
Headers Required: Authorization: Bearer <token>


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ITEM ENDPOINTS (Files & Folders)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /items
Description: List items (root level or by parent_id)
Query Params:
    - parent_id: int (optional, null = root)
    - page: int (default: 1)
    - page_size: int (default: 50, max: 100)
    - type: "file" | "folder" (optional filter)
    - starred: bool (optional filter)
Response: PaginatedResponse<ItemResponse>
Status: 200 OK
Headers Required: Authorization: Bearer <token>
Caching: Cache for 30 seconds

Example Response:
{
  "data": [
    {
      "id": 456,
      "item_name": "Project Proposal.pdf",
      "type": "file",
      "owner_id": 123,
      "parent_id": 789,
      "full_path": "/Work/Projects/Project Proposal.pdf",
      "is_starred": true,
      "size_bytes": 2048576,
      "mime_type": "application/pdf",
      "can_edit": true,
      "created_at": "2024-10-20T14:30:00Z"
    }
  ],
  "page": 1,
  "page_size": 50,
  "total": 150,
  "has_next": true
}

---

GET /items/:id
Description: Get single item details
Response: ItemResponse
Status: 200 OK / 403 Forbidden / 404 Not Found
Headers Required: Authorization: Bearer <token>
Caching: Cache for 1 minute
Side Effects:
    - Update last_accessed_at timestamp
    - Create audit log entry (action: "read")

---

POST /items
Description: Create new folder or file placeholder
Request Body: ItemCreateRequest
Response: ItemResponse
Status: 201 Created / 400 Bad Request / 403 Forbidden
Headers Required: Authorization: Bearer <token>
Side Effects:
    - Create item in database
    - Update parent's updated_at
    - Invalidate parent listing cache
    - Create audit log entry (action: "create")

Example Request:
{
  "item_name": "New Project",
  "type": "folder",
  "parent_id": 789
}

---

PATCH /items/:id
Description: Update item metadata (rename, star)
Request Body: ItemUpdateRequest
Response: ItemResponse
Status: 200 OK / 403 Forbidden / 404 Not Found
Headers Required: Authorization: Bearer <token>
Side Effects:
    - Update item
    - Invalidate item cache
    - Create audit log entry (action: "rename" or "update")

---

POST /items/:id/move
Description: Move item to different parent folder
Request Body: ItemMoveRequest
Response: ItemResponse
Status: 200 OK / 400 Bad Request / 403 Forbidden
Headers Required: Authorization: Bearer <token>
Validation:
    - Cannot move folder into itself or its descendants
    - Must have write permission on both source and destination
Side Effects:
    - Update item.parent_id and full_path
    - Invalidate caches for old and new parent
    - Create audit log entry (action: "move")

---

DELETE /items/:id
Description: Soft delete item (move to trash)
Response: SuccessResponse
Status: 200 OK / 403 Forbidden / 404 Not Found
Headers Required: Authorization: Bearer <token>
Side Effects:
    - Set deleted_at timestamp
    - Set deleted_by user_id
    - Invalidate parent listing cache
    - Create audit log entry (action: "delete")
Note: Files stay in trash for 30 days before permanent deletion


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE UPLOAD ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST /files/upload/initiate
Description: Start file upload (checks for deduplication)
Request Body: FileUploadInitiateRequest
Response: FileUploadInitiateResponse
Status: 201 Created / 400 Bad Request / 403 Forbidden
Headers Required: Authorization: Bearer <token>

CRITICAL: This implements content-addressable storage!

Flow:
1. Client calculates SHA-256 hash of file
2. Server checks if blob with this hash exists
3. If exists: Instant "upload" (just create version record)
4. If not exists: Return pre-signed S3 URL for actual upload

Example Request:
{
  "item_name": "presentation.pptx",
  "parent_id": 789,
  "size_bytes": 5242880,
  "mime_type": "application/vnd.ms-powerpoint",
  "checksum": "a3c5f7e9d2b4..."
}

Example Response (Deduplicated):
{
  "item_id": 1001,
  "version_id": 5,
  "upload_url": null,
  "deduplicated": true,
  "message": "File already exists, version created instantly"
}

Example Response (New Upload):
{
  "item_id": 1001,
  "version_id": 5,
  "upload_url": "https://s3.amazonaws.com/...",
  "deduplicated": false,
  "message": "Upload file to provided URL"
}

Side Effects:
    - Create item record (if new file)
    - Create file_version record
    - Create or reference blob_storage record
    - Increment blob reference count
    - Update user storage_used_bytes
    - Invalidate parent cache
    - Create audit log entry (action: "upload")

---

POST /files/upload/complete
Description: Mark upload as complete (webhook or client confirmation)
Request Body: { "version_id": 5 }
Response: FileVersionResponse
Status: 200 OK / 400 Bad Request
Headers Required: Authorization: Bearer <token>
Side Effects:
    - Verify file exists in S3
    - Update item.current_version_id
    - Trigger virus scanning (async)
    - Trigger thumbnail generation (async)

---

GET /files/:id/download
Description: Download file
Query Params:
    - version: int (optional, default = current version)
Response: Redirect to pre-signed S3 URL or file stream
Status: 200 OK / 302 Found / 403 Forbidden / 404 Not Found
Headers Required: Authorization: Bearer <token>
Side Effects:
    - Update last_accessed_at
    - Create audit log entry (action: "download")


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERSION HISTORY ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /items/:id/versions
Description: Get version history for file
Query Params: page, page_size
Response: PaginatedResponse<FileVersionResponse>
Status: 200 OK / 403 Forbidden / 404 Not Found
Headers Required: Authorization: Bearer <token>
Caching: Cache for 5 minutes

---

POST /items/:id/versions/:version_id/restore
Description: Restore previous version (creates new version)
Response: FileVersionResponse
Status: 201 Created / 403 Forbidden / 404 Not Found
Headers Required: Authorization: Bearer <token>
Side Effects:
    - Create new version pointing to same blob
    - Update item.current_version_id
    - Increment blob reference count
    - Create audit log entry (action: "restore")


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERMISSION ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /items/:id/permissions
Description: List permissions for item
Response: List<PermissionResponse>
Status: 200 OK / 403 Forbidden (only owner/admin can view)
Headers Required: Authorization: Bearer <token>
Caching: Cache for 2 minutes

---

POST /items/:id/permissions
Description: Grant permission to user
Request Body: PermissionGrantRequest
Response: PermissionResponse
Status: 201 Created / 400 Bad Request / 403 Forbidden
Headers Required: Authorization: Bearer <token>
Validation:
    - Only owner or admin can grant permissions
    - Cannot grant higher permission than you have
Side Effects:
    - Create or update permission record
    - Invalidate item cache
    - Send notification to user (async)
    - Create audit log entry (action: "permission_grant")

Example Request:
{
  "user_id": 456,
  "permission_type": "write"
}

---

DELETE /items/:id/permissions/:permission_id
Description: Revoke permission
Response: SuccessResponse
Status: 200 OK / 403 Forbidden / 404 Not Found
Headers Required: Authorization: Bearer <token>
Side Effects:
    - Delete permission record
    - Invalidate item cache
    - Create audit log entry (action: "permission_revoke")


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SHARE LINK ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /items/:id/share-links
Description: List share links for item
Response: List<ShareLinkResponse>
Status: 200 OK / 403 Forbidden
Headers Required: Authorization: Bearer <token>
Caching: Cache for 1 minute

---

POST /items/:id/share-links
Description: Create public share link
Request Body: ShareLinkCreateRequest
Response: ShareLinkResponse
Status: 201 Created / 403 Forbidden
Headers Required: Authorization: Bearer <token>
Side Effects:
    - Generate random token (UUID)
    - Hash password if provided
    - Create share_link record
    - Create audit log entry (action: "share")

Example Request:
{
  "permission_type": "read",
  "password": "secret123",
  "expires_at": "2024-12-31T23:59:59Z"
}

Example Response:
{
  "id": 789,
  "item_id": 456,
  "token": "a3c5f7e9-d2b4-4a1c-8e3f-9d7b2a5c1e4f",
  "permission_type": "read",
  "has_password": true,
  "expires_at": "2024-12-31T23:59:59Z",
  "access_count": 0,
  "created_at": "2024-10-26T10:00:00Z"
}

---

DELETE /items/:id/share-links/:link_id
Description: Delete share link
Response: SuccessResponse
Status: 200 OK / 403 Forbidden / 404 Not Found
Headers Required: Authorization: Bearer <token>
Side Effects:
    - Delete share_link record
    - Create audit log entry (action: "unshare")

---

GET /shared/:token
Description: Access item via share link (no auth required!)
Request Body: ShareLinkAccessRequest (if password protected)
Response: ItemResponse with download_url
Status: 200 OK / 401 Unauthorized / 404 Not Found / 410 Gone (expired)
Headers Required: None
Side Effects:
    - Increment share_link.access_count
    - Create audit log entry (user_id = null, action: "read")

Example Response:
{
  "id": 456,
  "item_name": "presentation.pptx",
  "type": "file",
  "size_bytes": 5242880,
  "mime_type": "application/vnd.ms-powerpoint",
  "download_url": "https://s3.amazonaws.com/...",
  "permission_type": "read",
  "expires_at": "2024-12-31T23:59:59Z"
}


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TAG ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /tags
Description: List all tags (for autocomplete)
Response: List<TagResponse>
Status: 200 OK
Headers Required: Authorization: Bearer <token>
Caching: Cache for 10 minutes

---

GET /items/:id/tags
Description: Get item's tags
Response: List<TagResponse>
Status: 200 OK / 403 Forbidden / 404 Not Found
Headers Required: Authorization: Bearer <token>
Caching: Cache for 5 minutes

---

PUT /items/:id/tags
Description: Replace item's tags
Request Body: ItemTagsUpdateRequest
Response: List<TagResponse>
Status: 200 OK / 403 Forbidden
Headers Required: Authorization: Bearer <token>
Side Effects:
    - Delete old tag associations
    - Create new tag associations
    - Update tag usage_counts
    - Invalidate item cache

Example Request:
{
  "tag_ids": [1, 5, 12]
}


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEARCH ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST /search
Description: Search files and folders
Request Body: SearchRequest
Response: PaginatedResponse<ItemResponse>
Status: 200 OK
Headers Required: Authorization: Bearer <token>
Caching: Cache for 30 seconds (per unique query)

Query Strategy:
1. Full-text search on item_name (PostgreSQL GIN index)
2. Filter by type, parent_id, tags
3. Only return items user has permission to access
4. Order by relevance (ts_rank)

Example Request:
{
  "query": "budget 2024",
  "type": "file",
  "tags": ["finance", "Q4"],
  "page": 1,
  "page_size": 20
}

Performance Considerations:
- Use PostgreSQL full-text search (GIN index)
- Limit search scope (only accessible items)
- Consider Elasticsearch for advanced search at scale


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRASH/RESTORE ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /trash
Description: List deleted items
Query Params: page, page_size
Response: PaginatedResponse<ItemResponse>
Status: 200 OK
Headers Required: Authorization: Bearer <token>
Caching: No cache (trash changes frequently)

---

POST /trash/:id/restore
Description: Restore item from trash
Response: ItemResponse
Status: 200 OK / 404 Not Found / 409 Conflict (parent deleted)
Headers Required: Authorization: Bearer <token>
Side Effects:
    - Set deleted_at = null
    - Set deleted_by = null
    - Invalidate parent cache
    - Create audit log entry (action: "restore")

---

DELETE /trash/:id
Description: Permanently delete item
Response: SuccessResponse
Status: 200 OK / 404 Not Found
Headers Required: Authorization: Bearer <token>
WARNING: This is irreversible!
Side Effects:
    - Delete item record (CASCADE to versions, permissions)
    - Decrement blob reference counts
    - Delete blobs with reference_count = 0
    - Update user storage_used_bytes
    - Create audit log entry (action: "delete")


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUDIT LOG ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /items/:id/activity
Description: Get activity log for item
Query Params: page, page_size
Response: PaginatedResponse<AuditLogEntryResponse>
Status: 200 OK / 403 Forbidden
Headers Required: Authorization: Bearer <token>
Caching: Cache for 1 minute

Example Response:
{
  "data": [
    {
      "id": 9876,
      "item_id": 456,
      "user_id": 123,
      "user": { UserResponse },
      "action": "download",
      "metadata": { "version": 3 },
      "ip_address": "192.168.1.1",
      "created_at": "2024-10-26T14:30:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 45,
  "has_next": true
}

---

GET /audit/me
Description: Get current user's activity across all items
Query Params: page, page_size, action (filter)
Response: PaginatedResponse<AuditLogEntryResponse>
Status: 200 OK
Headers Required: Authorization: Bearer <token>
Caching: No cache

"""


# ============================================
# API DESIGN DECISIONS & TRADE-OFFS
# ============================================

"""
DECISION 1: Content-addressable storage (blob_storage table)
WHY:
- Deduplicate identical files (save storage)
- Multiple users upload same file = stored once
- Version history doesn't duplicate data
- Trade-off: More complex upload flow, reference counting
ALTERNATIVE: Store each file separately (simpler, but wastes space)

DECISION 2: Soft deletes with trash
WHY:
- Users expect "undo" for deletes (like Google Drive)
- 30-day trash retention before permanent deletion
- Trade-off: More complex queries (WHERE deleted_at IS NULL)
ALTERNATIVE: Hard deletes (simpler, but no recovery)

DECISION 3: Materialized path (full_path column)
WHY:
- Fast breadcrumb display (/Documents/Work/Project)
- Efficient "get all descendants" queries
- Trade-off: Must update all descendants on move
ALTERNATIVE: Recursive queries with adjacency list (slower)

DECISION 4: Separate upload/initiate and upload/complete
WHY:
- Check for deduplication before upload
- Handle large file uploads (client uploads to S3 directly)
- Trade-off: Two-step process, more complex client logic
ALTERNATIVE: Single upload endpoint (simpler, but no deduplication check)

DECISION 5: Permission hierarchy (read < write < admin)
WHY:
- Clear permission model (admin can do everything)
- Simplifies permission checks
- Trade-off: Less granular than ACLs
ALTERNATIVE: Fine-grained ACLs (download, edit, delete, share separately)

DECISION 6: Share links with optional password and expiration
WHY:
- Public sharing without requiring account
- Security: password protection, time limits
- Track access with access_count
- Trade-off: Anonymous access complicates audit logs
ALTERNATIVE: Require recipient to create account (more secure, less convenient)

DECISION 7: Denormalized storage_used_bytes on user
WHY:
- Display storage quota bar on every page load
- Calculating SUM(size_bytes) across all files is slow
- Trade-off: Must update on upload/delete
ALTERNATIVE: Calculate on demand (too slow at scale)

DECISION 8: Audit log for everything
WHY:
- Compliance requirements (who accessed what, when)
- Debug user issues
- Security monitoring
- Trade-off: Large table, storage cost
ALTERNATIVE: Sample logging or shorter retention

DECISION 9: Version history never deleted
WHY:
- Users expect to restore old versions
- Blob deduplication makes storage cheap
- Trade-off: Storage grows forever
ALTERNATIVE: Limit version count or age

DECISION 10: Tags in separate table (normalized)
WHY:
- Autocomplete tags across all items
- Track tag popularity (usage_count)
- Trade-off: JOIN queries, more complex
ALTERNATIVE: JSON array in items table (simpler, no autocomplete)

WHAT WOULD BREAK AT SCALE:
- Full-text search on 100M+ files
  → Solution: Elasticsearch cluster
- Folder hierarchy with 100+ levels deep
  → Solution: Limit depth, use closure table pattern
- Single S3 bucket with billions of files
  → Solution: Partition by user_id or hash prefix
- Reference counting race conditions
  → Solution: Use database transactions, queue for cleanup
- Storage quota checks on every upload
  → Solution: Cache quota, eventual consistency

CACHING STRATEGY:
- User profiles: 5 minutes (rarely change)
- Item listings: 30 seconds (balance freshness)
- Permissions: 2 minutes (security-sensitive)
- Tags: 10 minutes (rarely change)
- Audit logs: 1 minute (near real-time)
- No cache for trash (too dynamic)
- Use ETags for conditional requests

SECURITY CONSIDERATIONS:
- All endpoints require authentication (except /shared/:token)
- Permission checks on every item access
- Rate limiting on search and download endpoints
- Virus scanning on upload completion (async)
- Audit log for security monitoring
- Pre-signed URLs expire after 1 hour
- Share link tokens are UUIDs (unguessable)
"""