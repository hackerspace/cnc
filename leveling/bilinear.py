import math
import os
def bilinear(x, y, zmap):
  def get_quadrant_idx(x, y, zmap):

    ysize = len(zmap)
    xsize = len(zmap[0])

    coord_l = list()

    for yi in range(ysize):
      for xi in range(xsize):
        coord_l.append(zmap[yi][xi])

    minx = min([ coord[0] for coord in coord_l])
    miny = min([ coord[1] for coord in coord_l])
    
    maxx = max([ coord[0] for coord in coord_l])
    maxy = max([ coord[1] for coord in coord_l])

    x_perc = (x - minx) / (maxx - minx) 
    y_perc = (y - miny) / (maxy - miny) 

    return (
      int( x_perc * (xsize - 1) ),
      int( y_perc * (ysize - 1) )
    )


  Qidx = get_quadrant_idx(x, y, zmap)
  #print x,y, Qidx
  try:
    Q = [[zmap[Qidx[1]][Qidx[0]],
          zmap[Qidx[1]][Qidx[0]+1]],
         [zmap[Qidx[1]+1][Qidx[0]],
          zmap[Qidx[1]+1][Qidx[0]+1]]]
  except Exception as e:
    print('No zmap for point {} {}'.format(x, y))
    print('Quadrant {}'.format(Qidx))
    print('Ensure your G-code is within probed area boundaries')
    print(zmap)
    raise e
  # Q now contains 4 triples (machine x, machine y, z height)
  # as Q11, Q12, Q21, Q22

  # linear interpolation along yIDX
  # there should be two - y1 and y2, that means indexing in Q
  import sys
  def lin_f_y(x, y, yIDX):
    # f(Q11)*(x2-x)/(x2-x1) + f(Q21)*(x-x1)/(x2-x1)
    return Q[yIDX][0][2]*(Q[yIDX][1][0]-x)/(Q[yIDX][1][0]-Q[yIDX][0][0]) \
         + Q[yIDX][1][2]*(x-Q[yIDX][0][0])/(Q[yIDX][1][0]-Q[yIDX][0][0])


  return lin_f_y(x, y, 0)*(Q[1][0][1]-y)/(Q[1][0][1]-Q[0][0][1]) \
       + lin_f_y(x, y, 1)*(y-Q[0][1][1])/(Q[1][1][1]-Q[0][1][1])

import time, math
def draw_pic(xmax, ymax, M, divs = None):
  from PIL import Image, ImageDraw
  if divs is None:
    divs = 100
  im = Image.new("L", (divs*xmax, divs*ymax), "black")
  putpixel = im.im.putpixel

  xp, yp = 0, 0
  for _y in range(ymax*divs):
    y = float(_y) / divs
    xp = 0
    for _x in range(xmax*divs):
      x = float(_x) / divs
      v = bilinear(x, y, M)
      putpixel((xp, yp), int(v*255))
      xp += 1
    yp += 1
  im.save('lol_{}-{}.png'.format(divs, time.time()))
  #im.show()

if __name__=="__main__":
  M = [[(0.0,  0.0, 1.0), (5.0,  0.0, 0.0), (10.0,  0.0, 1.0), (15.0,  0.0, 0.0)],
       [(0.0,  5.0, 0.0), (5.0,  5.0, 1.0), (10.0,  5.0, 0.0), (15.0,  5.0, 1.0)],
       [(0.0, 10.0, 1.0), (5.0, 10.0, 0.0), (10.0, 10.0, 1.0), (15.0, 10.0, 0.0)],
       [(0.0, 15.0, 0.0), (5.0, 15.0, 1.0), (10.0, 15.0, 0.0), (15.0, 15.0, 1.0)]]
  import timeit
  spd = 1
  for s in range(64, 1000, 400):
    print s, (s*15)**2, 'eta:', ((s*15)**2)/spd
    start = time.clock()
    draw_pic(15,15,M,divs=s)
    t = time.clock() - start
    spd = ((s*15)**2)/t
    print '{} pixels/s'.format(spd)
