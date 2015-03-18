import os, sys, random

if __name__=="__main__":
  for x in range(990):
    print 'G81 X{} Y{}'.format(round(random.random()*70, 5), round(random.random()*70, 5))
