# Task 5: list (create a one-way linked list)
# Define a Linked List with a structure
# function to display elements of the entire list
# Function to add item to n-th index of list - if n<0, the last element
# Function to delete item to n-th index of list - if n<0, the last element
class Node:
    def __init__(self, data, next):
        self.data = data
        self.next = None
class linkedList: # Defining a linked list
    def __init__(self):
        self.head = None
    def display(self): # function that displays elements of the entire list; note: REMOVED DATA PARAMETER AFTER SELF
        currentNode = self.head 
        while currentNode: 
            print(currentNode.data)
            currentNode = currentNode.next
    def add_to_nth_index(self, data, index): # function that adds element to nth index; but adds to the end if n<0
        newNode = Node(data, None)                          # note: CHANGED THIS FROM 1 PARAMETER TO 2 (ERROR: NO NEXT PARAMETER)
        if index < 0:           # when index < 0
            currentNode = self.head
            while currentNode:
                if currentNode.next == None:
                    currentNode.next = newNode
                    break
                currentNode = currentNode.next
        elif index == 0:        # when index = 0 (adding to the beginning of the list)
            newNode.next = self.head
            self.head = newNode
        else:           # when index >= 0
            currentNode = self.head
            position = 0 # note: CHANGED FROM -1 TO 0 TO FIX ERROR
            while currentNode:
                if index == position + 1:
                    if currentNode.next == None:
                        currentNode.next = newNode
                        break
                    newNode.next = currentNode.next
                    currentNode.next = newNode
                    break
                currentNode = currentNode.next
                position += 1           # ADDED THIS TO FIX ERROR
    def delete_nth_item(self, index):     # function that deletes item at nth index  Note: ERROR IN THIS CODE: DELETES ELEMENT AFTER INDEX
        currentNode = self.head     # self.head is the first element in the list (index of 0)
        if index == 0: # deleting 1st element
            if currentNode.next == None:    # if there is only one element in the list
                self.head = None
            currentNode.data = currentNode.next.data    # if there is more than one element in the list
            currentNode.next = currentNode.next.next
        elif index < 0:         # deleting last item in list (index < 0)
            while currentNode:
                if (currentNode.next.next == None):
                    currentNode.next = None
                    break
                currentNode = currentNode.next
        else:       # deleting nth element in list
            position = 0
            while currentNode:
                if index == position + 1:
                    currentNode.next = currentNode.next.next
                    break
                position += 1
                currentNode = currentNode.next
# Test code
test = linkedList()
test.add_to_nth_index(1, 0)
test.add_to_nth_index(2, 1)
test.add_to_nth_index(3, 2)
test.add_to_nth_index(4, -1)
test.add_to_nth_index(-1, 0)
test.add_to_nth_index("new", 2)
test.display()
print("deleting elements from list\n")
print("deleting first element\n")
test.delete_nth_item(0)
test.display()
print("deleting last element")
test.delete_nth_item(-1)
test.display()
print("deleting 2nd element (index 1)")
test.delete_nth_item(1)
test.display()
print("deleting last element (index 2)")
test.delete_nth_item(2)
test.display()
# For this task, I first looked up how to create a linked list in Python, and it said to use classes. So, I did some research on 
# what classes are and how they work, which led to reading the articles in the Python tutorial about what OOP is and what 
# classes and objects are.
# Sources: 
# multiple links in this Python tutorial (https://www.w3schools.com/python/default.asp)
# https://www.geeksforgeeks.org/python/python-linked-list/


# Task 6: stacks and queues
class stack: # Stack (LIFO)
    def __init__(self):
        self.head = None
    def push (self, value):   # push : value
        currentNode = self.head
        newNode = Node(value, None)
        if currentNode == None:
            newNode.next = self.head
            self.head = newNode
        while currentNode:
            if currentNode.next == None:
                currentNode.next = newNode
                break
            currentNode = currentNode.next
    def pop (self):         # pop (without getval element)
        currentNode = self.head
        if currentNode.next == None:    # if there is one element in the list
            currentNode = None
        while currentNode:
            if currentNode.next.next == None:
                currentNode.next = None
                break
            currentNode = currentNode.next
    def getval(self):
        currentNode = self.head
        while currentNode:
            if currentNode.next == None:
                return currentNode.data
            currentNode = currentNode.next
    def display(self):  # FOR TESTING 
        currentNode = self.head
        while currentNode:
            print(currentNode.data)
            currentNode = currentNode.next
# Test code
print("Stack test code: ")
stackTest = stack()
stackTest.push(1)
stackTest.push(2)
stackTest.push(3)
stackTest.display()
print("getval: " + str(stackTest.getval()))
print("pop first value")
stackTest.pop()
stackTest.display()
print("getval: " + str(stackTest.getval()))
print("pop second value")
stackTest.pop()
stackTest.display()
print("pop last value")
print("getval: " + str(stackTest.getval()))
stackTest.pop()
stackTest.display()


class queue:        # Queue (FIFO)
    def __init__(self):
        self.head = None
    def enqueue(self, value):
        newNode = Node(value, None)
        currentNode = self.head
        if currentNode == None:
            newNode.next = self.head
            self.head = newNode
        else: 
            while currentNode:
                if currentNode.next == None:
                    currentNode.next = newNode
                    break
                currentNode = currentNode.next
    def dequeue(self):
        currentNode = self.head
        if currentNode == None:
            print("There are no elements in the list")
        elif currentNode.next == None:
            self.head = None
        else:
            currentNode.data = currentNode.next.data
            currentNode.next = currentNode.next.next
    def getval(self):
        if self.head == None:
            print("There are no elements in the list")
        return self.head.data
    def display(self): # FOR TESTING
        currentNode = self.head
        while currentNode:
            print(currentNode.data)
            currentNode = currentNode.next
# Test code
print("Queue test code: ")
queueTest = queue()
queueTest.enqueue(1)
queueTest.enqueue(2)
queueTest.enqueue(3)
queueTest.display()
print("getval: " + str(queueTest.getval()))
print("pop first value")
queueTest.dequeue()
queueTest.display()
print("getval: " + str(queueTest.getval()))
print("pop second value")
queueTest.dequeue()
queueTest.display()
print("pop last value")
print("getval: " + str(queueTest.getval()))
queueTest.dequeue()
queueTest.display()
# Sources: Python tutorial (link in task 5)
