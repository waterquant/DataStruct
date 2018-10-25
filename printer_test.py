# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 13:44:50 2018

@author: 123
"""
import pandas as pd
import random
import re
import itertools


class Queue():
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def size(self):
        return len(self.items)

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()


class Printer():
    def __init__(self, ppm):
        self.pagerate = ppm
        self.remainingtime = 0
        self.currentTask = None

    def busy(self):
        if self.currentTask is not None:
            return True
        else:
            return False

    def tick(self):
        if self.currentTask is not None:
            self.remainingtime -= 1
        if self.remainingtime <= 0:
            self.currentTask = None

    def startNext(self, newtask):
        self.currentTask = newtask
        self.remainingtime = newtask.getPage() * 60 / self.pagerate


class Task():
    def __init__(self, time):
        self.stamp = time
        self.pages = random.randint(1, 21)

    def getStamp(self):
        return self.stamp

    def getPage(self):
        return self.pages

    def timeWait(self, currentSecond):
        return currentSecond - self.stamp


def newTaskstart():
    num = random.randrange(1, 181)
    if num == 180:
        return True
    else:
        return False


def simulation(numSeconds, ppm):
    labPrinter = Printer(ppm)
    printQueue = Queue()
    waitingtimes = []
    for currentSecond in range(numSeconds):
        if newTaskstart():
            printQueue.enqueue(Task(currentSecond))
        if (not printQueue.isEmpty()) and (not labPrinter.busy()):
            nextTask = printQueue.dequeue()
            waitingtimes.append(nextTask.timeWait(currentSecond))
            labPrinter.startNext(nextTask)
        labPrinter.tick()
    averageWaitTime = sum(waitingtimes)/len(waitingtimes)
    print(f'average wait time:{averageWaitTime} wait task:{printQueue.size()}')


'''
for i in range(20):
    simulation(3600,5)
'''


def maxDrawDown(date_line, capital_line):
    df = pd.DataFrame({'date': date_line, 'capital': capital_line})
    df['expand_most'] = df.capital.expanding().max()
    df['ex_cap'] = (df['expand_most'] - df['capital'])/df['expand_most']
    drawmost = df.ex_cap.max()
    return drawmost


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
        return self.items[len(self.items)]


def perChecker(symbolString):
    s = Stack()
    index = 0
    balanced = True
    while index < len(symbolString) and balanced:
        symbol = symbolString[index]
        if symbol in '([{':
            s.push(symbol)
        else:
            if s.isEmpty():
                balanced = False
            else:
                top = s.pop()
                if not matches(top, symbol):
                    balanced = False
        index += 1
    if balanced and s.isEmpty():
        return True
    else:
        return False


def matches(opend, close):
    opens = '([{'
    closes = ')]}'
    return opens.index(opend) == closes.index(close)


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
        return self.head is not None

    def size(self):
        current = self.head
        count = 0
        while current is not None:
            current = current.getNext()
            count += 1
        return count

    def search(self, data):
        current = self.head
        found = False
        while current is not None and not found:
            if current.getData() == data:
                found = True
            else:
                current = current.getNext()
        return found

    def remove(self, data):
        current = self.head
        previous = None
        stop = False
        found = False
        while current is not None and not found and not stop:
            if current.getData() == data:
                found = True
            elif current.getData() > data:
                stop = True
            else:
                previous = current
                current = current.getNext()
        if previous is None:
            self.head = current.getNext()
        else:
            previous.setNext(current.getNext())

    def add(self, data):
        current = self.head
        previous = None
        stop = False
        while current is not None and not stop:
            if current.getData() > data:
                stop = True
            else:
                previous = current
                current = current.getNext()
        temp = Node(data)
        if previous is None:
            temp.setNext(self.head)
            self.head = temp
        else:
            previous.setNext(temp)
            temp.setNext(current)


class Fabi():
    def __init__(self, n=10):
        self.a = 0
        self.b = 1
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        self.a, self.b = self.b, self.a + self.b
        if self.a > self.n:
            raise StopIteration
        else:
            return self.a


def solve(puzzle):
    words = re.findall('[A-Z]+', puzzle.upper())
    unique_characters = set(''.join(words))
    assert len(unique_characters) <= 10, 'Too many letters'
    first_letters = {word[0] for word in words}
    n = len(first_letters)
    sorted_characters = ''.join(first_letters) +\
        ''.join(unique_characters - first_letters)
    characters = tuple(ord(c) for c in sorted_characters)
    digits = tuple(ord(c) for c in '0123456789')
    zero = digits[0]
    for guess in itertools.permutations(digits, len(characters)):
        if zero not in guess[:n]:
            equation = puzzle.translate(dict(zip(characters, guess)))
            if eval(equation):
                return equation

