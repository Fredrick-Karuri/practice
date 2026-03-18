# Pattern: Greedy

Greedy algorithms make **locally optimal choices** at each step, never reconsidering previous decisions.

Works when local optimality leads to global optimality.

Think: *Make the best choice now, trust it's best overall.*

---

## When to Use Greedy

Use greedy when:
- Problem has **optimal substructure** (optimal solution contains optimal subsolutions)
- **Greedy choice property** holds (local optimum leads to global optimum)
- "Maximize/minimize" with clear best choice at each step
- Scheduling, interval, or resource allocation problems

Keywords: "maximum", "minimum", "earliest", "latest", "fewest steps"

---

## Core Mental Model

One-pass decision making:

> **Make best choice at current step, never look back.**

```python
def greedy_solution(items):
    result = initial_state
    
    for item in items:
        # Make locally optimal choice
        if is_best_choice(item):
            take_action(item)
            update_state()
    
    return result
```

---

## Common Variations

### Interval Problems
- Sort intervals by start/end time
- Greedily select non-overlapping intervals
- Examples: meeting rooms, minimum intervals to remove

### Jump Game
- Track farthest reachable position
- Update with each position's jump range
- Return when target reached or unreachable

### Gas Station
- Track running surplus/deficit
- If total surplus ≥ 0, solution exists
- Start from position after last deficit

### Task Scheduling
- Process high-frequency tasks first
- Maintain cooling period between same tasks
- Idle slots when necessary

---

## Key Patterns

**Sorting first**: Often need sorted order to make greedy choice

**Tracking extremes**: Max/min values, farthest reach, earliest deadline

**Single pass**: Process items once, no backtracking

**Proof by exchange**: Swap optimal with greedy, show no improvement

---

## Pitfalls

- **Wrong greedy choice**: Not all "maximize X" problems are greedy
- **Missing proof**: Greedy seems right but fails edge cases
- **Forgetting to sort**: Many greedy algorithms need sorted input
- **Premature optimization**: DP might be needed if greedy fails

---

## Greedy vs Dynamic Programming

Use **greedy** when: local optimum guarantees global optimum, one-pass solution

Use **DP** when: need to consider multiple choices, overlapping subproblems

Greedy is O(n) or O(n log n) with sorting; DP is typically O(n²) or higher.