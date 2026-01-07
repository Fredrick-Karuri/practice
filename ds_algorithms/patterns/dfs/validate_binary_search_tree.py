class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    """
    THE PROBLEM: Validate if binary tree is valid BST - Problem 98

    PATTERN: DFS with range validation

    INSIGHT: Each node must be within a valid range. Pass min/max bounds down
    the tree. Left child < node < right child isn't enough - must check against 
    ancestor bounds too.

    THE PLAN: 
    1. Use DFS with min/max bounds
    2.Check if current node value is within bounds
    3.Recursively validate left (update max bound) and right(update min bound)

    Example: [5,1,4,null,null,3,6] is INVALID
    - Node 4 < 5 violates BST (4 should be > root 5)

    TIME: O(n)
    SPACE: O(h) where h is height

    """
    def isValidBST(self, root: TreeNode | None) -> bool:
        
        is_bst_valid = self.validate(root,float('-inf'),float('inf'))
        return is_bst_valid

    def validate(self,node, min_val:float, max_val:float):
        if not node:
            return True
        
        # Check if current node violates bounds
        if not (min_val < node.val < max_val):
            return False
        
        # Validate left and right subtrees
        return (
            self.validate(node.left,min_val,node.val) and
            self.validate(node.right, node.val, max_val)
        )