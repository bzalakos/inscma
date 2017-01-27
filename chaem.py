"""Camera types and subtypes. Lights types and subtypes, maybe."""
from enum import Enum
import glfw
from numpy import clip, pi, arccos, arctan2
from pyrr import Vector3, Quaternion, Matrix44
from OpenGL.GL import glGetUniformLocation, glUniform3f, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER
from OpenGL.GL.shaders import compileShader, compileProgram
from loadthing import Thing

def make_lampshade():
    """Call this after initialisting glcontext ti set up the lamp shader."""
    global shaderl
    shaderl = compileProgram(
        compileShader(
            """#version 330 core
            layout (location = 0) in vec3 position;

            uniform mat4 projectmatrix;
            uniform mat4 viewmatrix;
            uniform mat4 modelmatrix;

            void main(){
                gl_Position = projectmatrix * viewmatrix * modelmatrix * vec4(position, 1.0);
            }""", GL_VERTEX_SHADER),
        compileShader(
            """#version 330 core
            out vec4 colour;

            void main(){
                colour = vec4(1.0);
            }""", GL_FRAGMENT_SHADER))

class Chaemera:
    """Moves around, looks at things."""
    def __init__(self, keys: dict, deltam: list):
        self.keys = keys    # Hold on to these. Mutable structures, so it should be fine.
        self.deltam = deltam
        self.pos = Vector3([0.0, 0.0, 5.0])
        self.ure = Vector3([0.0, 1.0, 0.0])
        self.xre = Vector3([1.0, 0.0, 0.0])
        self.zre = Vector3([0.0, 0.0, -1.0])
        # duplicate code just cause pylint doesn't like member initialisation outside of __init__
        self._pitch = 0
        self._yaw = 0
        self._dir = Vector3([0.0, 0.0, -1.0])
        self.myx = (self._dir ^ self.ure).normalised
        self.myy = (self.myx ^ self._dir).normalised

    @property
    def pitch(self) -> float:
        """Rotation about the myx axis."""
        return self._pitch

    @pitch.setter
    def pitch(self, value: float) -> None:
        """Sets the myx rotation."""
        self._pitch = clip(value, -pi * 0.4999, pi * 0.4999)
        self.dir = (Quaternion.from_axis_rotation(self.ure, self._yaw) *
                    Quaternion.from_axis_rotation(self.xre, self._pitch) * self.zre)

    @property
    def yaw(self) -> float:
        """Rotation about the yref axis."""
        return self._yaw

    @yaw.setter
    def yaw(self, value: float) -> None:
        """Sets the yref rotation."""
        self._yaw = value % (2 * pi)
        self.dir = (Quaternion.from_axis_rotation(self.ure, self._yaw) *
                    Quaternion.from_axis_rotation(self.xre, self._pitch) * self.zre)

    def pitya(self, pit: float, ya: float) -> None:
        """Sets the pitch and yaw simultaneously, saves a second round of vector normalisation?"""
        self._pitch = clip(pit, -pi * 0.4999, pi * 0.4999)
        self._yaw = ya % (2 * pi)
        self.dir = (Quaternion.from_axis_rotation(self.ure, self._yaw) *
                    Quaternion.from_axis_rotation(self.xre, self._pitch) * self.zre)

    @property
    def dir(self) -> Vector3:
        """The direction it is facing."""
        return self._dir

    @dir.setter
    def dir(self, value: Vector3) -> None:
        """Sets the normalised direction, as well as the local x and y axes.
        (Don't use this one: set the pitch and yaw instead.)"""
        self._dir = value.normalised
        self.myx = (self._dir ^ self.ure).normalised
        self.myy = (self.myx ^ self._dir).normalised

    def lookat(self) -> Matrix44:
        """Gets the lookat matrix from the posdir vectors."""
        return Matrix44.from_lookat(self.pos, self.pos + self.dir, self.ure)

class Fremv(Chaemera):
    """Chaemerae that can actually move around."""
    def __init__(self, *args):
        super().__init__(*args)
        self.latspe = 4
        self.rotspe = pi / 2

    def mochae(self, timedelta: float) -> None:
        """Move the thing according to a whole mess of Global State."""
        # Don't really want to annotate all these private minifunctions. pylint: disable-msg=C0111
        def trykey(code, todo):
            if self.keys.get(code, False):
                todo()
        def ad(x):
            def da():
                self.pos += x * self.latspe * timedelta
            return da
        # Back in my day we could just use a switch statement.
        d = {glfw.KEY_W: ad(self.dir), glfw.KEY_S: ad(-self.dir),
             glfw.KEY_A: ad(-self.myx), glfw.KEY_D: ad(self.myx),
             glfw.KEY_Q: ad(self.myy), glfw.KEY_E: ad(-self.myy),}
        self.pitya(self.pitch - self.deltam[1] * self.rotspe * timedelta,
                   self.yaw - self.deltam[0] * self.rotspe * timedelta)
        for x in d:
            trykey(x, d[x])

class Raimv(Chaemera):
    """Moves around, view trailing."""
    def __init__(self, *args):
        super().__init__(*args)
        self.latspe = 4
        self.rotspe = -pi    # Set this to +pi to make it spin the other way.
        self.states = Enum('states', 'stop forw')
        self.stat = self.states.stop
        self._movdir = self._dir.copy()
        self.orgp = self.pos.copy()

    @property
    def heading(self) -> float:
        """The direction it is moving, but expressed in radians."""
        return arctan2(self.ure | (self.zre ^ self.movdir), self.zre | self.movdir)

    @property
    def movdir(self) -> Vector3:
        """The direction it is moving."""
        return self._movdir

    @movdir.setter
    def movdir(self, value: Vector3) -> None:
        """Sets the normalised movement direction. If permitted to do so."""
        if self.stat == self.states.stop:
            self._movdir = value.normalised
            self.orgp = self.pos.copy()
            self.stat = self.states.forw

    def mochae(self, timedelta: float) -> None:
        """Do moving, but look slowly."""
        rent = arccos(clip(self.movdir | self.dir, -1, 1))    # Total remaining angle between dirs.
        comp = self.dir ^ self.movdir   # Comparison reference, for wisity checking.
        rent = arctan2(self.ure | comp, self.movdir | self.dir)
        if abs(rent) <= abs(self.rotspe * timedelta):
            self.dir = self.movdir.copy()     # Snap to alignment, don't risk rounding errors.
        else:
            r = Quaternion.from_axis_rotation(self.ure, self.rotspe * timedelta)
            self.dir = r * self.dir   # move over a little.

        if self.stat == self.states.forw:
            tent, rest = self.movdir * self.latspe * timedelta, self.orgp + self.movdir*2 - self.pos
            if tent.length > rest.length:   # Snap to grid.
                self.pos = ((self.pos + rest) * 2).round() / 2
                self.stat = self.states.stop
            else:
                self.pos += tent

class Grimv(Chaemera):
    """This one, not so much with the moving."""
    def __init__(self, *args):
        super().__init__(*args)
        self.latspe = 4
        self.rotspe = pi
        self.states = Enum('states', 'stop forw left righ')
        self.stat = self.states.stop
        self.orgp = self.pos.copy()
        self.ancy = self.yaw

    def mochae(self, timedelta: float) -> None:
        """More restrictions, yet harder to describe."""
        trykey = lambda x: self.keys.get(x, False)
        if self.stat == self.states.forw:
            tent, rest = self.dir * self.latspe * timedelta, self.orgp + self.dir*2 - self.pos
            if tent.length > rest.length:   # Snap to grid.
                self.pos = ((self.pos + rest) * 2).round() / 2
                self.stat = self.states.stop
            else:
                self.pos += tent
        if self.stat == self.states.left:
            tent, rest = self.rotspe * timedelta, pi - abs(abs(self.ancy + pi/2 - self.yaw) - pi)
            if abs(tent) > abs(rest):     # Round it to the nearest pi/2.
                self.yaw = round((self.yaw + rest) / (pi/2)) * (pi/2)
                self.stat = self.states.stop
            else:
                self.yaw += tent
        if self.stat == self.states.righ:
            tent, rest = -self.rotspe * timedelta, pi - abs(abs(self.ancy - pi/2 - self.yaw) - pi)
            if abs(tent) > abs(rest):     # Round it to the nearest pi/2.
                self.yaw = round((self.yaw + rest) / (pi/2)) * (pi/2)
                self.stat = self.states.stop
            else:
                self.yaw += tent
        if self.stat == self.states.stop:
            if trykey(glfw.KEY_W):
                self.orgp = self.pos.copy()
                self.stat = self.states.forw
            elif trykey(glfw.KEY_A):
                self.ancy = self.yaw
                self.stat = self.states.left
            elif trykey(glfw.KEY_D):
                self.ancy = self.yaw
                self.stat = self.states.righ

class Lamp:
    """A light source. Uses its own shader to look particularly lightsourceworthy."""
    def __init__(self, model: Thing, pos=Vector3([0.0, 0.0, 0.0]),
                 ambient=(0.1, 0.1, 0.1), diffuse=(1.0, 1.0, 1.0), specular=(1.0, 1.0, 1.0)):
        self.pos, self.ambient, self.diffuse, self.specular, self.model = \
            pos, ambient, diffuse, specular, model

    def bind(self):
        """Bind the light values to the shader. Not the lamp shader, the other one."""
        glUniform3f(glGetUniformLocation(self.model.shader, 'light.position'), *self.pos)
        glUniform3f(glGetUniformLocation(self.model.shader, 'light.ambient'), *self.ambient)
        glUniform3f(glGetUniformLocation(self.model.shader, 'light.diffuse'), *self.diffuse)
        glUniform3f(glGetUniformLocation(self.model.shader, 'light.specular'), *self.specular)
