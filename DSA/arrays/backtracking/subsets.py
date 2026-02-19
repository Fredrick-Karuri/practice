# DSA/arrays/backtracking/subsets.py
class Solution:
    """
    THE PROBLEM: Generate all possible subsets (power set) - Problem 78

    PATTERN: Backtracking

    INSIGHT: For each element, decide to include or exclude it.
    Build subsets incrementally

    THE PLAN:
    1. Use backtracking to build subsets
    2. At each position, include each element and recurse
    3. Backtrack and try without current element

    TIME: O(2^n * n )
    SPACE: O(n) for recursion depth
    """
    def subsets(self, nums: list[int]) -> list[list[int]]:
        all_subsets = []

        def build_subset(start_index:int, current_subset:list[int]):
            all_subsets.append(current_subset[:])

            for i in range(start_index, len(nums)):
                current_subset.append(nums[i])
                build_subset(i+1,current_subset )
                current_subset.pop()

        build_subset(0,[])
        return all_subsets

        