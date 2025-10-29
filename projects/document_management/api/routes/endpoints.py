from datetime import datetime
import uuid
from fastapi import (
    APIRouter, Depends, 
    HTTPException, status,
    Query,UploadFile,
    File
)
from sqlalchemy.orm import Session
from ...database import get_db
from ...models import AuditLog, BlobStorage, FileVersion, Item, User
from ..schemas import (
    FileUploadInitiateResponse, 
    ItemType, UserResponse,
    ItemResponse, 
    FileUploadInitiateRequest, 
    UserUpdateRequest
)
from ...auth import get_current_user
from ...storage import generate_presigned_upload_url
from ...cache import invalidate_cache

#====================
#  ROUTERS
#====================

user_router = APIRouter(prefix="/users",tags=["users"])
file_router = APIRouter(prefix="/files",tags=["files"])

#====================
#  USER ENDPOINTS
#====================

@user_router.get("/me",response_model=UserResponse)
async def get_current_user_profile(
    current_user:User = Depends (get_current_user),
    db:Session =Depends(get_db)
):
    """ Get current user profile and storage quota"""
    return current_user

@user_router.patch("/me",response_model=UserResponse)
async def update_user_profile(
    updates:UserUpdateRequest,
    current_user : User = Depends(get_current_user),
    db:Session = Depends(get_db)
):
    """ Update user profile"""
    if updates.display_name:
        current_user.display_name = updates.display_name
    
    commit_user_changes(current_user, db)

def commit_user_changes(current_user, db):
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)


#====================
#  FILE UPLOAD ENDPOINTS
#====================

@file_router.post("/upload/initiate", response_model=FileUploadInitiateResponse, status_code=201)
async def initiate_file_upload(
    upload_data: FileUploadInitiateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start file upload (checks for deduplication)"""
    # Check storage quota
    check_storage_quota(upload_data, current_user)
    
    # Convert hex checksum to bytes
    checksum_bytes = bytes.fromhex(upload_data.checksum)
    
    # Check if blob already exists (deduplication)
    existing_blob = get_existing_blob(db, checksum_bytes)
    
    deduplicated = existing_blob is not None
    
    # Create or get item
    item = get_existing_item(upload_data, current_user, db)
    
    item = initialize_item(upload_data, current_user, db, item)
    
    # Create blob if not exists
    blob = get_or_initialize_blob(upload_data, current_user, db, checksum_bytes, existing_blob)
    
    # Create version
    version = create_file_version(current_user, db, checksum_bytes, item)
    
    # Update item's current_version_id
    item.current_version_id = version.id
    
    # Increment blob reference count
    blob.reference_count += 1
    
    # Update user storage (only if new blob)
    update_user_storage(upload_data, current_user, db, deduplicated, version)
    
    # Generate presigned URL if new upload needed
    upload_url, message = generate_upload_response(upload_data, current_user, db, deduplicated, item, blob)
    
    return FileUploadInitiateResponse(
        item_id=item.id,
        version_id=version.id,
        upload_url=upload_url,
        deduplicated=deduplicated,
        message=message
    )

def get_existing_blob(db, checksum_bytes):
    existing_blob = db.query(BlobStorage).filter(BlobStorage.checksum == checksum_bytes).first()
    return existing_blob

def generate_upload_response(upload_data, current_user:User, db, deduplicated, item:Item, blob:BlobStorage):
    upload_url = None if deduplicated else generate_presigned_upload_url(blob.storage_key)
    
    message = "File already exists, version created instantly" if deduplicated else "Upload file to provided URL"
    
    invalidate_cache(f"items:parent:{upload_data.parent_id}")
    
    audit = AuditLog(item_id=item.id, user_id=current_user.id, action='upload')
    db.add(audit)
    db.commit()
    return upload_url,message

def update_user_storage(upload_data, current_user, db, deduplicated, version):
    if not deduplicated:
        current_user.storage_used_bytes += upload_data.size_bytes
    
    db.commit()
    db.refresh(version)

def create_file_version(current_user, db, checksum_bytes, item):
    last_version = db.query(FileVersion).filter(
        FileVersion.item_id == item.id
    ).order_by(FileVersion.version_number.desc()).first()
    
    version_number = (last_version.version_number + 1) if last_version else 1
    
    version = FileVersion(
        item_id=item.id,
        version_number=version_number,
        blob_checksum=checksum_bytes,
        created_by=current_user.id
    )
    db.add(version)
    db.flush()
    return version

def get_or_initialize_blob(upload_data, current_user, db, checksum_bytes, existing_blob):
    if not existing_blob:
        storage_key = f"blobs/{current_user.id}/{uuid.uuid4()}"
        blob = BlobStorage(
            checksum=checksum_bytes,
            storage_key=storage_key,
            size_bytes=upload_data.size_bytes,
            mime_type=upload_data.mime_type,
            reference_count=0
        )
        db.add(blob)
        db.flush()
    else:
        blob = existing_blob
    return blob

def initialize_item(upload_data, current_user, db, item):
    if not item:
        # Calculate full_path
        if upload_data.parent_id:
            parent = db.query(Item).filter(Item.id == upload_data.parent_id).first()
            full_path = f"{parent.full_path}/{upload_data.item_name}"
            path_depth = parent.path_depth + 1
        else:
            full_path = f"/{upload_data.item_name}"
            path_depth = 0
        
        item = Item(
            item_name=upload_data.item_name,
            type=ItemType.FILE,
            owner_id=current_user.id,
            parent_id=upload_data.parent_id,
            full_path=full_path,
            path_depth=path_depth
        )
        db.add(item)
        db.flush()
    return item

def get_existing_item(upload_data, current_user:User, db):
    item = db.query(Item).filter(
        Item.item_name == upload_data.item_name,
        Item.parent_id == upload_data.parent_id,
        Item.owner_id == current_user.id,
        Item.deleted_at.is_(None)
    ).first()
    
    return item

def check_storage_quota(upload_data, current_user:User):
    if current_user.storage_used_bytes + upload_data.size_bytes > current_user.storage_quota_bytes:
        raise HTTPException(status_code=400, detail="Storage quota exceeded")
