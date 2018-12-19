"""Draws a bunch of squares."""
# Ignore the invalid variable naming. pylint: disable-msg=C0103
# from random import random
import os
from math import cos, sin#, pi, radians, tan, sin, cos, atan2
from numpy import clip

from pyrr import Matrix44 as matrix, Vector3 as vector#, Quaternion as quaternion
import OpenGL.GL as GL
from OpenGL.GL import shaders
import pygame

from chaem import Fremv, Lamp, make_lampshade
from loadthing import texturit, buff_vertices, load_vertices, Thing, Material
os.chdir(os.path.dirname(__file__))

# Defining global variables somewhere other than the module level. pylint: disable-msg=W0601

def init():
    """Initialises the display."""
    global projectmatrix, modelmatrix, chaem
    GL.glClearColor(0.0, 0.2, 0.15, 0.0)
    GL.glClearDepth(1.0)
    GL.glDepthFunc(GL.GL_LESS)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glShadeModel(GL.GL_SMOOTH)
    shades()
    chaem = Fremv((), deltam)
    GL.glUniform3f(GL.glGetUniformLocation(shaderp, 'lightColour'), *[1.0, 1.0, 1.0])
    modelmatrix = matrix.from_scale([2, 2, 2]) * matrix.from_translation([0, 0, -1])
    wid, hig = window.get_size()
    hig = hig or 1
    projectmatrix = matrix.perspective_projection(whel, wid/hig, 0.01, 100)
    rematr()

def rematr(shader=None):
    """(Re)Sets the projection matrices. Pass in a shader reference if not the default one."""
    # This method has FOV in degrees for some reason???
    shader = shader if shader else shaderp
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shader, 'projectmatrix'), 1, False, projectmatrix)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shader, 'viewmatrix'), 1, False, chaem.lookat())
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shader, 'modelmatrix'), 1, False, modelmatrix)

def resiz(wid, hig):
    """Handles viewport resizing on window resize."""
    if hig == 0:
        hig = 1
    GL.glViewport(0, 0, wid, hig)
    rematr()

def shades():
    """Set up the Vertex and Fragment Shaders."""
    global shaderp
    shaderp = shaders.compileProgram(
        shaders.compileShader(
            """#version 330 core
            layout (location = 0) in vec3 position;
            layout (location = 1) in vec3 normal;
            layout (location = 2) in vec3 colour;
            layout (location = 3) in vec2 texcord;

            out vec3 worldpos;
            out vec3 ournormal;
            out vec3 ourcolour;
            out vec2 ourtex;

            uniform mat4 projectmatrix;
            uniform mat4 viewmatrix;
            uniform mat4 modelmatrix;

            void main(){
                worldpos = vec3(modelmatrix * vec4(position, 1.0));
                gl_Position = projectmatrix * viewmatrix * modelmatrix * vec4(position, 1.0);
                ournormal = normal;
                ourcolour = colour;
                ourtex = texcord;
            }""", GL.GL_VERTEX_SHADER),
        shaders.compileShader(
            """#version 330 core
            struct Material{
                vec3 ambient;
                vec3 diffuse;
                vec3 specular;
                float shininess;
            };

            in vec3 worldpos;
            in vec3 ournormal;
            in vec3 ourcolour;
            in vec2 ourtex;

            out vec4 colour;

            uniform sampler2D tex;
            uniform vec3 lightColour;
            uniform vec3 lightPos;
            uniform vec3 viewpos;
            uniform Material material;

            void main(){
                //Ambient level
                vec3 ambient = material.ambient * lightColour * 0.1;

                //Diffuse calculation
                vec3 norm = normalize(ournormal);
                vec3 lightdir = normalize(lightPos - worldpos);
                float diff = max(dot(norm, lightdir), 0.0);
                vec3 diffuse = diff * material.diffuse * lightColour;

                //Specular calculation
                vec3 viewdir = normalize(viewpos - worldpos);
                vec3 reflectdir = reflect(-lightdir, norm);
                float spec = pow(max(dot(viewdir, reflectdir), 0.0), material.shininess);
                vec3 specular = spec * material.specular * lightColour;

                vec3 totallight = ambient + diffuse + specular;
                colour = texture(tex, ourtex) * vec4(totallight * ourcolour, 1.0);
            }""", GL.GL_FRAGMENT_SHADER))
    GL.glUseProgram(shaderp)

def draw():
    """Put the main drawing code in here."""
    global luxp
    chaem.mochae(timedelta)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glEnable(GL.GL_TEXTURE_2D)

    GL.glUseProgram(shaderp)
    luxp = [sin(lasttime) * 5, cos(lasttime) * 5, 0.0]
    GL.glUniform3f(GL.glGetUniformLocation(shaderp, 'lightPos'), *luxp)
    GL.glUniform3f(GL.glGetUniformLocation(shaderp, 'viewpos'), *chaem.pos)
    rematr()
    architincture.draw()
    mmoodd = modelmatrix * matrix.from_scale([0.2, 0.2, 0.2]) * matrix.from_translation(luxp) * \
        matrix.from_eulers([lasttime, lasttime, lasttime])
    lux.draw(rematr, mmoodd)

def onsc(yof):
    """Wheels. """
    global whel, projectmatrix
    sz = window.get_size()
    whel = clip(whel - yof, 1, 180)
    projectmatrix = matrix.perspective_projection(whel, sz[0] / sz[1], 0.01, 100)

def main():
    """Do all this upon running the script."""
    global window, lasttime, timedelta, blanktex, architincture, lux, luxp, oldmouse, deltam, whel
    pygame.init()
    window = pygame.display.set_mode((640, 480), pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)
    oldmouse, deltam, whel, lasttime = (320, 240), [0, 0], 75, 0
    init()
    terrain = texturit('img/terrain.png')
    blanktex = texturit('img/plain.png')
    make_lampshade()
    architincture = Thing(*load_vertices('img/sph.ply'), shaderp, terrain, \
        Material(ambient=(1.0, 0.5, 0.31), diffuse=(1.0, 0.5, 0.31),
                 specular=(0.5, 0.5, 0.5), shininess=32.0))
    lux = Lamp(Thing(*load_vertices('img/cube.ply'), shaderp, blanktex, None, GL.GL_QUADS))
    clock = pygame.time.Clock()
    while True:
        for evn in pygame.event.get():
            if evn.type == pygame.QUIT or evn.type == pygame.KEYDOWN and evn.key == pygame.K_ESCAPE:
                pygame.quit()
                return
            if evn.type == pygame.VIDEORESIZE:
                resiz(*evn.size)
            if evn.type == pygame.MOUSEBUTTONDOWN and evn.button in (4, 5):
                onsc(-1 if evn.button == 4 else 1)
        timedelta = clock.tick() / 1000
        lasttime += timedelta
        chaem.keys = pygame.key.get_pressed()
        tmpm = pygame.mouse.get_pos()
        deltam[0], deltam[1] = tmpm[0] - oldmouse[0], tmpm[1] - oldmouse[1]
        oldmouse = tmpm
        draw()
        pygame.display.flip()

if __name__ == '__main__':
    main()
