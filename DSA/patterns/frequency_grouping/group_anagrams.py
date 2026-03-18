from typing import List


class Solution:
    """
    THE PROBLEM: Group strings that are anagrams of each other (PROBLEM - 49)

    PATTERN: Hashmap

    INSIGHT: Anagrams have identical sorted characters. Use sorted string as key

    THE PLAN: 
    1. Create hashmap : sorted_string -> list of anagrams
    2. For each string, sort it to get the key
    3. Add string to corresponding list
    4. Return all lists
    Example: ["eat","tea","tan","ate","nat","bat"]
    - "eat" → "aet" → group 1
    - "tea" → "aet" → group 1
    - "tan" → "ant" → group 2
    Result: [["eat","tea","ate"], ["tan","nat"], ["bat"]]

    Time: O(n * k log k) 
    Space: O(n * k)
    where k = max string length, n = number of strings 
    """
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        anagram_map = {}
        for word in strs:
            # sort characters to create key
            key = ''.join(sorted(word))

            if key not in anagram_map:
                anagram_map[key] = []
            anagram_map[key].append(word)
        return list(anagram_map.values())

        