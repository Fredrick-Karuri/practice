from typing import List


class Solution:
    def rotate(self, matrix: List[List[int]]) -> None:
        """
        THE PROBLEM:rotate 2D matrix by 90 degrees clockwise in-place
        PATTERN: Matrix manipulation(transpose + reverse)
        THE PLAN:
        1.Transposet he matrix(Swap rows and columns)
        2.Reverse each row

        Example:
        [1,2,3]     [1,4,7]     [7,4,1]
        [4,5,6]  →  [2,5,8]  →  [8,5,2]
        [7,8,9]     [3,6,9]     [9,6,3]
        (original)  (transpose) (reverse rows)

        INSIGHT:90 degres clockwise rotation = transpose + reverse each row
        Do not return anything, modify matrix in-place instead.

        """
        n = len(matrix)
        # Step 1: transpose (Swap matrix[i][j] with matrix[j][i])
        for i in range(n):
            for j in range(i+1, n):
                matrix[i][j],matrix[j][i] = matrix[j][i],matrix[i][j]
        
        # Step 2: reverse each row
        for i in range(n):
            matrix[i].reverse()
