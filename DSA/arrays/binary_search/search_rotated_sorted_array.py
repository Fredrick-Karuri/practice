class Solution:
    """
    THE PROBLEM: Search target in rotated sorted array

    PATTERN: Modified binary search

    INSIGHT: Atleast one half is always sorted. Determine which half, then check if 
    target is in sorted half

    THE PLAN: 
    1. Use binary search with left, right pointers
    2. Find midpoint
    3. Determine which half is sorted
    4. Check if target is in sorted half
    5. Move pointers accordingly

    Example: nums=[4,5,6,7,0,1,2], target=0
    - mid=7, left half [4,5,6,7] sorted, 0 not in range → search right
    - mid=1, right half [0,1,2] sorted, 0 in range → search left
    - Found at index 4

    TIME: O(log n)
    SPACE: O(1)
    """
    def search(self, nums: list[int], target: int) -> int:
        left , right = 0 , len(nums) - 1

        while left <= right:
            mid = (left + right) // 2

            if nums[mid] == target:
                return mid
            
            # Determine which half is sorted
            if nums[left] <= nums[mid]: # left half sorted
                if nums[left] <= target < nums[mid]:
                    right = mid - 1 # Target in left half
                else:
                    left = mid + 1 # Target in right half
            else: # Right half sorted
                if nums[mid] < target <= nums[right]:
                    left = mid + 1 # Target in right half
                else:
                    right = mid - 1 # Target in left half
        
        return -1
        