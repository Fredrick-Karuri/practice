class Solution:
    """
    THE PROBLEM: Find if a word exists in grid using adjacent cells (Problem 79)

    PATTERN: Backtracking + DFS

    INSIGHT: Try each cell as starting point. Use DFS to explore paths. Mark cells as visited 
    during search, unmark when backtracking.

    THE PLAN: 
    1. Try each cell as potential start
    2. DFS: check if current char matches, explore 4 directions
    3. Mark visited cells temporarily
    4. Backtrack if patht fails

    TIME: O(m * n * 4^L) where L is word length
    SPACE: O(L) for recursion depth
    """
    def exist(self, board: list[list[str]], word: str) -> bool:
        num_rows,num_cols = len(board), len(board[0])
        
        # try each cell as as starting point
        for row in range(num_rows):
            for col in range(num_cols):
                if self.search_from_position(row,col,0,board,word,num_rows,num_cols):
                    return True
        return False

    def search_from_position(
        self, 
        row:int,
        col:int,
        char_index:int, 
        board:list[list[str]], 
        word:str,
        num_rows:int, 
        num_cols:int
    ):
        if char_index == len(word):
            return True
        
        is_out_of_bounds = (
            row < 0 or row >= num_rows or
            col < 0 or col >= num_cols
        )
        if is_out_of_bounds:
            return False
        
        is_wrong_char = board[row][col] != word[char_index]
        is_already_used = board[row][col] == '#'

        if is_wrong_char or is_already_used:
            return False
        
        # Mark as visited
        original_char = board[row][col]
        board[row][col] = '#'

        # Explore 4 directions
        found = (
            self.search_from_position(row+1, col, char_index+1,board,word,num_rows,num_cols) or
            self.search_from_position(row-1, col, char_index+1,board,word,num_rows,num_cols) or
            self.search_from_position(row, col+1, char_index+1,board,word,num_rows,num_cols) or
            self.search_from_position(row, col-1, char_index+1,board,word,num_rows,num_cols) 
        )

        # Backtrack: Restore original character
        board[row][col] = original_char
        return found
