#!/usr/bin/python3

import os, sys, random
from math import *

if __name__=="__main__":

  offset = [25, 25, 0]

  points = list()

  for i in range(0, int(pi*2*3), 1):
      points.append([
          i*sin(i),
          i*cos(i),
          -1
      ])

  for point in points:
      point = [point[i] + offset[i] for i in range(len(point))]
      # G01 is generate by pcb2gcode
      print('G01 X{} Y{} Z{}'.format(*point))
    

