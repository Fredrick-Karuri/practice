##### String Operations #####

s = " Hello World"

#common operations
print("Lowercase:",s.lower())
print("Uppercase:",s.upper())
print("Split",s.split()) # split on white space by default
print("Split on 'o': ",s.split('o'))

#Joining strings
words = ["Hello","World"]
joined = ' '.join(words)
print("Joined:",joined)

# checking substring
print("'World' in s :", 'World' in s)

# String iteration
for i,char in enumerate(s):
    print(f"Index {i}: {char}")
    if i >=4:
        break
#  Reversing a string
reversed_s = s[::-1] # Slice with step -1
print("Reversed string: ", reversed_s)