from projects.document_management.models import Item, ItemType


class FileUploadService:
    def __init__(self,item_repo,blob_repo):
        self.item_repo = item_repo
        self.blob_repo = blob_repo
    
    def create_item_for_upload(self,name,parent_id,owner_id):
        if parent_id:
            parent = self.item_repo.get_by_id(parent_id)
            full_path = f"{parent.full_path}/{name}"
            path_depth = parent.path_depth +1
        else:
            full_path=f"/{name}"
            path_depth = 0
        # create the object

        item = Item(           
        item_name= name,
        type = ItemType.FILE,
        owner_id= owner_id,
        parent_id=parent_id,
        full_path= full_path,
        path_depth=path_depth
        )

        # delegate saving to repository
        return self.item_repo.save(item)






        