# Pattern: Depth-First Search (DFS)

Depth-First Search is used to **explore all reachable nodes**
from a starting point before backtracking.

DFS is about **reachability, connectivity, and structure** — not about
generating all combinations.

Think: *systematic exploration of a graph.*

---

## When to Use DFS

Use DFS when the problem asks:
- “How many connected components are there?”
- “Is there a path / cycle?”
- “Mark all reachable nodes”
- “Explore everything from this starting point”
- “Traverse a tree / graph deeply”

If the question is about **visiting**, not **choosing**, DFS is likely right.

---

## Core Mental Model

DFS does one thing well:

> **Go as deep as possible, then backtrack.**

```python
def dfs(node):
    mark node as visited

    for neighbor in neighbors(node):
        if not visited:
            dfs(neighbor)
