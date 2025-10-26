
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from enum import Enum

from apis.document_management.models import User

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


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class UserResponse(User):
    """User profile data"""
    pass


class ItemResponse(BaseModel):
    """File or folder with metadata"""
    id: int
    item_name: str
    type: ItemType
    owner_id: int
    owner: Optional[UserResponse]  # Nested for UI display
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



class ItemCreateRequest(BaseModel):
    """Create file or folder"""
    item_name: str = Field(..., max_length=255)
    type: ItemType
    parent_id: Optional[int] = None


class ItemUpdateRequest(BaseModel):
    """Update item metadata"""
    item_name: Optional[str] = Field(None, max_length=255)
    is_starred: Optional[bool] = None


class ItemMoveRequest(BaseModel):
    """Move item to different parent"""
    parent_id: Optional[int]  # None = root


class FileUploadInitiateRequest(BaseModel):
    """Start file upload (check for deduplication)"""
    item_name: str = Field(..., max_length=255)
    parent_id: Optional[int] = None
    size_bytes: int = Field(..., gt=0)
    mime_type: Optional[str] = None
    checksum: str  # SHA-256 hex string


class FileUploadInitiateResponse(BaseModel):
    """Upload details (may be deduplicated)"""
    item_id: int
    version_id: int
    upload_url: Optional[str]  # Pre-signed S3 URL (if not deduplicated)
    deduplicated: bool  # True if file already exists
    message: str


class FileVersionResponse(BaseModel):
    """Version history entry"""
    id: int
    item_id: int
    version_number: int
    size_bytes: int
    mime_type: Optional[str]
    created_by: int
    created_by_user: Optional[UserResponse]
    created_at: datetime
    model_config = ConfigDict(
        from_attributes= True
    )

class PermissionResponse(BaseModel):
    """Permission entry"""
    id: int
    item_id: int
    user_id: int
    user: Optional[UserResponse]
    permission_type: PermissionType
    granted_by: int
    granted_at: datetime
    model_config = ConfigDict(
        from_attributes= True
    )



class PermissionGrantRequest(BaseModel):
    """Grant permission to user"""
    user_id: int
    permission_type: PermissionType


class ShareLinkResponse(BaseModel):
    """Public/private share link"""
    id: int
    item_id: int
    token: str
    permission_type: Literal["read", "write"]
    has_password: bool  # Don't expose actual password
    expires_at: Optional[datetime]
    access_count: int
    created_by: int
    created_at: datetime
    model_config = ConfigDict(
        from_attributes= True
    )



class ShareLinkCreateRequest(BaseModel):
    """Create share link"""
    permission_type: Literal["read", "write"]
    password: Optional[str] = None
    expires_at: Optional[datetime] = None


class ShareLinkAccessRequest(BaseModel):
    """Access shared item"""
    password: Optional[str] = None


class TagResponse(BaseModel):
    """Tag definition"""
    id: int
    name: str
    usage_count: int
    created_at: datetime
    model_config = ConfigDict(
        from_attributes= True
    )


class ItemTagsUpdateRequest(BaseModel):
    """Update item's tags"""
    tag_ids: List[int]


class SearchRequest(BaseModel):
    """Search query"""
    query: str
    type: Optional[ItemType] = None
    parent_id: Optional[int] = None
    tags: Optional[List[str]] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)


class AuditLogEntryResponse(BaseModel):
    """Audit log entry"""
    id: int
    item_id: Optional[int]
    user_id: Optional[int]
    user: Optional[UserResponse]
    action: AuditAction
    metadata: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime

    model_config = ConfigDict(
        from_attributes= True
    )


class PaginatedResponse(BaseModel):
    """Standard pagination wrapper"""
    data: List[dict]
    page: int
    page_size: int
    total: int
    has_next: bool


class SuccessResponse(BaseModel):
    success: bool
    message: Optional[str] = None
