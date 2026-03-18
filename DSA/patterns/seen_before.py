
## Pattern 3 : Hash map for "seen before"
"""
How it works:
1.Create and empty set called seen
2.Loop through the array
3.If the currenet number is already in seen, its a duplicate, return it
4.Otherwise, add it to seen and continue

Common uses:
1.Finding duplicates
2.Checking for pairs that sum to a target
3.Tracking visted nodes in a graph
4.Detecting cycles

Why it's efficient: 
Set looksups and insertions are O(1) on average, making this O(n) overall instead of 
O(n^2) with nested loops.

"""
def find_duplicate(arr):
    """ Find first duplicate in array """
    seen = set()
    for num in arr:
        if num in seen:
            return num
        seen.add(num)
    return None

print("\n Find duplicate: ")
print("First Duplicate: ", find_duplicate([1,2,3,2,4]))
