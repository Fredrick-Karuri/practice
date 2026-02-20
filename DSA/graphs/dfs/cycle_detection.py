from typing import Dict, List
from enum import IntEnum

class VisitState(IntEnum):
    UNVISITED = 0
    VISITING = 1
    VISITED = 2


class Solution:
    """
    THE PROBLEM : Determine if all courses can be completed given prerequisites

    PATTERN: Graph Cycle Detection (DFS)

    INSIGHT: If there is a cycle in the prerequisite graph, courses can't be completed.
    Use DFS to detect cycles.

    THE PLAN:
    1.Build adjacency list: course -> list of courses that depend on it
    2.Use DFS with 3 states: unvisited, visiting, visited
    3.If we encounter a "visiting " node, there is a cycle.
    4.Return false if cycle found, true if all courses can be completed.

    Example: numCourses=2, prerequisites=[[1,0]]
    - Course 1 requires course 0
    - No cycle → return true

    Example: numCourses=2, prerequisites=[[1,0],[0,1]]
    - Course 1 requires 0, course 0 requires 1
    - Cycle detected → return false

    TIME: O(V + E) where V=courses, E = prerequisites
    SPACE: O(V + E) for adjacency list and recursion
    """
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        graph = self._build_dependency_graph(numCourses, prerequisites)
        cycle_detected = self._has_circular_dependency(graph,numCourses)
        return not cycle_detected
    

    def _build_dependency_graph(self, numCourses, prerequisites):
        """Build adjacency list where each course points to its prerequisites."""
        graph = {i:[] for i in range(numCourses)}
        for course, prereq in prerequisites:
            graph[course].append(prereq)
        return graph
    
    def _has_circular_dependency(self,numCourses:int,graph:Dict[int,List[int]]):
        """Check if the course dependency graph contains any cycles."""
        visit_states = [VisitState.UNVISITED] * numCourses
        for course in range(numCourses):
            if self._detect_cycle_from(course, graph, visit_states):
                return True
        return False

    def _detect_cycle_from(self,course:int, graph:Dict[int,List[int]], visit_states:List[VisitState]):
        """
        DFS to detect cycles starting from a course.
        Returns True if a cycle is detected.
        """
        if visit_states[course] == VisitState.VISITING:
            return True 
        if visit_states[course] == VisitState.VISITED:
            return False
        
        visit_states[course] = VisitState.VISITING

        for prereq in graph[course]:
            if self._detect_cycle_from(prereq,graph,visit_states):
                return True
        
        visit_states[course] = VisitState.VISITED
        return False   