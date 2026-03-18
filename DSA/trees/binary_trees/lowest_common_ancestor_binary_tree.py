class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

class Solution:
    """
    THE PROBLEM: Find lowest common ancestor of two nodes in a binary tree - Problem 236

    PATTERNS:  DFS (Post order traversal)

    INSIGHT: LCA  is the first node where p and q are in different subtrees, 
    or the node itself is p or q

    THE PLAN: 
    1. Base case: If node is None, p, or q -> return node
    2. Recursively search left and right subtrees
    3. If both sides return non-null -> current node is LCA
    4. Otherwise return whichever side found a node

    Example: tree=[3,5,1,6,2,0,8], p=5, q=1
    - Left of 3 finds 5, right finds 1 → LCA is 3

    TIME : O(n)
    SPACE: O(h) where h is tree height
    """
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        if not root or root == p or root == q:
            return root

        left_result = self.lowestCommonAncestor(root.left, p ,q)
        right_result = self.lowestCommonAncestor(root.right, p, q)

        both_subtrees_contain_a_node = left_result and right_result

        if both_subtrees_contain_a_node:
            return root
        
        return left_result or right_result
        