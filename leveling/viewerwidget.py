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
        fmt = QGLFormat.defaultFormat()
        fmt.setSampleBuffers(True)
        fmt.setSamples(32)

        super(ViewerWidget, self).__init__(fmt, parent)
        self.gcode_points = []
        self.oldpos = 0, 0
        self.filename = ''
        self.objsize = 0, 0, 0
        self.gcodesize = 0
        self._oc = (0, 0, 0)
        self._ogc = None

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

    def _recalc_object_center(self, obj):
        if len(obj) > 2:
          obj = obj[1:-1]
        x = sum(map(lambda _x: float(_x['X']), obj))
        y = sum(map(lambda _x: float(_x['Y']), obj))
        z = sum(map(lambda _x: float(_x['Z']), obj))
        l = len(obj)
        if l == 0:
          self._oc = 0, 0, 0
        self._oc = (x/l, y/l, z/l)

    def resetView(self):
      ViewerWidget.rotx = 0
      ViewerWidget.roty = 0
      self._recalc_object_center(self.gcode_points)
      ViewerWidget.tranx = 0
      ViewerWidget.trany = 0
      sz = self.object_size(self.gcode_points)
      ViewerWidget.tranz = (self._oc[1]+sz[1])#*2.2

      self.update()

    def paintGL(self):
        wtf = False

        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        L = 0
        glRotate(180, 0, 0, 1)
        glRotate(180, 0, 1, 0)
        glDisable(GL_DEPTH_TEST)
        glColor3f(0.8, 0.8, 0.8)
        self.renderText(20, 20, '{} | {} cmds'.format(
          self.filename, self.gcodesize))
        self.renderText(20, 40, '{:.4f} x {:.4f} x {:.4f} mm'.format(
          self.objsize[0], self.objsize[1], self.objsize[2]))
        self.renderText(20, 60, '{:.4f} , {:.4f} deg'.format(
          self.rotx, self.roty))
        self.renderText(20, 80, 'v: {:.4f} , {:.4f} , {:.4f}'.format(
          ViewerWidget.tranx, ViewerWidget.trany, ViewerWidget.tranz))
        self.renderText(20, 100, '{:.4f} x {:.4f} x {:.4f} mm'.format(
          self._oc[0], self._oc[1], self._oc[2]))
        glEnable(GL_DEPTH_TEST)

        glEnable(GL_MULTISAMPLE)

        glPushMatrix()
        if ViewerWidget.gcodelist == -1:
          ViewerWidget.gcodelist = glGenLists(1)
          glShadeModel(GL_SMOOTH)
          glNewList(ViewerWidget.gcodelist, GL_COMPILE_AND_EXECUTE)
          glBegin(GL_LINE_STRIP)
          for i, p in enumerate(self.gcode_points):
            _x, _y, _z = map(float, [p['X'], p['Y'], p['Z']])
            glColor3f(i/float(len(self.gcode_points)), 0.5, float(p['L']))
            glVertex3f(_x, _y, _z)
          glEnd()
          try:
            glEndList()
          except:
            wtf = True

          glCallList(self.gcodelist)
        else:
          glTranslate(ViewerWidget.tranx, ViewerWidget.trany, ViewerWidget.tranz)
          glScale(ViewerWidget.scale, ViewerWidget.scale, ViewerWidget.scale)
          glRotate(float(ViewerWidget.roty), 1.0, 0.0, 0.0)
          glRotate(float(ViewerWidget.rotx), 0.0, 0.0, 1.0)
          glTranslate(-self._oc[0], -self._oc[1], -self._oc[2])
          glCallList(ViewerWidget.gcodelist)
        glPopMatrix()
        self.swapBuffers()
        if wtf:
          self.update()

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
      self._recalc_object_center(self.gcode_points)
      self.updateGL()

    def mousePressEvent(self, m):
      self.oldpos = m.x(), m.y()

    def wheelEvent(self, m):
#      ViewerWidget.scale *= (120+m.angleDelta().y()/12)/120.0
      ViewerWidget.tranz -= m.angleDelta().y()/24.0
      self.update()

    def mouseMoveEvent(self, m):
      button = int(m.buttons())
      if button == 1:
        ViewerWidget.roty -= (self.oldpos[1]-m.y())/10.0
        if (int(ViewerWidget.roty) % 360) > 0 and (int(ViewerWidget.roty) % 360) < 180:
          ViewerWidget.rotx -= (self.oldpos[0]-m.x())/10.0
        else:
          ViewerWidget.rotx += (self.oldpos[0]-m.x())/10.0
      elif button == 2:
        c = 1
        if ViewerWidget.tranz < 0:
          c = -ViewerWidget.tranz/100.0
        ViewerWidget.tranx -= c*(self.oldpos[0]-m.x())/4.0
        ViewerWidget.trany -= c*(self.oldpos[1]-m.y())/4.0
      self.oldpos = m.x(), m.y()
      self.update()


