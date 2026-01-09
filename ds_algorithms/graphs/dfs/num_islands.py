from typing import List


class Solution:
    """
    THE PROBLEM: Count number of islands (connected '1's) in grid (Problem 200)
    
    PATTERN: DFS/BFS (Graph Traversal)
    
    INSIGHT: Each unvisited '1' starts a new island. Use DFS to mark 
    all connected land as visited.
    
    THE PLAN:
    1. Iterate through grid
    2. When finding unvisited '1', increment island count
    3. Use DFS to mark all connected '1's as visited
    4. Continue until grid fully explored
    
    Example: grid = [["1","1","0"],["1","0","0"],["0","0","1"]]
    - Find '1' at (0,0) → DFS marks (0,0), (0,1), (1,0) → island 1
    - Find '1' at (2,2) → DFS marks (2,2) → island 2
    Result: 2
    
    TIME: O(m × n) - visit each cell once
    SPACE: O(m × n) - recursion stack in worst case
    """
    def numIslands(self, grid: List[List[str]]) -> int:
        if not grid:
            return 0
        
        row_count, col_count = len(grid), len(grid[0])
        island_count = 0
        
        for row in range(row_count):
            for col in range(col_count):
                if self._is_unvisited_land(grid, row, col):
                    island_count += 1
                    self._mark_island_as_visited(grid,row, col,row_count,col_count)
        
        return island_count

    def _is_unvisited_land(self, grid, row, col):
        return grid[row][col] == '1'
    def _mark_island_as_visited(self,grid: List[List[str]], row:int, col:int, row_count:int,col_count:int):
        # Base cases: out of bounds or water or already visited
        invalid_cases = row < 0 or row >= row_count or col < 0 or col >= col_count or grid[row][col] != '1'
        if invalid_cases:
            return
        
        # Mark as visited
        grid[row][col] = '0'
        
        # Explore 4 directions
        self._mark_island_as_visited(grid,row + 1, col,row_count,col_count)  # down
        self._mark_island_as_visited(grid,row - 1, col,row_count,col_count)  # up
        self._mark_island_as_visited(grid,row, col + 1,row_count,col_count)  # right
        self._mark_island_as_visited(grid,row, col - 1,row_count,col_count)  # left