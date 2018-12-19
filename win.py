"""Draws a bunch of squares."""
# Ignore the invalid variable naming. pylint: disable-msg=C0103
# from random import random
import os
from numpy import clip, pi

from pyrr import Matrix44 as matrix, Vector3 as vector, Quaternion as quaternion
import OpenGL.GL as GL
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
import pygame
from dots import vs, room

os.chdir(os.path.dirname(__file__))
from chaem import Raimv
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
    modelmtx = matrix.from_scale([2, 2, 2]) * matrix.from_translation([0, 0, -.5])
    chaem = Raimv((), deltam)
    chaem.rotspe = 2*pi
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'viewmatrix'), 1, False, chaem.lookat())
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'), 1, False, modelmtx)

def rematr(wid, hig):
    """Resets the projection matrix."""
    if hig == 0:
        hig = 1
    # This method has FOV in degrees for some reason???
    pm = matrix.perspective_projection(whel, wid/hig, 0.01, 100)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'projectmatrix'), 1, False, pm)

def resiz(wid, hig):
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
    def inc(x, amount=1):
        return (x + amount) % 4
    def wlc(x):
        return (x >> 4) | x
    if chaem.stat == chaem.states.stop:
        x, z = int((chaem.pos.z + 1) / 2), int((chaem.pos.x + 1) / 2)
        spot = room[x][z]
        dire = inc(int(round(chaem.heading * 2 / pi)), 1)    # Get this into room coordinates (0-3)
        for x in [3, 0, 1, 2]:    # Check each side, starting with the right.
            if not wlc(spot) & (2 ** (inc(dire, x))):
                dire = inc(dire, x)
                break
        chaem.movdir = quaternion.from_y_rotation((dire - 1) * pi / 2) * vector([0., 0., -1.])
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

def onsc(window, yof):
    """Wheels. """
    global whel
    sz = window.get_size()
    whel = clip(whel - yof, 1, 180)
    pm = matrix.perspective_projection(whel, sz[0] / sz[1], 0.01, 100)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'projectmatrix'), 1, False, pm)

def main():
    """Do all this upon running the script."""
    global timedelta, terrain, blanktex, architincture, whel, deltam
    pygame.init()
    window = pygame.display.set_mode((640, 480), pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)
    deltam, whel =  [0, 0], 75
    init(640, 480)
    terrain = texturit('img/terrain.png')
    blanktex = texturit('img/plain.png')
    architincture = buff_vertices(vs, None)
    clock = pygame.time.Clock()
    while True:
        for evn in pygame.event.get():
            if evn.type == pygame.QUIT or evn.type == pygame.KEYDOWN and evn.key == pygame.K_ESCAPE:
                pygame.quit()
                return
            if evn.type == pygame.VIDEORESIZE:
                resiz(*evn.size)
            if evn.type == pygame.MOUSEBUTTONDOWN and evn.button in (4, 5):
                onsc(window, -1 if evn.button == 4 else 1)
        timedelta = clock.tick() / 1000
        chaem.keys = pygame.key.get_pressed()
        tmpm = pygame.mouse.get_pos()
        oldmouse = tmpm
        draw()
        pygame.display.flip()

if __name__ == '__main__':
    main()
