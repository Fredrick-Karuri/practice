# Pattern: Binary Search

Binary search efficiently finds a target in **sorted data** by repeatedly halving the search space.

Works on any monotonic property where you can eliminate half the possibilities at each step.

Think: *Divide and conquer on sorted/monotonic space.*

---

## When to Use Binary Search

Use binary search when:
- Data is **sorted** (or rotated sorted)
- Looking for a **specific value** or **boundary**
- Problem mentions "O(log n)" time
- Can determine which half contains the answer

Key insight: You need a way to decide "left or right?" at each step.

---

## Core Template (Mental Model)

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif condition_for_left_half:
            right = mid - 1
        else:
            left = mid + 1
    
    return -1  # not found
```

---

## Common Variations

### Standard Binary Search
- Sorted array, find exact target
- Time: O(log n), Space: O(1)

### Rotated Sorted Array
- Array sorted then rotated (e.g., `[4,5,6,7,0,1,2]`)
- At least one half is always sorted
- Check which half is sorted, then check if target is in range

### Finding Boundaries
- First/last occurrence of target
- Adjust condition to continue even after finding target

### Search in 2D Matrix
- Treat as flattened 1D array
- Convert index: `row = mid // cols`, `col = mid % cols`

---

## Key Patterns

**Rotated Array**: Identify sorted half, check if target in range

**Peak Finding**: Compare mid with neighbors

**Min/Max in Rotated**: Compare mid with endpoints

**Insert Position**: Return `left` when not found

---

## Pitfalls

- **Off-by-one errors**: Use `left <= right` for inclusive search
- **Integer overflow**: Use `mid = left + (right - left) // 2` for large arrays
- **Infinite loops**: Ensure pointers always move (`left = mid + 1`, not `mid`)