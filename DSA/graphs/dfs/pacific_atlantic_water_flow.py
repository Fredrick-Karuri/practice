class Solution:
    """
    THE PROBLEM: Find cells that can flow to both Pacific and Atlantic oceans (Problem 417)
    
    PATTERN: DFS from ocean borders (reverse flow)
    
    INSIGHT: Instead of checking if each cell reaches both oceans (expensive),
    start from ocean borders and find which cells can reach each ocean.
    Return intersection.
    
    THE PLAN:
    1. DFS from Pacific borders (top, left edges)
    2. DFS from Atlantic borders (bottom, right edges)
    3. Return cells reachable from both
    4. Flow condition: neighbor height >= current (reverse flow)
    
    TIME: O(m × n)
    SPACE: O(m × n)
    """
    def pacificAtlantic(self, heights: list[list[int]]) -> list[list[int]]:
        if not heights:
            return []
        
        num_rows, num_cols = len(heights), len(heights[0])
        cells_reaching_pacific:set[tuple[int,int]] = set()
        cells_reaching_atlantic:set[tuple[int,int]] = set()
        
        
        # Explore from Pacific ocean borders (top and left edges)
        for col in range(num_cols):
            self._explore_from_ocean(0, col, cells_reaching_pacific, num_rows, num_cols, heights)
        for row in range(num_rows):
            self._explore_from_ocean(row, 0, cells_reaching_pacific, num_rows, num_cols, heights)
        
        # Explore from Atlantic ocean borders (bottom and right edges)
        for col in range(num_cols):
            self._explore_from_ocean(num_rows - 1, col, cells_reaching_atlantic, num_rows, num_cols, heights)
        for row in range(num_rows):
            self._explore_from_ocean(row, num_cols - 1, cells_reaching_atlantic, num_rows, num_cols, heights)
        
        cells_reaching_both_oceans = cells_reaching_pacific & cells_reaching_atlantic
        return list(cells_reaching_both_oceans)
    
    def _explore_from_ocean(
        self, 
        row:int, 
        col:int, 
        cells_reachable_from_ocean:set[tuple[int,int]] , 
        num_rows:int, 
        num_cols:int,  
        heights: list[list[int]]
    ):
        cells_reachable_from_ocean.add((row, col))
        
        # Check all 4 directions
        for row_offset, col_offset in [(0,1), (0,-1), (1,0), (-1,0)]:
            neighbor_row = row + row_offset
            neighbor_col = col + col_offset
            
            is_within_bounds = (0 <= neighbor_row < num_rows and 
                                0 <= neighbor_col < num_cols)
            if not is_within_bounds:
                continue
                
            is_unvisited = (neighbor_row, neighbor_col) not in cells_reachable_from_ocean
            can_flow_upward = heights[neighbor_row][neighbor_col] >= heights[row][col]
            
            if is_within_bounds and is_unvisited and can_flow_upward:
                self._explore_from_ocean(neighbor_row, neighbor_col, cells_reachable_from_ocean, num_rows, num_cols, heights)
