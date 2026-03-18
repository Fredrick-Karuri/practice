class Solution:
    """
    THE PROBLEM: Schedule tasks with cooldown n between same tasks - Problem 621

    PATTERN: Greedy + Math

    INSIGHT: Most frequent task determines minimum time. Schedule high frequency tasks 
    first with gaps, fill gaps with other tasks

    THE PLAN: 
    1. Count task frequencies
    2. Find max frequency and how many tasks have that frequency
    3. Calculate minimum intervals needed
    4. Formula: max((max_freq - 1) * (n + 1) + num_max_freq_tasks , total_tasks)

    TIME: O(n)
    SPACE: O(1) - at most 26 task types
    """
    def leastInterval(self, tasks: list[str], n: int) -> int:
        task_counts: dict[str, int] = {}
        self._count_task_frequencies(tasks, task_counts)
        
        max_frequency: int = max(task_counts.values())
        num_tasks_with_max_freq: int = self._count_tasks_with_max_frequency(task_counts, max_frequency)

        min_total_tasks: int = self._calculate_minimum_total_tasks(tasks, n, max_frequency, num_tasks_with_max_freq)

        return min_total_tasks

    def _count_tasks_with_max_frequency(self, task_counts:dict[str, int], max_frequency:int):
        return sum( 1 for count in task_counts.values() 
                   if count == max_frequency
            )

    def _calculate_minimum_total_tasks(self, tasks:list[str], n:int, max_frequency:int, num_tasks_with_max_freq:int):
        num_completed_chunks = max_frequency - 1
        chunk_size = n + 1
        total_slots_needed = num_completed_chunks * chunk_size + num_tasks_with_max_freq

        min_total_tasks = max(total_slots_needed, len(tasks))
        return min_total_tasks

    def _count_task_frequencies(self, tasks:list[str], task_counts:dict[str, int]):
        for task in tasks:
            task_counts[task] = task_counts.get(task, 0) + 1

        