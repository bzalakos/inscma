"""Draws a bunch of squares."""
# Ignore the invalid variable naming. pylint: disable-msg=C0103
import sys
import time
# from random import random
import os
from math import pi, tan#sin#, cos, atan2
from PIL import Image
from numpy import array

from pyrr import Matrix44 as matrix
import OpenGL.GL as GL
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
import OpenGL.GLUT as GLUT

os.chdir(os.path.dirname(__file__))

window = 0
colro = 0
sides = 3
pion3 = pi / 3
# pylint: disable-msg=W0601
# Y is indeed the up/down axis. x y z r g b u v
l = 0.49   # To ease the sizing, use this constant.
vers = [[[-l, -l, -l], [+l, -l, -l], [+l, -l, +l], [-l, -l, +l],   # sol
         [-l, +l, -l], [+l, +l, -l], [+l, +l, +l], [-l, +l, +l]],  # plafond
        [[+l, +l, -l], [+l, +l, +l], [+l, -l, +l], [+l, -l, -l]],  # +x
        [[-l, +l, -l], [+l, +l, -l], [+l, -l, -l], [-l, -l, -l]],  # -z
        [[-l, +l, -l], [-l, +l, +l], [-l, -l, +l], [-l, -l, -l]],  # -x
        [[-l, +l, +l], [+l, +l, +l], [+l, -l, +l], [-l, -l, +l]],  # +z
       ]

# Not so bad when there's a bunch of repetition
uval = [[[0.7500, 0.000], [0.8750, 0.000], [0.8750, 0.250], [0.750, 0.250],
         [0.8750, 0.000], [0.9375, 0.000], [0.9375, 0.125], [0.875, 0.125]]] \
     + [[[0.5000, 0.000], [0.7500, 0.000], [0.7500, 0.500], [0.500, 0.500]]] * 4

# Sure is easy when they're all zeroes.
blankol = [[[1] * 3] * 8] + [[[1] * 3] * 4] * 4

walls = [[sum(x, []) for x in zip(vers[y], blankol[y], uval[y])] for y in range(len(vers))]

room = [[6, 2, 2, 3],   # x +->
        [4, 1, 0, 1],   # z
        [4, 8, 2, 1],   # +
        [12, 8, 8, 9]]  # v

def tadd(*args):
    """Element-wise addition of iterables."""
    return [sum(x) for x in zip(*args)]

def ttim(scal, ite):
    """Scalar multiplication of iterables."""
    return [x * scal for x in ite]

def wall(x, y, side):
    """Returns a list of lists of floats that forms a space."""
    res = [w for w in walls[0]]
    # Skip zero here, just did it.
    res += [w for i in range(4) for w in walls[i+1] if side & 2**i]
    # tile coordinates offset, tile size multiplier
    return [tadd([x, 0, y], r[:3]) + r[3:] for r in res]

vs = [t for y, i in enumerate(room) for x, w in enumerate(i) for t in wall(x, y, w)]

def rematr(wid, hig):
    """Resets the projection matrix."""
    global viewmatr
    if hig == 0:
        hig = 1
    v, a, n, f = 1/tan(pi/8), wid/hig, 0.01, 100
    # pyrr has FOV in degrees for some reason???
    pm = matrix.perspective_projection(75, wid/hig, 0.01, 100)
    viewmatr = matrix.from_translation([0, 0, -5])
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'projectmatrix'), 1, GL.GL_FALSE, pm)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'viewmatrix'), 1, GL.GL_FALSE, viewmatr)

def init(wid, hig):
    """Initialises the display."""
    global modelmtx
    GL.glClearColor(0.0, 0.2, 0.15, 0.0)
    GL.glClearDepth(1.0)
    GL.glDepthFunc(GL.GL_LESS)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glShadeModel(GL.GL_SMOOTH)
    GL.glEnable(GL.GL_TEXTURE_2D)
    shades()
    rematr(wid, hig)
    modelmtx = matrix.from_scale([1.8, 1.8, 1.8])
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'), 1, GL.GL_FALSE, modelmtx)

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
    uniform mat4 viewmatrix;
    uniform mat4 modelmatrix;
    out vec3 ourcolour;
    out vec2 ourtex;
    void main(){
        gl_Position = projectmatrix * viewmatrix * modelmatrix * vec4(position, 1.0);
        ourcolour = colour;
        ourtex = texcord;
    }""", GL.GL_VERTEX_SHADER)
    fragment_shader = shaders.compileShader("""#version 330 core
    in vec3 ourcolour;
    in vec2 ourtex;
    out vec4 colour;
    uniform sampler2D tex;
    void main(){
        colour = texture(tex, ourtex) * vec4(ourcolour, 1.0);
    }""", GL.GL_FRAGMENT_SHADER)
    shaderp = shaders.compileProgram(vertex_shader, fragment_shader)
    GL.glUseProgram(shaderp)

def resiz(wid, hig):
    """Handles matrix resizing on viewport resize."""
    if hig == 0:
        hig = 1
    GL.glViewport(0, 0, wid, hig)
    rematr(wid, hig)

def buff_vertices(verts: list, indes: list) -> int:
    """Given a list of vertex-like objects, and maybe a list of indices sets up a thing. VAO?"""
    vao = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(vao)

    v = vbo.VBO(array(verts, 'f'))
    v.bind()
    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 32, v)
    GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 32, v+12)
    GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, False, 32, v+24)
    GL.glEnableVertexAttribArray(0)
    GL.glEnableVertexAttribArray(1)
    GL.glEnableVertexAttribArray(2)
    # Maybe you want to include the vertices verbatim? Go for it.
    if indes is not None:
        pass

    GL.glBindVertexArray(0)
    return vao

def draw():
    """Put the main drawing code in here."""
    global lasttime#, modelmtx
    timedelta = time.time() - lasttime
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    # modelmtx = matrix.from_y_rotation(0.001/timedelta+1)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'), 1, GL.GL_FALSE, modelmtx)

    GL.glBindTexture(GL.GL_TEXTURE_2D, terrain)
    GL.glBindVertexArray(architincture)
    GL.glDrawArrays(GL.GL_QUADS, 0, len(vs))
    GL.glBindVertexArray(0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    GLUT.glutSwapBuffers()
    lasttime = time.time()

def onkey(code, x, y):
    """Alter Vue Mater"""
    global viewmatr
    d = {b'w': [0, 1, 0], b's': [0, -1, 0],
         b'd': [1, 0, 0], b'a': [-1, 0, 0],
         b'e': [0, 0, 1], b'q': [0, 0, -1],}
    if code == b'\x1b': # The Escape Key codevalue.
        exit()
    viewmatr = viewmatr * matrix.from_translation(d.get(code, [0, 0, 0]))
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'viewmatrix'), 1, GL.GL_FALSE, viewmatr)

def onmou(x, y):
    """Alter Moda Mater"""
    global modelmtx, moux, mouy
    modelmtx = modelmtx * matrix.from_y_rotation((moux-x)/99) * matrix.from_x_rotation((mouy-y)/99)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'), 1, GL.GL_FALSE, modelmtx)
    moux, mouy = x, y

def oncl(code, state, x, y):
    """Inite Curso Posit"""
    global moux, mouy
    moux, mouy = x, y

def main():
    """Do all this upon running the script."""
    global window, firsttime, lasttime, terrain, architincture
    GLUT.glutInit(sys.argv)
    GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH)
    GLUT.glutInitWindowSize(640, 480)
    window = GLUT.glutCreateWindow(b'test')
    GLUT.glutDisplayFunc(draw)
    GLUT.glutIdleFunc(draw)
    GLUT.glutReshapeFunc(resiz)
    GLUT.glutKeyboardFunc(onkey)
    GLUT.glutMotionFunc(onmou)
    GLUT.glutMouseFunc(oncl)
    init(640, 480)
    terrain = texturit('terrain.png')
    architincture = buff_vertices(vs, None)
    firsttime = lasttime = time.time()
    GLUT.glutMainLoop()

if __name__ == '__main__':
    main()
