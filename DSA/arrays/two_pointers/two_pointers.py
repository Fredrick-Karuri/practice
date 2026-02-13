
## Pattern 1 : Two pointers

""" 
When to use: When you need to compare elements from opposite ends or at different speeds

How it works:
1.left starts at index 0 (first element)
2.right starts at index len(arr) - 1
3.while left is less than right, print both values and bring the pointers towards each other
4.loop ends when pointers meet in the middle

Common uses:
1.finding pairs that sum to a target (in sorted arrays)
2.reversing arrays/strings
3.palindrome checking
4.removing duplicates

The setup:
left = 0
right = len(arr) -1
while left<right:
    #do somethin with arr[left] and arr[right]
    #move pointers based on some condition
    left += 1
    right -=1 

The technique is efficient (O(n) time) because each pointer traverses the array only once

 """
from typing import List


def two_pointers_example(arr):
    left,right = 0, len(arr) -1
    while left < right:
        print(f"Left:{arr[left]}, Right:{arr[right]}")
        left += 1
        right -= 1
print("Two Pointers:")

two_pointers_example([1,2,3,4,5])



def removeDuplicates(self, nums: List[int]) -> int:
    '''
    Slow/fast pointer approach:
    since array is sorted, duplicates are adjacent
    use two pointers:
    slow: tracks position where next unique element should go
    fast: scan through array looking for new unique elements

    '''
    if len(nums) == 0:
        return 0
    
    # slow pointer: position for next unique element
    slow = 0

    # fast pointer: scan through the array
    for fast in range(1,len(nums)):
        #found a new unique number?
        if nums[fast] != nums[slow]:
            slow +=1 # move slow forward
            nums[slow]=nums[fast] # place unique number at slow position
    #slow is index of last unique element
    #so number of unique element is slow +1
    return slow +1

def moveZeroes(self, nums: List[int]) -> None:
    """
    Do not return anything, modify nums in-place instead.

    problem: move all zeros to the end while maintaining relative order of non-zeros
    example:[0,1,0,3,12] -> [1,3,12,0,0]
    pattern: slow/fast two pointers

    the plan:
    1.initialize slow pointer at index 0(tracks position for next non-zero)
    2.use fast pointer to scan through the entire array
    3.for each element at fastpointer:
        -if nums[fast] is NON-ZERO:
            .swap nums[slow] with nums[fast]
            .move slow pointer forward (slow+=1)
        -if nums[fast] is ZERO:
            .do nothing just continue scanning with fast
    4.after loop completes, all non-zeros will be at the front and all zeros will 
        naturally be at the end

    why it works:
    -slow pointer marks where the next nonzero should go
    -we swap nonzeros to the front pushing zeros backwards
    -by swapping, (not overwriting) we preserve all elements
        
    """
    slow = 0
    array_length= range(len(nums))
    for fast in array_length:
        if nums[fast] != 0:
            nums[slow],nums[fast]=nums[fast],nums[slow]
            slow+=1




def threeSum(self, nums: List[int]) -> List[List[int]]:
    """
    THE PROBLEM: find all unique triplets that add to 0

    PATTERN: sort + two pointer 

    INSIGHT: fix one number, then use two pointers to find pairs that sum to its negative

    THE PLAN: 
    1.sort the array
    2.loop through each number as the "first" number
    3.for each first number, use two pointers(left and right) to find pairs
    4.skip duplicates to avoid duplicate triplets
    5.if sum == 0 , add triplet and move both pointers
    6.if sum < 0 ,move left pointer right (need larger sum)
    7.if sum > 0, move right pointer left (need smaller sum)

    Example: [-1,0,1,2,-1,-4] → sorted: [-4,-1,-1,0,1,2]
    - Fix -1: find two numbers that sum to 1 → found: [-1,0,1]

    """
    nums.sort() #sort first
    result = []
    n = len(nums)

    for i in range(n-2):
        #skip duplicate first numbers
        if i > 0 and nums[i] == nums[i-1]:
            continue
        
        #Two pointers for remaining array
        left =i+1
        right= n-1
        target = -nums[i] # we need two numbers that sum to this

        while left < right:
            current_sum = nums[left] +nums[right]

            if current_sum == target:
                result.append([nums[i],nums[left],nums[right]])

                #skip duplicates for left pointer
                while left < right and nums[left] == nums[left +1]:
                    left+=1
                # skip duplicates for right pointer
                while left < right and nums[right] == nums[right-1]:
                    right-=1
                
                left +=1
                right -=1
            elif current_sum <target:
                left +=1 #need larger sum
            else:
                right -=1 # need smaller sum
    return result    


        

            