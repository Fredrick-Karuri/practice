from typing import List


class Solution:
    """
    THE PROBLEM: Return matrix elements in spiral order(clockwise) [Question 54]

    PATTERN: Layer by layer traversal

    INSIGHT: Process outer layers then recursively process inner layers. Track boundaries
    top, bottom, left, right

    THE PLAN: 
    1. Define four boundaries(top, bottom, left, right)
    2. Traverse: right -> down -> left -> up
    3. After each direction, shrink corresponding boundary
    4. Continue until boundaries cross

    Example: [[1,2,3],[4,5,6],[7,8,9]]
    Right: 1,2,3 → Down: 6,9 → Left: 8,7 → Up: 4 → Right: 5
    Result: [1,2,3,6,9,8,7,4,5]


    """
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        if not matrix:
            return []
        
        result = []
        top,bottom = 0,len(matrix) -1
        left,right = 0, len(matrix[0]) - 1

        while top<=bottom and left<=right:
            # move right across top row
            for col in range(left,right+1):
                result.append(matrix[top][col])
            top+=1 # move top boundary down
            # move down right column
            for row in range(top,bottom+1):
                result.append(matrix[row][right])
            right -=1
            # Move left across bottom row(if row exists)
            if top<=bottom:
                for col in range(right,left-1,-1):
                    result.append(matrix[bottom][col])
                bottom-=1 #Move bottom boundary up
            # Move up left column (if column exists)
            if left<=right:
                for row in range(bottom,top-1,-1):
                    result.append(matrix[row][left])
                left+=1
        return result

                

        