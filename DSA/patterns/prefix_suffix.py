from typing import List

def productExceptSelf(self, nums: List[int]) -> List[int]:
    """
    THE PROBLEM: return array where each element is product of all others except itelf

    PATTERN: prefix and suffix products (two pass approach)

    THE PLAN: 
    1.create result array initialized with 1s
    2.Left pass: accumulate left products into result
    3.right pass: accumulate right products into result
    4.return result

    INSIGHT: for each position, answer = (product of all left) * (product of all right)


    """
    n=len(nums)
    result=[1]*n

    #left pass: result[i] = product of all elements to the left
    left_product = 1
    for i in range(n):
        result[i] = left_product
        left_product*=nums[i]
    
    #right pass:multiply by product of all elements to the right
    right_product = 1
    for i in range(n-1,-1,-1):
        result[i]*=right_product
        right_product*=nums[i]
    return result