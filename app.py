import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import shapes
import util
import camera

class App:
    def __init__(self, points):
        pygame.init()
        pygame.display.set_caption('ARCIDUCA: Minecraft world reconstruction')
        self.dimensions = []
        self.textures = []
        self.points = points
        self.point_index = 0
        self.show_original = True
        self.lights = True
        self.show_world = True
        pygame.display.set_mode(self.display, DOUBLEBUF|OPENGL)
        self._setup_opengl()
        self.change_dialog_step(0)

    def _setup_opengl(self):
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_READ_FRAMEBUFFER, fbo)

        glLight(GL_LIGHT0, GL_POSITION,  (10, 10, 10, 1)) # point light from the left, top, front
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
        glEnable(GL_DEPTH_TEST)

    @property
    def display(self):
        if len(self.dimensions) > 0:
            return self.dimensions[0]
        else:
            return (1376,745)

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
            pygame.display.set_mode(self.display, DOUBLEBUF|OPENGL)

    def toggle_original(self):
        self.show_original = not self.show_original

    def toggle_world(self):
        self.show_world = not self.show_world

    def toggle_lights(self):
        self.lights = not self.lights

    def change_dialog_step(self, change):
        new_index = self.point_index + change
        self.point_index = max(0, min(new_index, len(self.points)-1))
        self._load_images()
        self.camera_to_agent_position()

    def next_dialog_step(self):
        self.change_dialog_step(1)

    def prev_dialog_step(self):
        self.change_dialog_step(-1)

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
        if self.show_world:
            with shapes.glmatrix():
                for box in self.current_world:
                    with shapes.glmatrix():
                        glTranslatef(*box)
                        if self.lights:
                            shapes.cube(fill=(0.6,0.6,0.6,1), stroke=(0,0,0,1), stroke_width=2)
                        else:
                            shapes.cube(fill=(1,1,1,1))

    def draw_original(self):
        if len(self.textures) > 0 and self.show_original:
            glFramebufferTexture2D(GL_READ_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.textures[0], 0);
            glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);
            width, height = self.display
            glBlitFramebuffer(0, 0, width, height, 0, 0, width, height, GL_COLOR_BUFFER_BIT, GL_NEAREST);

    def draw_axis(self):
        if self.lights:
            glLoadIdentity()
            shapes.axis()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        if self.lights:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

            glShadeModel(GL_SMOOTH)
            glDepthFunc(GL_LESS);

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glEnable(GL_BLEND)

        self.draw_original()
        self.draw_world()
        self.draw_floor()
        self.draw_axis()

        glDisable(GL_BLEND)

        if self.lights:
            glDisable(GL_LIGHT0)
            glDisable(GL_LIGHTING)
            glDisable(GL_COLOR_MATERIAL)

        pygame.display.flip()

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
            pygame.time.wait(10)
