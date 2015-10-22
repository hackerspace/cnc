#!/usr/bin/python2

import random
from math import *

a = 10
b = 10

for y in range(a):
    for x in range(b):
        if y > 0:
            print ",",
        print  x*5, y*5, sin(y) + cos(x),

    print 

