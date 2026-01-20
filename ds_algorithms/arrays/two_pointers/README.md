# Pattern: Two Pointers

Two pointers uses multiple pointers to traverse data structures efficiently, often reducing time complexity from O(n²) to O(n).

Works when you can make decisions based on values at pointer positions.

Think: *Strategic pointer movement to explore solution space.*

---

## When to Use Two Pointers

Use two pointers when:
- Array/string is **sorted** (or can be sorted)
- Looking for **pairs/triplets** with certain properties
- Need to **compare elements** at different positions
- **Optimizing brute force** nested loops
- Processing from **both ends** or **same direction**

Common keywords: "pair", "triplet", "subarray", "palindrome", "container"

---

## Core Mental Model

Two main approaches:

> **Opposite direction**: Start at both ends, move toward each other
> 
> **Same direction**: Both start at beginning, move at different speeds

```python
# Opposite direction
left, right = 0, len(arr) - 1
while left < right:
    if condition:
        # process
        left += 1
    else:
        right -= 1

# Same direction (fast/slow)
slow = fast = 0
while fast < len(arr):
    # process
    fast += 1
    if condition:
        slow += 1
```

---

## Common Variations

### Opposite Direction (Squeeze)
- Start at both ends
- Move pointers based on comparison
- Examples: two sum (sorted), container with most water, valid palindrome

### Same Direction (Fast/Slow)
- Both start at beginning
- Fast pointer explores, slow pointer tracks valid position
- Examples: remove duplicates, move zeros, partition array

### Sliding Window
- Expand window with right pointer
- Shrink with left pointer when condition violated
- Examples: longest substring, minimum window

### Three Pointers
- Extension for triplet problems
- Fix one pointer, use two pointers on remaining elements
- Example: three sum

---

## Key Patterns

**Greedy movement**: Move pointer that can't improve solution (e.g., shorter height in container problem)

**Comparison-based**: Compare values at pointers to decide movement

**Invariant maintenance**: Keep certain property true as pointers move

**Early termination**: Stop when pointers meet or cross

---

## Pitfalls

- **Infinite loops**: Ensure pointers always move in each iteration
- **Off-by-one**: Use `left < right` vs `left <= right` carefully
- **Not sorted**: Many two-pointer problems require sorted input first
- **Edge cases**: Empty array, single element, all duplicates

---

## Two Pointers vs Other Patterns

Use **two pointers** when: can make greedy decisions, linear scan suffices

Use **binary search** when: need O(log n), searching specific value

Use **sliding window** when: need contiguous subarray/substring with constraint