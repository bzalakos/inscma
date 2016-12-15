"""Draws a bunch of squares."""
# Ignore the invalid variable naming. pylint: disable-msg=C0103
import sys
# from random import random
from math import pi#, sin, cos, atan2
from ctypes import c_float
from numpy import array

import OpenGL.GL as GL
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT

window = 0
colro = 0
sides = 3
pion3 = pi / 3

# Y is indeed the up/down axis.
walls = [[(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1),   # floor
          (-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)],      # plafond
         [(1, 1, -1), (1, 1, 1), (1, -1, 1), (1, -1, -1)],      # +x
         [(-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1)],  # -z
         [(-1, 1, -1), (-1, 1, 1), (-1, -1, 1), (-1, -1, -1)],  # -x
         [(-1, 1, 1), (1, 1, 1), (1, -1, 1), (-1, -1, 1)],      # +z
        ]

room = [[6, 2, 2, 3],   # x +->
        [4, 0, 0, 1],   # z
        [4, 0, 0, 1],   # +
        [12, 8, 8, 9]]  # v

vertex_size = 3 * c_float

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
    res = [ttim(fill, w) for w in walls[0]]     # Skip zero, that's the roofloor.
    res += [ttim(fill, w) for i in range(4) for w in walls[i+1] if side & 2**i]
    return [tadd((x, 0, y), tadd(ttim(scale, r), offset)) for r in res]

vs = [t for y, i in enumerate(room) for x, w in enumerate(i) for t in wall(x, y, w)
     ] + [(0.1, 0.1, 0), (-0.1, -0.1, 0), (0.1, -0.1, 0)]

def rematr(wid, hig):
    """Resets the projection matrix."""
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GLU.gluPerspective(45.0, wid / hig, 0.1, 100.0)
    GL.glMatrixMode(GL.GL_MODELVIEW)

def init(wid, hig):
    """Initialises the display."""
    GL.glClearColor(0.0, 0.2, 0.15, 0.0)
    GL.glClearDepth(1.0)
    GL.glDepthFunc(GL.GL_LESS)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glShadeModel(GL.GL_SMOOTH)
    GL.glEnable(GL.GL_TEXTURE_2D)
    rematr(wid, hig)

    # # Set up the Shaders as well.
    # vertex_shader = shaders.compileShader("""#version 330 core
    # layout (location = 0) in vec3 position;
    # void main(){
    # gl_Position = vec4(position.x, position.y, position.z, 1.0);
    # }""", GL.GL_VERTEX_SHADER)
    # fragment_shader = shaders.compileShader("""#version 330 core
    # out vec4 colour;
    # void main(){
    # colour = vec4(1.0, 0.5, 0.2, 1.0);
    # }""", GL.GL_FRAGMENT_SHADER)
    # GL.glUseProgram(shaders.compileProgram(vertex_shader, fragment_shader))

def resiz(wid, hig):
    """Handles matrix resizing on viewport resize."""
    if hig == 0:
        hig = 1
    GL.glViewport(0, 0, wid, hig)
    rematr(wid, hig)

def buff_vertices(verts: list) -> vbo.VBO:
    """Given a list of vertex-like objects, sets up a VBO and draws it. Then unsets the vbo."""
    v = vbo.VBO(array(verts, 'f'))
    v.bind()
    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    GL.glVertexPointerf(v)  # ughghhggghhhhgggg   pylint: disable-msg=E1101
    GL.glDrawArrays(GL.GL_QUADS, 0, len(verts))
    v.unbind()
    GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

def draw():
    """Put the main drawing code in here."""
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glLoadIdentity()

    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glRotatef(0.01, 0, 1, 0)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    buff_vertices(vs)
    #
    # GL.glBegin(GL.GL_QUADS)
    # GL.glColor3f(1, 0, 0)
    #
    # for v in vs:
    #     GL.glVertex3f(*v)
    #
    # GL.glEnd()

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
