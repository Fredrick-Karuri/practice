# Pattern: Dynamic Programming (DP)

Dynamic Programming is used when a problem can be broken into
**overlapping subproblems** and the solution to a larger problem
depends on solutions to **smaller versions of the same problem**.

DP is not about cleverness.
It is about **remembering answers so you don’t recompute them**.

---

## The Core DP Question

Every DP problem answers this first:

> **What is the smallest subproblem that helps me build the answer?**

If you can’t define that clearly, stop and think — coding too early
always leads to confusion.

---

## When to Use DP

Use DP when the problem asks for:
- minimum / maximum value
- number of ways
- optimal choice under constraints
- whether something is possible

And:
- brute force is exponential
- subproblems repeat

Classic signals:
- “min cost”
- “max profit”
- “how many ways”
- “best possible”
- “can we reach…”

---

## DP Mental Model (Very Important)

DP is about **the last decision**.

Ask:
> “If I’m already at the answer, what was the final step I took?”

That final step defines the transition.

Example (Coin Change):
- Last step = choosing the last coin
- Remaining problem = amount − coin

---

## DP Recipe (Use This Every Time)

1. **Define the state**
   - What does `dp[i]` represent?
   - Be precise. One sentence.

2. **Define the base case**
   - Smallest input that is obviously solvable

3. **Define the transition**
   - How does a bigger state depend on smaller ones?

4. **Choose the order**
   - Bottom-up: smallest → largest
   - Top-down: recursion + memo

If you skip any step, DP will feel random.

---

## DP Categories in This Repo

### 1️⃣ 1D DP
State depends on a single variable.

Examples:
- Coin Change
- House Robber
- Climbing Stairs

Shape:
```text
dp[i] ← dp[i - something]
