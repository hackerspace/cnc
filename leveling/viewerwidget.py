#!/usr/bin/python
#GPLv2
import sys
import os
from OpenGL.GL import *
from PyQt5 import QtGui, uic, QtCore, QtWidgets
from PyQt5.QtOpenGL import *

import util

class ViewerWidget(QGLWidget):
    rotx = 0
    roty = 0
    tranx = 0
    trany = 0
    tranz = 0
    scale = 1.0
    gcodelist = -1

    def __init__(self, parent = None):
        super(ViewerWidget, self).__init__(parent)
        self.gcode_points = []
        self.oldpos = 0, 0
        self.filename = ''
        self.objsize = 0, 0, 0
        self.gcodesize = 0

    def object_size(self, obj):
      try:
        x = map(lambda _x: float(_x['X']), obj)
        xmax = max(x)
        xmn = min(x)

        y = map(lambda _y: float(_y['Y']), obj)
        ymax =max(y)
        ymn = min(y)

        z = map(lambda _z: float(_z['Z']), obj)
        zmax =max(z)
        zmn = min(z)

        return (xmax-xmn), (ymax-ymn), (zmax-zmn)
      except ValueError:
        return 0,0,0

    def resetView(self):
      ViewerWidget.rotx = 0
      ViewerWidget.roty = 0
      s = self.object_size(self.gcode_points)
      ViewerWidget.tranx = 0
      ViewerWidget.trany = 0
      ViewerWidget.tranz = -s[1]*3

      self.update()

    def paintGL(self):

        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        L = 0
        glDisable(GL_DEPTH_TEST)
        glColor3f(0.8, 0.8, 0.8)
        self.renderText(20, 20, self.filename)
        self.renderText(20, 40, str(self.gcodesize) + ' cmds')
        self.renderText(20, 60, str(self.objsize) + ' mm')
        glEnable(GL_DEPTH_TEST)

        glRotatef(90, 1, 0, 0)
        glEnable(GL_MULTISAMPLE)

        glPushMatrix()
        if ViewerWidget.gcodelist == -1:
          ViewerWidget.gcodelist = glGenLists(1)
          glShadeModel(GL_SMOOTH)
          glNewList(ViewerWidget.gcodelist, GL_COMPILE_AND_EXECUTE)
          glBegin(GL_LINES)
          for i in range(len(self.gcode_points) - 1):
            start = self.gcode_points[i]
            end = self.gcode_points[i+1]
            try:
              glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
              glColor3f(i/float(len(self.gcode_points)), 0.5, float(start['L']))
              glNormal3f(0,0,1)
              glVertex3f(*map(float, [start['X'], start['Y'], start['Z']]))

              glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
              glColor3f((i+1)/float(len(self.gcode_points)), 0.5, float(end['L']))
              glNormal3f(0,0,1)
              glVertex3f(*map(float, [end['X'], end['Y'], end['Z']]))
            except ValueError as e:
              print>>sys.stderr, e.message
              glVertex3f(0,0,0)
          glEnd()
          glEndList()

          glCallList(self.gcodelist)
        else:
          glTranslate(ViewerWidget.tranx, ViewerWidget.tranz, ViewerWidget.trany)
          glScale(ViewerWidget.scale, ViewerWidget.scale, ViewerWidget.scale)
          glRotate(float(ViewerWidget.roty), 1.0, 0.0, 0.0)
          glRotate(float(ViewerWidget.rotx), 0.0, 0.0, 1.0)
          glTranslate(-self.objsize[0]/2, -self.objsize[1]/2, -self.objsize[2]/2)
          glCallList(ViewerWidget.gcodelist)
        glPopMatrix()
        self.swapBuffers()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        x = float(w) / h
#        glOrtho(-100, 100, -100, 100, -15000.0, 15000.0)
        glFrustum(-x, x, -1, 1, 1, 15000.0)

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

#        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, -130, 0])
        glEnable(GL_COLOR_MATERIAL)




    def loadGCode(self, filename):
      if not ViewerWidget.gcodelist == -1:
        glDeleteLists(ViewerWidget.gcodelist, 1)
        ViewerWidget.gcodelist = -1
      self.gcode_points = util.load_gcode_commands(filename)
      s = self.object_size(self.gcode_points)
#      ViewerWidget.tranx = -s[0]/2
#      ViewerWidget.trany = -s[2]/2
      ViewerWidget.tranz = -s[1]*3
      #ViewerWidget.scale = -s[1]*3
      self.filename = filename
      self.gcodesize = len(self.gcode_points)
      self.objsize = s
      self.updateGL()

    def mousePressEvent(self, m):
      self.oldpos = m.x(), m.y()

    def wheelEvent(self, m):
#      ViewerWidget.scale *= (120+m.angleDelta().y()/12)/120.0
      ViewerWidget.tranz += m.angleDelta().y()/24.0
      self.update()

    def mouseMoveEvent(self, m):
      button = int(m.buttons())
      if button == 1:
        ViewerWidget.rotx += (self.oldpos[0]-m.x())/10.0
        ViewerWidget.roty -= (self.oldpos[1]-m.y())/10.0
      elif button == 2:
        ViewerWidget.tranx -= (self.oldpos[0]-m.x())/4.0
        ViewerWidget.trany -= (self.oldpos[1]-m.y())/4.0
      self.oldpos = m.x(), m.y()
      self.update()


