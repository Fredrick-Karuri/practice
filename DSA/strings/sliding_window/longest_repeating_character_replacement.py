def characterReplacement(self, s: str, k: int) -> int:
    """
    THE PROBLEM: replace at most k characters to form longest repeating substring

    PATTERN = sliding window

    INSIGHT: window is valid if : window_size - most_frequent_char <= k
    (we can replace all non frequent chars to make them all the same)

    THE PLAN:
    1.use two pointers (left, right) for sliding window
    2.track character counts in current window
    3.expand window by moving right pointer
    4.if window invalid(replacement needed > k), shrink from left
    5.track maximum valid window size seen

    Example: s = "AABABBA", k = 1
    - Window "AAB": size=3, max_freq=2, replacements=1 ✓
    - Window "AABA": size=4, max_freq=3, replacements=1 ✓

    """
    char_count = {}
    left = 0
    max_length = 0
    max_freq = 0 #most frequent character count in current window
    n=len(s)

    for right in range(n):
        #add right characters to the window
        char_count[s[right]] = char_count.get(s[right],0) +1
        max_freq = max(max_freq,char_count[s[right]])

        #check if window is valid
        window_size = right - left+1
        replacements_needed = window_size - max_freq

        #if invalid, shrink window from left
        if replacements_needed > k :
            char_count[s[left]] -=1
            left+=1
        
        #update max length (window is now valid)
        max_length = max(max_length, right-left+1)
    return max_length