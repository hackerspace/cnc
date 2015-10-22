#!/usr/bin/python3

from util import *
from math import *
import sys
import heapq

def point_distance(p1, p2):
    return sqrt(sum([ (p1[i] - p2[i])**2 for i in range(len(p1)) ]))

def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]

    return c

def vector(p1, p2):
    return [ p1[i] - p2[i] for i in range(len(p1)) ]

def z_distance(point, triangle):
    v1 = vector(triangle[0], triangle[1])
    v2 = vector(triangle[0], triangle[2])

    a,b,c = cross(v1, v2)

    # ax + by + cz + d = 0
    d = -( a*triangle[0][0] + b*triangle[0][1] + c*triangle[0][2] )

    # now let's get a z coordinate of point [x,y,z] that shares x,y with 'point' and is on the plane made by triangle

    z = -(a*point[0] + b*point[1] + d)/c

    return z - point[2]



def find_triangle(point, map):

    heap = []

    for row in map:
        for m_point in row:
            heapq.heappush(heap, (point_distance(point, m_point), m_point))

    triangle = list()

    for i in range(3):
        triangle.append(
            heapq.heappop(heap)[1]
        )


    line = True
    while not line:
        line = False
        for axis in [0, 1]:
            if triangle[0][axis] == triangle[1][axis] and triangle[0][axis] == triangle[2][axis]:
                line = True

        triangle.pop()
        triangle.append(
            heapq.heappop(heap)[1]
        )


    return triangle

def move_correction(start, end, map, resolution):
    # returns list of ne positions where it should go!
    dist = point_distance(start, end)

    steps_n = int(dist // resolution) + 1
    v = vector(end, start)


    positions = list()

    for i in range(1, steps_n + 1):
        pos = [ start[j] + v[j]*(i/steps_n) for j in range(3)]

        triangle = find_triangle(pos, map)
        z_correction = z_distance(pos, triangle)

        #print(triangle, pos, z_correction)

        pos[2] += z_correction

        positions.append(pos)


    return positions


if __name__ == "__main__":
    if len(sys.argv) > 1:
        gcode_file = sys.argv[1]
        ssv_file = sys.argv[2]
    else:
        gcode_file = "input.gcode"
        ssv_file = "readings.ssv"

    calib_map = load_calibration_matrix(ssv_file)

    commands = load_gcode_commands(gcode_file)
    for i in range(len(commands)):
        if i == 0:
            p = dict(commands[0])
            v = [p['X'], p['Y'], p['Z']]

            v = [float(x) for x in v]

            z_correction = z_distance(v, find_triangle(v, calib_map))
            p['Z'] = float(p['Z']) + z_correction
            print("{cmd} X{X} Y{Y} Z{Z}".format(**p))

            continue

        start = commands[i - 1]
        end   = commands[i]

        start_v = [start['X'], start['Y'], start['Z']]
        end_v = [end['X'], end['Y'], end['Z']]

        start_v = [float(x) for x in start_v]
        end_v = [float(x) for x in end_v]

        if point_distance(start_v, end_v) != 0:

            mid_positions = move_correction(start_v, end_v, calib_map, resolution=1)
            #print(start,end)
            for pos in mid_positions:
                print("{} X{} Y{} Z{}".format(end['cmd'], *pos))

        else:

            print("{cmd} X{X} Y{Y} Z{Z}".format(**end))