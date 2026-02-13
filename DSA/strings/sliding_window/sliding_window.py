
## Pattern 2 : Sliding window
"""
When to use: When you need to find something in a contiguous subarray/substring

How it works:
1.calculate the sum for the first k element
2."Slide" the window one position at a time by:
    .substracting from the leftmost element that's leaving the window
    .adding the new righmost element entering the window

Common uses:
1.Maximum/minimum sum of k consecutive elements
2.Average of subarrays
3.Finding substrings with specific properties
4.Moving averages
5.Longest substring with condition
6.Finding all anagrams
7.Character frequency in window
    
The technique is efficient because : instead of recalculatin the entire sum of each window (O(n*k)), you
reuse the previous sum and adjust it (O(n)).

The setup:
left = 0
for right in range(len(arr)):
    # add arr[right] to window

    #shrink window if needed
    while window_invalid:
        #remove arr[left] from window
        left+=1
    #check if current window is valid answer

"""
from typing import List


def sliding_window_example(arr,k):
    """ Find the sum for every k-length subarray """
    window_sum = sum(arr[:k]) # initial window
    print(f"Window sum for first {k} elements {window_sum}")

    # Slide the window
    for i in range (k,len(arr)):
        window_sum = window_sum - arr[i-k] + arr[i] # remove left and right
        print(f"Window sum:",window_sum)

print("Sliding Window:")
sliding_window_example([1,2,3,4,5],3)


def findMaxAverage( nums: List[int], k: int) -> float:

    """
    problem:find contiguous subarray of length k with maximum average

    pattern: sliding window (fixed size)

    the plan:
    1.calculate the sum of the first k elements (initial window)
    2.track this as max_sum
    3.slide the window one position at a time:
        .remove leftmost element (substract nums[new_index-k])
        .add new rightmost element (add nums[new_index])
        .update max_sum if current sum is larger
    4.return max_sum/k (the maximum average)

    """
    current_sum = sum(nums[:k])
    max_sum = current_sum

    for new_index in range(k,len(nums)):
        #remove left element, add right element
        current_sum = current_sum - nums[new_index - k] + nums[new_index]
        #update max if needed
        max_sum = max(max_sum,current_sum)
    return max_sum/k


def containsNearbyDuplicate(self, nums: List[int], k: int) -> bool:
    """
    PROBLEM: check if duplicate exists within k distance

    PATTERN: sliding window + set

    THE PLAN:  
    1.use a set to track numbers in current window (size <=k)
    2.slide through the array:
        .if current number already in set -> found duplicate within k distance return true
        .add current number to set
        .if window size exceeds k, remove leftmost element from the set
    3.if no duplicates found return False

    """
    window=set()
    range_of_indices = range(len(nums))
    for current_index in range_of_indices:
        if nums[current_index] in window:
            return True
        window.add(nums[current_index])

        if len(window)>k:
            window.remove(nums[current_index-k])
    return False


def minSubArrayLen(self, target: int, nums: List[int]) -> int:
    """
    PROBLEM:find minimal length subarray with sum>= target

    PATTERN:sliding window (variable size)

    THE PLAN:
    1.use left and right pointers, current sum, and min_length tracker
    2.expand window: add nums[right] to current_sum
    3.shrink window: while sum is >= target:
        .update min_length
        .remove nums[left], move left forward
    4.return min_length (or 0 if never found)
    
    """
    left = 0
    current_sum = 0
    min_length = float('inf')

    for right in range(len(nums)):
        #expand: add right element
        current_sum += nums[right]
        #shrink:while valid, try smaller windows
        while current_sum >= target:
            min_length = min(min_length,right-left+1)
            current_sum-=nums[left]
            left +=1
    return min_length if min_length != float('inf') else 0


def lengthOfLongestSubstring(self, s: str) -> int:

    """
    PROBLEM:longest substing without repeating characters

    PATTERN:sliding window + set/hashmap

    THE PLAN:
    1.use left pointer, set to track characters in window, max_length
    2.expand: add s[right] to window
    3.shrink: whiles[right] is duplicate:
        .remove s[left] from set
        .move left forward
    4.update max_length after each window adjustment

    TIME: O(n) , SPACE: O(min(n,charset_size))

    KEY INSIGHT:when you hit a duplicate, shrink from left until the duplicate is removed,
        then continue expanding.

    
    """
    left = 0
    char_set = set()
    max_length = 0

    for right in range(len(s)):
        #shrink while duplicates exist
        while s[right] in char_set:
            char_set.remove(s[left])
            left+=1
        #add current character
        char_set.add(s[right])

        # update max length
        max_length = max(max_length, right-left +1)

    return max_length

def totalFruit(self, fruits: List[int]) -> int:

    """
    PROBLEM: max fruits you can pick with only 2 baskets(2 fruit types)

    PATTERN: sliding window + hashmap

    THE PLAN:
    1.track fruit type in current window with a hashmap {fruit_type:count}
    2.expand:add fruits[right] to the window
    3.shrink:while more than 2 fruit tpes:
        .remove fruits[left] from hashmap
        .if count becomes 0 delete from hashmap
        .move left forward
    4.update max_fruits after each valid window

    TIME:O(n) SPACE O(1) - max 3 fruit types in map

    KEY INSIGHT: "2 baskets" = max 2 distinct fruit types in window. use hashmap to 
        track counts

    """
    left = 0
    fruit_count = {}
    max_fruits = 0

    for right in range(len(fruits)):
        #add current fruit
        fruit_count[fruits[right]]=fruit_count.get(fruits[right],0) + 1

        #shrink while more than 2 types
        while len(fruit_count) > 2:
            fruit_count[fruits[left]] -=1
            if fruit_count[fruits[left]] == 0:
                del fruit_count[fruits[left]]
            left +=1
        
        # update max
        max_fruits = max(max_fruits,right-left+1)
    return max_fruits

class Solution:
    """
    THE PROBLEM: Find all start indices where p's anagram appears in s [Question 438]

    PATTERN: Sliding window + hashmap

    INSIGHT: Anagrams have same character frequencies. Use fixed size sliding window 
    of length p, compare frequency maps.

    THE PLAN: 
    1. Count character frequencies in p
    2. Use sliding window of size len(p) on s
    3. Track character frequencies in current window
    4. When window matches p's frequency, record start index
    5. Slide window: remove left character, add right character

    Example: s="cbaebabacd", p="abc"
    Windows: "cba"✓, "bae"✗, "aeb"✗, "eba"✗, ..."bac"✓, ...
    Result: [0, 6]
    """
    def findAnagrams(self, s: str, p: str) -> List[int]:
        if len(p) > len(s):
            return[]
        
        result = []
        p_count = {}
        window_count = {}

        # Count frequencies in p
        for char in p:
            p_count[char] =p_count.get(char,0) + 1
        # Initial window
        for i in range(len(p)):
            char = s[i]
            window_count[char] = window_count.get(char,0) +1
        # Check first window
        if window_count == p_count:
            result.append(0)
        # Slide window
        for i in range(len(p), len(s)):
            # Add new character
            new_char = s[i]
            window_count[new_char] = window_count.get(new_char,0)+1

            # Remove old character
            old_char = s[i - len(p)]
            window_count[old_char] -=1

            if window_count[old_char] == 0:
                del window_count[old_char]
            # check if anagram
            if window_count == p_count:
                result.append(i- len(p) +1)
        return result
        