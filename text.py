from freetype import *
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *


_vertex_shader = """
#version 120

//attribute
varying vec2 UV;

void main()
{
    //UV = gl_TexCoord[0].xy;
    UV = gl_MultiTexCoord0.xy;
    gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;
}
"""

_frag_shader = """
#version 120

// Interpolated values from the vertex shaders
varying vec2 UV;

// Ouput data
uniform vec4 backgroundColor = vec4(1,1,0,1);

// Values that stay constant for the whole mesh.
uniform sampler2D tex;

uniform vec2 flip = vec2(1.0,1.0);


void main(){

    // Output color = color of the texture at the specified UV
    vec2 scaledUV = (UV*vec2(2,2));//+vec2(0.2,0.2);
    vec2 flippedUV = (flip - scaledUV);// + vec2(0.2,0.2);
    vec4 txt = texture2D(tex, flippedUV);// * flip);
    gl_FragColor = vec4(mix(backgroundColor.rgb, txt.rgb, txt.a),1);
    //gl_FragColor = mix(backgroundColor, txt, txt.a);
    //gl_FragColor = vec4(gl_FragCoord.x, gl_FragCoord.y, 1, 1);
    //gl_TexCoord[0].xy
    //gl_FragColor = vec4(UV.xy*flip, 1, 1);
    //gl_FragColor = vec4(gl_TexCoord[0].xy*flip,1,1)
    //gl_FragColor = vec4(scaledUV.xy,1,1);
}
"""

#FRAG_SHADER = shaders.compileShader(_frag_shader, GL_FRAGMENT_SHADER)
#VERTEX_SHADER = shaders.compileShader(_vertex_shader, GL_VERTEX_SHADER)

class Text:
    def __init__(self, font_path, font_size):
        self.font_size = font_size
        self.font = Face(font_path)
        self.font.set_pixel_sizes(0, font_size)
        self.characters = {}
        self.frag_shader = shaders.compileShader(_frag_shader, GL_FRAGMENT_SHADER)
        self.vertex_shader = shaders.compileShader(_vertex_shader, GL_VERTEX_SHADER)
        self.shader = shaders.compileProgram(self.vertex_shader, self.frag_shader)

    def enableShader(self, char, background):
        texture = self.character_texture(char)
        glBindTexture(GL_TEXTURE_2D, texture)
        glActiveTexture(GL_TEXTURE0)
        shaders.glUseProgram(self.shader)
        uniform = glGetUniformLocation(self.shader, "tex")
        backgroundUniform = glGetUniformLocation(self.shader, "backgroundColor")
        #glUniform1i(uniform, texture)
        glUniform4fv(backgroundUniform, 1, background)
        glUniform1i(uniform, 0)

    def disableShader(self):
        shaders.glUseProgram(0)

    class Character:
        def __init__(self, font, x):
            self.font = font 
            self.letter = x
            self.font.load_char(x, FT_LOAD_RENDER)
            self.glyph   = self.font.glyph
            self.bitmap  = self.glyph.bitmap
            self.size    = self.bitmap.width, self.bitmap.rows
            self.bearing = self.glyph.bitmap_left, self.glyph.bitmap_top 
            self.advance = self.glyph.advance.x
            self.tex = None

        def texture(self):
            if self.tex is None:
                self.tex = glGenTextures(1)
                glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, self.tex)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
                ###glTexImage2D(GL_TEXTURE_2D, 0, GL_R8, self.size[0], self.size[1], 0, GL_RED, GL_UNSIGNED_BYTE, self.bitmap.buffer) 
                ###glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, self.size[0], self.size[1], 0, GL_RED, GL_UNSIGNED_BYTE, self.bitmap.buffer) 
                glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, self.size[0], self.size[1], 0, GL_ALPHA, GL_UNSIGNED_BYTE, self.bitmap.buffer) 
                glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
                glBindTexture(GL_TEXTURE_2D, 0) 
            return self.tex

    def character(self, x):
        if x not in self.characters:
            self.characters[x] = Text.Character(self.font, x)
        return self.characters[x]
        
    def character_texture(self, x):
        return self.character(x).texture()
