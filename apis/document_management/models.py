

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


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
    pass

class Item(BaseModel):
    pass

class FileVersion(BaseModel):
    pass

class AuditLog(BaseModel):
    pass