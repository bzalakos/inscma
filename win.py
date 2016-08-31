"""Draws a bunch of squares."""
# Ignore the invalid variable naming. pylint: disable-msg=C0103
import sys
from math import sin, cos, atan2, pi

import OpenGL.GL as GL
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT

window = 0
colro = 0
sides = 3
pion3 = pi / 3

def rematr(wid, hig):
	"""Resets the projection matrix."""
	GL.glMatrixMode(GL.GL_PROJECTION)
	GL.glLoadIdentity()
	GLU.gluPerspective(45.0, wid / hig, 0.1, 100.0)
	GL.glMatrixMode(GL.GL_MODELVIEW)

def init(wid, hig):
	"""Resets the display."""
	GL.glClearColor(0.0, 0.0, 0.0, 0.0)
	GL.glClearDepth(1.0)
	GL.glDepthFunc(GL.GL_LESS)
	GL.glEnable(GL.GL_DEPTH_TEST)
	GL.glShadeModel(GL.GL_SMOOTH)
	rematr(wid, hig)

def resiz(wid, hig):
	"""Handles matrix resizing on viewport resize."""
	if hig == 0:
		hig = 1
	GL.glViewport(0, 0, wid, hig)
	rematr(wid, hig)

def draw():
	"""Put the main drawing code in here."""
	global colro
	colro += 0.002
	GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
	GL.glLoadIdentity()

	GL.glMatrixMode(GL.GL_PROJECTION)
	GL.glRotatef(0, 1, 0, 1)
	GL.glMatrixMode(GL.GL_MODELVIEW)

	# plus = 0.5
	# divide = 2

	# GL.glBegin(GL.GL_POLYGON)
	# for x in range(sides):
	# 	y = 0.5 #(x % 2) + 1
	# 	x *= 2 * pi / sides
	# 	GL.glColor3f((sin(x + colro) + plus) / divide, \
	# 		(sin(x + colro + (2 * pion3)) + plus) / divide, \
	# 		(sin(x + colro + (4 * pion3)) + plus) / divide)
	# 	GL.glVertex3f(cos(x + colro) / y, -sin(x + colro) / y, -5)
	# GL.glEnd()

	room = [[6, 2, 2, 3], \
			[4, 0, 0, 1], \
			[4, 0, 0, 1], \
			[12, 8, 8, 9]]

	GL.glBegin(GL.GL_QUADS)
	GL.glColor3f(1, 0, 0)

	for y, i in enumerate(room):
		for x, w in enumerate(i):
			[GL.glVertex3f(*t) for t in wall(x, y, w)]

	GL.glEnd()
	GLUT.glutSwapBuffers()

def wall(x, y, side):
	"""Returns a list of tuples of floats that forms a square."""
	scale, fill = 0.4, 0.9/2
	offset = (0, 0, -5)
	defa = [(-fill, -fill, -fill), \
		(fill, -fill, -fill), \
		(fill, fill, -fill), \
		(-fill, fill, -fill)]
	res = defa[:]
	res += [trod(side & i, defa) for i in [2 ^ x for x in range(4)] if side & i]
	return exyt(x, y, [tadd(ttim(x, scale), offset) for x in res])

def exyt(x, y, ls):
	"""Inserts coordi"""
	return [tadd(t, (x, y, 0)) for t in ls]

def trod(ang, ls):
	"""Rotates a tuple gruple"""
	if ang == 1:
		return []

def tadd(*args):
	"""Element-wise addition of tuples."""
	return tuple([sum(x) for x in zip(*args)])

def ttim(scal, tup):
	"""Scalar multiplication of tuples."""
	return tuple([x * scal for x in tup])

def main():
	"""Do all this upon running the script."""
	global window

	GLUT.glutInit(sys.argv)
	GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH)
	GLUT.glutInitWindowSize(640, 480)
	window = GLUT.glutCreateWindow(b'test')
	GLUT.glutDisplayFunc(draw)
	GLUT.glutIdleFunc(draw)
	GLUT.glutReshapeFunc(resiz)
	init(640, 480)
	GLUT.glutMainLoop()

if __name__ == '__main__':
	main()
