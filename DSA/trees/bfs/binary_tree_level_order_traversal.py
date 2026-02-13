class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    """
    THE PROBLEM: Return nodes grouped by level (left to right) (Problem 102)

    PATTERN: BFS(Breadth-First Search)

    INSIGHT: Use queue to process nodes level by level

    THE PLAN:
    1.Use queue starting with root
    2.For each level process all nodes in queue
    3.Add children to queue for the next level
    4.Store value for current level

    Example: Input: root = [3,9,20,null,null,15,7]
        - Level 1: [3]
        - Level 2: [9, 20]
        - Level 3: [15, 7]
    Output: [[3],[9,20],[15,7]]

    TIME: O(n)
    SPACE: O(w) where w is the max width of tree

    """
    def levelOrder(self, root: TreeNode | None) -> list[list[int]]:
        if not root:
            return []
        
        levels_grouped_by_depth:list[list[int]] = []
        nodes_at_current_depth:list[TreeNode] = [root]

        while nodes_at_current_depth:
            values_at_current_depth:list[int] = []
            nodes_at_next_depth:list[TreeNode] = []

            self._process_current_level(
                levels_grouped_by_depth, 
                nodes_at_current_depth, 
                values_at_current_depth, 
                nodes_at_next_depth
            )
        return levels_grouped_by_depth

    def _process_current_level(
        self, 
        levels_grouped_by_depth:list[list[int]], 
        nodes_at_current_depth:list[TreeNode], 
        values_at_current_depth:list[int], 
        nodes_at_next_depth:list[TreeNode]
    )-> None:
        for current_node in nodes_at_current_depth:
            values_at_current_depth.append(current_node.val)

            if current_node.left:
                nodes_at_next_depth.append(current_node.left)
                
            if current_node.right:
                nodes_at_next_depth.append(current_node.right)
            
        levels_grouped_by_depth.append(values_at_current_depth)
        nodes_at_current_depth = nodes_at_next_depth

        