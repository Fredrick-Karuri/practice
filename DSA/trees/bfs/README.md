# Pattern: Breadth-First Search (BFS)

Breadth-First Search explores nodes **level by level** using a queue, visiting all neighbors before going deeper.

BFS finds **shortest paths** and processes nodes by **distance from source**.

Think: *Layer-by-layer exploration using a queue.*

---

## When to Use BFS

Use BFS when the problem asks:
- "Process nodes **level by level**"
- "Find **shortest path** (unweighted graph)"
- "Nearest/closest node to…"
- "Minimum number of steps/moves"
- "Level order traversal"

If distance or order by depth matters, BFS is likely right.

---

## Core Mental Model

BFS does one thing well:

> **Process all nodes at current distance before moving to next distance.**

```python
from collections import deque

def bfs(start):
    queue = deque([start])
    visited = {start}
    
    while queue:
        node = queue.popleft()
        # process node
        
        for neighbor in neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

---

## Common Variations

### Level-by-Level Processing
- Track current level size before processing
- Process all nodes at current level before moving to next
- Examples: binary tree level order, right side view

### Shortest Path
- Return distance when target found
- Each level represents one step
- Examples: word ladder, knight moves, maze shortest path

### Multi-Source BFS
- Start with multiple nodes in queue
- All sources at distance 0
- Examples: rotting oranges, walls and gates

### Bidirectional BFS
- Search from both start and end
- Meet in the middle for optimization
- Reduces search space significantly

---

## Key Patterns

**Queue usage**: FIFO ensures level-by-level processing

**Visited tracking**: Prevent cycles and redundant work

**Level tracking**: Process `len(queue)` nodes to handle one level

**Distance tracking**: Each level increment represents +1 distance

**Early termination**: Return immediately when target found (shortest path guaranteed)

---

## Pitfalls

- **Forgetting visited set**: Can cause infinite loops in graphs with cycles
- **Wrong queue operations**: Use `popleft()` not `pop()` for deque
- **Level size miscalculation**: Capture `len(queue)` before inner loop starts
- **Memory for wide graphs**: BFS can use more memory than DFS for wide structures

---

## BFS vs DFS

Use **BFS** when: shortest path needed, level order matters, want nodes by distance

Use **DFS** when: paths matter, structural validation, memory is limited, exploring all possibilities

BFS guarantees shortest path in unweighted graphs; DFS does not.