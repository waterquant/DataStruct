# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 16:36:48 2018

@author: 123
"""


class TreeNode():
    def __init__(self, key, val, left=None, right=None, parent=None):
        self.key = key
        self.val = val
        self.leftChild = left
        self.rightChild = right
        self.parent = parent
        self.bf = 0

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
            current = current.leftChild
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


class AVLTree():
    def __init__(self):
        self.root = None
        self.size = 0

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
                self.updateBalance(currentNode.leftChild)
        elif key > currentNode.key:
            if currentNode.hasRightChild():
                self._put(key, val, currentNode.rightChild)
            else:
                currentNode.rightChild = TreeNode(key, val, parent=currentNode)
                self.updateBalance(currentNode.rightChild)
        else:
            currentNode.val = val

    def __setitem__(self, k, v):
        self.put(k, v)

    def updateBalance(self, node):
        if node.bf > 1 or node.bf < -1:
            self.rebalance(node)
            return
        if node.parent:
            if node.isLeftChild():
                node.parent.bf += 1
            elif node.isRightChild():
                node.parent.bf -= 1
            if node.parent.bf != 0:
                self.updateBalance(node.parent)

    def rotateLeft(self, rotRoot):
        newRoot = rotRoot.rightChild
        rotRoot.rightChild = newRoot.leftChild
        if newRoot.leftChild:
            newRoot.leftChild.parent = rotRoot
        newRoot.parent = rotRoot.parent
        if rotRoot.isRoot():
            self.root = newRoot
        else:
            if rotRoot.isLeftChild():
                rotRoot.parent.leftChild = newRoot
            else:
                rotRoot.parent.rightChild = newRoot
        newRoot.leftChild = rotRoot
        rotRoot.parent = newRoot
        rotRoot.bf = rotRoot.bf + 1 - min(
                                    newRoot.bf, 0)
        newRoot.bf = newRoot.bf + 1 + max(
                                    rotRoot.bf, 0)

    def rotateRight(self, rotRoot):
        newRoot = rotRoot.leftChild
        rotRoot.leftChild = newRoot.rightChild
        if newRoot.rightChild:
            newRoot.rightChild.parent = rotRoot
        newRoot.parent = rotRoot.parent
        if rotRoot.isRoot():
            self.root = newRoot
        else:
            if rotRoot.isRightChild():
                rotRoot.parent.rightChild = newRoot
            else:
                rotRoot.parent.leftChild = newRoot
        newRoot.rightChild = rotRoot
        rotRoot.bf = rotRoot.bf + 1 + max(
                                    newRoot.bf, 0)
        newRoot.bf = newRoot.bf + 1 - min(
                                    rotRoot.bf, 0)

    def rebalance(self, node):
        if node.bf < 0:
            if node.rightChild.bf > 0:
                self.rotateRight(node.rightChild)
                self.rotateLeft(node)
            else:
                self.rotateLeft(node)
        elif node.bf > 0:
            if node.leftChild.bf < 0:
                self.rotateLeft(node.leftChild)
                self.rotateRight(node)
            else:
                self.rotateRight(node)

    def height(self):
        return self._height(self.root)

    def _height(self, node):
        if not node:
            return -1
        else:
            return max(self._height(node.leftChild),
                       self._height(node.rightChild)) + 1

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

    def output(self):
        self._output(self.root)

    def _output(self, startNode):
        if startNode:
            self._output(startNode.leftChild)
            print(startNode.key, startNode.val)
            self._output(startNode.rightChild)

    def remove(self, currentNode):
        if currentNode.isLeaf():
            if currentNode == currentNode.parent.leftChild:
                currentNode.parent.leftChild = None
            else:
                currentNode.parent.rightChild = None
        elif currentNode.hasBothChild():
            succ = currentNode.rightChild.findMin()
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


if __name__ == '__main__':
    b = AVLTree()
    b[10] = 'cat'
    b[20] = 'dog'
    b[30] = 'tiger'
    b[40] = 'fish'
    b[35] = 'monkey'
    b[50] = 'sheep'
    b.output()
    print(f'b.height={b.height()}')
