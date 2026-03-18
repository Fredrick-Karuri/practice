class Solution:
    """
    THE PROBLEM: Can we reach the last index by jumping?

    PATTERN: Greedy

    INSIGHT:Track farthest reachable position. If we can't reach current position, 
    we can't proceed further

    THE PLAN:
    1.Track max reachable position
    2.For each position, check if reachable
    3.Update max reachable with current position + jump length
    4.Return true if we can reach or pass last index

    Example: nums=[2,3,1,1,4]
    - pos 0: reach 2
    - pos 1: reach 4 (1+3)
    - Reached end ✓

    TIME: O(n)
    SPACE: O(1)
    """
    def canJump(self, nums: list[int]) -> bool:
        farthest_reachable = 0

        for current_position in range(len(nums)):
            if current_position > farthest_reachable:
                return False
            
            max_jump_from_here = current_position + nums[current_position]
            farthest_reachable = max(farthest_reachable,max_jump_from_here)

            if farthest_reachable >= len(nums) - 1:
                return True
        return True
        