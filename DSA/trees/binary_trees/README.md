# Pattern: Tree Construction

Tree construction rebuilds a binary tree from traversal sequences by exploiting the **relationship between different traversal orders**.

Each traversal type reveals different structural information.

Think: *Using traversal properties to locate roots and partition subtrees.*

---

## When to Use Tree Construction

Use this pattern when:
- Given **two traversal sequences** (preorder/inorder, postorder/inorder)
- Need to **reconstruct binary tree**
- Serialization/deserialization problems

Note: Cannot uniquely reconstruct tree from preorder + postorder alone (without full/complete tree constraint).

---

## Core Mental Model

Key insight for each traversal:

> **Preorder**: Root is first, then left subtree, then right subtree
> 
> **Inorder**: Left subtree, then root, then right subtree
> 
> **Postorder**: Left subtree, then right subtree, then root is last

```python
def buildTree(preorder, inorder):
    # Preorder tells us the root
    # Inorder tells us left/right partition
    
    inorder_map = {val: idx for idx, val in enumerate(inorder)}
    
    def build(left, right):
        if left > right:
            return None
        
        root_val = next_from_preorder()
        root = TreeNode(root_val)
        
        mid = inorder_map[root_val]
        root.left = build(left, mid - 1)
        root.right = build(mid + 1, right)
        
        return root
```

---

## Common Variations

### Preorder + Inorder
- Preorder gives root (first element)
- Find root in inorder to split left/right
- Process preorder left-to-right
- Recurse left subtree first, then right

### Postorder + Inorder
- Postorder gives root (last element)
- Find root in inorder to split left/right
- Process postorder right-to-left
- Recurse right subtree first, then left

### Serialize/Deserialize
- Use marker for null nodes (e.g., "#")
- Can use single traversal with nulls marked
- Preorder or level-order with nulls is sufficient

---

## Key Patterns

**Hashmap for O(1) lookup**: Map values to indices in inorder array

**Boundary tracking**: Pass left/right bounds instead of copying arrays

**Index/pointer management**: Track position in preorder/postorder with variable

**Base case**: Return null when boundaries invalid (`left > right`)

---

## Pitfalls

- **Duplicate values**: Standard approach assumes unique values
- **Wrong traversal order**: Postorder processes right-to-left, preorder left-to-right
- **Array copying**: Avoid slicing arrays, use boundaries for O(n) space
- **Forgetting hashmap**: Linear search makes solution O(n²) instead of O(n)

---

## Why Two Traversals?

**Inorder alone**: Cannot determine structure (multiple valid trees)

**Preorder/Postorder alone**: Cannot determine left/right split

**Inorder + Pre/Post**: Inorder provides partition, other provides root order