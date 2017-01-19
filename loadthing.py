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
    def __init__(self, shader, ambient=(0.1, 0.1, 0.1), diffuse=(1.0, 1.0, 1.0),
                 specular=(1.0, 1.0, 1.0), shininess=32.0):
        self.ambient, self.diffuse, self.specular, self.shininess, self.shader \
                        = ambient, diffuse, specular, shininess, shader

    def bind(self):
        """Binds a bunch of GLSL Uniforms. Do try not to change their names or anything."""
        glUniform3f(glGetUniformLocation(self.shader, 'material.ambient'), *self.ambient)
        glUniform3f(glGetUniformLocation(self.shader, 'material.diffuse'), *self.diffuse)
        glUniform3f(glGetUniformLocation(self.shader, 'material.specular'), *self.specular)
        glUniform1f(glGetUniformLocation(self.shader, 'material.shininess'), self.shininess)

class Thing:
    """A Thing: A VAO, a texture, a draw(). Pass in a Vertex Array Object handle, the number of
    vertices or vertex notation indices it uses, a Texture handle, a material struct,
    and the polygon shape mode to use in the glDrawArrays call."""
    def __init__(self, vao: int, leng: int, tex: int, mat: Material, shape: int=GL_TRIANGLES):
        self.vao, self.leng, self.tex, self.mat, self.shape = vao, leng, tex, mat, shape

    def draw(self):
        """Binds the vao, binds the texture, draws the vertices."""
        glBindVertexArray(self.vao)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        self.mat.bind()
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
