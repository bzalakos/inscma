"""Loading images to Textures, and vertex lists to VAOs as well, that sort of thing."""
from PIL import Image
from numpy import array
from OpenGL.arrays import vbo
from OpenGL.GL import glBindVertexArray, glGenVertexArrays, glVertexAttribPointer, \
    glEnableVertexAttribArray, glGenBuffers, glBindBuffer, glBufferData, \
    glGenTextures, glBindTexture, glTexParameter, glTexImage2D, glGenerateMipmap, \
    GL_FLOAT, GL_ELEMENT_ARRAY_BUFFER, GL_STATIC_DRAW, GL_UNSIGNED_BYTE, GL_TEXTURE_2D, GL_RGBA, \
    GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE, \
    GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_NEAREST

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
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indes)*8, indes, GL_STATIC_DRAW)

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
