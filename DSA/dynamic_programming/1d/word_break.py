class Solution:
    """
    THE PROBLEM: Can string s be segmented using words from wordDict? - Problem 139

    PATTERN : Dynamic Programming 

    INSIGHT: dp[i] = true if s[0:i] can be segmented
    For each position, check if any word ending at that position is valid.

    THE PLAN: 
    1.Create dp array: dp[i] = can segment s[0:i]
    2.Base case: dp[0] = true (empty string)
    3.For each position i, check all positions j<i
    4.If dp[j] is true and s[j:i] is in wordDict, then dp[i] = true

    TIME: 0(n^2 * m ) where m is max word length
    SPACE:O(n)
    """
    def wordBreak(self, s: str, wordDict: list[str]) -> bool:
        word_set = set(wordDict)
        string_length = len(s)
        can_segment_up_to = [False] * (string_length + 1)
        can_segment_up_to[0] = True

        for end_position in range(1,string_length + 1):
            for start_position in range(end_position):
                substring = s[start_position:end_position]
                previous_segment_valid = can_segment_up_to[start_position]
                current_word_in_dict = substring in word_set

                if previous_segment_valid and current_word_in_dict:
                    can_segment_up_to[end_position] = True
                    break
        
        return can_segment_up_to[string_length]