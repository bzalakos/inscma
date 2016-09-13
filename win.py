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

walls = [[(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1),
          (-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)],
         [(1, 1, -1), (1, 1, 1), (1, -1, 1), (1, -1, -1)],
         [(-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1)],
         [(-1, 1, -1), (-1, 1, 1), (-1, -1, 1), (-1, -1, -1)],
         [(-1, 1, 1), (1, 1, 1), (1, -1, 1), (-1, -1, 1)]]

room = [[6, 2, 2, 3],
        [4, 0, 0, 1],
        [4, 0, 0, 1],
        [12, 8, 8, 9]]

def tadd(*args):
    """Element-wise addition of tuples."""
    return tuple([sum(x) for x in zip(*args)])

def ttim(scal, tup):
    """Scalar multiplication of tuples."""
    return tuple([x * scal for x in tup])

def wall(x, y, side):
    """Returns a list of tuples of floats that forms a square."""
    scale, fill = 0.8, 0.9/2
    offset = (0, 0, -5)
    res = [ttim(fill, w) for w in walls[0]]
    res += [ttim(fill, w) for i in range(4) for w in walls[i] if side & 2**i]
    return [tadd((x, 0, y), tadd(ttim(scale, r), offset)) for r in res]

vs = [t for y, i in enumerate(room) for x, w in enumerate(i) for t in wall(x, y, w)]

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
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glLoadIdentity()

    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glRotatef(0.001, 1, 0, 1)
    GL.glMatrixMode(GL.GL_MODELVIEW)

    GL.glBegin(GL.GL_QUADS)
    GL.glColor3f(1, 0, 0)

    for v in vs:
        GL.glVertex3f(*v)

    GL.glEnd()
    GLUT.glutSwapBuffers()

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
