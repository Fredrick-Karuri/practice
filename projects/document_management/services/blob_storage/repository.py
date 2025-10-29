from typing import Optional
from projects.document_management.models import BlobStorage


class BlobRepository:
    def get_by_checksum(self, checksum:bytes)->Optional[BlobStorage]:
        """ Finds a blob by its checksum, returns None if not found"""
        pass