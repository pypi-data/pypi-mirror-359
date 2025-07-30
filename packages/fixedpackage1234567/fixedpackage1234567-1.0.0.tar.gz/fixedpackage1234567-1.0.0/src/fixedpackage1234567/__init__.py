# Task 1
def hello():
    print("Hello world")

# Task 2
def loop():
    sum = 0
    for i in range(100):
        sum += (i + 1)**2
    print(sum)

# Task 3
def task3(i):
    if i == 1:
        return 1
    return (i**2) + task3(i - 1)

# Task 4
class st:
    def __init__(self, key, str):
        self.key = key
        self.str = str
    def output(self):
        print("key: " + str(self.key) + " str: " + self.str)

# Task 5
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

# Task 6
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

# Task 7
class treeNode:
    def __init__(self, data, left, right):
        self.data = data
        self.left = None
        self.right = None

def displayTree(node):
    if node is not None:
        print(node.data)
        if node.left is not None:
            displayTree(node.left)
        if node.right is not None:
            displayTree(node.right)

def searchTree(root, data):
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

def addElementTree(root, data):
    if searchTree(root, data) is not None:
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

def deleteElementTree(root, value):
    deleteThisNode = searchTree(root, value)
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

# Task 8
def hash_function(key):
    firstthree = int(key[:3])
    secondthree = int(key[3:6])
    last4digits = int(key[-4:])
    sum = firstthree + secondthree + last4digits
    return sum % 1234123412

# Task 9
class hashTreeNode:
    def __init__(self, key, data, left, right):
        self.key = key
        self.data = data
        self.left = None
        self.right = None

def displayHashTree(node):
    if node is not None:
        print("key: " + str(node.key) + " data: " + str(node.data))
        if node.left is not None:
            displayHashTree(node.left)
        if node.right is not None:
            displayHashTree(node.right)

def searchHashTree(root, key, value):
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

def predRightHashTree(node):
    currentNode = node
    while currentNode:
        if currentNode.right is not None:
            currentNode = currentNode.right
        else:
            break
    return currentNode

def predHashTree(node):
    pred = node
    if node.left is not None:
        pred = predRightHashTree(node.left)
    return pred

def parentHashTree(root, node):
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
    
def deleteElementHashTree(root, data):
    key = hash_function(data)
    deleteThisNode = searchHashTree(root, key, data)
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
            predecessor = predHashTree(deleteThisNode)
            # two cases: if predecessor has zero or one child
            if (predecessor.left is None) and (predecessor.right is None):
                parentPredecessor = parentHashTree(root, predecessor)
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
                parentPredecessor = parentHashTree(root, predecessor)
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
            parent1 = parentHashTree(root, deleteThisNode)
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
            predecessor = predHashTree(deleteThisNode)
            # case 1: predecessor has no children
            if (predecessor.left is None) and (predecessor.right is None):
                parentPredecessor = parentHashTree(root, predecessor)
                if parentPredecessor.left == predecessor:
                    parentPredecessor.left = None
                elif parentPredecessor.right == predecessor:
                    parentPredecessor.right = None
                parentDeleted = parentHashTree(root, deleteThisNode)
                if parentDeleted.left == deleteThisNode:
                    parentDeleted.left = predecessor
                elif parentDeleted.right == deleteThisNode:
                    parentDeleted.right = predecessor
                predecessor.right = deleteThisNode.right
                return root
            #case 2: predecessor has one child
            elif predecessor.left is not None:
                # make the parent of the predecessor point to the child of the predecessor
                parentPredecessor = parentHashTree(root, predecessor)
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
                parentDeleted = parentHashTree(root, deleteThisNode)
                if parentDeleted.left == deleteThisNode:
                    parentDeleted.left = predecessor
                elif parentDeleted.right == deleteThisNode:
                    parentDeleted.right = predecessor
                return root
    return root
            