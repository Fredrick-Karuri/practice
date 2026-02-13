
#### Exercise #####

# function that counts how many times each word appears in a sentence
def count_words(sentence):
    """
    how to do it :
    1.split the sentence into individual words
    2.create an empty dict
    3.loop through each word
    4.if the word is already in the dictionary increase its count
    5.if its new add it with a count of 1 
    """
    sentence_words = sentence.split()
    seen_words={}

    for word in sentence_words:
        if word in seen_words:
            seen_words[word] += 1 # increase the count
        else:
            seen_words[word] =1 # first time seeing it 
            
    return seen_words


# function that returns true if a string is a palindrome
def is_palindrome(s):
    """
    the plan:
    1.start with one pointer at the beginning
    2.start another pointer at the end
    3.compare the characters at both pointers
    4.if they dont match, not a palindrome, return false
    5.if they match, move the pointers closer together and keep checking
    6.if we make it through without finding mismatches, its a palindrome, return true
    """
    left = 0
    right = len(s)-1

    while left < right:
        if not s[left] == s[right]:
            return False
        left +=1
        right -=1
    return True



# function that finds the two numbers in an array that add up to a target
def two_sum(numbers_array,target):
    """
    the plan:
    1.create empty hashmap to store numbers we have seen and their indices
    2.loop through the array with index and value
    3.calculate the  complement: target - current number
    4.check if complement exists in hashmap
        .if yes , we found the pair, return their indices
        .if no store the current number and its index in hashmap, keep going
    5.if we finish the loop without finding the pair, return None
    
    """

    seen_numbers={}
    for current_index, num in enumerate(numbers_array):
        complement = target - num
        if complement in seen_numbers:
            return [seen_numbers[complement],current_index ] #return both indices
        seen_numbers[num] = current_index # store number with its index
    return None
    

print("Word count:",count_words("hello world hello"))
print("Is 'racecar' a palindrome:" ,is_palindrome("racecar"))
print ("Two sum:",two_sum([2,7,11,15],9))