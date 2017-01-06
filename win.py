"""Draws a bunch of squares."""
# Ignore the invalid variable naming. pylint: disable-msg=C0103
# from random import random
import os
from math import pi#, radians, tan, sin, cos, atan2
from PIL import Image
from numpy import array

from pyrr import Matrix44 as matrix, Vector3 as vector
import OpenGL.GL as GL
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
import glfw
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

def resiz(window, wid, hig):
    """Handles viewport resizing on window resize."""
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

def mochae(latspe, rotspe):
    """A whole bunch of Arcane Nonsense, because I just can't stand repeated code, apparently."""
    # pylint: disable-msg=C0111
    def trykey(code, todo):
        if keys.get(code, False):
            todo()
    def ad(x):
        def da():
            chaem.pos += x * latspe
        return da
    def rt(x):
        def tr():
            chaem.dir = matrix.from_y_rotation(x) * chaem.dir
        return tr
    d = {glfw.KEY_W: ad(chaem.dir), glfw.KEY_S: ad(-chaem.dir),
         glfw.KEY_A: ad(-chaem.myx), glfw.KEY_D: ad(chaem.myx),
         glfw.KEY_Q: ad(chaem.myy), glfw.KEY_E: ad(-chaem.myy),
         glfw.KEY_LEFT: rt(-rotspe), glfw.KEY_RIGHT: rt(rotspe)}
    for x in d:
        trykey(x, d[x])
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'viewmatrix'), 1, False, chaem.lookat())

def draw():
    """Put the main drawing code in here."""
    mochae(4 * timedelta, (pi / 2) * timedelta) # Four 'meters', and one quarter turn per second.

    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'), 1, False, modelmtx)
    GL.glBindVertexArray(architincture)
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glBindTexture(GL.GL_TEXTURE_2D, terrain)
    GL.glDrawArrays(GL.GL_QUADS, 0, len(vs))
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    GL.glBindVertexArray(0)

    origine()

def origine():
    """Draws a set of lines at 0,0,0"""
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'),
                          1, False, matrix.identity())

    GL.glLineWidth(5)
    # No. I use the spaces for vertex subtype visibility. pylint: disable-msg=C0326
    x = [[+1, 0, 0,  1.0, 0.0, 0.0,   0, 0,],
         [-1, 0, 0,  1.0, 0.0, 0.0,   0, 0,],
         [0, +1, 0,  0.0, 1.0, 0.0,   0, 0,],
         [0, -1, 0,  0.0, 1.0, 0.0,   0, 0,],
         [0, 0, +1,  0.0, 0.0, 1.0,   0, 0,],
         [0, 0, -1,  0.0, 0.0, 1.0,   0, 0,],
         # And, one for the Chaemera.
         [*(chaem.pos + chaem.dir + [+0.1, 0, 0]),   1.0, 0.0, 0.0,   0, 0,],
         [*(chaem.pos + chaem.dir + [-0.1, 0, 0]),   1.0, 0.0, 0.0,   0, 0,],
         [*(chaem.pos + chaem.dir + [0, +0.1, 0]),   0.0, 1.0, 0.0,   0, 0,],
         [*(chaem.pos + chaem.dir + [0, -0.1, 0]),   0.0, 1.0, 0.0,   0, 0,],
         [*(chaem.pos + chaem.dir + [0, 0, +0.1]),   0.0, 0.0, 1.0,   0, 0,],
         [*(chaem.pos + chaem.dir + [0, 0, -0.1]),   0.0, 0.0, 1.0,   0, 0,]]

    v = vbo.VBO(array(x, 'f'))
    v.bind()
    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 32, v)
    GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, 32, v+12)
    GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, False, 32, v+24)
    GL.glEnableVertexAttribArray(0)
    GL.glEnableVertexAttribArray(1)
    GL.glEnableVertexAttribArray(2)
    GL.glBindTexture(GL.GL_TEXTURE_2D, blanktex)
    GL.glDrawArrays(GL.GL_LINES, 0, len(x))
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    v.unbind()
    v.delete()

def onkey(window, key, code, action, mode):
    """Record keys"""
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    keys[key] = bool(action)   # PRESS is 1, RELEASE is zero. Maps nicely enough.

def main():
    """Do all this upon running the script."""
    global firsttime, lasttime, timedelta, terrain, blanktex, architincture, keys, oldmouse
    glfw.init()
    # glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    # glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    # glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # glfw.window_hint(glfw.RESIZABLE, False)
    # GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH)
    window = glfw.create_window(640, 480, 'Test', None, None)
    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, resiz)
    glfw.set_key_callback(window, onkey)
    # GLUT.
    init(640, 480)
    terrain = texturit('terrain.png')
    blanktex = texturit('plain.png')
    architincture = buff_vertices(vs, None)
    firsttime = lasttime = glfw.get_time()
    keys = {}
    while not glfw.window_should_close(window):
        timedelta = glfw.get_time() - lasttime or glfw.get_timer_frequency()
        lasttime = glfw.get_time()
        glfw.poll_events()
        draw()
        glfw.swap_buffers(window)

        oldmouse = glfw.get_cursor_pos(window)
    glfw.terminate()

class Chaemera:
    """Moves around, looks at things."""
    def __init__(self):
        self.pos = vector([0.0, 0.0, 5.0])
        self.ure = vector([0.0, 1.0, 0.0])
        # duplicate code just cause pylint doesn't like member initialisation outside of __init__
        self._dir = vector([0.0, 0.0, -1.0])
        self.myx = self._dir ^ self.ure
        self.myy = self.myx ^ self._dir

    @property
    def dir(self):
        """The direction it is facing."""
        return self._dir

    @dir.setter
    def dir(self, value: vector):
        """Sets the normalised direction, as well as the local x and y axes."""
        self._dir = value.normalised
        self.myx = self._dir ^ self.ure
        self.myy = self.myx ^ self._dir

    def lookat(self) -> matrix:
        """Gets the lookat matrix from the posdir vectors."""
        return matrix.from_lookat(self.pos, self.pos + self.dir, self.ure)

if __name__ == '__main__':
    main()
