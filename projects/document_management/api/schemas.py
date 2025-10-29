
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from enum import Enum

from projects.document_management.models import AuditAction, AuditLog, FileVersion, Item, ItemType, PermissionType, User

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class UserResponse(User):
    """User profile data"""
    pass

class UserUpdateRequest(BaseModel):
    display_name: Optional[str]
    email: Optional[str]

class ItemResponse(Item):
    """File or folder with metadata"""
    pass


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


class FileVersionResponse(FileVersion):
    """Version history entry"""
    pass


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


class AuditLogEntryResponse(AuditLog):
    """Audit log entry"""
    pass



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
