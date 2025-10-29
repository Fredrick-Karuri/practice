from fastapi import HTTPException
from projects.document_management.models import User


class StorageQuotaService:
    def __init__(self):
        pass
  
    
    def check_quota(self,user:User,additional_bytes:int) ->None:
        """ 
        Check if user has enough quota for additional storage
        Raises Exception if quota exceeded
        
        """
        if user.storage_used_bytes +additional_bytes > user.storage_quota_bytes:
            raise HTTPException(status_code=400, detail="storage quota exceeded")