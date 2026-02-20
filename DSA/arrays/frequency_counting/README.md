# Pattern: Frequency Counting

Frequency counting uses hashmaps to track occurrences, often combined with sorting or bucketing for selection problems.

Efficient way to find top/bottom K elements or group by frequency.

Think: *Count occurrences, then select/sort by frequency.*

---

## When to Use Frequency Counting

Use this pattern when:
- "Find top K most/least frequent elements"
- "Group by frequency"
- "K closest/farthest elements"
- Need to track occurrence counts
- Selection based on frequency

Keywords: "top K", "most frequent", "least common", "by occurrence"

---

## Core Mental Model

Two-phase approach:

> **Phase 1**: Count frequencies using hashmap
> 
> **Phase 2**: Select/sort based on frequencies

```python
# Count frequencies
freq = {}
for item in items:
    freq[item] = freq.get(item, 0) + 1

# Select top K (various methods)
# Method 1: Sort by frequency
# Method 2: Heap
# Method 3: Bucket sort
```

---

## Common Variations

### Top K Frequent (Bucket Sort)
- Create buckets where index = frequency
- Place items in corresponding buckets
- Collect from high frequency down
- Time: O(n), Space: O(n)

### Top K Frequent (Heap)
- Use min-heap of size K
- Keep K most frequent items
- Time: O(n log k), Space: O(n)

### Top K Frequent (Sort)
- Sort by frequency descending
- Take first K items
- Time: O(n log n), Space: O(n)

### Group by Frequency
- Use frequency as key in grouping map
- Collect all items with same frequency
- Examples: group anagrams, equal frequency

---

## Key Patterns

**Counter dict**: Use `collections.Counter` or manual dict for frequency

**Bucket sort optimization**: When K is large or need O(n), use bucket sort

**Heap for small K**: When K << n, heap is space efficient

**Frequency as key**: Invert map to group by frequency

---

## Pitfalls

- **Bucket size**: Array size should be `len(items) + 1` (max frequency)
- **Empty buckets**: Skip empty buckets when collecting
- **Tie breaking**: Problem may require specific order for equal frequencies
- **Memory for buckets**: Bucket sort uses O(n) space even for small K

---

## Selection Methods Comparison

**Bucket Sort**: O(n) time, best when K is large or need linear time

**Heap**: O(n log k) time, best when K is small

**Sort**: O(n log n) time, simplest implementation, good enough for small inputs