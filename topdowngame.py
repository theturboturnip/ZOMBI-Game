#!/usr/bin/env python
         
import time
import pygame, os,sys,music
import pygame.locals
from graphics import *
from OpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math import atan2,degrees,sqrt,pow,atan,sin,cos
import random
path = os.path.split(os.path.abspath(__file__))[0]
pygame.init()
flag = pygame.locals.OPENGL | pygame.locals.DOUBLEBUF

screen = pygame.display.set_mode((1000, 500), flag)
opengl_init(1000,500)

goal_img=Texture(path+"/Resources/Graphics/goal_star.png",False)
#a lines
class line:
    thickness=5
    type="line"
    is_wall=False
    def __init__(self,data):
        [[x,y],[destx,desty]]=data
        self.start=[x,y]
        self.end=[destx,desty]
        dist=[destx-x,desty-y]
        (self.m,self.c,self.length)=get_formula_of_line(self.start,self.end)
        self.angle=degrees(atan2(dist[0],dist[1]))
        if not self.is_wall:
            collision_data=self.collides_with_wall()
            if collision_data[0][0]:
                self.end=[collision_data[0][1],collision_data[0][2]]
    def recalculate_with_len(self,new_len):
        new_end=[0,0]
        try:
            new_end[0] = int(self.start[0] + (self.end[0] - self.start[0]) / self.length * new_len)
            new_end[1] = int(self.start[1] + (self.end[1] - self.start[1]) / self.length * new_len)
        except ZeroDivisionError:
            return self
        self.end=new_end
        self.length=new_len
        if not self.is_wall:
            collision_data=self.collides_with_wall()
            if collision_data[0][0]:
                self.end=[collision_data[0][1],collision_data[0][2]]
        return self
    def collides_with_box(self,box):
        lines=[]
        lines.append(line([ [box[0],box[1]] , [box[0]+box[2],box[1]] ]))
        lines.append(line([ [box[0]+box[2],box[1]] , [box[0]+box[2],box[1]+box[3]]]))
        lines.append(line([ [box[0]+box[2],box[1]+box[3]] , [box[0],box[1]+box[3]]]))
        lines.append(line([ [box[0],box[1]+box[3]] , [box[0],box[1]] ]))

        for line_data in lines:
            does_collide=self.intersects_with_line(line_data)
            if does_collide is not None:
                return does_collide
        return False
    def find_intersection(self,line_data):
        ld=[line_data.end[0]-line_data.start[0]+0.0,line_data.end[1]-line_data.start[1]+0.0]
        ls=(line_data.start[0]+0.0,line_data.start[1]+0.0)
        gd=[self.end[0]-self.start[0]+0.0,self.end[1]-self.start[1]+0.0]
        gs=(self.start[0]+0.0,self.start[1]+0.0)
        determinant=(gd[0]*ld[1]-gd[1]*ld[0])
        if not (-0.0001 < determinant < 0.0001):
            a=((gs[0]*gd[1]-gs[1]*gd[0])-(ls[0]*gd[1]-ls[1]*gd[0]))/-determinant
            b=((ls[0]*ld[1]-ls[1]*ld[0])-(gs[0]*ld[1]-gs[1]*ld[0]))/determinant
            P=[ls[0]+a*ld[0],ls[1]+a*ld[1]]
            return (a,b,P)
        return None
    def intersects_with_line(self,line_data):
        intersection = self.find_intersection(line_data)
        if intersection:
            (a,b,P)=intersection
            if (0 <= a <= 1) and (0 <= b <= 1):
                return P
        return None
    def collides_with_line(self,line_data):
        intersection = self.find_intersection(line_data)
        if intersection:
            (a,b,P)=intersection
            if (0 <= a <= 1) and (b > 0):
                return True,P[0],P[1]
        return False,0,0
    def collides_with_wall(self):
        global walls
        if not self.is_wall:
            for wall_data in walls:
                does_collide=self.collides_with_line(wall_data)
                if does_collide[0]:
                    return does_collide,wall_data
        return [False,0,0],None
    def collides_with_enemy(self,game):
        for enemy in game.enemies:
            if self.collides_with_box(enemy.specs):
                return [True,enemy]
        return [False,None]
    def collides_with_anything(self,game,count_player,count_enemies):
        hit_wall=self.collides_with_wall()
        hit_enemy=self.collides_with_enemy(game)
        hit_enemy[0]*=count_enemies
        hit_player=[self.collides_with_box(game.player.specs)*int(count_player),game.player]
        hit_human=hit_enemy
        if hit_player[0] and not hit_enemy[0]:
            hit_human=hit_player
        #elif not count_enemies:
        #    hit_human=[False,None]
        if hit_wall[0][0]:
            return hit_wall[0][0],hit_wall[1]
        if hit_human[0]:
            return hit_human
        return False,None
    def draw(self):
        draw_line(self.start[0],self.start[1],self.end[0],self.end[1],(0,0,0),self.thickness)
        
class wall(line):
    thickness=5
    is_wall=True


walls=[]
#a functions
def angle_between(angle1,angle2,angle3):
    if angle1<360 and angle1>270:
        if (angle3<360 and angle3>=angle1) or angle3<angle2:
            return True
    if angle3>angle1 and angle3<=angle2:
        return True
    return False
def get_formula_of_line(start,dest):
    dx=float(dest[0]-start[0])
    dy=float(dest[1]-start[1])
    if dx!=0:
        gradient=dy/dx
    else:
        gradient=0;
    extra=dest[1]-(gradient*dest[0])
    length=line_len(start,dest)
    return (gradient,extra,length)
def line_len(start,dest):
    return sqrt(((start[0]-dest[0])*(start[0]-dest[0]))+((start[1]-dest[1])*(start[1]-dest[1])))
def collide(a,b):
    if a[0]+a[2]<b[0]:
        return False
    if a[0]>b[0]+b[2]:
        return False
    if a[1]+a[3]<b[1]:
        return False
    if a[1]>b[1]+b[3]:
        return False
    return True
#a character class
class character:
    #b init
    def __init__(self,x,y,data_name,game):
        self.game=game
        self.pos=[x,y]           
        self.movement_keys=[pygame.K_w,pygame.K_s,pygame.K_a,pygame.K_d,pygame.K_LSHIFT]
        self.walk_speed=4
        self.crouch_speed=2
        self.move_speed=self.walk_speed
        self.angle=0
        self.previous_mouse_buttons=[]
        self.dead=False
        self.w=40
        self.h=40
        self.specs=[x,y,self.w,self.h]
        self.moving=False
        self.crouching=False
        self.arm_data=[0,0.25]
        self.load_data(data_name)
        self.pathfinding=True
        self.nodes=[]
    #b load_data
    def load_data(self, name):
        new_path=path+"/Resources/Characters/"+name
        self.head=Texture(new_path+"/head.png",False)
        self.rfoot=Texture(new_path+"/foot.png",False)
        self.lfoot=Texture(new_path+"/foot.png",True)
        self.rhand=Texture(new_path+"/hand.png",False)
        self.lhand=Texture(new_path+"/hand.png",True)
        color_data= open(new_path+"/color_data.txt", 'r')
        body_color_str=color_data.readlines()[1]
        self.body_color=(int(body_color_str[0]),int(body_color_str[2]),int(body_color_str[4]))
    #b should_aim
    def should_aim(self, mouse_buttons):
        return False
    #b drawing functions
    def draw(self):
        self.animate_arms()
        self.draw_body()
        self.draw_head()
    def rotate_pos(self,pixel_pos):
        def rad(a): return a/180.0*3.14159265
        # pixel_pos is relative to the centre of the character
        # the return value is relative to the top left of the screen
        return [cos(rad(self.angle))*(pixel_pos[0]) + sin(rad(self.angle))*(pixel_pos[1])+(self.pos[0]+(self.w/2)),
                cos(rad(self.angle))*(pixel_pos[1]) - sin(rad(self.angle))*(pixel_pos[0])+(self.pos[1]+(self.h/2))]
    def animate_arms(self):
        if self.moving:
            self.arm_data[0]+=(self.arm_data[1]*self.move_speed)
            if self.arm_data[0]>=self.h/2 or self.arm_data[0]<=-self.h/2:
                self.arm_data[1]=-self.arm_data[1]
        else:
            self.arm_data[0]=0.1
        r1=self.rotate_pos([self.w/2,0])
        r2=self.rotate_pos([self.w/2+((self.h/4)*int(self.crouching)),self.arm_data[0]])

        l1=self.rotate_pos([-self.w/2,0])
        l2=self.rotate_pos([-self.w/2-((self.h/4)*int(self.crouching)),-self.arm_data[0]])
        
        r=line([r1,r2])
        l=line([l1,l2])
        
        r.draw()
        l.draw()

    def draw_body(self):
        topleft=self.rotate_pos([-self.w/2,-self.h/2])
        topright=self.rotate_pos([self.w/2,-self.h/2])
        bottomleft=self.rotate_pos([-self.w/2,self.h/2])
        bottomright=self.rotate_pos([self.w/2,self.h/2])
        draw_box([topleft,topright,bottomleft,bottomright],self.body_color)
    def draw_head(self):
        head_pos=[self.pos[0]+self.w/2-10 , self.h/2-10+self.pos[1]]
        self.head.draw(head_pos[0],head_pos[1],0.5,angle=self.angle)
    #b loop
    def loop(self):
        self.bullet_pos=[self.pos[0]+20,self.pos[1]]
        self.move()
        if self.angle<0:
            self.angle+=360
        elif self.angle>360:
            self.angle-=360
        self.specs=[self.pos[0],self.pos[1],self.w,self.h]
        self.moving=self.move_speed!=0
    #b shoot
    def shoot(self,mouse_pos):
        bullet=line([self.bullet_pos,mouse_pos])
        bullet.recalculate_with_len(1200)
        hits_wall=bullet.collides_with_wall()
        if hits_wall[0]:
            mouse_pos=[hits_wall[1],hits_wall[2]]
        else:
            mouse_pos=bullet.end
            self.game.shot_fired(bullet,self)
        bullet.draw()
        return
    #get_shot
    def get_shot(self,bullet_specs):
        self.die()
        return True
    #b die
    def die(self):
        pass
    #b get_directional_buttons
    def get_directional_buttons(self,pressed_buttons):
        return {"up":False,"down":False,"left":False,"right":False},False
    #b move
    def move(self):
        pressed_buttons=pygame.key.get_pressed()
        mouse_buttons=pygame.mouse.get_pressed()
        self.mouse_pos=pygame.mouse.get_pos()
        self.angle=self.rotate_towards(self.mouse_pos)

        directional_buttons=self.get_directional_buttons(pressed_buttons)
        self.crouching=directional_buttons[1]
        directional_buttons=directional_buttons[0]
        if self.should_aim(mouse_buttons) and self.should_shoot(mouse_buttons):
            self.shoot(self.mouse_pos)
        self.previous_mouse_buttons=mouse_buttons
        target_pos=[self.pos[0],self.pos[1]]
        if True in directional_buttons.values():
            if directional_buttons["up"]:
                target_pos[1]-=self.move_speed
                #self.angle=0
            elif directional_buttons["down"]:
                target_pos[1]+=self.move_speed
                #self.angle=180
            if directional_buttons["left"]:
                target_pos[0]-=self.move_speed
                """if self.angle==180:
                    self.angle=135
                elif self.angle==0:
                    self.angle=45
                else: 
                    self.angle=90"""
            elif directional_buttons["right"]:
                target_pos[0]+=self.move_speed
                """if self.angle==180:
                    self.angle=225
                elif self.angle==0:
                    self.angle=-45
                else:
                    self.angle=270"""
            if self.crouching:
                self.move_speed=self.crouch_speed
            else:
                self.move_speed=self.walk_speed
            self.go_towards(target_pos)
        else:
            self.move_speed=0
        self.previous_mouse_buttons=mouse_buttons
    #b make_nodes
    def get_node(self, target):
        node=[0,0]
        node_dist_list=[0,0]
        line_between = line([self.pos,target])
        interruption=line_between.collides_with_anything(self.game,False,True)
        if interruption[0]:
            if interruption[1].type=="wall":
                node[0]=interruption[1].change_len(-40)
                node[1]=interruption[1].change_len(interruption[1].len+40)
            else:
                return line_between.recalculate_with_len(self.move_speed).end
            node_dist_list[0]=line_dist(node1,target)
            node_dist_list[1]=line_dist(node2,target)
            node_to_check=node[0]
            if node_dist_list[0]>node_dist_list[1]:
                node_to_check=node[1]
            if line(self.pos,node_to_check).collides_with_wall[0]:
                if node_to_check==node[0]:
                    node_to_check=node[1]
                else:
                    node_to_check=node[0]
                if line(self.pos,node_to_check).collides_with_wall[0]:
                    return None
            return node_to_check
        else:
            return target
    #b go_towards
    def go_towards(self,target_pos):
        global walls
        if self.pathfinding:
            target_pos=self.get_node(target_pos)
        old_pos=self.pos
        line_between=line([self.pos,target_pos])
        line_between.recalculate_with_len(self.move_speed)
        new_specs=[line_between.end[0],line_between.end[1],self.w,self.h]
        old_specs=self.specs
        self.specs=new_specs
        if self.collides_with_enemy() or self.collides_with_wall(): 
            self.specs=old_specs
            return                                       
        self.pos=line_between.end
    #b collides_with_wall
    def collides_with_wall(self):
        global walls
        for wall in walls:
            if wall.collides_with_box(self.specs):
                return True
        return False
    #b should_shoot
    def should_shoot(self,mouse_buttons):
        return False
    #b rotate_towards
    def rotate_towards(self,target):
        difference=(target[0]-self.pos[0],target[1]-self.pos[1])
        return -degrees(atan2(difference[1],difference[0]))-90
    def collides_with_enemy(self):
        for enemy in self.game.enemies:
            if collide(self.specs,enemy.specs) and enemy!=self:
                return True
        return False
#a player
class player(character):
    type="player"
    pathfinding=False
    def get_directional_buttons(self,pressed_buttons):
        return {"up":pressed_buttons[self.movement_keys[0]],
                "down":pressed_buttons[self.movement_keys[1]],
                "left":pressed_buttons[self.movement_keys[2]],
                "right":pressed_buttons[self.movement_keys[3]]},pressed_buttons[self.movement_keys[4]]
    def should_shoot(self,mouse_buttons):
        if mouse_buttons[0] and not self.previous_mouse_buttons[0]:
            return True
        return False
    def should_aim(self,mouse_buttons):
        return True
    def shoot(self,mouse_pos):
        bullet=line([self.bullet_pos,mouse_pos])
        bullet.recalculate_with_len(60)
        self.game.shot_fired(bullet,self)
    def collides_with_enemy(self):
        return False
#a enemy
class enemy(character):
    type="enemy"
    radius=200
    fov=90
    pathfinding=True
    move_speed=1
    def __init__(self,x,y,weapon,game,angle,player):
        character.__init__(self,x,y,weapon,game)
        self.angle=angle
        self.player=player
        self.could_see=False
        self.suspicion_level=0
        self.is_suspicious=False
        self.suspicion_point=self.pos
    def can_see_player(self,mouse_buttons):
        self.distance=sqrt(pow((self.player.pos[0]-self.pos[0]),2)+pow((self.player.pos[1]-self.pos[1]),2))
        if self.distance<self.radius:
            angle1=self.angle-(self.fov/2)
            angle2=self.angle+(self.fov/2)
            if angle1<0:
                angle1+=360
            if angle2>360:
                angle2-=360

            angle3=self.rotate_towards(self.player.pos)
            if angle3<0:
                angle3+=360
            elif angle3>360:
                angle3-=360
            if angle_between(angle1,angle2,angle3):
                line_between=line([self.pos,self.player.pos])
                #line_between.recalculate_with_len(int(self.distance+1))
                walldata = line_between.collides_with_wall()
                can_see=not walldata[0]
                if can_see:
                    self.mouse_pos=self.player.pos
                    return True
        return False
    def move(self):
        self.move_speed=0
        if self.can_see_player(False):
            self.suspicion_point=self.player.pos
            if self.suspicion_level<10:
                self.suspicion_level+=0.1
        if self.suspicion_point!=self.pos:
            self.move_speed=3
            self.angle=self.rotate_towards(self.suspicion_point)
            self.go_towards(self.suspicion_point)
        elif self.suspicion_level!=0:
            self.suspicion_level-=0.1
        if self.should_shoot():
            self.shoot()
    def should_shoot(self):
        return self.suspicion_level>=10
    def shoot(self):
        #print "THE HORDE WAS SUMMONED"
        #self.game.summon_horde()
        pass
#a horde_enemy
class horde_enemy(enemy):
    def __init__(self,start,player,game):
        character.__init__(self,start[0],start[1],"Basic",game)
        self.pos=start
        self.player=player
        self.specs=[start[0],start[1],40,40]
        self.bullet_data=[self.pos,[self.pos[0],self.pos[1]+50]]
        self.move_speed=3

    def move(self):
        self.go_towards(self.player.pos)
    def loop(self):
        self.angle=self.rotate_towards(self.player.pos)
        enemy.loop(self)
        if collide(self.player.specs,self.specs):
            bullet=line([self.pos,self.player.pos])
            self.game.shot_fired(bullet,self)
        
    def should_aim(self,mouse_buttons):
        return True
#a Misc classes
class Title:
    def __init__(self,title,color,pos,active_time):
        self.active=True
        self.active_timer=1
        self.title,self.color,self.pos,self.active_time=title,color,pos,active_time
        self.len=len(title)*9
    def loop(self):
        self.active_timer+=1
        if self.active_timer==self.active_time:
            self.active=False
        self.draw()
        return self.active
    def draw(self):
        draw_text(self.title,self.pos[0]-(self.len/2),self.pos[1],self.color)
class portal:
    def __init__(self,data):
        self.box=[data[0],data[1],40,40]
        self.pos=[data[0],data[1]]
        self.destination=data[2]
        self.do_draw=data[3]
        self.angle=0
    def draw(self):
        if self.do_draw:
            self.angle+=1
            if self.angle>360:
                self.angle-=360
            goal_img.draw(self.box[0],self.box[1],1,self.angle)
    def collides_with_box(self,box):
        return collide(self.box,box),self.destination

#a Game class
class Game:
    destination=""
    def load_level(self,level):
        global walls
        self.level_title=Title(level.title,(1,0,0),[500,50],300)
        self.level=level
        self.enemies=[]
        self.portals=[]
        walls=[]
        self.player=player(self.level.player_spawn[0],self.level.player_spawn[1],"Basic",self)
        for new_enemy in self.level.enemies:
            self.enemies.append(enemy(new_enemy[0],new_enemy[1],new_enemy[2],self,new_enemy[3],self.player))
        for wall_data in self.level.walls:
            new_wall=wall(wall_data)
            walls.append(new_wall)
        for portal_data in self.level.portals:
            self.portals.append(portal(portal_data))
        self.level_size=[level.w,level.h]
        self.camera_pos=[self.player.pos[0]-(level.w/2),self.player.pos[1]-125]
        self.prev_camera_pos=self.camera_pos
    def start(self):
        while self.destination=="":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit();sys.exit()
            self.camera_pos=[self.player.pos[0]-(self.level.w/2),0]
            if self.camera_pos[0]<0:
                self.camera_pos[0]=0
            elif self.camera_pos[0]>=self.level_size[0]:
                self.camera_pos[0]=self.level_size[0]
            if self.prev_camera_pos!=self.camera_pos:
                set_ortho(self.camera_pos)
            glClearColor(1,1,1,1)
            glClear(GL_COLOR_BUFFER_BIT,GL_DEPTH_BUFFER_BIT)
            self.loop(False)
            pygame.display.flip()
            self.prev_camera_pos=self.camera_pos
        go_to=self.destination
        self.destination=""
        return go_to
    def loop(self,has_won):
        self.player.loop()
        for enemy in self.enemies:
            enemy.loop()
        self.draw_all()
        if not has_won:
            for portal_data in self.portals:
                does_collide=portal_data.collides_with_box(self.player.specs)
                if does_collide[0]:
                    self.end("Victory!",does_collide[1])
    def shot_fired(self,bullet,shooter):
        if shooter is not self.player:
            collide_point=bullet.collides_with_box(self.player.specs)
            if collide_point is not None:
                bullet.end = collide_point
                self.end("Killed!","")
                return
        for enemy in self.enemies:
            collide_point=bullet.collides_with_box(enemy.specs)
            if collide_point and enemy is not shooter:
                bullet.end = collide_point
                self.enemies.remove(enemy)
    def end(self,condition,destination):
        print condition
        i=0
        while i<5:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit();sys.exit()
            self.draw_all()
            pygame.display.flip()
            glClearColor(1,1,1,1)
            glClear(GL_COLOR_BUFFER_BIT,GL_DEPTH_BUFFER_BIT)
            i+=1
        if destination!="":
            self.destination=destination
            print "Going to "+self.destination
        else:
            self.load_level(self.level)
    def draw_all(self):
        if self.level_title!=None:
            if not self.level_title.loop():
                self.level_title=None
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        for wall in walls:
            wall.draw()
        for portal in self.portals:
            portal.draw()
    def summon_horde(self):
        for i in range(len(self.enemies)):
            self.enemies.append(horde_enemy(self.enemies[i].pos,self.player,self))
            self.enemies.remove(self.enemies[i])
        for portal_data in self.portals:
            num_of_enemies=random.randint(1,1)
            for i in range(num_of_enemies):
                self.enemies.append(horde_enemy(portal_data.pos,self.player,self))

