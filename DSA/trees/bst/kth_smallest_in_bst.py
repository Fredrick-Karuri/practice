# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    """
    THE PROBLEM: Find kth smallest value in BST (I-indexed) (Problem 230)

    PATTERN: Inorder Traversal DFS

    INSIGHT: In-order traversal of BST visits nodes in ascending order.
    Stop after vising k nodes.

    THE PLAN: 
    1. Perform in-order traversal (left -> node -> right)
    2. Count nodes visited
    3. Return value when count reaches k

    Example: BST[3,1,4,null,2], k =1
    In-order: 1, 2, 3, 4
    Return: 1

    TIME O(k) - stop after k nodes
    SPACE: O(h) - recursion stack

    """
    def kthSmallest(self, root: TreeNode | None , k: int) -> int:
        nodes_visited = 0
        result = None

        def inorder_traversal(node):
            nonlocal nodes_visited, result

            if not node or nodes_visited >= k:
                return
            
            # Traverse left subtree
            inorder_traversal(node.left)

            # Process current node
            nodes_visited += 1
            if nodes_visited == k:
                result = node.val
                return
            
            # Traverse right subtree
            inorder_traversal(node.right)
        
        inorder_traversal(root)
        return result
        