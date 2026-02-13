# Dynamic Programming — 1D

1D Dynamic Programming is used when the state of the problem
depends on **a single variable**, and each answer can be built
from **smaller values of that same variable**.

Think of it as:
> “I’m moving forward one step at a time, reusing what I already solved.”

---

## When a Problem Is 1D DP

A problem is **1D DP** if:

- The state can be written as `dp[i]`
- `i` usually represents:
  - an index
  - an amount
  - a step
  - a position in a string or array
- `dp[i]` depends only on `dp[j]` where `j < i`

If you only need **one number to describe progress**, it’s 1D DP.

---

## Common 1D DP Questions

Look for phrases like:
- “minimum cost”
- “maximum profit”
- “fewest steps”
- “how many ways”
- “can we reach…”

And the answer grows as `i` increases.

---

## Core 1D DP Template

```python
dp = [inf] * (n + 1)
dp[0] = base_case

for i in range(1, n + 1):
    for each possible move:
        dp[i] = best(dp[i], dp[i - move] + cost)


