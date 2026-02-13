
class Solution:
    """
    THE PROBLEM: Find three integers whose sum is closest to target
    
    PATTERN: Sort + Two Pointers
    
    INSIGHT: Similar to 3Sum - fix one number, use two pointers for the other two.
    Track the closest sum seen so far.
    
    THE PLAN:
    1. Sort the array
    2. Loop through each number as the "first" number
    3. Use two pointers (left, right) to find best pair
    4. Track closest sum by comparing absolute difference from target
    5. Move pointers based on whether sum is too small or too large
    """
    def threeSumClosest(self, nums: list[int], target: int) -> int:
        nums.sort()
        n = len(nums)
        closest_sum = float('inf')
        
        for i in range(n - 2):
            left = i + 1
            right = n - 1
            
            while left < right:
                current_sum = nums[i] + nums[left] + nums[right]
                
                # Update closest sum if this is closer
                if abs(current_sum - target) < abs(closest_sum - target):
                    closest_sum = current_sum
                
                # If exact match, return immediately
                if current_sum == target:
                    return target
                
                # Move pointers based on comparison
                if current_sum < target:
                    left += 1
                else:
                    right -= 1
        
        return closest_sum
