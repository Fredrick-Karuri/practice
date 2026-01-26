class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    """
    THE PROBLEM: Build tree from inorder and preorder traversals (Problem 105)

    PATTERN: Recursion + Hashmap

    INSIGHT:
    - Preorder: first element is root
    - Inorder: elements before root are left subtree, after are right
    - Recursively build left and right subtrees

    THE PLAN:
    1.First element in preorder is root
    2.Find root in inorder to split left/right subtrees
    3.Recursively build left and right
    4.Use hashmap for O(1) lookup for root position

    TIME: O(n)
    SPACE: O(n)
    """
    def buildTree(self, preorder: list[int], inorder: list[int]) -> TreeNode | None:
        value_to_index_inorder = {val:idx for idx, val in enumerate(inorder)}
        preorder_index = 0

        def build_subtree(left_boundary, right_boundary):
            nonlocal preorder_index

            if left_boundary > right_boundary:
                return None
            
            root_value = preorder[preorder_index]
            root = TreeNode(root_value)
            preorder_index += 1

            root_position_in_inorder = value_to_index_inorder[root_value]

            root.left = build_subtree(left_boundary,root_position_in_inorder - 1 )
            root.right = build_subtree(root_position_in_inorder + 1, right_boundary)

            return root
        
        return build_subtree(0,len(inorder) - 1)
        