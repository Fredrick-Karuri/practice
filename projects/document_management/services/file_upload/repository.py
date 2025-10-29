from projects.document_management.models import Item


class ItemRepository:
    def save( self , item:Item) -> Item:
        """ 
        save and item tot he database and return the persisted item
        """
        pass
    
    def get_by_id (self,item_id) -> Item:
        """ retrive and item by id """
        pass