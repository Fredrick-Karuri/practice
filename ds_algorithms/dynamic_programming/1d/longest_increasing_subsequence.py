class Solution:
    """
    THE PROBLEM: Find the length of longest strictly increasing subsequence

    PATTERN: Dynamic Programming + Binary Search (greedy)

    INSIGHT: Maintain array where tails[i] = smallest ending value of all 
    increasing subsequences of length i + 1. Use binary search to efficiently 
    find where each number belongs.

    THE PLAN: 
    1. Maintain array of small tail values for each subsequence length.
    2. For each number, binary search for its position
    3. If position is at end, we found a longer subsequence (append)
    4. Otherwise replace to keep smallest possible tail (greedy)
    5. Length of tail array is our answer

    Example: [10,9,2,5,3,7,101,18]
    - Process 10: tails=[10]
    - Process 9: replace 10 with 9, tails=[9] (smaller tail is better)
    - Process 2: replace 9 with 2, tails=[2]
    - Process 5: append, tails=[2,5]
    - Process 3: replace 5 with 3, tails=[2,3] (length 2, smaller tail)
    - Process 7: append, tails=[2,3,7]
    - Process 101: append, tails=[2,3,7,101]
    - Process 18: replace 101 with 18, tails=[2,3,7,18]
    Answer: 4

    TIME: O(n log n) - n iterations, each with binary search
    SPACE: O(n) - tails array
    """
    def lengthOfLIS(self, nums: list[int]) -> int:
        smallest_tail_for_each_length = []

        for current_number in nums:
            # Binary search for position where current number should go
            left_boundary = 0
            right_boundary = len(smallest_tail_for_each_length)

            while left_boundary < right_boundary :
                middle = (left_boundary + right_boundary) // 2

                if smallest_tail_for_each_length[middle] < current_number:
                    left_boundary = middle + 1
                else:
                    right_boundary = middle
            
            # If position is at end, we found a longer subsequence
            position = left_boundary
            is_new_longest = position == len(smallest_tail_for_each_length)

            if is_new_longest:
                smallest_tail_for_each_length.append(current_number)
            else:
                # Replace with smaller value, greedy choice for future
                smallest_tail_for_each_length[position] = current_number
        return len(smallest_tail_for_each_length)
        