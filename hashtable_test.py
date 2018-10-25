# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 14:27:55 2018

@author: 123
"""


class HashTable():
    def __init__(self, size):
        self.size = size
        self.slots = [None]*self.size
        self.data = [None]*self.size

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
            while self.slots[nextslot] is not None \
                    and self.slots[nextslot] != key:
                nextslot = self.rehash(nextslot)
            if self.slots[nextslot] is None:
                self.slots[nextslot] = key
                self.data[nextslot] = value
            else:
                self.data[nextslot] = value

    def get(self, key, default=None):
        startslot = self.hashFunction(key)
        position = startslot
        found = False
        stop = False
        data = default
        while self.slots[position] and not found and not stop:
            if self.slots[position] == key:
                data = self.data[position]
                found = True
            else:
                position = self.rehash(position)
                if position == startslot:
                    stop = True
        return data

    def __setitem__(self, key, value):
        self.put(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __repr__(self):
        k = [s for s in self.slots if s is not None]
        v = [s for s in self.data if s is not None]
        return '{' + str(list(zip(k, v))).strip('[').strip(']') + '}'
