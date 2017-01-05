"""Draws a bunch of squares."""
# Ignore the invalid variable naming. pylint: disable-msg=C0103
import sys
import time
# from random import random
import os
from math import pi, radians, tan, sin, cos, atan2
from PIL import Image
from numpy import array

from pyrr import Matrix44 as matrix, Vector3 as vector
import OpenGL.GL as GL
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
import OpenGL.GLUT as GLUT
from dots import vs

os.chdir(os.path.dirname(__file__))

# pylint: disable-msg=W0601

def init(wid, hig):
    """Initialises the display."""
    global modelmtx, chaem
    GL.glClearColor(0.0, 0.2, 0.15, 0.0)
    GL.glClearDepth(1.0)
    GL.glDepthFunc(GL.GL_LESS)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glShadeModel(GL.GL_SMOOTH)
    GL.glEnable(GL.GL_TEXTURE_2D)
    shades()
    rematr(wid, hig)
    modelmtx = matrix.from_scale([1.8, 1.8, 1.8])
    chaem = Chaemera()
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'viewmatrix'), 1, False, chaem.lookat())
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'), 1, False, modelmtx)

def rematr(wid, hig):
    """Resets the projection matrix."""
    if hig == 0:
        hig = 1
    # This method has FOV in degrees for some reason???
    pm = matrix.perspective_projection(75, wid/hig, 0.01, 100)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'projectmatrix'), 1, False, pm)

def resiz(wid, hig):
    """Handles matrix resizing on viewport resize."""
    if hig == 0:
        hig = 1
    GL.glViewport(0, 0, wid, hig)
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
        ebo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(indes)*8, indes, GL.GL_STATIC_DRAW)

    GL.glBindVertexArray(0)
    return vao

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

def draw():
    """Put the main drawing code in here."""
    global lasttime, modelmtx
    timedelta = time.time() - lasttime
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    # modelmtx = matrix.from_y_rotation(0.001/timedelta+1)
    GL.glBindVertexArray(architincture)
    GL.glBindTexture(GL.GL_TEXTURE_2D, terrain)
    GL.glDrawArrays(GL.GL_QUADS, 0, len(vs))
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    GL.glBindVertexArray(0)

    # rad = 10
    # cx = sin(time.time()) * rad
    # cy = cos(time.time()) * rad
    # chaem.pos = vector([cx, 0, cy])
    # GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'viewmatrix'), 1, False, chaem.lookat())

    origine()

    GLUT.glutSwapBuffers()
    lasttime = time.time()

def origine():
    """Draws a set of lines at 0,0,0"""
    GL.glLineWidth(5)
    GL.glBegin(GL.GL_LINES)
    GL.glColor(1, 0, 0)
    GL.glVertex(1, 0, 0)
    GL.glVertex(-1, 0, 0)
    GL.glColor(0, 1, 0)
    GL.glVertex(0, 1, 0)
    GL.glVertex(0, -1, 0)
    GL.glColor(0, 0, 1)
    GL.glVertex(0, 0, 1)
    GL.glVertex(0, 0, -1)
    GL.glEnd()

def onkey(code, x, y):
    """Alter Vue Mater"""
    global chaem
    d = {b'w': [0, 1, 0], b's': [0, -1, 0],
         b'd': [1, 0, 0], b'a': [-1, 0, 0],
         b'e': [0, 0, 1], b'q': [0, 0, -1],}
    if code == b'\x1b': # The Escape Key codevalue.
        exit()
    chaem.pos += d.get(code, [0, 0, 0])
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'viewmatrix'), 1, False, chaem.lookat())

def onmou(x, y):
    """Alter Moda Mater"""
    global modelmtx, moux, mouy
    modelmtx = modelmtx * matrix.from_y_rotation((moux-x)/99) * matrix.from_x_rotation((mouy-y)/99)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'), 1, False, modelmtx)
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
    GLUT.glutSpecialFunc(onkey)
    GLUT.glutMotionFunc(onmou)
    GLUT.glutMouseFunc(oncl)
    init(640, 480)
    terrain = texturit('terrain.png')
    architincture = buff_vertices(vs, None)
    firsttime = lasttime = time.time()
    GLUT.glutMainLoop()

class Chaemera:
    """Moves around, looks at things."""
    def __init__(self):
        self.pos = vector([0, 0, 5.5])
        self.targ = vector([0, 0, 0])

    def lookat(self) -> matrix:
        """Gets the lookat matrix from the postarg vectors."""
        return matrix.from_lookat(self.pos, self.targ, [0,1,0])

if __name__ == '__main__':
    main()
