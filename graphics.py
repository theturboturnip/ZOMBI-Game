#!/usr/bin/env python
import pygame,random
from OpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
draw_queue=[]
change_list=[]
def opengl_init(screenW,screenH):
    global scrW,scrH
    scrW,scrH=screenW,screenH
    #glEnable(GL_DEPTH_TEST)
    glClearColor(1,1,1,1)
    glClear(GL_COLOR_BUFFER_BIT,GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    set_ortho([0,0])

    #set textures
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    return True
def set_ortho(pos):
    global scrW,scrH
    glOrtho(pos[0],scrW,scrH,pos[1],0,1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def draw_floor(floor,color):
    draw_line(floor[0],floor[1],floor[0]+floor[2],floor[1],color,0)
def draw_vertical_line(x,y,a,b,(color1,color2,color3),thickness):
    glDisable(GL_TEXTURE_2D)
    glColor(color1,color2,color3)
    glBegin(GL_QUADS)
    glVertex(x,y)
    glVertex(x+thickness,y)
    glVertex(a+thickness,b)
    glVertex(a,b)
    glEnd()
    
def draw_line(x,y,a,b,(color1,color2,color3),thickness):
    #thickness/=2
    glDisable(GL_TEXTURE_2D)
    glColor(color1,color2,color3)
    glLineWidth(thickness)

    glBegin(GL_LINES)
    glVertex2d(x, y)
    glVertex2d(a, b)
    glEnd()

def draw_text(text,x,y,colour):
    glDisable(GL_TEXTURE_2D)
    glColor(colour[0],colour[1],colour[2])
    glRasterPos(x,y)
    font = GLUT_BITMAP_9_BY_15
    for ch in text:
        glutBitmapCharacter( font , ctypes.c_int( ord(ch) ) )
def draw_box((topleft,topright,bottomleft,bottomright),(color1,color2,color3)):
    glDisable(GL_TEXTURE_2D)
    glColor(color1,color2,color3)
    glBegin(GL_QUADS)
    glVertex(topleft[0],topleft[1])
    glVertex(topright[0],topright[1])
    glVertex(bottomright[0],bottomright[1])
    glVertex(bottomleft[0],bottomleft[1])
    glEnd()

class Texture(object):
    tex_kind=GL_TEXTURE_2D
    happened_once=False
    def __init__(self, src,flipped):
        self.happened_once=True

        self.n = 0
        self.flipped=flipped
        self.image = pygame.image.load(src)
        self.w, self.h = self.image.get_width(),self.image.get_height()
        texdata = pygame.image.tostring(self.image,"RGBA",0)
        self.texid = glGenTextures(1)

        glBindTexture(self.tex_kind, self.texid)
        glTexParameteri(self.tex_kind, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(self.tex_kind, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,self.w,self.h,0,GL_RGBA,GL_UNSIGNED_BYTE,texdata)
        self.distance=0
        self.coming_in=False
        #print >>sys.stderr,"inited texture %d.%s"%(self.texid, src)
        self.pixels=[]
        self.pxs_in_place=False
    def rot_center(self,image, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        texdata = pygame.image.tostring(rot_image,"RGBA",0)
        glBindTexture(self.tex_kind, self.texid)
        glTexParameteri(self.tex_kind, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(self.tex_kind, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,self.w,self.h,0,GL_RGBA,GL_UNSIGNED_BYTE,texdata)
    def come_in(self):
        self.coming_in=True
        for x in range(self.image.get_width()):
            for y in range(self.image.get_height()):
                new_px=[x,y,500,0]
                px_color=self.image.get_at((x,y))
                if (x == 10 and y ==30):
                    print px_color
                px_color[0]/=255
                px_color[1]/=255
                px_color[2]/=255
                px_color=(px_color[0],px_color[1],px_color[2])
                new_px.append(px_color)
                self.pixels.append(new_px)
    def draw(self,x,y,distance,angle=0):
        (self.x,self.y,self.distance)=(x,y,distance)
        self.rot_center(self.image,angle)
        if(self.distance<=0):
            return False
        scale=1.0/(self.distance)
        w = self.w * scale
        h = self.h * scale
        self.distance = -self.distance/100.0            
        #glColor(random.randint(0,1),random.randint(0,1),random.randint(0,1))
        glColor(1,1,1)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(self.tex_kind, self.texid)
        glBegin(GL_QUADS)
        flipped_num=0
        glTexCoord2f(0,0); glVertex3f(self.x,self.y,self.distance)
        glTexCoord2f(0,1); glVertex3f(self.x,self.y+h,self.distance)
        glTexCoord2f(1,1); glVertex3f(self.x+w,self.y+h,self.distance)
        glTexCoord2f(1,0); glVertex3f(self.x+w,self.y,self.distance)
        glEnd()

    def __repr__(self):
        return "Texture#(%f,%f,%f):(%f,%f,%s)"%(self.x,self.y,self.distance,self.w,self.h,str(self.texid))
