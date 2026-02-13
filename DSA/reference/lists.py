#### lists ######
nums = [1, 2, 3, 4, 5]
print ("original list:",nums)

##Key operations
nums.append(6) #add to end - O(1)
print ("after append:",nums)

nums.pop() # remove from end - O(1)
print("After pop",nums)

nums.insert(0,0) # insert at index - O(n)
print ("After insert at 0:",nums)

## Accessing elements
first = nums[0] # first element
last = nums[-1] # last element
print(f"First element:{first}, Last Element: {last}")

## Slicing (important)
first_three_elements =nums[0:3] #Index 0,1,2 not including 3
middle=nums[2:5] #Index 2,3,4 
print("First three elements:",first_three_elements)
print("Middle:",middle)

## list comprehension (we'll use this a lot)
doubled =[x*2 for x in nums]
evens = [x for x in nums if x %2 == 0]
print ("Doubled:",doubled)
print ("Evens only:",evens)