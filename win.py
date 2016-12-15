"""Draws a bunch of squares."""
# Ignore the invalid variable naming. pylint: disable-msg=C0103
import sys
import time
# from random import random
from math import pi#, sin#, cos, atan2
from numpy import array

import OpenGL.GL as GL
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
# import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT

window = 0
colro = 0
sides = 3
pion3 = pi / 3
# pylint: disable-msg=W0601
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

# vs = [t for y, i in enumerate(room) for x, w in enumerate(i) for t in wall(x, y, w)]
vs = [(0.1, 0.1, 0, 1, 1, 1), (0.1, -0.1, 0, 1, 1, 1),
      (-0.1, -0.1, 0, 1, 1, 1), (-0.1, 0.1, 0, 1, 1, 1)]

def rematr(wid, hig):
    """Resets the projection matrix."""
    wid, hig = hig, wid
    # GL.glMatrixMode(GL.GL_PROJECTION)
    # GL.glLoadIdentity()
    # GLU.gluPerspective(45.0, wid / hig, 0.1, 100.0)
    # GL.glMatrixMode(GL.GL_MODELVIEW)

def init(wid, hig):
    """Initialises the display."""
    global shaderp
    GL.glClearColor(0.0, 0.2, 0.15, 0.0)
    GL.glClearDepth(1.0)
    GL.glDepthFunc(GL.GL_LESS)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glShadeModel(GL.GL_SMOOTH)
    GL.glEnable(GL.GL_TEXTURE_2D)
    rematr(wid, hig)

    # Set up the Shaders as well.
    vertex_shader = shaders.compileShader("""#version 330 core
    layout (location = 0) in vec3 position;
    layout (location = 1) in vec3 colour;
    uniform vec4 projectmatrix;
    out vec3 ourcolour;
    void main(){
    gl_Position = vec4(position.xyz, 1.0);
    ourcolour = colour;
    }""", GL.GL_VERTEX_SHADER)
    #uniform vec4 ourcolour;
    fragment_shader = shaders.compileShader("""#version 330 core
    in vec3 ourcolour;
    out vec4 colour;
    void main(){
    colour = vec4(ourcolour.xyz, 1.0);
    }""", GL.GL_FRAGMENT_SHADER)
    shaderp = shaders.compileProgram(vertex_shader, fragment_shader)
    GL.glUseProgram(shaderp)

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
    GL.glEnableClientState(GL.GL_COLOR_ARRAY)
    GL.glVertexPointer(3, GL.GL_FLOAT, 24, v)
    GL.glColorPointer(3, GL.GL_FLOAT, 24, v+12)
    GL.glDrawArrays(GL.GL_QUADS, 0, len(verts))
    v.unbind()
    GL.glDisableClientState(GL.GL_COLOR_ARRAY)
    GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

def draw():
    """Put the main drawing code in here."""
    global lasttime
    timedelta = time.time() - lasttime
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glLoadIdentity()

    buff_vertices(vs)

    GLUT.glutSwapBuffers()
    lasttime = time.time()

def main():
    """Do all this upon running the script."""
    global window, firsttime, lasttime
    GLUT.glutInit(sys.argv)
    GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH)
    GLUT.glutInitWindowSize(640, 480)
    window = GLUT.glutCreateWindow(b'test')
    GLUT.glutDisplayFunc(draw)
    GLUT.glutIdleFunc(draw)
    GLUT.glutReshapeFunc(resiz)
    init(640, 480)
    firsttime = lasttime = time.time()
    GLUT.glutMainLoop()

if __name__ == '__main__':
    main()
