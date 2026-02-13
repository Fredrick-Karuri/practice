class Solution:
    """
    THE PROBLEM: Find the longest palindromic substring in s
    
    PATTERN: Expand Around Center
    
    INSIGHT: Each palindrome has a center. Check all possible centers
    (n centers for odd length, n-1 for even) and expand outward.
    
    THE PLAN:
    1. For each position, treat it as palindrome center
    2. Expand outward while characters match
    3. Handle both odd-length (single center) and even-length (two centers)
    4. Track longest palindrome found
    
    Example: s = "babad"
    - Center 'b': "b"
    - Center 'a': "bab" ✓
    - Center 'b': "bab" or "aba" ✓
    Result: "bab" or "aba"
    
    TIME: O(n²) - n centers, each expands up to n
    SPACE: O(1) - only storing indices
    """
    def longestPalindrome(self, s: str) -> str:
        if len(s) < 2:
            return s
        
        max_start, max_end = 0, 0
        
        for i in range(len(s)):
            max_start, max_end = self._update_max_palindrome(s, max_start, max_end, i)
    
        longest_palindrome = s[max_start:max_end + 1]
        return longest_palindrome

    def _update_max_palindrome(self, s:str, max_start:int, max_end:int, center:int):

        odd_start, odd_end = self._expand(center, center,s)
        even_start, even_end = self._expand(center, center + 1,s)
         
        if odd_end - odd_start > max_end - max_start:
            max_start, max_end = odd_start, odd_end
        if even_end - even_start > max_end - max_start:
            max_start, max_end = even_start, even_end
        return max_start,max_end
    
    def _expand(left:int, right:int,s:str):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - 1