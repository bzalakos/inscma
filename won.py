"""Draws a bunch of squares."""
# Ignore the invalid variable naming. pylint: disable-msg=C0103
# from random import random
import os
from math import cos, sin#, pi, radians, tan, sin, cos, atan2
from numpy import clip

from pyrr import Matrix44 as matrix, Vector3 as vector#, Quaternion as quaternion
import OpenGL.GL as GL
from OpenGL.GL import shaders
import glfw
from dots import vs, lx

os.chdir(os.path.dirname(__file__))
from chaem import Fremv
from loadthing import texturit, buff_vertices, load_vertices, Thing, Material

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
    chaem = Fremv(keys, deltam)
    GL.glUniform3f(GL.glGetUniformLocation(shaderp, 'lightColour'), *[1.0, 1.0, 1.0])
    modelmatrix = matrix.from_scale([2, 2, 2]) * matrix.from_translation([0, 0, -1])
    wid, hig = glfw.get_window_size(window)
    hig = hig if hig else 1
    projectmatrix = matrix.perspective_projection(whel, wid/hig, 0.01, 100)
    rematr()

def rematr():
    """(Re)Sets the projection matrices."""
    # This method has FOV in degrees for some reason???
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'projectmatrix'), 1, False, projectmatrix)
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'viewmatrix'), 1, False, chaem.lookat())
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'), 1, False, modelmatrix)

def resiz(window, wid, hig):
    """Handles viewport resizing on window resize."""
    if hig == 0:
        hig = 1
    GL.glViewport(0, 0, wid, hig)
    rematr()

def shades():
    """Set up the Vertex and Fragment Shaders."""
    global shaderp, shaderl

    vertex_shader = shaders.compileShader(
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
        }""", GL.GL_VERTEX_SHADER)
    fragment_shader = shaders.compileShader(
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

            colour = texture(tex, ourtex) * vec4((ambient + diffuse + specular) * ourcolour, 1.0);
        }""", GL.GL_FRAGMENT_SHADER)
    shaderp = shaders.compileProgram(vertex_shader, fragment_shader)
    GL.glUseProgram(shaderp)

    fragment_shader_l = shaders.compileShader(
        """#version 330 core
        out vec4 colour;
        uniform sampler2D tex;
        uniform vec3 lightColour;
        void main(){
            colour = vec4(1.0);
        }""", GL.GL_FRAGMENT_SHADER)
    shaderl = shaders.compileProgram(vertex_shader, fragment_shader_l)

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

    GL.glUseProgram(shaderl)
    rematr()
    GL.glBindVertexArray(lux)
    mmoodd = modelmatrix * matrix.from_scale([0.2, 0.2, 0.2]) * matrix.from_translation(luxp) * \
        matrix.from_eulers([lasttime, lasttime, lasttime])
    GL.glUniformMatrix4fv(GL.glGetUniformLocation(shaderp, 'modelmatrix'), 1, False, mmoodd)
    GL.glDrawArrays(GL.GL_QUADS, 0, len(lx))
    GL.glBindVertexArray(0)

def onkey(window, key, code, action, mode):
    """Record keys"""
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    keys[key] = bool(action)   # PRESS is 1, RELEASE is zero. Maps nicely enough.

def onsc(window, xof, yof):
    """Wheels. """
    global whel, projectmatrix
    sz = glfw.get_window_size(window)
    whel = clip(whel - yof, 1, 180)
    projectmatrix = matrix.perspective_projection(whel, sz[0] / sz[1], 0.01, 100)

def main():
    """Do all this upon running the script."""
    global window, firsttime, lasttime, timedelta, blanktex, architincture, \
        lux, luxp, keys, oldmouse, deltam, whel
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
    init()
    terrain = texturit('img/terrain.png')
    blanktex = texturit('img/plain.png')
    architincture = Thing(*load_vertices('img/sph.ply'), terrain, Material(shaderp, \
        ambient=(1.0, 0.5, 0.31), diffuse=(1.0, 0.5, 0.31), specular=(0.5, 0.5, 0.5), shininess=32.0))
    lux = buff_vertices(lx, None)
    luxp = vector([0.0, 0.0, 0.0])
    firsttime = lasttime = glfw.get_time()
    while not glfw.window_should_close(window):
        timedelta = glfw.get_time() - lasttime or glfw.get_timer_frequency()
        lasttime = glfw.get_time()
        tmpm = glfw.get_cursor_pos(window)
        deltam[0], deltam[1] = tmpm[0] - oldmouse[0], tmpm[1] - oldmouse[1]
        oldmouse = tmpm
        glfw.poll_events()
        draw()
        glfw.swap_buffers(window)
    glfw.terminate()

if __name__ == '__main__':
    main()
