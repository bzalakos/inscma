"""Draws a bunch of squares."""
# Ignore the invalid variable naming. pylint: disable-msg=C0103
# from random import random
import os
# from math import #, radians, tan, sin, cos, atan2
from numpy import array, clip

from pyrr import Matrix44 as matrix, Vector3 as vector, Quaternion as quaternion
import OpenGL.GL as GL
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
import glfw
from dots import vs

os.chdir(os.path.dirname(__file__))
from chaem import Grimv
from loadthing import texturit, buff_vertices

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
    modelmtx = matrix.from_scale([2, 2, 2]) * matrix.from_translation([0, 0, -1])
    chaem = Grimv(keys, deltam)
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

def shades():
    """Set up the Vertex and Fragment Shaders."""
    global shaderp

    vertex_shader = shaders.compileShader("""#version 330 core
    layout (location = 0) in vec3 position;
    layout (location = 1) in vec3 normal;
    layout (location = 2) in vec3 colour;
    layout (location = 3) in vec2 texcord;
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
    chaem.mochae(timedelta)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'), 1, False, modelmtx)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'viewmatrix'), 1, False, chaem.lookat())
    GL.glBindVertexArray(architincture)
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glBindTexture(GL.GL_TEXTURE_2D, terrain)
    GL.glDrawArrays(GL.GL_QUADS, 0, len(vs))
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    GL.glBindVertexArray(0)

def onkey(window, key, code, action, mode):
    """Record keys"""
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    keys[key] = bool(action)   # PRESS is 1, RELEASE is zero. Maps nicely enough.

def onsc(window, xof, yof):
    """Wheels. """
    global whel
    sz = glfw.get_window_size(window)
    whel = clip(whel - yof, 1, 180)
    pm = matrix.perspective_projection(whel, sz[0] / sz[1], 0.01, 100)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'projectmatrix'), 1, False, pm)

def main():
    """Do all this upon running the script."""
    global firsttime, lasttime, timedelta, terrain, blanktex, architincture, \
        keys, oldmouse, deltam, whel
    glfw.init()
    window = glfw.create_window(640, 480, 'Test', None, None)
    oldmouse = (320, 240)
    whel = 75
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, resiz)
    glfw.set_key_callback(window, onkey)
    glfw.set_scroll_callback(window, onsc)
    keys = {}
    deltam = [0, 0]
    init(640, 480)
    terrain = texturit('img/terrain.png')
    blanktex = texturit('img/plain.png')
    architincture = buff_vertices(vs, None)
    firsttime = lasttime = glfw.get_time()
    while not glfw.window_should_close(window):
        timedelta = glfw.get_time() - lasttime or glfw.get_timer_frequency()
        lasttime = glfw.get_time()
        tmpm = glfw.get_cursor_pos(window)
        deltam[0], deltam[1] = tmpm[0] - oldmouse[0], tmpm[1] - oldmouse[1]
        oldmouse = tmpm
        glfw.poll_events()
        glfw.swap_buffers(window)
        draw()
    glfw.terminate()

if __name__ == '__main__':
    main()
