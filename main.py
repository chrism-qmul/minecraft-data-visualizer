import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import cube
from math import radians, cos, sin
import numpy as np
import data
import cv2


"""
minecraft coordinate system
https://minecraft.fandom.com/wiki/Coordinates

world block coordinates are the lower northwest corner of the block
+z is south
+y is up
+x is east

(this seems to be the same as OpenGL)

"""


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
        return v
    return v / norm

SQRT2 = 2 ** .5
render_distance_chunks = 12

def load_images(paths):
    textures = glGenTextures(len(paths)+1)
    dimensions = []
    print(textures)
    for texture, path in zip(textures, paths):
        print("path", path)
        try:
            im = cv2.imread(path)
            print("loaded img", im.shape)
            dimensions.append((im.shape[1], im.shape[0]))
            im = cv2.flip(im, 0)
            im = cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
            im = im.astype(np.float32)
        except Exception:
            print("unable to load image @ {}".format(path))
            return

        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1);

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, im.shape[1], im.shape[0], 0, GL_RGB, GL_UNSIGNED_BYTE, im)
    return textures, dimensions

class Camera:
    def __init__(self, width, height, x, y, z, yaw=-90.0, pitch=0.0, world_up=None):
        self.position = np.array([x, y, z])
        self.world_up = world_up or np.array([0,1,0])
        self.width = width
        self.height = height
        self.yaw = yaw
        self.pitch = pitch

    @property
    def front(self):
        return np.array([cos(radians(self.yaw)) * cos(radians(self.pitch)),\
                         sin(radians(self.pitch)),\
                         sin(radians(self.yaw)) * cos(radians(self.pitch))])

    @property
    def right(self):
        return normalize(np.cross(self.front, self.world_up))

    @property
    def up(self):
        return normalize(np.cross(self.right, self.front));

    def apply(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70, self.width/float(self.height or 1), .05, (render_distance_chunks * 16) * SQRT2)
        center = self.position + self.front
        gluLookAt(self.position[0], self.position[1], self.position[2],\
                  center[0], center[1], center[2],\
                  self.up[0], self.up[1], self.up[2])
        glMatrixMode(GL_MODELVIEW)

def draw_world(world, fill=None, stroke=None, texture=None):
    for box in world:
        x, y, z = box
        glPushMatrix()
        #glScalef(5.5,5.5,5.5)
        #glScalef(0.5,0.5,0.5)
        glTranslatef(x, y, z)
        #glTranslatef(0.5, 0.5, 0.5)
        #glScalef(x, y, z)
        cube.draw(fill, stroke, 2)
        #cube.draw(texture=texture)
        glPopMatrix()


def convert_point(point):
    x = point.get("BuilderPosition").get("X")
    y = point.get("BuilderPosition").get("Y")+0.56
    z = point.get("BuilderPosition").get("Z")#-.85#*-1#*-1-1.5
    yaw = point.get("BuilderPosition").get("Yaw")+90#-180
    pitch = point.get("BuilderPosition").get("Pitch")*-1
    world = [(xyz['X'], xyz['Y']-1, xyz['Z']) for xyz in [p['AbsoluteCoordinates'] for p in point['BlocksInGrid']]]
    return {"builder_position": {"x": x, "y": y, "z": z, "yaw": yaw, "pitch": pitch}, "world": world, "view": point.get("builder_view")}

def display_points(points):
    pygame.init()
    display = (1376,745)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption('ARCIDUCA: Minecraft world reconstruction')
    #pygame.display.set_icon(None)

    point_index = 0

    def get_player_position(point):
        x = point["builder_position"]["x"]
        y = point["builder_position"]["y"]
        z = point["builder_position"]["z"]
        yaw = point["builder_position"]["yaw"]
        pitch = point["builder_position"]["pitch"]
        return x, y, z, yaw, pitch

    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_READ_FRAMEBUFFER, fbo)

    glLight(GL_LIGHT0, GL_POSITION,  (5, 5, 5, 1)) # point light from the left, top, front
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
    glEnable(GL_DEPTH_TEST)

    shift_pressed = lambda: pygame.key.get_mods() & pygame.KMOD_SHIFT

    point = points[point_index]
    x, y, z, yaw, pitch = get_player_position(point)
    world = point['world']
    print("builder views",point['view'])
    print(point)
    textures = []
    dimensions = []
    if "view" in point:
        textures, dimensions = load_images((point['view'],))
        if dimensions:
            display = dimensions[0]
        pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    print(textures)

    show_original = True
    lights = True

    while True:
        builder_cam = Camera(width=display[0], height=display[1], x=x, y=y, z=z, yaw=yaw, pitch=pitch, world_up=None)
        builder_cam.apply()
        pressed_keys = pygame.key.get_pressed()
        if (pressed_keys[pygame.K_SPACE]): #reset
            x, y, z, yaw, pitch = get_player_position(point)
        if (pressed_keys[pygame.K_RIGHT] and shift_pressed()) or (pressed_keys[pygame.K_d] and not shift_pressed()): #right
            x += 0.1 
        if (pressed_keys[pygame.K_LEFT] and shift_pressed()) or (pressed_keys[pygame.K_a] and not shift_pressed()): #left
            x -= 0.1 
        if (pressed_keys[pygame.K_UP] and shift_pressed()): #up
            y += 0.1 
        if (pressed_keys[pygame.K_DOWN] and shift_pressed()): #down
            y -= 0.1 
        if (pressed_keys[pygame.K_RIGHT] and not shift_pressed()): #pan right
            yaw = (yaw + 2) % 360
        if (pressed_keys[pygame.K_LEFT] and not shift_pressed()): #pan left 
            yaw = (yaw - 2) % 360
        if (pressed_keys[pygame.K_UP] and not shift_pressed()): #pan up
            pitch = (pitch + 2) % 360
        if (pressed_keys[pygame.K_DOWN] and not shift_pressed()): #pan down
            pitch = (pitch - 2) % 360
        if pressed_keys[pygame.K_w]: #forward
            z -= 0.1 
        if pressed_keys[pygame.K_s]: #backward
            z += 0.1 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            print("x:{}, y:{}, z:{}, pitch: {}, yaw: {}, world: {}".format(x, y, z, pitch, yaw, world))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFTBRACKET:
                    point_index = max(point_index - 1, 0)
                    point = points[point_index]
                    x, y, z, yaw, pitch = get_player_position(point)
                    world = point['world']
                    textures, dimensions = load_images([point['view']])
                    if dimensions:
                        print("display", display)
                        display = dimensions[0]
                        pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
                if event.key == pygame.K_RIGHTBRACKET:
                    point_index = min(len(points)-1, point_index + 1)
                    point = points[point_index]
                    world = point['world']
                    x, y, z, yaw, pitch = get_player_position(point)
                    textures, dimensions = load_images([point['view']])
                    if dimensions:
                        display = dimensions[0]
                        print("display", display)
                        pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
                if event.key == pygame.K_1:
                    print("switching to front cam! (from south)")
                    x, y, z = 0, 0, 10
                    pitch = 0
                    yaw = -90
                if event.key == pygame.K_2:
                    print("switching to top cam!")
                    x, y, z = 0, 10, 0
                    pitch = -90
                    yaw = -90
                if event.key == pygame.K_m:
                    show_original = not show_original
                if event.key == pygame.K_l:
                    lights = not lights
    
        #glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        if lights:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

            glShadeModel(GL_SMOOTH)
            glDepthFunc(GL_LESS);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glEnable(GL_BLEND)
      #glTranslatef(5, 0, 5)
      #cube.draw()
        #glEnable(GL_TEXTURE_2D)

        with cube.glmatrix():
            #glTranslatef(0,-.55,0)
            if len(textures) > 0 and show_original:
                glFramebufferTexture2D(GL_READ_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, textures[0], 0);
                glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);
                width, height = display
                if show_original:
                    glBlitFramebuffer(0, 0, width, height, 0, 0, width, height, GL_COLOR_BUFFER_BIT, GL_NEAREST);
            with cube.glmatrix():
                if lights:
                    draw_world(world,fill=(0.6,0.6,0.6,1), stroke=(0,0,0,1))
                else:
                    draw_world(world, fill=(1,1,1,1))
            #floor
            with cube.glmatrix():
                glRotatef(-90,0,0,0)
                glTranslate(-5,-5,0)
                glTranslate(0.5,0.5,-0.5)
                cube.plane(11, 11, fill=(1,1,1,0.5), stroke=(0,0,0,1))

            #px, py, pz, pyaw, ppitch = get_player_position(point)
            #with cube.glmatrix():
                #glScalef(0.3,0.3,0.3)
            #    glRotatef(ppitch,pyaw,0,0)
            #    glTranslatef(px, py, pz)
            #    cube.draw(fill=(1,0,1,1))
            #cube.draw(fill=(1,0,0,1))
            glLoadIdentity()
            cube.axis()
        glDisable(GL_BLEND)
        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)

        pygame.display.flip()
        pygame.time.wait(10)

def is_valid_point(point):
    return point.get("BuilderPosition") and point.get

#print(list(data.load(data.log_path))[-1])
points = [convert_point(p) for p in data.load(data.log_path) if is_valid_point(p)]
#point = convert_point(data_stream[10])
#print(data_stream[-1])
#point = convert_point(data_stream[-5])
#load_image(point['view'])

#print(point)
#print("builder_view", points.get('view'))


test_point = [{"builder_position": {"x": 0, "y": 2, "z":10, "yaw": -90.0, "pitch": -10}, "world": [(0,0,0),(1,1,0),(2,2,0),(1,3,0),(0,4,0),(0,2,0)]}]

display_points(points)
#display_point(test_point)
