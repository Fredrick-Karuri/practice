from typing import List


class Solution:
    """
    THE PROBLEM: Find all unique combinations that sum to target (reuse allowed) - Problem 39

    PATTERN: Backtracking

    INSIGHT: Build combinations recursively. At each step, decide to include current
    number or move to next. Allow reuse by staying at same index.

    THE PLAN: 
    1.Use backtracking with current combination and remaining sum
    2.Base case: if remaining == 0, add combination to result
    3.For each canditate, try including it (if doesn't exceed target)
    4.Backtrack by removing last added element
    5.Start from current index to allow reuse and avoid duplicates

    Example:candidates=[2,3,6,7], target=7
    - [2,2,3]: 2+2+3=7 ✓
    - [7]: 7=7 ✓
    Result: [[2,2,3],[7]]

    TIME: O(N^(T/M)) where N = candidates T = target, M = min candidate
    SPACE: O(T/M) for recursion depth
    """
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        result = []
        self.backtrack(0,[],target, result, candidates)
        return result

    def backtrack(self, start:int, current:List[int], remaining:List[int], result:List[List[int]] ,candidates:List[int] ):
        if remaining == 0:
            result.append(current[:]) # found valid combination
            return
        if remaining < 0:
            return # exceeded target
        
        for i in range(start, len(candidates)):
            current.append(candidates[i])
            # stay at i to allow reuse
            self.backtrack(i , current, remaining-candidates[i], result, candidates)
            current.pop() # Backtrack