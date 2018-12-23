#!/usr/bin/python
# -*- coding: UTF-8 -*-

from copy import deepcopy


def hello():
    q = [1, 2, 3]
    w = [4, 5, 6]
    e = [7, 8, 9]
    return q, w, e


a, b, c = hello()
print(a)
print(b)
print(c)
