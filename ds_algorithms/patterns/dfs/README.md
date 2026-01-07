# Pattern: Depth-First Search (DFS)

Depth-First Search is used to **explore all reachable nodes**
from a starting point before backtracking.

DFS is about **reachability, connectivity, and structure** — not about
generating all combinations.

Think: *systematic exploration of a graph.*

---

## When to Use DFS

Use DFS when the problem asks:
- "How many connected components are there?"
- "Is there a path / cycle?"
- "Mark all reachable nodes"
- "Explore everything from this starting point"
- "Traverse a tree / graph deeply"

If the question is about **visiting**, not **choosing**, DFS is likely right.

### Tree-Specific DFS
For binary trees, use DFS when:
- Need **path from root to leaf**
- Problem involves **ancestor constraints**
- Validating **structural properties** (like BST)
- Finding **depth or height**
- Need to process **subtrees independently**

If order matters: preorder (root first), inorder (left-root-right), postorder (children first).

---

## Core Mental Model

DFS does one thing well:

> **Go as deep as possible, then backtrack.**

### Graph DFS
```python
def dfs(node):
    mark node as visited

    for neighbor in neighbors(node):
        if not visited:
            dfs(neighbor)
```

### Tree DFS
```python
def dfs(node, state):
    if not node:
        return base_case
    
    # Process current node
    # Update state based on node
    
    # Recurse on children
    left_result = dfs(node.left, updated_state)
    right_result = dfs(node.right, updated_state)
    
    # Combine results
    return combined_result
```

---

## Common Variations

### Graph: Connected Components
- Mark nodes as visited
- Count number of DFS calls needed to visit all nodes
- Each call starts a new component

### Graph: Cycle Detection
- Track nodes in current recursion stack
- If you revisit a node in the stack, there's a cycle

### Tree: Range Validation (BST)
- Pass min/max bounds down the tree
- Each node must satisfy: `min < node.val < max`
- Update bounds when recursing: left gets new max, right gets new min

### Tree: Path Tracking
- Accumulate path in parameter or backtrack
- Check condition at leaves
- Clone or restore state after recursion

### Tree: Height/Depth
- Return height from leaves upward
- Combine left and right heights
- Add 1 for current level

### Tree: Subtree Properties
- Process both subtrees
- Combine their results at current node
- Return aggregate information upward

---

## Key Patterns

**Graph: Visited tracking**: Use set or array to avoid revisiting

**Graph: Recursion stack**: Track current path for cycle detection

**Tree: Top-down**: Pass information from root to leaves (bounds, path sum)

**Tree: Bottom-up**: Collect information from leaves to root (height, subtree properties)

**Tree: Backtracking**: Build path, recurse, then remove current node from path

**Early termination**: Return immediately when condition fails

---

## Pitfalls

- **Forgetting null checks**: Always check `if not node` first
- **Not updating state correctly**: Clone lists/sets when needed for independent paths
- **Wrong boundary conditions**: Use `<` vs `<=` carefully (BST validation)
- **Stack overflow**: Very deep trees can exceed recursion limit (use iterative for production)

---

## DFS vs BFS

Use **DFS** when: paths matter, structural validation, memory is limited

Use **BFS** when: level-order matters, shortest path needed, want nodes by distance from root