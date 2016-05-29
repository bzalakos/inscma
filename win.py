from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
from math import sin, cos, atan2, pi

window = 0

def rematr(wid, hig):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, wid / hig, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def init(wid, hig):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)   
    rematr(wid, hig)

def resize(wid, hig):
    if hig == 0: hig = 1
    glViewport(0, 0, wid, hig)
    rematr(wid, hig)

def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glBegin(GL_POLYGON)
    #for x in range(10):
    #    x *= pi / 10
    #    y = (x % 2) + 1
    #    glVertex3f(cos(x) / y, -sin(x) / y, 0)
    glVertex3f(0.0, 1.0, 0.0)           # Top
	glVertex3f(1.0, -1.0, 0.0)          # Bottom Right
	glVertex3f(-1.0, -1.0, 0.0)
    
    glEnd()
    glutSwapBuffers()

def main():
    global window

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    window = glutCreateWindow(b'test')
    glutDisplayFunc(draw)
    glutIdleFunc(draw)
    glutReshapeFunc(resize)
    init(640 ,480)
    glutMainLoop()

main()