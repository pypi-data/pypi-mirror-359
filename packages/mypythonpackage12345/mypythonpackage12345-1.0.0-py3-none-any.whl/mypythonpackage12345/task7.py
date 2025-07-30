# Task 7: Tree Structure

# display all tree elements and depths below the start point : start point
# Search for nodes with key : key
# Add one Node with key as its value to the tree : key
# Add one node to the tree, by using a key given by the user, only if the key is not in the tree.
# Delete a node with key from the tree : key
# Delete one node to the tree, by using a key given by the user.

# Sources: 
# Python tutorial (link in task 5)
# tasks 5-6 for Python
# https://dnmtechs.com/referring-to-the-class-from-within-recursive-function-in-python-3/
# https://stackoverflow.com/questions/132988/is-there-a-difference-between-and-is
# https://www.w3schools.com/python/ref_keyword_not.asp
# task 7 for C


class treeNode:
    def __init__(self, data, left, right):
        self.data = data
        self.left = None
        self.right = None

def display(node):
    if node is not None:
        print(node.data)
        if node.left is not None:
            display(node.left)
        if node.right is not None:
            display(node.right)

def search(root, data):
    currentNode = root
    while currentNode:
        if currentNode.data == data:
            return currentNode
        else:
            if data < currentNode.data:
                currentNode = currentNode.left
            elif data > currentNode.data:
                currentNode = currentNode.right
    return None

def addElement(root, data):
    if search(root, data) is not None:
        print("The element is already in the tree")
        return root
    newNode = treeNode(data, None, None)
    currentNode = root
    if currentNode == None:
        currentNode = newNode
        return currentNode
    else:
        while currentNode:
            if data < currentNode.data:
                if currentNode.left is None:
                    currentNode.left = newNode
                    return root
                currentNode = currentNode.left
            elif data > currentNode.data:
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
            if node.data < currentNode.data:
                currentNode = currentNode.left
            elif node.data > currentNode.data:
                currentNode = currentNode.right
    return currentNode

def deleteElement(root, value):
    deleteThisNode = search(root, value)
    # if deleteThisNode is the root of the tree
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
                if value < currentNode.data:
                    if (currentNode.left).data == value:
                        currentNode.left = None
                        break
                    currentNode = currentNode.left
                elif value > currentNode.data:
                    if (currentNode.right).data == value:
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
    

print("Task 7 tree test code:")
test = treeNode(7, None, None)
test = addElement(test, 2)
test = addElement(test, 9)
test = addElement(test, 1)
test = addElement(test, 3)
test = addElement(test, 8)
test = addElement(test, 10)
display(test)
print("deleting the element 10 (no children)")
test = deleteElement(test, 10)
display(test)
print("deleting the element 9 (has one child)")
test = deleteElement(test, 9)
display(test)
print("deleting the element 2 (has two children and is not the root)")
test = deleteElement(test, 2)
display(test)
print("deleting the element 7 (has two children and is the root)")
test = deleteElement(test, 7)
display(test)