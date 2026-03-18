# Pattern: Knapsack (0/1 Dynamic Programming)

Knapsack problems involve selecting items to maximize/minimize value subject to constraints, where each item can be used **at most once**.

Core principle: **for each item, decide to take it or leave it**.

Think: *Subset selection under constraints.*

---

## When to Use Knapsack

Use knapsack when:
- "Can we achieve target sum using subset?"
- "Maximize value with weight/capacity constraint"
- "Partition into equal subsets"
- "Count ways to reach target"
- Each item used **zero or one time** (0/1)

Keywords: "subset sum", "partition", "target", "capacity", "each item once"

---

## Core Mental Model

Two equivalent approaches:

> **2D DP**: For each item, for each capacity, decide take or skip
> 
> **1D DP (optimized)**: Track achievable states, iterate backwards to avoid reusing items

```python
# 2D approach
dp[i][w] = can we achieve weight w using items 0..i?
dp[i][w] = dp[i-1][w] or dp[i-1][w-nums[i]]
           # skip item    # take item

# 1D optimized
dp = {0}  # achievable sums
for num in nums:
    new_sums = set()
    for current in dp:
        new_sums.add(current + num)
    dp.update(new_sums)
```

---

## Common Variations

### Subset Sum (Boolean)
- Can we reach exact target?
- Track achievable sums as set
- Return `target in dp`

### Partition Equal Subset
- Special case: target = sum(nums) / 2
- Check if total sum is even first
- Find subset that sums to half

### Target Sum (Count Ways)
- Count number of ways to reach target
- Use dictionary: `dp[sum] = count`
- Add counts from take/skip decisions

### 0/1 Knapsack (Max Value)
- Maximize value under weight constraint
- Track `dp[weight] = max_value`
- Choose max(skip, take + value)

---

## Key Patterns

**Subset problems**: Track achievable sums/states in set

**Counting problems**: Use dict to track count for each state

**Optimization problems**: Track best value for each capacity

**Space optimization**: Process items in reverse to reuse array

**Early termination**: Return immediately when target reached

---

## Pitfalls

- **Reusing items**: When using 1D array, iterate backwards or use separate set
- **Odd sum in partition**: Check `sum % 2 == 0` before attempting partition
- **Large targets**: Space complexity O(target), can be prohibitive
- **Integer overflow**: With large sums, consider type limits

---

## Knapsack vs Other DP

Use **0/1 knapsack** when: each item used at most once

Use **unbounded knapsack** when: unlimited supply of each item

Use **backtracking** when: need all valid subsets, not just existence/count