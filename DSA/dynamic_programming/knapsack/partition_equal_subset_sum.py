class Solution:
    """
    THE PROBLEM: Can we partition array into 2 equal-sum subsets? (Problem 416)

    PATTERN: Dynamic Programming (Subset sum)

    INSIGHT: If total sum is odd, impossible. Otherwise, find if subset
    exists that sums to total/2 (the other half automatically sums to total/2)

    THE PLAN: 
    1. Calculate total sum, return false if odd
    2. Target = total/2
    3. Use DP to check if any subset can sum to target
    4. dp[i] = true if sum is achievable

    Example: nums = [1,5,11,5]
    Total = 22, target = 11
    Can make 11? [1,5,5] = 11 ✓

    TIME: O(n * sum)
    SPACE: O(sum)
    """
    def canPartition(self, nums: list[int]) -> bool:
        total_sum = sum(nums)

        if total_sum %2 == 1:
            return False
        
        target = total_sum // 2
        achievable_sums = {0}

        for num in nums:
            new_sums = set()
            for current_sum in achievable_sums:
                new_sum = current_sum + num
                if new_sum == target:
                    return True
                if new_sum < target:
                    new_sums.add(new_sum)
            achievable_sums.update(new_sums)

        return target in achievable_sums
        