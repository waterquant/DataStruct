# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 10:13:46 2018

@author: 123
"""


class TreeNode():
    def __init__(self, key, val, left=None, right=None, parent=None):
        self.key = key
        self.val = val
        self.leftChild = left
        self.rightChild = right
        self.parent = parent

    def isRoot(self):
        return not self.parent

    def isLeaf(self):
        return not (self.leftChild or self.rightChild)

    def hasLeftChild(self):
        return self.leftChild

    def hasRightChild(self):
        return self.rightChild

    def isLeftChild(self):
        return self.parent and self.parent.leftChild == self

    def isRightChild(self):
        return self.parent and self.parent.rightChild == self

    def hasAnyChild(self):
        return self.leftChild or self.rightChild

    def hasBothChild(self):
        return self.leftChild and self.rightChild

    def replaceNodeData(self, key, val, lc, rc):
        self.key = key
        self.val = val
        self.leftChild = lc
        self.rightChild = rc
        if self.hasLeftChild():
            self.leftChild.parent = self
        if self.hasRightChild():
            self.rightChild.parent = self

    def findMin(self):
        current = self
        while current.hasLeftChild():
            current = self.leftChild
        return current

    def spliceOut(self):
        if self.isLeaf():
            if self.isLeftChild():
                self.parent.leftChild = None
            else:
                self.parent.rightChild = None
        else:
            self.parent.leftChild = self.rightChild
            self.rightChild.parent = self.parent


class BnrySrchTr():
    def __init__(self):
        self.root = None
        self.size = 0

    def length(self):
        return self.size

    def __len__(self):
        return self.size

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

    def __setitem__(self, key, val):
        self.put(key, val)

    def get(self, key, default='Nothing'):
        if self.root:
            res = self._get(key, self.root)
            if res:
                return res.val
            else:
                return default
        else:
            return default

    def _get(self, key, currentNode):
        if not currentNode:
            return None
        elif currentNode.key == key:
            return currentNode
        elif key < currentNode.key:
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
        if self.root is None:
            raise KeyError('the tree is empty, can not be deleted')
        elif self.size == 1 and self.root.key == key:
            self.size = 0
            self.root = None
        else:
            nodeToRemove = self._get(key, self.root)
            if nodeToRemove:
                self.remove(nodeToRemove)
                self.size -= 1
            else:
                raise KeyError('the key not found in tree')

    def __delitem__(self, key):
        self.delete(key)

    def remove(self, currentNode):
        if currentNode.isLeaf():
            if currentNode.isLeftChild():
                currentNode.parent.leftChild = None
            else:
                currentNode.parent.rightChild = None
        elif currentNode.hasBothChild():
            succ = currentNode.rightChild.findMin()
            succ.spliceOut()
            currentNode.key = succ.key
            currentNode.val = succ.val
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

    @ staticmethod
    def midTraversal(currentNode):
        if currentNode:
            BnrySrchTr.midTraversal(currentNode.leftChild)
            print(currentNode.key, currentNode.val)
            BnrySrchTr.midTraversal(currentNode.rightChild)

    def output(self):
        BnrySrchTr.midTraversal(self.root)


class HashTable():
    def __init__(self, size):
        self.size = size
        self.slots = [None]*self.size
        self.data = [None]*self.size

    def __len__(self):
        return self.size

    def hashFunction(self, key):
        return key % self.size

    def rehash(self, oldhash):
        return (oldhash+1) % self.size

    def put(self, key, value):
        hashvalue = self.hashFunction(key)
        if self.slots[hashvalue] is None:
            self.slots[hashvalue] = key
            self.data[hashvalue] = value
        elif self.slots[hashvalue] == key:
            self.data[hashvalue] = value
        else:
            nextslot = self.rehash(hashvalue)
            while self.slots[nextslot] and self.slots[nextslot] != key:
                nextslot = self.rehash(nextslot)
            if self.slots[nextslot] == key:
                self.data[nextslot] = value
            else:
                self.slots[nextslot] = key
                self.data[nextslot] = value

    def __setitem__(self, key, val):
        self.put(key, val)

    def get(self, key, default=None):
        startslot = self.hashFunction(key)
        position = startslot
        found = False
        stop = False
        data = default
        while self.slots[position] and not found and not stop:
            if self.slots[position] == key:
                found = True
                data = self.data[position]
            position = self.rehash(position)
            if position == startslot:
                stop = True
        return data

    def __getitem__(self, key):
        return self.get(key)

    def __repr__(self):
        k = [s for s in self.slots if s]
        v = [s for s in self.data if s]
        return '{' + str(list(zip(k, v))).strip('[').strip(']') + '}'

    def output(self):
        k = [s for s in self.slots if s]
        v = [s for s in self.data if s]
        print(list(zip(k, v)))


if __name__ == '__main__':
    b = BnrySrchTr()
    # b = HashTable(11)
    b[10] = 'tiger'
    b[20] = 'cat'
    b[50] = 'dog'
