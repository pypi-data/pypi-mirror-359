# Basic Programming (second quest) Python file


# Task 1: Hello World
print("Hello World")


# Task 2: loop (find the sum of 1^2, 2^2, 3^2,..., 100^2)
sum = 0
for i in range(100):
    sum += (i + 1)**2
print(sum)
# Sources: 
# needed to review syntax for exponents in Python (https://www.w3schools.com/python/python_functions.asp)


# Task 3: recursion (use recursive calls to find the sum of 1^2, 2^2, 3^2,..., 100^2)
def task3(i):
    if i == 1:
        return 1
    return (i**2) + task3(i - 1)
print(task3(100))
# Sources:
# Needed to review syntax for a function (https://pythonguides.com/square-a-number-in-python/)


# Task 4: structures (Define a data type equivalent to the following structure (C), Output all members.)
# Structures are not in Python, so classes can be used to replicate the code in the instructions
class st:
    def __init__(self, key, str):
        self.key = key
        self.str = str
    def output(self):
        print("key: " + str(self.key) + " str: " + self.str)
task4 = st(101, "This is hell.")
task4.output()
# Sources:
# https://stackoverflow.com/questions/12018992/print-combining-strings-and-numbers
# https://stackoverflow.com/questions/35988/c-like-structures-in-python
# https://www.w3schools.com/python/python_classes.asp