# Pattern: Backtracking

Backtracking is used when the problem asks for **all possible solutions**
under some constraints.

It explores the solution space incrementally and **undoes decisions**
when a path becomes invalid.

Think: *DFS with explicit state rollback.*

---

## When to Use Backtracking

Use backtracking when the problem says:
- “find **all** combinations”
- “generate **all** permutations / subsets”
- “return **every possible** valid arrangement”
- “count all ways to…”

If the output size can be large, backtracking is usually involved.

---

## Core Template (Mental Model)

Every backtracking problem follows this shape:

1. **Choose** an option
2. **Explore** deeper recursively
3. **Un-choose** (backtrack)

```python
def backtrack(state):
    if state is valid:
        record solution
        return

    for choice in choices:
        make choice
        backtrack(updated_state)
        undo choice
