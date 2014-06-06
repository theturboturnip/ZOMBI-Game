#!/usr/bin/env python

import pygame,pygame.locals,sys,random,topdowngame
from graphics import *
#from classes import *
from levels import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


random.seed(1)
pygame.init()

flag = pygame.locals.OPENGL | pygame.locals.DOUBLEBUF

screen = pygame.display.set_mode((1000,500),flag)
max_x=1000
max_y=500
pygame.display.set_caption("SHTEALTHHH")
opengl_init(max_x,max_y)
game=topdowngame.Game()
Mission=mission()
print "Loading level",Mission.levels[0].title
random.seed=1
game.load_level(Mission.levels[0])
while True:
    level_to_load=game.start()
    level_to_load=Mission.find_level(level_to_load)
    if level_to_load!=None:
        game.load_level(level_to_load)
    else:
        print "Doesnt exist"
        break


