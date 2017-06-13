"""Loading images to Textures, and vertex lists to VAOs as well, that sort of thing."""
from PIL import Image
from numpy import array
from OpenGL.arrays import vbo
from OpenGL.GL import glBindVertexArray, glGenVertexArrays, glVertexAttribPointer, \
    glEnableVertexAttribArray, glGenBuffers, glBindBuffer, glBufferData, \
    glGenTextures, glBindTexture, glTexParameter, glTexImage2D, glGenerateMipmap, glDrawArrays, \
    glGetUniformLocation, glUniform3f, glUniform1f, \
    GL_FLOAT, GL_ELEMENT_ARRAY_BUFFER, GL_STATIC_DRAW, GL_UNSIGNED_BYTE, \
    GL_TEXTURE_2D, GL_RGBA, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE, \
    GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_NEAREST, GL_TRIANGLES

class Material:
    """A set of reflection values, declares how shiny something is and how something is shiny.
    Also need to pass a reference to the shader it's to be used in. Apparently."""
    def __init__(self, ambient=(0.1, 0.1, 0.1), diffuse=(1.0, 1.0, 1.0),
                 specular=(1.0, 1.0, 1.0), shininess=32.0):
        self.ambient, self.diffuse, self.specular, self.shininess, \
                        = ambient, diffuse, specular, shininess

    def bind(self, shader):
        """Binds a bunch of GLSL Uniforms. Do try not to change their names or anything."""
        glUniform3f(glGetUniformLocation(shader, 'material.ambient'), *self.ambient)
        glUniform3f(glGetUniformLocation(shader, 'material.diffuse'), *self.diffuse)
        glUniform3f(glGetUniformLocation(shader, 'material.specular'), *self.specular)
        glUniform1f(glGetUniformLocation(shader, 'material.shininess'), self.shininess)

materials = {
    # Yeah, it's long, you aren't supposed to read these, it's fine. pylint: disable-msg=C0301
    'Emerald': Material((0.0215, 0.1745, 0.0215), (0.07568, 0.61424, 0.07568), (0.633, 0.727811, 0.633), 0.6),
    'Jade': Material((0.135, 0.2225, 0.1575), (0.54, 0.89, 0.63), (0.316228, 0.316228, 0.316228), 0.1),
    'Obsidian': Material((0.05375, 0.05, 0.06625), (0.18275, 0.17, 0.22525), (0.332741, 0.328634, 0.346435), 0.3),
    'Pearl': Material((0.25, 0.20725, 0.20725), (1, 0.829, 0.829), (0.296648, 0.296648, 0.296648), 0.088),
    'Ruby': Material((0.1745, 0.01175, 0.01175), (0.61424, 0.04136, 0.04136), (0.727811, 0.626959, 0.626959), 0.6),
    'Turquoise': Material((0.1, 0.18725, 0.1745), (0.396, 0.74151, 0.69102), (0.297254, 0.30829, 0.306678), 0.1),
    'Brass': Material((0.329412, 0.223529, 0.027451), (0.780392, 0.568627, 0.113725), (0.992157, 0.941176, 0.807843), 0.21794872),
    'Bronze': Material((0.2125, 0.1275, 0.054), (0.714, 0.4284, 0.18144), (0.393548, 0.271906, 0.166721), 0.2),
    'Chrome': Material((0.25, 0.25, 0.25), (0.4, 0.4, 0.4), (0.774597, 0.774597, 0.774597), 0.6),
    'Copper': Material((0.19125, 0.0735, 0.0225), (0.7038, 0.27048, 0.0828), (0.256777, 0.137622, 0.086014), 0.1),
    'Gold': Material((0.24725, 0.1995, 0.0745), (0.75164, 0.60648, 0.22648), (0.628281, 0.555802, 0.366065), 0.4),
    'Silver': Material((0.19225, 0.19225, 0.19225), (0.50754, 0.50754, 0.50754), (0.508273, 0.508273, 0.508273), 0.4),
    'Black_Plastic': Material((0.0, 0.0, 0.0), (0.01, 0.01, 0.01), (0.50, 0.50, 0.50), .25),
    'Cyan_Plastic': Material((0.0, 0.1, 0.06), (0.0, 0.50980392, 0.50980392), (0.50196078, 0.50196078, 0.50196078), .25),
    'Green_Plastic': Material((0.0, 0.0, 0.0), (0.1, 0.35, 0.1), (0.45, 0.55, 0.45), .25),
    'Red_Plastic': Material((0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.7, 0.6, 0.6), .25),
    'White_Plastic': Material((0.0, 0.0, 0.0), (0.55, 0.55, 0.55), (0.70, 0.70, 0.70), .25),
    'Yellow_Plastic': Material((0.0, 0.0, 0.0), (0.5, 0.5, 0.0), (0.60, 0.60, 0.50), .25),
    'Black_Rubber': Material((0.02, 0.02, 0.02), (0.01, 0.01, 0.01), (0.4, 0.4, 0.4), .078125),
    'Cyan_Rubber': Material((0.0, 0.05, 0.05), (0.4, 0.5, 0.5), (0.04, 0.7, 0.7), .078125),
    'Green_Rubber': Material((0.0, 0.05, 0.0), (0.4, 0.5, 0.4), (0.04, 0.7, 0.04), .078125),
    'Red_Rubber': Material((0.05, 0.0, 0.0), (0.5, 0.4, 0.4), (0.7, 0.04, 0.04), .078125),
    'White_Rubber': Material((0.05, 0.05, 0.05), (0.5, 0.5, 0.5), (0.7, 0.7, 0.7), .078125),
    'Yellow_Rubber': Material((0.05, 0.05, 0.0), (0.5, 0.5, 0.4), (0.7, 0.7, 0.04), .078125),}

class Thing:
    """A Thing: A VAO, a shader, a texture, a draw(). Pass in a Vertex Array Object handle, the number of
    vertices or vertex notation indices it uses, a Texture handle, a material struct,
    and the polygon shape mode to use in the glDrawArrays call."""
    def __init__(self, vao: int, leng: int, shader: int, tex: int, mat: Material, shape: int=GL_TRIANGLES):
        self.vao, self.shader, self.leng, self.tex, self.mat, self.shape = vao, shader, leng, tex, mat, shape

    def draw(self):
        """Binds the vao, binds the texture, draws the vertices."""
        glBindVertexArray(self.vao)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        if self.mat is not None:
            self.mat.bind(self.shader)
        glDrawArrays(self.shape, 0, self.leng)
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindVertexArray(0)

def load_vertices(filn: str) -> (int, int):
    """Loads a csv file of vertex data. First, the rows of vertices, then the indices.
    VX needs to be the [[pX, pY, pZ, nX, nY, nZ, cR, cR, cB, tU, tV]] * len sort of format.
    And the Is all on the last row."""
    with open(filn) as fil:
        lines = fil.readlines()
        hmode, vcount, vcounted, verts, indes = True, 0, 0, [], []
        for line in lines:
            words = line.split()
            if hmode:
                # Suspect you may come to regret ignoring the vertex property order?
                if words[0] in ('ply', 'format', 'comment', 'property'):
                    continue
                elif words[0] == 'element':
                    if words[1] == 'vertex':
                        vcount = int(words[2])
                elif words[0] == 'end_header':
                    hmode = False
            else:
                if vcounted < vcount:
                    verts.append([float(word) for word in words])
                    vcounted += 1
                    # continue
                else:
                    indes.extend([int(word) for word in words[1:]])
    return buff_vertices(verts, indes), len(indes)

def buff_vertices(verts: list, indes: list=None) -> int:
    """Given a list of vertex-like objects, an optional list of indices, returns a VAO handle.
    Format (all should be floats): [[pX, pY, pZ, nX, nY, nZ, cR, cR, cB, tU, tV]] * len."""
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    v = vbo.VBO(array(verts, 'f'))
    v.bind()
    glVertexAttribPointer(0, 3, GL_FLOAT, False, 44, v)
    glVertexAttribPointer(1, 3, GL_FLOAT, False, 44, v+12)
    glVertexAttribPointer(2, 3, GL_FLOAT, False, 44, v+24)
    glVertexAttribPointer(3, 2, GL_FLOAT, False, 44, v+36)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glEnableVertexAttribArray(2)
    glEnableVertexAttribArray(3)
    # Maybe you want to include the vertices verbatim? Go for it.
    if indes is not None:
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indes)*8, array(indes, 'i'), GL_STATIC_DRAW)

    glBindVertexArray(0)
    return vao

def texturit(filn: str) -> int:
    """Import a Texture and return the texture buffer handle. Better by RGBA formatted, too."""
    wa = glGenTextures(1)
    with Image.open(filn) as i:
        ix, iy, im = i.size[0], i.size[1], i.tobytes('raw', 'RGBA')
        glBindTexture(GL_TEXTURE_2D, wa)

        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, im)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
    return wa
