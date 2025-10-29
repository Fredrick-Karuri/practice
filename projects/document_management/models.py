

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ============================================
# ENUMS
# ============================================

class ItemType(str, Enum):
    FILE = "file"
    FOLDER = "folder"

class PermissionType(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"
    SHARE = "share"
    UNSHARE = "unshare"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    RENAME = "rename"
    MOVE = "move"
    PERMISSION_GRANT = "permission_grant"
    PERMISSION_REVOKE = "permission_revoke"

class User(BaseModel):
    """User profile data"""
    id: int
    email: str
    display_name: Optional[str]
    storage_quota_bytes: int
    storage_used_bytes: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(
        from_attributes=True
    )

class BlobStorage(BaseModel):
    """ Blob storage"""
    checksum:str
    storage_key:str
    size_bytes:Optional[int]
    mime_type:Optional[str]
    reference_count:Optional[int]
    created_at:datetime

class Item(BaseModel):
    id: int
    item_name: str
    type: ItemType
    owner_id: int
    owner: Optional[User]  # Nested for UI display
    parent_id: Optional[int]
    current_version_id: Optional[int]
    full_path: Optional[str]
    path_depth: int
    is_starred: bool
    last_accessed_at: Optional[datetime]
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    # Computed fields
    size_bytes: Optional[int]  # From current version
    mime_type: Optional[str]
    can_edit: bool  # Based on current user's permissions
    model_config = ConfigDict(
        from_attributes=True
    )


class FileVersion(BaseModel):
    id: int
    item_id: int
    version_number: int
    size_bytes: int
    mime_type: Optional[str]
    created_by: int
    created_by_user: Optional[User]
    created_at: datetime
    model_config = ConfigDict(
        from_attributes= True
    )

class AuditLog(BaseModel):
    id: int
    item_id: Optional[int]
    user_id: Optional[int]
    user: Optional[User]
    action: AuditAction
    metadata: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime
    model_config = ConfigDict(
        from_attributes= True
    )