from collections import OrderedDict
class LRUCache:
    """
    THE PROBLEM: Implement LRU cache with 0(1) get and put operations.
    PATTERN: Hashmap + Doubly Linkedlist
    INSIGHT: 
    -Hashmap gives 0(1) lookup 
    -Double linked list maintains order(most recent at head, least recent at tail)
    -Combining both, gives 0(1) for all operations
    THE PLAN:
    1.Use OrderedDict (maintains insertion order)
    2.For get:move accessed key to end(most recent)
    3.For put:add/update at end, evict from begining if over capacity
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        #  Move to end (most recent)
        self.cache.move_to_end(key)
        return self.cache[key]
        

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Move to end if exists
            self.cache.move_to_end(key)
            
        self.cache[key] = value

        if len(self.cache) > self.capacity:
            # remove first item (least recent)
            self.cache.popitem(last= False)


        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)