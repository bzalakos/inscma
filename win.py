"""Draws a bunch of squares."""
# Ignore the invalid variable naming. pylint: disable-msg=C0103
import sys
import time
# from random import random
import os
from math import pi, tan#sin#, cos, atan2
from PIL import Image
from numpy import array

import OpenGL.GL as GL
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
import OpenGL.GLUT as GLUT
# import transformations as TR

os.chdir(os.path.dirname(__file__))

window = 0
colro = 0
sides = 3
pion3 = pi / 3
# pylint: disable-msg=W0601
# Y is indeed the up/down axis. x y z r g b u v
vers = [[[-1, -1, -1], [1, -1, -1], [1, -1, 1], [-1, -1, 1],   # sol
         [-1, 1, -1], [1, 1, -1], [1, 1, 1], [-1, 1, 1]],      # plafond
        [[1, 1, -1], [1, 1, 1], [1, -1, 1], [1, -1, -1]],      # +x
        [[-1, 1, -1], [1, 1, -1], [1, -1, -1], [-1, -1, -1]],  # -z
        [[-1, 1, -1], [-1, 1, 1], [-1, -1, 1], [-1, -1, -1]],  # -x
        [[-1, 1, 1], [1, 1, 1], [1, -1, 1], [-1, -1, 1]],      # +z
       ]

# Not so bad when there's a bunch of repetition
uval = [[[0.75, 1], [0.875, 1], [0.875, 0.75], [0.75, 0.75], [0.875, 1], [0.9375, 1],
         [0.9375, 0.875], [0.875, 0.875]]] + [[[0.5, 1], [0.75, 1], [0.75, 0.5], [0.5, 0.5]]] * 4

# Sure is easy when they're all zeroes.
blankol = [[[0] * 3] * 6] + [[[0] * 3] * 4] * 4

walls = [[sum(x, []) for x in zip(vers[y], blankol[y], uval[y])] for y in range(len(vers))]

room = [[6, 2, 2, 3],   # x +->
        [4, 0, 0, 1],   # z
        [4, 0, 0, 1],   # +
        [12, 8, 8, 9]]  # v

def tadd(*args):
    """Element-wise addition of iterables."""
    return [sum(x) for x in zip(*args)]

def ttim(scal, ite):
    """Scalar multiplication of iterables."""
    return [x * scal for x in ite]

def wall(x, y, side):
    """Returns a list of lists of floats that forms a space."""
    scale, fill = 4.8, 0.9/2
    offset = (0, 0, -5)
    res = [ttim(fill, w[:3]) + w[3:] for w in walls[0]]
    # Skip zero here, just did it.
    res += [ttim(fill, w[:3]) + w[3:] for i in range(4) for w in walls[i+1] if side & 2**i]
    # tile coordinates offset, tile size multiplier
    return [tadd((x, 0, y), tadd(ttim(scale, r[:3]), offset)) + r[3:] for r in res]

# vs = [t for y, i in enumerate(room) for x, w in enumerate(i) for t in wall(x, y, w)]
vs = [(+1.0, +1.0, +0.0,
       +1.0, +1.0, +0.0,
       +0.0, +0.0),
      (+1.0, -1.0, +0.0,
       +1.0, +0.0, +0.0,
       +0.0, +1.0),
      (-1.0, -1.0, -0.0,
       +0.0, +0.0, +1.0,
       +1.0, +1.0),
      (-1.0, +1.0, -0.0,
       +0.0, +1.0, +0.0,
       +1.0, +0.0)]

def rematr(wid, hig):
    """Resets the projection matrix."""
    if hig == 0:
        hig = 1
    v, a, n, f = 1/tan(pi/8), wid/hig, 0.01, 100
    print(v/a, v, (f+n)/(f-n), 2*f*n/(n-f))
    # pm = array([[v/a, 0, 0, 0], [0, v, 0, 0], [0, 0, (f+n)/(n-f), -1], [0, 0, 2*f*n/(n-f), 0]], 'f')
    pm = array([[v/a, 0, 0, 0], [0, v, 0, 0], [0, 0, (f+n)/(n-f), -1], [0, 0, 2*f*n/(n-f), 0]], 'f')
    mm = array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, -5, 1]], 'f')
    # mm = array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0.5,0,-5,1]], 'f')
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'projectmatrix'), 1, GL.GL_FALSE, pm)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'), 1, GL.GL_FALSE, mm)

def init(wid, hig):
    """Initialises the display."""
    GL.glClearColor(0.0, 0.2, 0.15, 0.0)
    GL.glClearDepth(1.0)
    GL.glDepthFunc(GL.GL_LESS)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glShadeModel(GL.GL_SMOOTH)
    GL.glEnable(GL.GL_TEXTURE_2D)
    shades()
    rematr(wid, hig)

def texturit(filn: str) -> int:
    """Import a Texture."""
    wa = GL.glGenTextures(1)
    with Image.open(filn) as i:
        ix, iy, im = i.size[0], i.size[1], i.tobytes('raw', 'RGBA')
        GL.glBindTexture(GL.GL_TEXTURE_2D, wa)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, ix, iy, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE,
                        im)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    return wa

def shades():
    """Set up the Vertex and Fragment Shaders."""
    global shaderp

    vertex_shader = shaders.compileShader("""#version 330 core
    layout (location = 0) in vec3 position;
    layout (location = 1) in vec3 colour;
    layout (location = 2) in vec2 texcord;
    uniform mat4 projectmatrix;
    uniform mat4 modelmatrix;
    out vec3 ourcolour;
    out vec2 ourtex;
    void main(){
        gl_Position = projectmatrix * modelmatrix * vec4(position, 1.0);
        ourcolour = colour;
        ourtex = texcord;
    }""", GL.GL_VERTEX_SHADER)
    # if(colour == vec3(0,0,0))
    #   ourcolour = vec3(1,0,0);
    # else
    # ourcolour = vec3(0,1,0);
    #uniform vec4 ourcolour;
    fragment_shader = shaders.compileShader("""#version 330 core
    in vec3 ourcolour;
    in vec2 ourtex;
    out vec4 colour;
    uniform sampler2D tex;
    void main(){
        colour = texture(tex, ourtex);
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
    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 32, v)
    GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 32, v+12)
    GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, False, 32, v+24)
    GL.glEnableVertexAttribArray(0)
    GL.glEnableVertexAttribArray(1)
    GL.glEnableVertexAttribArray(2)
    GL.glDrawArrays(GL.GL_QUADS, 0, len(verts))
    v.unbind()
    GL.glDisableVertexAttribArray(0)
    GL.glDisableVertexAttribArray(1)
    GL.glDisableVertexAttribArray(2)

def draw():
    """Put the main drawing code in here."""
    global lasttime
    timedelta = time.time() - lasttime
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    GL.glBindTexture(GL.GL_TEXTURE_2D, terrain)
    buff_vertices(vs)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    GLUT.glutSwapBuffers()
    lasttime = time.time()

def main():
    """Do all this upon running the script."""
    global window, firsttime, lasttime, terrain
    GLUT.glutInit(sys.argv)
    GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH)
    GLUT.glutInitWindowSize(640, 480)
    window = GLUT.glutCreateWindow(b'test')
    GLUT.glutDisplayFunc(draw)
    GLUT.glutIdleFunc(draw)
    GLUT.glutReshapeFunc(resiz)
    GLUT.glutKeyboardFunc(lambda *args: exit())
    init(640, 480)
    terrain = texturit('terrain.png')
    firsttime = lasttime = time.time()
    GLUT.glutMainLoop()

if __name__ == '__main__':
    main()
