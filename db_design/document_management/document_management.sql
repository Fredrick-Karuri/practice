-- Document Management System Database Schema
-- Design Goal: Google Drive-like file storage with folders, versions, permissions, and sharing

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    display_name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Storage quota management
    storage_quota_bytes BIGINT DEFAULT 10737418240, -- 10GB default
    storage_used_bytes BIGINT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_storage CHECK (storage_used_bytes >= 0),
    CONSTRAINT valid_quota CHECK (storage_quota_bytes > 0)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_display_name ON users(display_name);


-- ============================================
-- ITEMS TABLE (Files and Folders)
-- ============================================
CREATE TABLE items (
    id BIGSERIAL PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    type VARCHAR(10) NOT NULL,
    owner_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    
    -- Self-referencing for folder hierarchy (adjacency list pattern)
    parent_id BIGINT REFERENCES items(id) ON DELETE CASCADE,
    
    -- Pointer to current version (NULL for folders, required for files)
    current_version_id BIGINT NULL,
    
    -- Materialized path for fast lookups (e.g., "/Documents/Work/Project")
    full_path TEXT,
    path_depth INT DEFAULT 0,
    
    -- Metadata
    is_starred BOOLEAN DEFAULT false,
    last_accessed_at TIMESTAMP,
    
    -- Soft deletes for trash/recycle bin
    deleted_at TIMESTAMP NULL,
    deleted_by BIGINT REFERENCES users(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_type CHECK (type IN ('file', 'folder')),
    CONSTRAINT no_self_parent CHECK (id != parent_id),
    CONSTRAINT version_for_files CHECK (
        (type = 'folder' AND current_version_id IS NULL) OR
        (type = 'file')
    )
);

-- Critical indexes for performance
CREATE INDEX idx_items_parent_name ON items(parent_id, item_name) WHERE deleted_at IS NULL;
CREATE INDEX idx_items_owner ON items(owner_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_items_type ON items(type) WHERE deleted_at IS NULL;
CREATE INDEX idx_items_full_path ON items(full_path) WHERE deleted_at IS NULL;
CREATE INDEX idx_items_deleted ON items(deleted_at) WHERE deleted_at IS NOT NULL;

-- Full-text search index for item names
CREATE INDEX idx_items_name_search ON items USING gin(to_tsvector('english', item_name)) 
    WHERE deleted_at IS NULL;


-- ============================================
-- BLOB STORAGE (Content-addressable storage)
-- ============================================
CREATE TABLE blob_storage (
    checksum BYTEA PRIMARY KEY, -- SHA-256 hash of content
    storage_key VARCHAR(500) UNIQUE NOT NULL, -- S3/blob storage path
    size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100),
    
    -- Reference counting for deduplication
    reference_count INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_size CHECK (size_bytes >= 0),
    CONSTRAINT positive_refs CHECK (reference_count >= 0)
);

CREATE INDEX idx_blob_storage_refs ON blob_storage(reference_count);


-- ============================================
-- FILE VERSIONS TABLE
-- ============================================
CREATE TABLE file_versions (
    id BIGSERIAL PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    version_number INT NOT NULL,
    
    -- Reference to deduplicated blob storage
    blob_checksum BYTEA NOT NULL REFERENCES blob_storage(checksum),
    
    created_by BIGINT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_version CHECK (version_number > 0),
    CONSTRAINT unique_version UNIQUE (item_id, version_number)
);

CREATE INDEX idx_file_versions_item ON file_versions(item_id, version_number DESC);
CREATE INDEX idx_file_versions_blob ON file_versions(blob_checksum);

-- Add foreign key from items to file_versions (completes circular reference)
ALTER TABLE items 
ADD CONSTRAINT fk_items_current_version 
FOREIGN KEY (current_version_id) 
REFERENCES file_versions(id) ON DELETE RESTRICT;


-- ============================================
-- PERMISSIONS TABLE
-- ============================================
CREATE TABLE permissions (
    id BIGSERIAL PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_type VARCHAR(20) NOT NULL,
    
    granted_by BIGINT NOT NULL REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_permission CHECK (permission_type IN ('read', 'write', 'admin')),
    CONSTRAINT unique_permission UNIQUE (item_id, user_id)
);

CREATE INDEX idx_permissions_item_user ON permissions(item_id, user_id);
CREATE INDEX idx_permissions_user ON permissions(user_id);


-- ============================================
-- TAG NAMES TABLE (Normalized tags)
-- ============================================
CREATE TABLE tag_names (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tag_names_name ON tag_names(name);


-- ============================================
-- ITEM TAGS TABLE (Many-to-Many)
-- ============================================
CREATE TABLE item_tags (
    item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES tag_names(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (item_id, tag_id)
);

CREATE INDEX idx_item_tags_tag ON item_tags(tag_id);


-- ============================================
-- SHARE LINKS TABLE (Public/private sharing)
-- ============================================
CREATE TABLE share_links (
    id BIGSERIAL PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    token VARCHAR(64) UNIQUE NOT NULL, -- Random UUID for URL
    permission_type VARCHAR(20) NOT NULL,
    
    -- Optional password protection
    password_hash VARCHAR(255) NULL,
    
    -- Expiration
    expires_at TIMESTAMP NULL,
    
    -- Tracking
    access_count INT DEFAULT 0,
    created_by BIGINT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_share_permission CHECK (permission_type IN ('read', 'write'))
);

CREATE INDEX idx_share_links_token ON share_links(token) WHERE expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP;
CREATE INDEX idx_share_links_item ON share_links(item_id);


-- ============================================
-- AUDIT LOG TABLE (Track all actions)
-- ============================================
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    item_id BIGINT REFERENCES items(id) ON DELETE SET NULL,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    
    -- Additional context as JSON
    metadata JSONB,
    
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_action CHECK (action IN (
        'create', 'read', 'update', 'delete', 'restore',
        'share', 'unshare', 'download', 'upload', 
        'rename', 'move', 'permission_grant', 'permission_revoke'
    ))
);

CREATE INDEX idx_audit_log_item ON audit_log(item_id, created_at DESC);
CREATE INDEX idx_audit_log_user ON audit_log(user_id, created_at DESC);
CREATE INDEX idx_audit_log_action ON audit_log(action, created_at DESC);


-- ============================================
-- MATERIALIZED VIEW: Effective Permissions
-- ============================================
CREATE MATERIALIZED VIEW effective_permissions AS
WITH RECURSIVE inherited_perms AS (
    -- Base case: Direct permissions
    SELECT 
        p.item_id,
        p.user_id,
        p.permission_type,
        i.parent_id,
        0 as inheritance_depth,
        i.owner_id
    FROM permissions p
    JOIN items i ON p.item_id = i.id
    WHERE i.deleted_at IS NULL
    
    UNION
    
    -- Recursive case: Inherited from parent folders
    SELECT 
        i.id as item_id,
        ip.user_id,
        ip.permission_type,
        i.parent_id,
        ip.inheritance_depth + 1,
        i.owner_id
    FROM items i
    JOIN inherited_perms ip ON i.parent_id = ip.item_id
    WHERE i.deleted_at IS NULL
      AND ip.inheritance_depth < 20  -- Prevent infinite loops, max depth
),
-- Add owner permissions (owners always have admin)
owner_perms AS (
    SELECT 
        id as item_id,
        owner_id as user_id,
        'admin' as permission_type,
        -1 as inheritance_depth
    FROM items
    WHERE deleted_at IS NULL
)
-- Combine and get closest permission (lowest inheritance_depth wins)
SELECT DISTINCT ON (item_id, user_id)
    item_id,
    user_id,
    permission_type
FROM (
    SELECT * FROM inherited_perms
    UNION ALL
    SELECT item_id, user_id, permission_type, inheritance_depth FROM owner_perms
) combined
ORDER BY item_id, user_id, inheritance_depth ASC;

-- Indexes on materialized view
CREATE UNIQUE INDEX idx_effective_permissions_item_user ON effective_permissions(item_id, user_id);
CREATE INDEX idx_effective_permissions_user ON effective_permissions(user_id);

-- Refresh function (call after permission changes)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY effective_permissions;


-- ============================================
-- EXAMPLE QUERIES
-- ============================================

-- 1. List folder contents with permissions
SELECT 
    i.id,
    i.item_name,
    i.type,
    i.created_at,
    i.updated_at,
    u.display_name as owner_name,
    bs.size_bytes,
    bs.mime_type,
    ep.permission_type as user_permission,
    ARRAY_AGG(tn.name) FILTER (WHERE tn.name IS NOT NULL) as tags
FROM items i
JOIN users u ON i.owner_id = u.id
LEFT JOIN file_versions fv ON i.current_version_id = fv.id
LEFT JOIN blob_storage bs ON fv.blob_checksum = bs.checksum
LEFT JOIN effective_permissions ep ON i.id = ep.item_id AND ep.user_id = ?
LEFT JOIN item_tags it ON i.id = it.item_id
LEFT JOIN tag_names tn ON it.tag_id = tn.id
WHERE i.parent_id = ? -- Or IS NULL for root
  AND i.deleted_at IS NULL
  AND (ep.permission_type IS NOT NULL OR i.owner_id = ?) -- Has permission or is owner
GROUP BY i.id, u.display_name, bs.size_bytes, bs.mime_type, ep.permission_type
ORDER BY i.type DESC, i.item_name ASC; -- Folders first


-- 2. Get full path using recursive CTE
WITH RECURSIVE path AS (
    SELECT 
        id, 
        item_name, 
        parent_id, 
        item_name as path,
        1 as depth
    FROM items
    WHERE id = ?
    
    UNION ALL
    
    SELECT 
        i.id, 
        i.item_name, 
        i.parent_id, 
        i.item_name || '/' || p.path,
        p.depth + 1
    FROM items i
    JOIN path p ON i.id = p.parent_id
)
SELECT '/' || path as full_path, depth
FROM path 
WHERE parent_id IS NULL;


-- 3. Check if user has permission (using materialized view)
SELECT 
    COALESCE(ep.permission_type, 
        CASE WHEN i.owner_id = ? THEN 'admin' END
    ) as permission
FROM items i
LEFT JOIN effective_permissions ep ON i.id = ep.item_id AND ep.user_id = ?
WHERE i.id = ?;


-- 4. Create new file with version (TRANSACTION)
BEGIN;

-- Insert into blob_storage (with deduplication)
INSERT INTO blob_storage (checksum, storage_key, size_bytes, mime_type, reference_count)
VALUES (?, ?, ?, ?, 1)
ON CONFLICT (checksum) DO UPDATE 
SET reference_count = blob_storage.reference_count + 1
RETURNING checksum;

-- Create item (without version initially)
INSERT INTO items (item_name, type, owner_id, parent_id, full_path, path_depth)
VALUES (?, 'file', ?, ?, ?, ?)
RETURNING id;

-- Create version
INSERT INTO file_versions (item_id, version_number, blob_checksum, created_by)
VALUES (?, 1, ?, ?)
RETURNING id;

-- Update item with current_version_id
UPDATE items SET current_version_id = ? WHERE id = ?;

-- Update user's storage usage
UPDATE users 
SET storage_used_bytes = storage_used_bytes + ?
WHERE id = ?;

-- Log action
INSERT INTO audit_log (item_id, user_id, action, metadata)
VALUES (?, ?, 'upload', ?);

COMMIT;


-- 5. Create new version of existing file
BEGIN;

-- Increment reference count for blob (or create new)
INSERT INTO blob_storage (checksum, storage_key, size_bytes, mime_type, reference_count)
VALUES (?, ?, ?, ?, 1)
ON CONFLICT (checksum) DO UPDATE 
SET reference_count = blob_storage.reference_count + 1;

-- Get next version number
SELECT COALESCE(MAX(version_number), 0) + 1 
FROM file_versions 
WHERE item_id = ?;

-- Create new version
INSERT INTO file_versions (item_id, version_number, blob_checksum, created_by)
VALUES (?, ?, ?, ?)
RETURNING id;

-- Update item's current_version_id
UPDATE items 
SET current_version_id = ?, updated_at = CURRENT_TIMESTAMP
WHERE id = ?;

-- Update storage usage (delta)
UPDATE users 
SET storage_used_bytes = storage_used_bytes + (? - ?)
WHERE id = ?;

COMMIT;


-- 6. Move item to different folder (with path update)
BEGIN;

-- Update parent_id
UPDATE items 
SET parent_id = ?, updated_at = CURRENT_TIMESTAMP
WHERE id = ?;

-- Rebuild materialized path (simplified - production would use trigger)
UPDATE items
SET full_path = ? || '/' || item_name,
    path_depth = ?
WHERE id = ?;

-- Log action
INSERT INTO audit_log (item_id, user_id, action, metadata)
VALUES (?, ?, 'move', jsonb_build_object('from_parent', ?, 'to_parent', ?));

COMMIT;


-- 7. Soft delete (move to trash)
UPDATE items 
SET deleted_at = CURRENT_TIMESTAMP, deleted_by = ?
WHERE id = ?;


-- 8. Restore from trash
UPDATE items 
SET deleted_at = NULL, deleted_by = NULL
WHERE id = ?;


-- 9. Permanent delete with cleanup
BEGIN;

-- Get all versions for this item
WITH item_versions AS (
    SELECT blob_checksum, bs.size_bytes
    FROM file_versions fv
    JOIN blob_storage bs ON fv.blob_checksum = bs.checksum
    WHERE fv.item_id = ?
)
-- Decrement reference counts
UPDATE blob_storage
SET reference_count = reference_count - 1
WHERE checksum IN (SELECT blob_checksum FROM item_versions);

-- Delete orphaned blobs (reference_count = 0)
DELETE FROM blob_storage WHERE reference_count = 0;

-- Update user storage
UPDATE users
SET storage_used_bytes = storage_used_bytes - (
    SELECT COALESCE(SUM(size_bytes), 0) FROM item_versions
)
WHERE id = ?;

-- Delete item (CASCADE will handle versions, permissions, tags)
DELETE FROM items WHERE id = ?;

COMMIT;


-- 10. Search files by name and tags
SELECT DISTINCT
    i.id,
    i.item_name,
    i.full_path,
    u.display_name as owner,
    bs.size_bytes,
    i.updated_at,
    ARRAY_AGG(tn.name) as tags
FROM items i
JOIN users u ON i.owner_id = u.id
LEFT JOIN file_versions fv ON i.current_version_id = fv.id
LEFT JOIN blob_storage bs ON fv.blob_checksum = bs.checksum
LEFT JOIN item_tags it ON i.id = it.item_id
LEFT JOIN tag_names tn ON it.tag_id = tn.id
LEFT JOIN effective_permissions ep ON i.id = ep.item_id AND ep.user_id = ?
WHERE i.type = 'file'
  AND i.deleted_at IS NULL
  AND (
    i.item_name ILIKE '%' || ? || '%'
    OR tn.name = ANY(?)  -- Array of tag names
    OR to_tsvector('english', i.item_name) @@ plainto_tsquery('english', ?)
  )
  AND (ep.permission_type IS NOT NULL OR i.owner_id = ?)
GROUP BY i.id, u.display_name, bs.size_bytes
ORDER BY i.updated_at DESC
LIMIT 50;


-- 11. Get file version history
SELECT 
    fv.version_number,
    fv.created_at,
    u.display_name as created_by,
    bs.size_bytes,
    bs.mime_type,
    i.current_version_id = fv.id as is_current
FROM file_versions fv
JOIN users u ON fv.created_by = u.id
JOIN blob_storage bs ON fv.blob_checksum = bs.checksum
JOIN items i ON fv.item_id = i.id
WHERE fv.item_id = ?
ORDER BY fv.version_number DESC;


-- 12. Generate share link
INSERT INTO share_links (item_id, token, permission_type, expires_at, created_by)
VALUES (?, gen_random_uuid()::text, 'read', CURRENT_TIMESTAMP + INTERVAL '7 days', ?)
RETURNING token;


-- 13. Access file via share link
SELECT 
    i.*,
    sl.permission_type,
    bs.storage_key,
    bs.size_bytes
FROM share_links sl
JOIN items i ON sl.item_id = i.id
JOIN file_versions fv ON i.current_version_id = fv.id
JOIN blob_storage bs ON fv.blob_checksum = bs.checksum
WHERE sl.token = ?
  AND (sl.expires_at IS NULL OR sl.expires_at > CURRENT_TIMESTAMP)
  AND i.deleted_at IS NULL;

-- Increment access count
UPDATE share_links SET access_count = access_count + 1 WHERE token = ?;


-- 14. Get folder size (recursive)
WITH RECURSIVE folder_tree AS (
    SELECT id, parent_id
    FROM items
    WHERE id = ?
    
    UNION ALL
    
    SELECT i.id, i.parent_id
    FROM items i
    JOIN folder_tree ft ON i.parent_id = ft.id
    WHERE i.deleted_at IS NULL
)
SELECT COALESCE(SUM(bs.size_bytes), 0) as total_size
FROM folder_tree ft
JOIN items i ON ft.id = i.id
LEFT JOIN file_versions fv ON i.current_version_id = fv.id
LEFT JOIN blob_storage bs ON fv.blob_checksum = bs.checksum
WHERE i.type = 'file';


-- 15. Find duplicate files (same content)
SELECT 
    bs.checksum,
    bs.size_bytes,
    bs.reference_count,
    ARRAY_AGG(i.item_name) as file_names,
    ARRAY_AGG(i.full_path) as paths
FROM blob_storage bs
JOIN file_versions fv ON bs.checksum = fv.blob_checksum
JOIN items i ON fv.item_id = i.id AND i.current_version_id = fv.id
WHERE bs.reference_count > 1
  AND i.deleted_at IS NULL
GROUP BY bs.checksum, bs.size_bytes, bs.reference_count
ORDER BY bs.size_bytes DESC;
