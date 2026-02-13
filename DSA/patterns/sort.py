from typing import List


class Solution:
    """
    THE PROBLEM:Merge all overlapping intervals
    PATTERN:Sort + Greedy
    INSIGHT: After sorting by start time, intervals overlap if current.start <= previous.end

    THE PLAN: 
    1.Sort invervals by start time
    2.Initialize result with first interval
    3.For each interval:
        -If overlapped with last merged interval, extend the end
        -Otherwise add as new interval
    Example: [[1,3],[2,6],[8,10],[15,18]]
    - [1,3] and [2,6] overlap → merge to [1,6]
    - [8,10] doesn't overlap → add as is
    - [15,18] doesn't overlap → add as is
    Result: [[1,6],[8,10],[15,18]]
    """
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        if not intervals:
            return []
        
        # sort by start time
        intervals.sort(key = lambda x: x[0])

        merged = [intervals[0]]

        for i in range(1, len(intervals)):
            current = intervals[i]
            last_merged = merged[-1]

            # Check if overlaps
            if current[0] <= last_merged[1]:
                # Merge by extending the end
                last_merged[1] = max(last_merged[1],current[1])
            else:
                # no overlap, add new interval
                merged.append(current)
        return merged


        