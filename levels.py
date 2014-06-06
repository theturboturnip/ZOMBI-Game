#!/usr/bin/env python
door_height=70
import random

class level:
    title=""
    player_spawn=(0,0)
    walls=[]
    portals=[]
    enemies=[]
    def print_data(self):
        print self.title,self.player_spawn,self.walls,self.portals,self.enemies

class new_level(level):
    def __init__(self,title="",player_spawn=(0,0),walls=[],portals=[],enemies=[]):
        self.title=title
        self.player_spawn=player_spawn
        self.walls=walls
        self.portals=portals
        self.enemies=enemies

class ArmsTestLevel(level):
    player_spawn=(100,100)
    walls=[
            [[100,100],[140,100]],
            [[140,100],[140,140]],
            [[140,140],[100,140]],
            [[100,140],[100,100]]
          ]
class StealthTestLevel(level):
    title="Stealth_Test"
    player_spawn=(100,150)
    walls=[
            [[100,100],[150,150]],
            [[100,100],[100,50]]
          ]
    portals=[[100,400,"Westy",True]]#,[400,400,"TestLvl"]]
    enemies=[(400,250,"Basic",180)]
    w=1000
    h=500
class WestcottLevel(level):
    title="Westy"
    player_spawn=(20,20)
    walls=[]
    portals=[[960,460,"Stealth_Test",True]]
    enemies=[(50,100,5,180),(50,150,5,90)]
class GenericBuilding(level):
    title="Building"
    walls=[ 
            [[0,250],[50,250]],
            [[130,250],[1000,250]]
          ]
    portals=[[960,125,"City",True]]
class City(level):
    title="City"
    portals=[[80,250,"Building0",True]]
    player_spawn=(0,250)
class TestLevel(level):
    title="TestLvl"
    portals=[[80,80,"Westy"],[160,160,"Stealth_Test"]]
class mission:
    def __init__(self):
        self.levels=[StealthTestLevel()]
        self.generate_buildings(5)
    def find_level(self,name):
        self.levels[0].portals[0][2]="Building"+str(random.randint(0,len(self.levels)-2))
        for level_data in self.levels:
            if level_data.title==name:
                return level_data
        return None
    def generate_building(self,on_left):
        level_title="Building"+str(len(self.levels)-1)
        level_walls=[]
        level_enemies=[]
        level_walls.append( ([0,0],[1000,0]) )
        level_walls.append( ([0,500],[1000,500]) )
        level_walls.append( ([500,0],[500,125-door_height/2]) )
        level_walls.append( ([500,125+door_height/2],[500,500]) )

        player_y=random.randint(1,4)*125+62-40
        portal_y=player_y
        if on_left:
            portal_x=-40
            player_x=50
            level_walls.append( ([1000,0],[1000,500]) )
            level_walls.append( ([0,0],[0,player_y-(door_height/2)]) )
            level_walls.append( ([0,player_y+door_height],[0,500]) )
        else:
            portal_x=1000
            player_x=910
            level_walls.append( ([0,0],[0,500]) )
            level_walls.append( ([1000,0],[1000,player_y-(door_height/2)]) )
            level_walls.append( ([1000,player_y+door_height],[1000,500]) )
        left_gap=random.randint(10,500)
        right_gap=random.randint(500,1000-door_height-10)
        level_walls.append( ([0,250],[left_gap,250]) )
        level_walls.append( ([left_gap+door_height,250],[right_gap,250]) )
        level_walls.append( ([right_gap+door_height,250],[1000,250]) )

        level_portals=[(portal_x,portal_y,"City",False)]
        level_data=new_level(title=level_title,walls=level_walls,portals=level_portals,enemies=level_enemies,player_spawn=(player_x,player_y))
        return level_data
    def generate_buildings(self,num_of_buildings):
        for i in range(num_of_buildings):
            self.levels.append(self.generate_building(False))
        
    

