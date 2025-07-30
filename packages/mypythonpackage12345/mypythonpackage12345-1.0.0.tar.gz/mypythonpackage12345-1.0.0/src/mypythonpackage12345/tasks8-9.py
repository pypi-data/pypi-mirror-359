# Task 8: Hash function
# Takes a key and computes a hash value, Do not use existing hash libraries such as sha256, Create your own hash function.
# Sources: I used some of these links to understand hash tables/functions 
# https://www.geeksforgeeks.org/hash-functions-and-list-types-of-hash-functions/
# https://www.youtube.com/watch?v=b4b8ktEV4Bg
# https://www.crowdstrike.com/en-us/cybersecurity-101/data-protection/data-hashing/
# https://www.geeksforgeeks.org/computer-networks/what-is-the-md5-algorithm/
# https://www.ssldragon.com/blog/sha-256-algorithm/
# https://www.geeksforgeeks.org/python/ascii-in-python/
# https://stackoverflow.com/questions/7983820/get-the-last-4-characters-of-a-string
# https://www.geeksforgeeks.org/python/what-is-a-modulo-operator-in-python/
# https://www.geeksforgeeks.org/python/how-to-substring-a-string-in-python/

# using folding method described in https://www.geeksforgeeks.org/hash-functions-and-list-types-of-hash-functions/
def hash_function(key):
    firstthree = int(key[:3])
    secondthree = int(key[3:6])
    last4digits = int(key[-4:])
    sum = firstthree + secondthree + last4digits
    return sum % 1234123412

# Test code in test_tasks7-9.py


# Task 9: hash value collision avoidance
# Combine the hash function and tree structure you have created so far, 
# Create a function that avoids collisions between hash values obtained from different inputs.

# make a hash that is a number that can be used as a key to find later (searching in a binary tree)
# take something, pass it through hash function, find it in tree, compare key and return value
# if two values have the same has, need to still store it somewhere

class hashTreeNode:
    def __init__(self, key, data, left, right):
        self.key = key
        self.data = data
        self.left = None
        self.right = None

def display(node):
    if node is not None:
        print("key: " + str(node.key) + " data: " + str(node.data))
        if node.left is not None:
            display(node.left)
        if node.right is not None:
            display(node.right)

def search(root, key, value):
    currentNode = root
    while currentNode:
        if currentNode.key == key:
            if currentNode.data == value:
                return currentNode
            currentNode = currentNode.left
            continue
        if currentNode.key < key:
            currentNode = currentNode.left
        elif currentNode.key > key:
            currentNode = currentNode.left
    return None

def addElementAvoidingCollisions(root, data):
    key = hash_function(data)
    newNode = hashTreeNode(key, data, None, None)
    if root == None:
        root = newNode
        return newNode
    else:
        currentNode = root
        while currentNode:
            if key <= currentNode.key:
                if currentNode.left is None:
                    currentNode.left = newNode
                    return root
                currentNode = currentNode.left
            elif key > currentNode.key:
                if currentNode.right is None:
                    currentNode.right = newNode
                    return root
                currentNode = currentNode.right
    return root

def predRight(node):
    currentNode = node
    while currentNode:
        if currentNode.right is not None:
            currentNode = currentNode.right
        else:
            break
    return currentNode

def pred(node):
    pred = node
    if node.left is not None:
        pred = predRight(node.left)
    return pred

def parent(root, node):
    if root == node:
        return None
    else:
        currentNode = root
        while currentNode:
            if currentNode.left == node or currentNode.right == node:
                return currentNode
            if node.key <= currentNode.key:
                currentNode = currentNode.left
            elif node.key > currentNode.key:
                currentNode = currentNode.right
        return currentNode

def deleteElement(root, data):
    key = hash_function(data)
    deleteThisNode = search(root, key, data)
    if root == deleteThisNode:
        if (deleteThisNode.left is None) and (deleteThisNode.right is None):
            return None
        elif ((deleteThisNode.left is not None) and not (deleteThisNode.right is not None)) or (not (deleteThisNode.left is not None) and (deleteThisNode.right is not None)):
            if deleteThisNode.left is not None:
                temp = deleteThisNode.left
                deleteThisNode.left = None
                return temp
            elif deleteThisNode.right is not None:
                temp = deleteThisNode.right
                deleteThisNode.right = None
                return temp
        elif (deleteThisNode.left is not None) and (deleteThisNode.right is not None):
            predecessor = pred(deleteThisNode)
            # two cases: if predecessor has zero or one child
            if (predecessor.left is None) and (predecessor.right is None):
                parentPredecessor = parent(root, predecessor)
                if parentPredecessor.left == predecessor:
                    parentPredecessor.left = None
                elif parentPredecessor.right == predecessor:
                    parentPredecessor.right = None
                if deleteThisNode.left is not None:
                    predecessor.left = deleteThisNode.left
                if deleteThisNode.right is not None:
                    predecessor.right = deleteThisNode.right
                return predecessor
            #case 2: predecessor has one child
            elif (predecessor.left is not None) or (predecessor.right is not None):
                parentPredecessor = parent(root, predecessor)
                if parentPredecessor.left == predecessor:
                    if predecessor.left is not None:
                        parentPredecessor.left = predecessor.left
                        predecessor.left = None
                    elif predecessor.right is not None:
                        parentPredecessor.left = predecessor.right
                        predecessor.right = None
                elif parentPredecessor.right == predecessor:
                    if predecessor.left is not None:
                        parentPredecessor.right = predecessor.left
                        predecessor.left = None
                    elif predecessor.right is not None:
                        parentPredecessor.right = predecessor.right
                        predecessor.right = None
                # switch root with predecessor
                if deleteThisNode.left is not None:
                    predecessor.left = deleteThisNode.left
                if deleteThisNode.right is not None:
                    predecessor.right = deleteThisNode.right
                return predecessor
    # if deleteThisNode is not the root
    else:
        if (deleteThisNode.left is None) and (deleteThisNode.right is None):
            currentNode = root
            while currentNode:
                if deleteThisNode.key <= currentNode.key:
                    if currentNode.left == deleteThisNode:
                        currentNode.left = None
                        break
                    currentNode = currentNode.left
                elif deleteThisNode.key > currentNode.key:
                    if currentNode.right == deleteThisNode:
                        currentNode.right = None
                        break
                    currentNode = currentNode.right
            return root
        # if deleteThisNode has one child
        elif ((deleteThisNode.left is not None) and not (deleteThisNode.right is not None)) or (not (deleteThisNode.left is not None) and (deleteThisNode.right is not None)):
            parent1 = parent(root, deleteThisNode)
            if parent1.left == deleteThisNode:
                if deleteThisNode.left is not None:
                    parent1.left = deleteThisNode.left
                elif deleteThisNode.right is not None:
                    parent1.left = deleteThisNode.right
            elif parent1.right == deleteThisNode:
                if deleteThisNode.left is not None:
                    parent1.right = deleteThisNode.left
                elif deleteThisNode.right is not None:
                    parent1.right = deleteThisNode.right
            return root
        # if deleteThisNode has two children
        elif (deleteThisNode.left is not None) and (deleteThisNode.right is not None):
            predecessor = pred(deleteThisNode)
            # case 1: predecessor has no children
            if (predecessor.left is None) and (predecessor.right is None):
                parentPredecessor = parent(root, predecessor)
                if parentPredecessor.left == predecessor:
                    parentPredecessor.left = None
                elif parentPredecessor.right == predecessor:
                    parentPredecessor.right = None
                parentDeleted = parent(root, deleteThisNode)
                if parentDeleted.left == deleteThisNode:
                    parentDeleted.left = predecessor
                elif parentDeleted.right == deleteThisNode:
                    parentDeleted.right = predecessor
                predecessor.right = deleteThisNode.right
                return root
            #case 2: predecessor has one child
            elif predecessor.left is not None:
                # make the parent of the predecessor point to the child of the predecessor
                parentPredecessor = parent(root, predecessor)
                if parentPredecessor.left == predecessor:
                    parentPredecessor.left = predecessor.left
                elif parentPredecessor.right == predecessor:
                    parentPredecessor.right = predecessor.left
                # make the predecessor point to the left and right sides of deleteThisNode
                if deleteThisNode.left is not None:
                    predecessor.left = deleteThisNode.left
                if deleteThisNode.right is not None:
                    predecessor.right = deleteThisNode.right
                # make the parent of the deleted node point to the predecessor
                parentDeleted = parent(root, deleteThisNode)
                if parentDeleted.left == deleteThisNode:
                    parentDeleted.left = predecessor
                elif parentDeleted.right == deleteThisNode:
                    parentDeleted.right = predecessor
                return root
    return root

one = hash_function("9739179225")
tree = hashTreeNode(one, "9739179225", None, None)
tree = addElementAvoidingCollisions(tree, "2015727917")
tree = addElementAvoidingCollisions(tree, "0000000000")
tree = addElementAvoidingCollisions(tree, "1234567989")
tree = addElementAvoidingCollisions(tree, "9999999999")
tree = addElementAvoidingCollisions(tree, "1234123412")
tree = addElementAvoidingCollisions(tree, "2015727918")
tree = addElementAvoidingCollisions(tree, "2015727981")
tree = addElementAvoidingCollisions(tree, "2015727916")
display(tree)