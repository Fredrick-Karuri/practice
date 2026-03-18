class Solution:
    """
    THE PROBLEM: Return k most frequent elements - Problem 347

    PATTERN: Hash map + Bucket Sort

    INSIGHT: Use bucket sort where index = frequency. Elements with same 
    frequency go in same bucket. Collect from high frequency down.

    THE PLAN: 
    1. Count frequency of each number using a hashmap
    2. Create buckets where index = frequency
    3. Place numbers in corresponding frequency buckets
    4. Collect from high frequency down until we have k elements

    Example: nums=[1,1,1,2,2,3], k=2
    - Frequencies: {1:3, 2:2, 3:1}
    - Buckets: [[], [3], [2], [1], [], [], []]
    - Result: [1, 2]

    TIME: O(n)
    SPACE: O(n)

    """
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        frequency_map = {}
        self._count_frequency_for_each_number(nums, frequency_map)
        
        # Bucket sort: index = frequency
        max_frequency, buckets = self._create_buckets(nums, frequency_map)
        
        # Collect topk from highest frequency
        result = []
        for freq in range(max_frequency, 0, -1):
            for num in buckets[freq]:
                result.append(num)
                if len(result) == k:
                    return result
        return result

    def _create_buckets(self, nums:list[int], frequency_map:dict[int, int]):
        max_frequency = len(nums)
        buckets = [[] for _ in range(max_frequency + 1)]

        for num, freq in frequency_map.items():
            buckets[freq].append(num)
        return max_frequency,buckets

    def _count_frequency_for_each_number(self, nums:list[int], frequency_map:dict[int, int]):
        for num in nums:
            frequency_map[num] = frequency_map.get(num,0) + 1

        