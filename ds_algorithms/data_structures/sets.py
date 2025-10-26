
######## Sets #######

# Sets = no duplicates, O(1) lookup
unique_nums = {1,2,3,3,4,4,5}
print("Set (Duplicates removed) :",unique_nums)

# Adding and removing
unique_nums.add(6)
print("After adding:",unique_nums)
unique_nums.remove(1)
print("After removing:",unique_nums)

# Check membership - O(1) time
print("Is 3 in set:", 3 in unique_nums )

# converting list to set (removes duplices)
nums_with_dups = [1,2,2,3,3,3,4]
unique = set(nums_with_dups)
print("Unique set from list:",unique)

# Set operations
set1={1,2,3,4}
set2 = {3,4,5,6}

print ("Intersection:",set1 & set2) #common elements
print ("Union:", set1 | set2) # All elements
print ("Difference:", set1 - set2) # In set1 but not in set2