class Solution:
    """
    THE PROBLEM: Find two lines that form container with the most water (Problem 11)

    PATTERN: Two pointer (Greedy)

    INSIGHT: Start with widest container, (leftmost and rightmost lines). Move the pointer
    with shorter height inward - move taller one can't improve area

    THE PLAN:
    1.Start pointers at both ends
    2.Calculate the current area
    3.Move pointer with shorter height inward
    4.Track maximum area seen

    Example:height = [1,8,6,2,5,4,8,3,7]
    - left=0, right=8: area = min(1,7) × 8 = 8
    - left=1, right=8: area = min(8,7) × 7 = 49 ✓
    Maximum: 49

    TIME: O(n)
    SPACE: O(1)

    """
    def maxArea(self, height: list[int]) -> int:
        left_index = 0
        right_index = len(height) - 1
        max_water = 0

        return self._calculate_max_water_area(height, left_index, right_index, max_water)

    def _calculate_max_water_area(self, height:list[int], left_index:int, right_index:int, max_water:int):
        while left_index < right_index:
            width = right_index - left_index
            container_height = min(height[left_index], height[right_index])
            current_water = width * container_height
            max_water = max(max_water,current_water)

            # Move pointer with short height
            self._move_shorter_pointer(height, left_index, right_index)
        return max_water

    def _move_shorter_pointer(self, height:list[int], left_index:int, right_index:int):
        if height[left_index] < height[right_index]:
            left_index += 1
        else:
            right_index -= 1
        