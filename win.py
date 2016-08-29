import sys
from math import sin, cos, atan2, pi

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

window = 0
colro = 0
sides = 3
pion3 = pi / 3

def rematr(wid, hig):
	"""Resets the view matricies."""
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(45.0, wid / hig, 0.1, 100.0)
	glMatrixMode(GL_MODELVIEW)

def init(wid, hig):
	"""(Re)Sets up the initial rendering settings."""
	glClearColor(0.0, 0.0, 0.0, 0.0)
	glClearDepth(1.0)
	glDepthFunc(GL_LESS)
	glEnable(GL_DEPTH_TEST)
	glShadeModel(GL_SMOOTH)
	rematr(wid, hig)

def resize(wid, hig):
	"""Resets the matrix proportions when the viewport is resized."""
	if hig == 0: hig = 1
	glViewport(0, 0, wid, hig)
	rematr(wid, hig)

def draw():
	"""Put all of the drawing stuff in here."""
	global colro
	colro += 0.002
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()

	glMatrixMode(GL_PROJECTION)
	glRotatef(0, 1, 0, 1)
	glMatrixMode(GL_MODELVIEW)

	plus = 0.5
	divide = 2

	glBegin(GL_POLYGON)
	for x in range(sides):
		y = 0.5 #(x % 2) + 1
		x *= 2 * pi / sides
		glColor3f((sin(x + colro) + plus) / divide, (sin(x + colro + (2 * pion3)) + plus) / divide, (sin(x + colro + (4 * pion3)) + plus) / divide)
		glVertex3f(cos(x + colro) / y, -sin(x + colro) / y, -5)
	glEnd()

	room = [[6, 2, 2, 3],
			[4, 0, 0, 1],
			[4, 0, 0, 1],
			[12,8, 8, 9]]

	glBegin(GL_QUADS)
	glColor3f(1,1,1)

	for y in room:
		for x in y:
			pass

	glEnd()
	glutSwapBuffers()

def main():
	"""Do this when executing the script."""
	global window

	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
	glutInitWindowSize(640, 480)
	window = glutCreateWindow(b'Test')
	glutDisplayFunc(draw)
	glutIdleFunc(draw)
	glutReshapeFunc(resize)
	init(640, 480)
	glutMainLoop()

if __name__ == '__main__':
	main()
