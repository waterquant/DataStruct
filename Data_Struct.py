# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 09:22:53 2018

@author: 123
"""


class Queue():
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)


def hotPotato(namelist, num):
    q = Queue()
    for name in namelist:
        q.enqueue(name)
    while q.size() > 1:
        for i in range(num):
            q.enqueue(q.dequeue())
        q.dequeue()
    return q.dequeue()


class Deque():
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def addFront(self, item):
        self.items.append(item)

    def addRear(self, item):
        self.items.insert(0, item)

    def removeFront(self):
        return self.items.pop()

    def removeRear(self):
        return self.items.pop(0)

    def size(self):
        return len(self.items)


def huiChecker(namelist):
    d = Deque()
    Flag = True
    for name in namelist:
        d.addFront(name)
    while d.size() > 1 and Flag:
        if d.removeFront() != d.removeRear():
            Flag = False
    return Flag


class Node():
    def __init__(self, initdata):
        self.data = initdata
        self.next = None

    def getData(self):
        return self.data

    def getNext(self):
        return self.next

    def setData(self, newdata):
        self.data = newdata

    def setNext(self, newnext):
        self.next = newnext


class OrderedList():
    def __init__(self):
        self.head = None

    def isEmpty(self):
        return self.head is None

    def size(self):
        count = 0
        current = self.head
        while current is not None:
            current = current.getNext()
            count += 1
        return count

    def search(self, item):
        stop = False
        found = False
        current = self.head
        while current is not None and not found and not stop:
            if current.getData() == item:
                found = True
            elif current.getData() > item:
                stop = True
            else:
                current = current.getNext()
        return found

    def remove(self, item):
        found = False
        stop = False
        current = self.head
        previous = None
        while current is not None and not stop and not found:
            if current.getData() == item:
                found = True
            elif current.getData() > item:
                stop = True
            else:
                previous = current
                current = current.getNext()
        if previous is None:
            if not stop:
                self.head = current.getNext()
            else:
                print('item not found')
        elif found:
            previous.setNext(current.getNext())
        else:
            print('item not found')

    def add(self, item):
        found = False
        current = self.head
        previous = None
        while current is not None and not found:
            if current.getData() > item:
                found = True
            else:
                previous = current
                current = current.getNext()
        temp = Node(item)
        if previous is None:
            temp.setNext(self.head)
            self.head = temp
        else:
            previous.setNext(temp)
            temp.setNext(current)


def recMC(coinValueList, change):
    minCoins = change
    if minCoins in coinValueList:
        return 1
    else:
        for i in [c for c in coinValueList if c <= change]:
            numCoins = 1 + recMC(coinValueList, change - i)
            if numCoins < minCoins:
                minCoins = numCoins
    return minCoins


'''
start = time.time()
print(recMC([1,5,10,21,25],63))
end = time.time()
print(f'time cost:{end-start}')
'''


class Stack():
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def size(self):
        return len(self.items)

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[self.size - 1]


def perChecker(symbolString):
    s = Stack()
    index = 0
    balance = True
    while index < len(symbolString) and balance:
        symbol = symbolString[index]
        if symbol in '{[(':
            s.push(symbol)
        else:
            if s.isEmpty():
                balance = False
            else:
                top = s.pop()
                if not matches(top, symbol):
                    balance = False
        index += 1
    if balance and s.isEmpty():
        return True
    else:
        return False


def matches(opend, close):
    opends = '([{'
    closes = ')]}'
    return opends.index(opend) == closes.index(close)


class HashTable():
    def __init__(self, size):
        self.size = size
        self.slots = [None]*self.size
        self.data = [None]*self.size

    def hashFunction(self, key):
        return key % self.size

    def rehash(self, oldhash):
        return (oldhash+1) % self.size

    def put(self, key, data):
        hashvalue = self.hashFunction(key)
        if self.slots[hashvalue] is None:
            self.slots[hashvalue] = key
            self.data[hashvalue] = data
        elif self.slots[hashvalue] == key:
            self.data[hashvalue] = data
        else:
            nextslot = self.rehash(hashvalue)
            while self.slots[nextslot] is not None and \
                    self.slots[nextslot] == key:
                nextslot = self.rehash(nextslot)
            if self.slots[nextslot] is None:
                self.slots[nextslot] = key
                self.data[nextslot] = data
            else:
                self.data[nextslot] = data

    def get(self, key, default=None):
        startslot = self.hashFunction(key)
        position = startslot
        stop = False
        found = False
        data = default
        while self.slots[position] is not None and not stop and not found:
            if self.slots[position] == key:
                found = True
                data = self.data[position]
            else:
                position = self.rehash(position)
                if position == startslot:
                    stop = True
        return data

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, data):
        self.put(key, data)

    def __len__(self):
        return len(self.keys())

    def __str__(self):
        return '{'+str(list(zip(self.keys(),
                                self.values()))).strip('[').strip(']')+'}'

    def __repr__(self):
        return '{'+str(list(zip(self.keys(),
                                self.values()))).strip('[').strip(']')+'}'

    def length(self):
        return len(self.keys())

    def keys(self):
        return [s for s in self.slots if s is not None]

    def values(self):
        return [s for s in self.data if s is not None]

    def pop(self, key, default=None):
        startslot = self.hashFunction(key)
        position = startslot
        stop = False
        found = False
        data = default
        while self.slots[position] is not None and not stop and not found:
            if self.slots[position] == key:
                found = True
                data = self.data[position]
                self.slots[position] = None
                self.data[position] = None
            else:
                position = self.rehash(position)
                if position == startslot:
                    stop = True
        return data

    def update(self, hashtable):
        if self.length() + hashtable.length() <= self.size:
            for k, v in zip(hashtable.keys(), hashtable.values()):
                self.put(k, v)
        else:
            print('out of the range of hashtable')

    def clear(self):
        self.slots = [None]*self.size
        self.data = [None]*self.size

    def fromkeys(self, seq, val=None):
        if len(seq) <= self.size:
            for k, v in zip(seq, [val]*len(seq)):
                self.put(k, v)
        else:
            print('out of the range of hashtable')


# 用两个Stack实现Queue
class QueueStack():
    def __init__(self):
        self.s1 = Stack()
        self.s2 = Stack()

    def isEmpty(self):
        return self.s1.isEmpty() and self.s2.isEmpty()

    def size(self):
        return self.s1.size() + self.s2.size()

    def enqueue(self, item):
        self.s1.push(item)

    def dequeue(self):
        if self.s2.isEmpty():
            while not self.s1.isEmpty():
                self.s2.push(self.s1.pop())
            return self.s2.pop()
        else:
            return self.s2.pop()


# 找到和最大子串
def findMaxsum(alist):
    sumall, sumtarget, bigsum, i_end, i_start = [0]*5
    for i in range(len(alist)-1):
        sumall += alist[i]
        if sumall < 0:
            sumall = 0
        if bigsum < sumall:
            bigsum = sumall
            i_end = i
    for i in range(i_end, 0, -1):
        sumtarget += alist[i]
        if sumtarget == bigsum:
            i_start = i
    return bigsum, alist[i_start:i_end]


class DoublyNode():
    def __init__(self, initdata):
        self.data = initdata
        self.next = None
        self.last = None

    def getData(self):
        return self.data

    def getNext(self):
        return self.next

    def getLast(self):
        return self.last

    def setData(self, newdata):
        self.data = newdata

    def setNext(self, newnext):
        self.next = newnext

    def setlast(self, newlast):
        self.last = newlast


class DoublyOrderedList():
    def __init__(self):
        self.head = None

    def isEmpty(self):
        return self.head is None

    def size(self):
        count = 0
        cur = self.head
        while cur:
            count += 1
            cur = cur.getNext()
        return count

    def search(self, item):
        found = False
        cur = self.head
        while cur and not found:
            if cur.getData() == item:
                found = True
            else:
                cur = cur.getNext()
        return found

    def remove(self, item):
        found = False
        cur = self.head
        pre = None
        while cur and not found:
            if cur.getData() == item:
                found = True
            else:
                pre = cur
                cur = cur.getNext()
        if pre is None:
            self.head = None
        if cur is None:
            print('item not found')
        else:
            pre.setNext(cur.getNext())
            cur.getNext().setLast(pre)

    def add(self, item):
        pass

    def output(self):
        cur = self.head
        while cur:
            print(cur.getData())
            cur = cur.getNext()


class A():
    def show(self):
        print('base class show')


class B(A):
    def show(self):
        print('derivated class show')


class C(object):
    def __init__(self, a, b):
        self.a1 = a
        self.b1 = b
        print('init')

    def mydefault(self):
        print('default')

    def __getattr__(self, name):
        return self.mydefault


class BinHeap():
    def __init(self):
        self.heapList = [0]
        self.currentSize = 0

    def percUp(self, i):
        while i//2 > 0:
            if self.heapList[i] < self.heapList[i//2]:
                self.heapList[i], self.heapList[i//2] =\
                    self.heapList[i//2], self.heapList[i]
            i = i//2

    def insert(self, k):
        self.heapList.append(k)
        self.currentSize += 1
        self.percUp(self.currentSize)

    def minChild(self, i):
        if i * 2 + 1 > self.currentSize:
            return i*2
        else:
            if self.heapList[i*2] < self.heapList[i*2+1]:
                return i*2
            else:
                return i*2 + 1

    def percDown(self, i):
        while i*2 <= self.currentSize:
            mc = self.minChild(i)
            if self.heapList[i] > self.heapList[mc]:
                self.heapList[i], self.heapList[mc] =\
                    self.heapList[mc], self.heapList[i]
            i = mc

    def delMin(self):
        retval = self.heapList[1]
        self.heapList[1] = self.heapList[self.currentSize]
        self.currentSize -= 1
        self.heapList.pop()
        self.percDown(1)
        return retval

    def buildHeap(self, alist):
        i = len(alist) // 2
        self.currentSize = len(alist)
        self.heapList = [0] + alist[:]
        while i > 0:
            self.percDown(i)
            i -= 1

    def output(self):
        temp = self.heapList[1:self.currentSize+1]
        for s in temp:
            print(s)


class BinarySearchTree():
    def __init__(self):
        self.root = None
        self.size = 0

    def length(self):
        return self.size

    def __len__(self):
        return self.size

    def __iter__(self):
        return self.root.__iter__()

    def put(self, key, val):
        if self.root:
            self._put(key, val, self.root)
        else:
            self.root = TreeNode(key, val)
        self.size += 1

    def _put(self, key, val, currentNode):
        if key < currentNode.key:
            if currentNode.hasLeftChild():
                self._put(key, val, currentNode.leftChild)
            else:
                currentNode.leftChild = TreeNode(key, val, parent=currentNode)
        else:
            if currentNode.hasRightChild():
                self._put(key, val, currentNode.rightChild)
            else:
                currentNode.rightChild = TreeNode(key, val, parent=currentNode)

    def __setitem__(self, k, v):
        self.put(k, v)

    def get(self, k):
        if self.root:
            res = self._get(k, self.root)
            if res:
                return res.payload
            else:
                return None
        else:
            return None

    def _get(self, key, currentNode):
        if not currentNode:
            return None
        elif currentNode.key == key:
            return currentNode
        elif currentNode.key < key:
            return self._get(key, currentNode.leftChild)
        else:
            return self._get(key, currentNode.rightChild)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        if self._get(key, self.root):
            return True
        else:
            return False

    def delete(self, key):
        if self.size > 1:
            nodeToRemove = self._get(key, self.root)
            if nodeToRemove:
                self.remove(nodeToRemove)
                self.size -= 1
            else:
                raise KeyError('Error, key not in tree')
        elif self.size == 1 and self.root.key == key:
            self.root = None
            self.size = 0
        else:
            raise KeyError('Error, key not in tree')

    def __delitem__(self, key):
        self.delete(key)

    def spliceOut(self, key):
        if self.isLeaf():
            if self.isLeftChild():
                self.parent.leftChild = None
            else:
                self.parent.rightChild = None
        elif self.hasAnyChildren():
            if self.hasLeftChild():
                if self.isLeftChild():
                    self.parent.leftChild = self.leftChild
                else:
                    self.parent.rightChild = self.leftChild
                self.leftChild.parent = self.parent
            else:
                if self.hasLeftChild():
                    self.parent.leftChild = self.rightChild
                else:
                    self.parent.rightChild = self.rightChild
                self.rightChild.parent = self.parent

    def findSuccessor(self):
        succ = None
        if self.hasRightChild():
            succ = self.rightChild.findMin()
        else:
            if self.parent:
                if self.isLeftChild():
                    succ = self.parent
                else:
                    self.parent.rightChild = None
                    succ = self.parent.findSuccessor()
                    self.parent.rightChild = self
        return succ

    def findMin(self):
        current = self
        while current.hasLeftChild():
            current = current.leftChild
        return current

    def remove(self, currentNode):
        if currentNode.isLeaf():
            if currentNode == currentNode.parent.leftChild:
                currentNode.parent.leftChild = None
            else:
                currentNode.parent.rightChild = None
        elif currentNode.hasBothChildren():
            succ = currentNode.findSuccessor()
            succ.spliceOut()
            currentNode.key = succ.key
            currentNode.payload = succ.payload
        else:
            if currentNode.hasLeftChild():
                if currentNode.isLeftChild():
                    currentNode.leftChild.parent = currentNode.parent
                    currentNode.parent.leftChild = currentNode.leftChild
                elif currentNode.isRightChild():
                    currentNode.leftChild.parent = currentNode.parent
                    currentNode.parent.rightChild = currentNode.leftChild
                else:
                    currentNode.replaceNodeData(
                            currentNode.leftChild.key,
                            currentNode.leftChild.val,
                            currentNode.leftChild.leftChild,
                            currentNode.leftChild.rightChild)
            else:
                if currentNode.isLeftChild():
                    currentNode.rightChild.parent = currentNode.parent
                    currentNode.parent.leftChild = currentNode.rightChild
                elif currentNode.isRightChild():
                    currentNode.rightChild.parent = currentNode.parent
                    currentNode.parent.rightChild = currentNode.rightChild
                else:
                    currentNode.replaceNodeData(
                            currentNode.rightChild.key,
                            currentNode.rightChild.val,
                            currentNode.rightChild.leftChild,
                            currentNode.rightChild.rightChild)


class TreeNode():
    def __init__(self, key, val, left=None, right=None, parent=None):
        self.key = key
        self.payload = val
        self.leftChild = left
        self.rightChild = right
        self.parent = parent

    def hasLeftChild(self):
        return self.leftChild

    def hasRightChild(self):
        return self.rightChild

    def isLeftChild(self):
        return self.parent and self.parent.leftChild == self

    def isRightChild(self):
        return self.parent and self.parent.rightChild == self

    def isRoot(self):
        return not self.parent

    def isLeaf(self):
        return not (self.leftChild or self.rightChild)

    def hasAnyChildren(self):
        return self.leftChild or self.rightChild

    def hasBothChildren(self):
        return self.leftChild and self.rightChild

    def replaceNodeData(self, key, val, lc, rc):
        self.key = key
        self.payload = val
        self.leftChild = lc
        self.rightChild = rc
        if self.hasLeftChild():
            self.leftChild.parent = self
        if self.hasRightChild():
            self.rightChild.parent = self
