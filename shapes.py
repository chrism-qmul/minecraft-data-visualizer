from OpenGL.GL import *
from OpenGL.GLU import *
from contextlib import contextmanager

@contextmanager
def glmatrix():
    glPushMatrix()
    yield
    glPopMatrix()

def square(fill=None, stroke=None, stroke_width=1, texture=None):
    glLineWidth(stroke_width)
    if fill and fill[3] < 1:
        glDisable(GL_DEPTH_TEST)
    if fill or texture:
        if fill:
            glColor4f(*fill)
        if texture:
            glBindTexture(GL_TEXTURE_2D, texture)
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, 1)
        if texture: 
            glTexCoord2f(0,0)
        glVertex3f(-0.5, -0.5, 0.5)
        if texture: 
            glTexCoord2f(1,0)
        glVertex3f(0.5, -0.5, 0.5)
        if texture: 
            glTexCoord2f(1,1)
        glVertex3f(0.5, 0.5, 0.5)
        if texture: 
            glTexCoord2f(0,1)
        glVertex3f(-0.5, 0.5, 0.5)
        glEnd()
    if fill and fill[3] < 1:
        glEnable(GL_DEPTH_TEST)
    if stroke:
        glColor4f(*stroke)  #/ Set the color for the square.
        glBegin(GL_LINE_LOOP)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glEnd() 
    glLineWidth(1)

def plane(width, height, fill=None, stroke=None, stroke_width=1, texture=None):
    for w in range(width):
        for h in range(height):
            with glmatrix():
                glTranslatef(w, h, 0)
                square(fill, stroke, stroke_width, texture)

def cube(fill=None, stroke=None, stroke_width=1, texture=None):
    with glmatrix():
        glTranslatef(0.5,0.5,0.5)
        with glmatrix(): # front face
            square(fill, stroke, stroke_width, texture)
        with glmatrix(): # right face
            glRotatef(90, 0, 1, 0)
            square(fill, stroke, stroke_width, texture)
        with glmatrix(): # top face
            glRotatef(-90, 1, 0, 0)
            square(fill, stroke, stroke_width, texture)
        with glmatrix(): # back face
            glRotatef(180, 0, 1, 0)
            square(fill, stroke, stroke_width, texture)
        with glmatrix(): # left face
            glRotatef(-90, 0, 1, 0)
            square(fill, stroke, stroke_width, texture)
        with glmatrix(): # bottom face
            glRotatef(90, 1, 0, 0)
            square(fill, stroke, stroke_width, texture)

def axis():
    glLineWidth(8)
    glBegin(GL_LINES)
    #x
    glColor3f(1,0,0)
    glVertex3f(0, 0, 0)
    glVertex3f(2.5, 0, 0)
    #y
    glColor3f(0,1,0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 2.5, 0)
    #z
    glColor3f(0,0,1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 2.5)
    glEnd()
    glLineWidth(1)

