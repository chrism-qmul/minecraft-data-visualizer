import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import string
import shapes
import util
import camera
from text import Text
import numpy as np
from collections import Counter

color_name_to_rgb = {"green": (0,1,0,1),
    "red": (1,0,0,1),
    "blue": (0,0,1,1),
    "yellow": (1, 1, 0, 1),
    "orange": (1,0.5,0,1),
    "purple": (0.5,0,0.5,1),
    "unknown":(0.5,0.5,0.5,1)}

font_path = "/Library/Fonts/Arial Unicode.ttf"
#font_path= "env/lib/python3.9/site-packages/pygame/freesansbold.ttf"

class App:
    def __init__(self, points, starting_step):
        pygame.init()
        pygame.display.set_caption('ARCIDUCA: Minecraft world reconstruction')
        self.dimensions = []
        self.textures = []
        self.points = points
        self.point_index = 0
        self.show_original = True
        self.lights = True
        self.show_world = True
        self.screen = pygame.display.set_mode(self.display, DOUBLEBUF|OPENGL)
        print("VERSION",glGetString(GL_VERSION))
        print("SHADER LANGUAGE VERSION",glGetString(GL_SHADING_LANGUAGE_VERSION))
        self._setup_opengl()
        self.text = Text(font_path, 200)
        self.change_dialog_step(starting_step)

    def _setup_opengl(self):
        self.fbo = glGenFramebuffers(1)
        #glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fbo)
        glLight(GL_LIGHT0, GL_POSITION,  (10, 5, 5, 1)) # point light from the left, top, front
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
        glEnable(GL_DEPTH_TEST)

    def write_pixels(self, path):
        im = glReadPixels(0,0,*self.display, GL_BGR, GL_FLOAT)
        im = np.frombuffer(im, np.float32)
        im.shape = self.display[1], self.display[0], 3
        im = im[::-1, :]*255
        util.write_image(im, path)

    @property
    def display(self):
        if len(self.dimensions) > 0:
            return self.dimensions[0]
        else:
            return (1366,745)
            #return (1376,0)

    def _load_images(self):
        if "view" in self.current_point:
            paths = [self.current_point['view']]
            self.textures = glGenTextures(len(paths)+1)
            self.dimensions = []
            for texture, path in zip(self.textures, paths):
                print("path", path)
                im = util.load_texture(path)
                if im is not None:
                    self.dimensions.append((im.shape[1], im.shape[0]))

                    glBindTexture(GL_TEXTURE_2D, texture)
                    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                    glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, im.shape[1], im.shape[0], 0, GL_RGB, GL_UNSIGNED_BYTE, im)
            self.screen = pygame.display.set_mode(self.display, DOUBLEBUF|OPENGL)

    def toggle_original(self):
        self.show_original = not self.show_original

    def toggle_world(self):
        self.show_world = not self.show_world

    def toggle_lights(self):
        self.lights = not self.lights

    @property
    def current_step(self):
        return self.point_index

    def change_dialog_step(self, change):
        new_index = self.point_index + change
        old_point_index = self.point_index
        self.point_index = max(0, min(new_index, len(self.points)-1))
        if self.point_index == old_point_index:
            return False
        print("Changed: ", self.point_index)
        self._load_images()
        print(self.display)
        self.camera_to_agent_position()
        return True

    def next_dialog_step(self):
        return self.change_dialog_step(1)

    def prev_dialog_step(self):
        return self.change_dialog_step(-1)

    @property
    def current_point(self):
        return self.points[self.point_index]

    @property
    def current_world(self):
        return self.current_point['world']

    @property
    def current_builder_position(self):
        return self.current_point['builder_position']

    def move_camera(self, x=0, y=0, z=0, yaw=0, pitch=0):
        self.camera.move(x=x, y=y, z=z, yaw=yaw, pitch=pitch)
        print(self.camera)
        self.camera.apply()

    def reset_camera(self, x, y, z, yaw, pitch):
        width, height = self.display
        self.camera = camera.Camera(x=x,y=y,z=z,width=width,height=height,pitch=pitch,yaw=yaw)
        print(self.camera)
        self.camera.apply()

    def camera_to_agent_position(self):
        self.reset_camera(**self.current_builder_position)

    def front_camera(self):
        self.reset_camera(x=0, y=0, z=10, pitch=0, yaw=-90)

    def top_camera(self):
        self.reset_camera(x=0,y=10,z=0,pitch=-90,yaw=-90)

    def draw_floor(self):
        if self.lights and self.show_world:
            with shapes.glmatrix():
                glRotatef(-90,0,0,0)
                glTranslate(-5,-5,0)
                glTranslate(0.5,0.5,-0.5)
                shapes.plane(11, 11, fill=(1,1,1,0.5), stroke=(0,0,0,1))

    def draw_world(self):
        counts = Counter()
        if self.show_world:
            with shapes.glmatrix():
                for i,(box,color) in enumerate(self.current_world):
                    letter = (string.ascii_letters + string.digits)[counts[color]]
                    counts[color] += 1
                    with shapes.glmatrix():
                        glTranslatef(*box)
                        if self.lights:
                            #shapes.cube(fill=color, stroke=(0,0,0,1), stroke_width=2)
                            #glEnable(GL_BLEND)
                            #glBlendFunc(GL_SRC_ALPHA, GL_CONSTANT_COLOR)
                            #glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                            #glBlendColor(*color)
                            #glBlendEquation(GL_FUNC_SUBTRACT)
                            #shapes.cube(fill=(0,0,1,0.5))
                            #shapes.cube(fill=color, texture=self.text.character_texture(letter))
                            #shapes.cube(texture=self.text.character_texture(letter))
                            #shapes.cube(fill=color,texture=self.circle)
                            #self.text.enableShader(letter, color) 
                            #shapes.cube(fill=(1,0,0,1),texture=self.text.character_texture(letter))#, stroke_width=2)
                            #shapes.cube(fill=(1,0,0,1),texture=self.text.character_texture(letter))#, stroke_width=2)
                            #shapes.cube(stroke_width=2)
                            shapes.text_cube(color_name_to_rgb[color],(0.9,0.9,0.9,1),self.text.character(letter))
                            #self.text.disableShader()
                            #shapes.cube()
                        else:
                            shapes.cube(fill=(1,1,1,1))

    def draw_original(self):
        if len(self.textures) > 0 and self.show_original:
            glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fbo)
            glFramebufferTexture2D(GL_READ_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.textures[0], 0);
            glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);
            width, height = self.display
            glBlitFramebuffer(0, 0, width, height, 0, 0, width, height, GL_COLOR_BUFFER_BIT, GL_NEAREST);
            glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)

    def draw_axis(self):
        if self.lights:
            glLoadIdentity()
            shapes.axis()

    def draw(self):
        glClearColor(0.67,0.84,0.9,1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        #glEnable(GL_MULTISAMPLE)
        if self.lights:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

            glShadeModel(GL_SMOOTH)
            #glDepthFunc(GL_LESS)

        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        #glEnable(GL_BLEND)
        self.draw_original()
        self.draw_floor()
        self.draw_world()
        self.draw_axis()
        #green=(0,1,0,0.5)
        #letter = self.text.character_texture("X")
        #shapes.text_square((1,1,0,1),(0.9,0.9,0.9,1),self.text.character("X"))
        #shapes.square(texture=self.circle)
        #shapes.square(texture=letter)

       # glDisable(GL_BLEND)

        if self.lights:
            glDisable(GL_LIGHT0)
            glDisable(GL_LIGHTING)
            glDisable(GL_COLOR_MATERIAL)


    def run_to_file(self, path):
        self.show_original = False
        self.draw() 
        pygame.time.wait(10)
        self.write_pixels(path)
        #pygame.display.flip()

    def run(self):
        while True:
            # CONTINUOUS ACTIONS
            shift_pressed = lambda: pygame.key.get_mods() & pygame.KMOD_SHIFT
            pressed_keys = pygame.key.get_pressed()
            if (pressed_keys[pygame.K_SPACE]): #reset
                self.camera_to_agent_position()
            if (pressed_keys[pygame.K_RIGHT] and shift_pressed()) or (pressed_keys[pygame.K_d] and not shift_pressed()): #right
                self.move_camera(x=0.1)
            if (pressed_keys[pygame.K_LEFT] and shift_pressed()) or (pressed_keys[pygame.K_a] and not shift_pressed()): #left
                self.move_camera(x=-0.1)
            if (pressed_keys[pygame.K_UP] and shift_pressed()): #up
                self.move_camera(y=0.1)
            if (pressed_keys[pygame.K_DOWN] and shift_pressed()): #down
                self.move_camera(y=-0.1)
            if (pressed_keys[pygame.K_RIGHT] and not shift_pressed()): #pan right
                self.move_camera(yaw=2)
            if (pressed_keys[pygame.K_LEFT] and not shift_pressed()): #pan left 
                self.move_camera(yaw=-2)
            if (pressed_keys[pygame.K_UP] and not shift_pressed()): #pan up
                self.move_camera(pitch=2)
            if (pressed_keys[pygame.K_DOWN] and not shift_pressed()): #pan down
                self.move_camera(pitch=-2)
            if pressed_keys[pygame.K_w]: #forward
                self.move_camera(z=-0.1)
            if pressed_keys[pygame.K_s]: #backward
                self.move_camera(z=0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                # DISCRETE ACTIONS
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFTBRACKET:
                        self.prev_dialog_step()
                    if event.key == pygame.K_RIGHTBRACKET:
                        self.next_dialog_step()
                    if event.key == pygame.K_1:
                        print("switching to front cam! (from south)")
                        self.front_camera()
                    if event.key == pygame.K_2:
                        print("switching to top cam!")
                        self.top_camera()
                    if event.key == pygame.K_m:
                        self.toggle_original()
                    if event.key == pygame.K_h:
                        self.toggle_world()
                    if event.key == pygame.K_l:
                        self.toggle_lights()
            self.draw()
            pygame.display.flip()
            #pygame.display.update()
            pygame.time.wait(10)
