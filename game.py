#!/usr/bin/env python
root="/Users/Shared/Projects/PyGame/Samuel Projects/2014-/Plane Shooter/Resources/"

import pygame, pygame.locals
import sys
import random
from texture import *

random.seed(1)
pygame.init()
flag = pygame.locals.OPENGL | pygame.locals.DOUBLEBUF
screen = pygame.display.set_mode((1000,500),flag)
max_x=1000
max_y=500
drawDistance=7
gameSpeed=1
bulletSpeed=10
planeSpeed=2.5
imgStart=root+"PlaneImgs/Front/front"
enemyImgs=[Texture(imgStart+"normal.png",False),Texture(imgStart+"bankleft.png",False),Texture(imgStart+"bankright.png",False)]
imgStart=root+"PlaneImgs/Back/back"
playerImgs=[Texture(imgStart+"normal.png",False),Texture(imgStart+"bankleft.png",False),Texture(imgStart+"bankright.png",False)]
opengl_init(max_x,max_y)
def collideNoClass(a,b):
    if a[0]+a[1]<b[0]:
        return False
    if a[0]>b[0]+b[2]:
        return False
    if a[1]+a[3]<b[1]:
        return False
    if a[1]>b[1]+b[3]:
        return False
    if a[4]-1==b[4]:
        return True
#a classes
#b base classes
class thing:
    def __init__(self,x,y,color=(255,0,0)):
        self.color=color
        self.pos=[x,y]
        self.drawPos=self.pos
        #These always need to be set by the player
        self.width=0
        self.height=0
        self.exists=True
        self.distance=1
        self.speedCounter=1
        self.speed=500
        self.maxDistance=25
        self.scale=0
        self.exploding=False
        self.health=10
        self.loops=1
    def draw(self,distance):
        if self.exists:
            return True
    def loop(self):
        if self.distance<=0:
            self.exists=False
        if self.exists:
            #self.checkDistance()
            self.draw(self.distance)
            return True
        return False
    def checkDistance(self,increment):
        self.speedCounter+=gameSpeed
        if(self.speedCounter>=self.speed):
            self.distance-=increment
            self.speedCounter=1
            self.loops+=1
            if self.distance<0 or self.exploding==True:
                self.exists=False
                return False
            return True
    def collide(self,x,y,w,h,distance,hitOnCollide):
        if(collideNoClass([self.pos[0],self.pos[1],self.width,self.height,self.distance],[x,y,w,h,distance]) and hitOnCollide):
            self.loseHealth()
    def loseHealth(self):
        self.health-=1
    def die(self):
        self.exists=False
class imageThing(thing):
    def __init__(self,x=0,y=0,w=0,h=0,texturePath=root+"sky_0.png",explosionPath=root+"explosion.png",distance=0):
        thing.__init__(self,x,y,(0,0,0))
        self.image=Texture(texturePath,False)
        self.explosionImage=Texture(explosionPath,False)
        self.newImage=self.image
        (self.originalWidth,self.originalHeight)=(self.image.w,self.image.h)
        self.width=w
        self.height=h #*-(1-maxDistance-distance)
        self.explodeOnCollide=False
        self.distance=distance
        self.maxDistance=distance
        self.moveHorizontally=True
        self.loops=1
    def draw(self,distance):
        hasGrown=thing.checkDistance(self,1)
        if thing.draw(self,distance):
            self.image.add_to_queue(self.pos[0],self.pos[1],distance)
            return True

        return False
    def explode(self):
        self.image=self.explosionImage
        (self.originalWidth,self.originalHeight)=(self.image.w,self.image.h)
        self.draw(self.distance)
        self.exploding=True
        self.speedCounter=0
        self.speed=20
    def die(self):
        self.explode()
class Bullet(thing):
    def __init__(self,pos,destPos,distance,destDistance,isPlayer):
        thing.__init__(self,pos[0],pos[1],(0,0,0))
        self.pos=[pos[0],pos[1]]
        self.destPos=[destPos[0],destPos[1]]
        self.distance=distance
        self.destDistance=destDistance
        self.speed=5
        self.increment=1
        if(destDistance>distance):
            self.increment=-1
        elif(destDistance==distance):
            self.exists=False
        self.laserSound=pygame.mixer.Sound(root+"laser.wav")
        self.laserSound.set_volume(0.1)
        self.laserSound.play()
        self.isPlayer=isPlayer
        if not isPlayer:
            self.speed=20
    def loop(self):
        global drawDistance
        if(self.exists):
            if(self.pos==self.destPos) or self.distance>=drawDistance:
                Game.bulletHit(self.pos,self.distance,self.isPlayer)
                self.exists=False
                return
            thing.checkDistance(self,self.increment)
            self.move()
            self.draw()
    def draw(self):
        draw_line(self.pos[0],self.pos[1],self.destPos[0],self.destPos[1],(1,0.9,0.9),10)
    def move(self):
        global gameSpeed,bulletSpeed
        self.pos[0]-=(self.pos[0]-self.destPos[0])/(gameSpeed*bulletSpeed)
        self.pos[1]-=(self.pos[1]-self.destPos[1])/(gameSpeed*bulletSpeed)
            
#b fighter classes
class plane(imageThing):
    def __init__(self,x,y,w,h,distance,moveSpeed,imgs):
        imageThing.__init__(self,x=x,y=y,w=w,h=h,texturePath=imgStart+"normal.png",distance=distance)
        self.width=w
        self.height=h
        self.speed=100
        self.speedCounter=1
        #self.scale=1
        self.distance=distance
        self.moveSpeed=moveSpeed
        self.imgs=imgs
    def loop(self):
        if self.exists:
            self.pos=[int(self.pos[0]),int(self.pos[1])]
            self.checkDistance(1)
            #self.scale=self.distance

            if self.distance==1:
                self.speed=500
            self.draw(self.distance+2)
        if (self.distance<=0 or self.health<=0) and self.exists:
            self.exists=False
            self.die()
    def bank(self,bankLeft):
        global gameSpeed
        if bankLeft:
            self.image=self.imgs[1]

            self.pos[0]+=gameSpeed*self.moveSpeed
        else:
            self.image=self.imgs[2]

            self.pos[0]-=gameSpeed*self.moveSpeed

    def pull(self,pullUp):
        global gameSpeed
        if pullUp:
            self.pos[1]+=gameSpeed*self.moveSpeed

        else:
            self.pos[1]-=gameSpeed*self.moveSpeed
        self.wingThickness=10

class balloon(imageThing):
    def __init__(self,x,y,distance):
        imageThing.__init__(self,x,y,50,50,root+"Resources/balloon_blue.png", root+"Resources/explosion.png",distance)
        self.speed=100
    #def draw(self):
    #    if(imageThing.draw(self)):
    #        pygame.draw.lines(screen, (0,0,0), False, [(self.drawPos[0],self.drawPos[1]),(self.drawPos[0],500)], self.scale/2)
    
#b fighter extention
class enemy(plane):
    def __init__(self,x,y,w,h,distance):
        global planeSpeed,enemyImgs
        plane.__init__(self,x,y,w,h,distance,planeSpeed,enemyImgs)
        self.health=5
    def loop(self):
        global Game
        if self.exists:
            self.ai()
            plane.loop(self)
            
    def ai(self):
        global Game
        bankNum=random.randint(0,70)
        pullNum=random.randint(0,70)
        shootNum=random.randint(0,50)
        if pullNum==30:
            self.pull(True)
        elif pullNum==60:
            self.pull(False)
        if bankNum==30:
            self.bank(True)
        elif bankNum==60:
            self.bank(False)
        if(shootNum==50):
            self.shootAtPlayer()
    def shootAtPlayer(self):
        global Game
        newBullet=Bullet(self.pos,Game.player.pos,self.distance,1,False)
        Game.bullets.append(newBullet)
    def die(self):
        global Game
        #self.explode()
        #Game.addEnemy()
class player(plane):
    def __init__(self,x,y,distance):
        global planeSpeed,playerImgs
        plane.__init__(self,x,y,50,50,distance,-planeSpeed,playerImgs)
        self.health=100
#b Terrain
class terrain(imageThing):
    def __init__(self,x,y,rects):
        imageThing.__init__(self,x,y,150,84,root+"hill.png",root+"hill.png",10)
        self.rects=rects
        self.health=-1 
        self.speed=30
        self.moveHorizontally=False
    def collide(self,x,y,w,h,distance,hurtOnCollide):
        #for rect in self.rects:
        #    newRect=[rect[0]+self.pos[0],rect[1]+self.pos[1],rect[2]*self.scale,rect[3]*self.scale,self.distance]
        #    if collideNoClass(newRect,[x,y,w,h,distance]):
        #        return True
        return False
    def draw(self,distance):
        imageThing.draw(self,distance)
        for rect in self.rects:
            pygame.draw.rect(screen,(0,0,0),(rect[0]+self.pos[0],rect[1]+self.pos[1],rect[2],rect[3]),5)
#a Game Class
class game:
    def __init__(self):
        self.enemies=[]
        self.terrain=[terrain(100,500,[[0,0,50,50]])]
        self.player=player(250,250,1)
        self.player.distance=10
        self.playerPos=[500,250]
        self.moveSpeed=5
        self.player.maxDistance=1
        self.pressedButtons=pygame.key.get_pressed()
        self.background=Texture(root+"sky_0.png",False)
        self.bullets=[]
        self.reticule=[0,0]
        for i in range(1):
            self.addEnemy()
    def loop(self):
        global gameSpeed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 pygame.quit(); sys.exit();
            if event.type == pygame.MOUSEBUTTONUP:
                newBullet=Bullet(self.player.pos,self.reticule,1,10,True)
                self.bullets.append(newBullet)
        self.player.speedCounter=0
        self.pressedButtons=pygame.key.get_pressed()
        
        self.movePlayer()
        glEnable(GL_DEPTH_TEST)

        glClearColor(1,1,1, 1.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #self.draw()
        self.background.draw_background(500,250)
        mousePos=pygame.mouse.get_pos()
        self.reticule=[mousePos[0],mousePos[1]]
        #pygame.draw.circle(screen, (0,0,255),mousePos,10,0)
        
        for enemy in self.enemies:
            enemy.loop()
        for bullet in self.bullets:
            bullet.loop()
        for terrain in self.terrain:
            terrain.loop()
            if terrain.collide(self.player.pos[0],self.player.pos[1],self.player.width,self.player.height,self.player.distance,False):
                self.player.die()
                pygame.quit();sys.exit()
        self.player.loop()
        draw_all()
        if self.pressedButtons[pygame.K_h] and gameSpeed<1:
            glClearColor(1,1,1,1)
            gameSpeed=1
        elif self.pressedButtons[pygame.K_k] and gameSpeed==1:
            glClearColor(1,1,1,1)
            gameSpeed=0.25
        draw_text(str(self.player.health),0,0,(0,0,0))

    def addEnemy(self):
        newEnemy=enemy(random.randint(0,999),random.randint(0,499),50,50,random.randint(7,10))
        self.enemies.append(newEnemy)
    def movePlayer(self):
        
        if self.pressedButtons[pygame.K_a]:
             self.player.bank(True)
        elif self.pressedButtons[pygame.K_d]:
            self.player.bank(False)

        if self.pressedButtons[pygame.K_w]:
            self.player.pull(True)
        elif self.pressedButtons[pygame.K_s]:
            self.player.pull(False)

        if self.player.pos[0]<0:
            self.player.pos[0]=0
        elif self.player.pos[0]>max_x:
            self.player.pos[0]=max_x
        if self.player.pos[1]<0:
            self.player.pos[1]=0
        elif self.player.pos[1]>max_y:
            self.player.pos[1]=max_y
    def bulletHit(self,bulletPos,bulletDistance,isPlayer):
        if isPlayer:
            for enemy in self.enemies:
                if enemy.exists:
                    enemy.collide(bulletPos[0],bulletPos[1],25,25,enemy.distance-1,True)
        else:
            self.player.collide(bulletPos[0],bulletPos[1],50,50,self.player.distance-1,True)
    #def draw(self):
        
#a Base Loop
Game= game()
while True:
    pygame.display.set_caption("Dogfight")
    glClearColor(1,1,1,1)
    Game.loop()
    pygame.display.flip()
    

        
