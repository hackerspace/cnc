#!/usr/bin/python3

from util import *

import sys

if "--help" in sys.argv:

    print("""
    Usage: {name} gcode_file ssv_file
       takes ssv data from ssv_file and gcode data from ssv_file and prints data to be used in openscad,
       you propably want to > vis.scad it everytime, also tip: enable automatic reload in scad
    """)

    exit(0)

gcode_file = sys.argv[1]
ssv_file = sys.argv[2]

map =  load_calibration_matrix(ssv_file)
points = list()

for rows in map:
    for point in rows:
       points.append(point)

triangles = list()
for x in range(len(map)-1):
    for y in range(len(map[x]) - 1):
        triangles.append([
            points.index(map[x][y]),
            points.index(map[x+1][y]),
            points.index(map[x][y+1])
        ])

        triangles.append([
            points.index(map[x+1][y+1]),
            points.index(map[x+1][y]),
            points.index(map[x][y+1])
        ])

print( "polyhedron(points={}, triangles={});".format(points, triangles) )

gcode_points = load_gcode_commands(gcode_file)

for i in range(len(gcode_points) - 1):
    start = gcode_points[i]
    end = gcode_points[i+1]

    print ("color([0.5,{g},0])hull(){{translate([{s[X]}, {s[Y]}, {s[Z]}]) sphere(r=0.1); translate([{e[X]}, {e[Y]}, {e[Z]}]) sphere(r=0.1);}}".format(g=i/len(gcode_points), s=start, e=end))
