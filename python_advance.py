# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 13:58:40 2018

@author: 123
"""
import sys
import copy


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def new_object(cls, x, y):
        return cls(x, y)

    def __repr__(self):
        return f'x:{self.x}, y:{self.y}'


def make_object(Class, *args, **kwargs):
    return Class(*args, **kwargs)


point1 = Point(1, 2)
point2 = eval(f"{'Point'}({2},{4})")
# point2 = eval('{}({},{})'.format('Point', 2, 4))
point3 = getattr(sys.modules[__name__], 'Point')(3, 6)
point4 = globals()['Point'](4, 8)
point5 = make_object(Point, 5, 10)
point6 = copy.deepcopy(point5)
point6.x = 6
point6.y = 12
point7 = point1.__class__(7, 14)
point8 = Point.new_object(8, 16)


# 闭包延迟绑定：闭包中用到的变量的值，是在内部函数被调用的时候才查询得到的
def squares():
    return [lambda x, i=i: i**x for i in range(3)]


'''
for square in squares():
    print(square(2))
'''
