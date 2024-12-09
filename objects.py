"""
Filename: objects.py
Author(s): Talieisn Reese, Vladislav Plotnikov, Drew Scebold, Zaid Kakish, Logan Jenison, John Millar
Version: 1.19
Date: 12/3/2024
Purpose: object classes for "MathWiz!"
"""
import pygame
import json
import random
import math
from functools import partial
from copy import deepcopy

import GameData as state
import tilecollisions
import moves
import animHandlers

#basic class to build other objects onto
class gameObject:
    def __init__(self, locus, depth, parallax,layer,extras):
        self.children = []
        self.extras = extras
        self.pos = locus
        self.lastpos = locus
        self.depth = depth
        self.parallax = parallax
        self.layer = layer
        self.speed = [0,0]
        self.nextspeedadj = [0,0]
        #add to list of objects that are updated every frame
        state.objects.append(self)
        #resort list to ensure objects are rendered in the correct order
        state.objects.sort(key = lambda item: item.depth, reverse = True)

    #check collisions between two game objects
    def checkobjcollide(self,obj1,obj2):
        if obj1.left[0]<=obj2.left[0]<=obj1.right[0] or obj1.left[0]<=obj2.right[0]<=obj1.right[0] or obj2.left[0]<=obj1.left[0]<=obj2.right[0] or obj2.left[0]<=obj1.right[0]<=obj2.right[0] or obj1.left[0]>=obj2.left[0]>=obj1.right[0] or obj1.left[0]>=obj2.right[0]>=obj1.right[0] or obj2.left[0]>=obj1.left[0]>=obj2.right[0] or obj2.left[0]>=obj1.right[0]>=obj2.right[0]:
            if obj1.top[1]<=obj2.top[1]<=obj1.bottom[1] or obj1.top[1]<=obj2.bottom[1]<=obj1.bottom[1] or obj2.top[1]<=obj1.top[1]<=obj2.bottom[1] or obj2.top[1]<=obj1.bottom[1]<=obj2.bottom[1] or obj1.top[1]>=obj2.top[1]>=obj1.bottom[1] or obj1.top[1]>=obj2.bottom[1]>=obj1.bottom[1] or obj2.top[1]>=obj1.top[1]>=obj2.bottom[1] or obj2.top[1]>=obj1.bottom[1]>=obj2.bottom[1]:
                return True
    #remove self from object list
    def delete(self):
        try:
            state.objects.remove(self)
            if state.cam.focusobj == self:
                state.cam.focusobj = None
        except:
            pass

    def checkupdatedist(self):
        dist = math.sqrt((state.cam.pos[0]+(state.screensize[0]/2)-self.pos[0])**2+(state.cam.pos[1]+(state.screensize[1]/2)-self.pos[1])**2)
        if dist <= 3600:
            return True
            
    #calcualte the points to use in collision detection
    def getpoints(self):
        self.left = [self.pos[0],int(self.pos[1]+self.size[1]/2)]
        self.right = [self.pos[0]+self.size[0],int(self.pos[1]+self.size[1]/2)]
        self.top = [int(self.pos[0]+self.size[0]/2),self.pos[1]]
        self.bottom = [int(self.pos[0]+self.size[0]/2),self.pos[1]+self.size[1]]

#slightly less basic class to build characters on--players, enemies, moving platforms, bosses, etc.
class character(gameObject):
    def __init__(self,locus,depth,parallax,name, layer, extras):
        #extra data used for individual object types
        self.data = state.objectsource[name]
        super().__init__(locus,depth,parallax, layer, extras)
        #extra variables handle things unique to objects with more logic: movement, gravity, grounded state, etc.
        self.movement = [0,0]
        if "flip" in self.extras.keys():
            self.direction = self.extras["flip"]
        else:
            self.direction = 1
        self.lastdirection = 1
        self.maxspeed = [20,75,-100]
        self.gravity = 5
        self.grounded = True
        self.actiontimer = 0
        self.blockable = False
        self.name = name
        if "Deathtype" in self.data.keys():
            self.deathtype = self.data["Deathtype"]
        else:
            self.deathtype = type(self).__name__
        #get object info: Grapics, animations, etc.
        self.infoname = state.objectsource[name]["Info"]
        self.info = state.infosource[self.infoname]
        
        self.size = self.info["Sizes"]["Default"]
        #sprite used to show player. Replace these calls with animation frame draws
        self.sprite = pygame.Surface([self.size[0]*state.scaleamt,self.size[1]*state.scaleamt])
        self.colorbrush = pygame.Surface([self.size[0]*state.scaleamt,self.size[1]*state.scaleamt])
        self.sprite.set_colorkey(state.invis)
        self.pallate = "Default"
        self.storepal = None
        #stuff for animation
        self.shoottimer = 0
        self.animname = "Idle"
        self.lastanim = "Idle"
        self.animframe = 0
        self.animtime = 0
        self.requestanim = False
        self.lastframe = self.info["Frames"][self.info["Animations"][self.animname][self.animframe][0]]
        self.animationupdate()
        #determine points for collision
        self.getpoints()
        self.lastbottom = self.bottom.copy()
        self.lasttop = self.top.copy()
        self.lastleft = self.left.copy()
        self.lastright = self.right.copy()
        self.collidepoints = [self.left,self.top,self.right,self.bottom,self.lastleft,self.lasttop,self.lastright,self.lastbottom]
        #the action queue is used to hold the current action.
        self.actionqueue = []
        self.stun = False
        self.iframes = 0
        #allegience value for projectile and damage collisions.
        self.allegience = "Enemy"
        #limits for weapons to shoot
        if "WeapLimits" in self.data.keys():
            self.shotLimits = self.data["WeapLimits"]
        else:
            self.shotLimits = {}
        self.bulletCounts = {weapon: 0 for weapon in self.shotLimits}

    #run every frame to update the character's logic    
    def update(self):
        self.lastanim = self.animname
        self.lastpos = self.pos.copy()
        self.lastbottom = self.bottom.copy()
        self.lasttop = self.top.copy()
        self.lastleft = self.left.copy()
        self.lastright = self.right.copy()
        self.lastdir = self.direction
        self.getpoints()
        if self.iframes > 0:
            self.iframes -= state.deltatime
        else:
            self.iframes = 0
        if self in state.objects:
            self.physics()
            self.movement = [self.speed[0]*state.deltatime,self.speed[1]*state.deltatime]
            while self.movement != [0,0]:
                self.move()
                self.collide()
                self.objcollide()
            self.objcollide()
            self.collide()
            self.render()
        self.actionupdate()
        for item in self.children:
            item.pos[0] = item.pos[0]+(self.pos[0]-self.lastpos[0])
            item.pos[1] = item.pos[1]+(self.pos[1]-self.lastpos[1])
        self.speed[0] += self.nextspeedadj[0]
        self.speed[1] += self.nextspeedadj[1]
        self.nextspeedadj = [0,0]

    def actionupdate(self):
        #iterate through every action in the queue.
        actionnum = 0
        while actionnum < len(self.actionqueue):
            action = self.actionqueue[actionnum]
            actionnum+=1
            #if the action has a starttimer above zero, iterate that down a peg.
            if action[0] > 0:
                action[0] -= state.deltatime
            #otherwise, do the thing.
            else:
                if type(self) ==Boss and action[1][0] == "jump":
                    print(action[1][0],self.speed,self.grounded)
                getattr(moves,action[1][0])(self, action[1][1])
                #if the action's popcondidtion is met, pull it from the queue and skip.
                match action[2][0]:
                    case "self":
                        if getattr(self,action[2][1]) == action[2][2]:
                            self.actionqueue.remove(action)
                            actionnum -= 1
                    case "state":
                        if getattr(state,action[2][1]) == action[2][2]:
                            self.actionqueue.remove(action)
                            actionnum -= 1
                    case "keys":
                        if state.keys[action[2][1]] == action[2][2]:
                            self.actionqueue.remove(action)
                            actionnum -= 1
                    case "time":
                        if action[2][1] <= 0:
                            self.actionqueue.remove(action)
                            actionnum -= 1
                        else:
                            action[2][1] -= state.deltatime
                    #remove the action immediately if the source isn't found
                    case _:
                        self.actionqueue.remove(action)
                        actionnum -= 1

    def kill(self):
        if hasattr(moves,f"die{self.deathtype}"):
            getattr(moves,f"die{self.deathtype}")(self,None)
        else:
            moves.dieDefault(self,None)
        
    
        
    def animationupdate(self):
        if self.shoottimer > 0:
            self.shoottimer -= state.deltatime
        else:
            self.shoottimer = 0
        self.sprite.fill(state.invis)
        self.animtime += state.deltatime
        anim = self.info["Animations"][self.animname]
        if anim != []:
            if self.animtime >= anim[self.animframe][3]:
                self.animframe += 1
                self.animtime = 0
                if self.animframe >= len(anim):
                    self.animframe = 0
                    self.requestanim = False
            #draw the sprite
            frame = self.info["Frames"][anim[self.animframe][0]]
            center = frame[6:]
            #adjust the size of the canvas if the sprite size is different.
            if self.size != frame[2:4]:
                self.size = frame[2:4]
                self.sprite = pygame.Surface([self.size[0]*state.scaleamt,self.size[1]*state.scaleamt])
                self.colorbrush = pygame.Surface([self.size[0]*state.scaleamt,self.size[1]*state.scaleamt])
                self.sprite.set_colorkey(state.invis)
                self.sprite.fill(state.invis)
                #also, adjust position to match around a center point.
                self.pos[0] += self.lastframe[6]-center[0]
                if self.grounded:
                    self.pos[1] += self.lastframe[3]-self.size[1]
                else:
                    self.pos[1] += self.lastframe[7]-center[1]
            self.sprite.blit(state.spritesheet, [frame[4]*state.scaleamt,frame[5]*state.scaleamt],([frame[0]*state.scaleamt,frame[1]*state.scaleamt,frame[2]*state.scaleamt,frame[3]*state.scaleamt]))
            self.sprite = pygame.transform.rotate(pygame.transform.flip(self.sprite,anim[self.animframe][1][0],anim[self.animframe][1][1]),anim[self.animframe][2])
            #pygame.draw.rect(self.sprite,(255,255,255),(0,center[1],240,10))
            #get the sprite drawn with the correct palatte
            #optimize this later
            if self.pallate != "Default":
                for color in range(len(state.infosource[self.infoname]["Pallates"][self.pallate])):
                    self.colorbrush.fill(state.infosource[self.infoname]["Pallates"][self.pallate][color])
                    self.sprite.set_colorkey(state.infosource[self.infoname]["Pallates"]["Default"][color])
                    self.colorbrush.blit(self.sprite,(0,0))
                    self.sprite.blit(self.colorbrush,(0,0))
                self.sprite.set_colorkey(state.invis)
            self.lastframe = frame

    #check if a point is colliding with the ground. Add logic for moving platforms later
    def pointcollide(self, point):
        #find layers to do collision on:
        for item in state.objects:
            if type(item).__name__ == "drawlayer" and item.layernum == self.layer:
                #get the tile that the point is positioned on
                tile = [int(point[0]//state.tilesize),int(point[1]//state.tilesize)]
                #get values from said tile
                #UNLESS the layer is supposed to loop--THEN simply loop the information from the list
                if item.loop[0] == True:
                    tile[0] = tile[0]%(item.longest)
                    tile[1] = tile[1]%(len(state.level.tilemap[item.layernum]))
                #unless it doesn't exist. Then, treat it as if it were solid to prevent out-of-bounds errors
                if (tile[0] < 0 or tile[1] < 0) or (tile[0] >= item.longest or tile[1] >= len(state.level.tilemap[item.layernum])):
                    tiletype = 1
                    tileflip = 0
                    tilerotate = 0
                else:
                    tiletype = state.level.tilemap[item.layernum][tile[1]][tile[0]]
                    tileflip = state.level.flipmap[item.layernum][tile[1]][tile[0]]
                    tilerotate = state.level.spinmap[item.layernum][tile[1]][tile[0]]
                #calculate the position of the point within the tile
                x=point[0]%state.tilesize
                y=point[1]%state.tilesize

                #treat the coordinates differently if the tile is flipped and/or rotated
                if tileflip == 1:
                    x = state.tilesize - x
                elif tileflip == 2:
                    x = state.tilesize - x
                    y = state.tilesize - y
                elif tileflip == 3:
                    y = state.tilesize - y

                if tilerotate == 1:
                    burner = y
                    y = x
                    x = state.tilesize - burner
                elif tilerotate == 2:
                    x = state.tilesize - x
                    y = state.tilesize - y
                elif tilerotate == 3:
                    burner = x
                    x = y
                    y = state.tilesize - burner
                #get the results of the appropriate block collision equation
                if state.tilesource["tiles"][str(tiletype)][5] == 1:
                    return tilecollisions.solid((x,y))
                elif state.tilesource["tiles"][str(tiletype)][5] == 2:
                    return tilecollisions.fortyfive((x,y))
                elif state.tilesource["tiles"][str(tiletype)][5] == 3:
                    return tilecollisions.lowtwentytwo((x,y))
                elif state.tilesource["tiles"][str(tiletype)][5] == 4:
                    return tilecollisions.hightwentytwo((x,y))
                elif state.tilesource["tiles"][str(tiletype)][5] == 5:
                    return tilecollisions.slab((x,y))
                else:
                    return False

    #calculate physics for the object
    def physics(self):
        #if not touching the ground, add gravity until terminal velocity is reached
        if self.grounded == False:
            if type(self) == Player:
                pass
            self.speed[1] += self.gravity*state.deltatime/2
            self.nextspeedadj[1] += self.gravity*state.deltatime/2
            if self.speed[1] >= self.maxspeed[1]:
                self.speed[1] = self.maxspeed[1]
            elif self.speed[1] <= self.maxspeed[2]:
                self.speed[1] = self.maxspeed[2]
        #otherwise, don't add gravity at all. doing so would cause the player to gain fallspeed while they stood, and causes them to fall like a ton of bricks if the ground ceases to hold them (i.e. they walk off a ledge)
        else:
            self.speed[1] = 0
            #self.nextspeedadj[1] = 0
        #if type(self) == Player:
        #    print(self.pos, self.speed, self.nextspeedadj)
        #decrease move speed    
        if self.speed[0] > 0:
            self.speed[0] -= 4*state.deltatime
            if (self.speed[0]) < 1:
                self.speed[0] = 0
            else:
                self.nextspeedadj[0] -= 4*state.deltatime
        elif self.speed[0] < 0:
            self.speed[0] += 4*state.deltatime
            if (self.speed[0]) > -1:
                self.speed[0] = 0
            else:
                self.nextspeedadj[0] += 4*state.deltatime
            
    #pretty self-explanitory: add the movement speed to the character        
    def move(self):
        if abs(self.movement[1]) > state.movetickamount:
            if self.movement[1] > 0:
                self.pos[1] += state.movetickamount
                self.movement[1]-=state.movetickamount
                if self.movement[1] < 0:
                    self.movement[1] = 0
            elif self.movement[1] < 0:
                self.pos[1] -= state.movetickamount
                self.movement[1]+=state.movetickamount
                if self.movement[1] > 0:
                    self.movement[1] = 0
        else:
            if type(self) == Boss:
                print(self.movement)
            self.pos[1] += self.movement[1]
            self.movement[1] = 0

        if abs(self.movement[0]) > state.movetickamount:
            if self.movement[0] > 0:
                self.pos[0] += state.movetickamount
                self.movement[0]-=state.movetickamount
                if self.movement[0] > 0:
                    self.movement[0] = 0
            elif self.movement[0] < 0:
                self.pos[0] -= state.movetickamount
                self.movement[0]+=state.movetickamount
                if self.movement[0] > 0:
                    self.movement[0] = 0
        else:
            self.pos[0] += self.movement[0]
            self.movement[0] = 0
        self.pos = [round(self.pos[0]),round(self.pos[1])]

    def groundsnap(self):
        #this check is exclusive to the bottom point. If the distance to the ground is less than the current forwards momentum, snap player to the ground.
        if (not self.grounded) and type(self) == Player:
            dist = 1
            while dist <= abs(self.bottom[0] - self.lastbottom[0]):
                if self.pointcollide([self.bottom[0],self.bottom[1]+dist]) != True:
                    dist += 1
                else:
                    self.pos[1] += dist
                    self.grounded = True
                    self.getpoints()
                    break
                
    #check for collisions on all four points. if a collision is found, find how far the point is into the ground and move it so that it is only 1px of less deep.  
    def collide(self):
        self.getpoints()
        #if the left or right points are blocked, the character is pressing against a wall on that side
        #if the bottom point is blocked, the player is on the ground
        self.grounded = self.pointcollide([self.bottom[0],self.bottom[1]])
        if self.grounded:
            dist = 1
            while dist <= 600:
                if self.pointcollide([self.bottom[0],self.bottom[1]-dist]) == True:
                    dist += 1
                else:
                    self.pos[1] -= dist-1
                    self.getpoints()
                    break

        #if the top point is blocked, the character is bumping into a ceiling
        self.getpoints()
        self.topblock =  self.pointcollide(self.top)
        if self.topblock:
            dist = 1
            while dist <= 600:
                if not self.pointcollide([self.top[0],self.top[1]+dist]):
                    self.pos[1]+=dist-1
                    self.getpoints()
                    break
                dist += 1
        #if the left or right points are blocked, the character is pressing against a wall on that side
        self.getpoints()
        self.leftblock =  self.pointcollide(self.left)
        if self.leftblock:
            dist = 1
            while dist <= 600:
                if not self.pointcollide([self.left[0]+dist,self.left[1]]):
                    self.pos[0]+=dist-1
                    self.getpoints()
                    break
                dist += 1
                
        self.getpoints()
        self.rightblock =  self.pointcollide(self.right)
        if self.rightblock:
            dist = 1
            while dist <= 600:
                if not self.pointcollide([self.right[0]-dist,self.right[1]]):
                    self.pos[0]-=dist-1
                    self.getpoints()
                    break
                dist += 1
            
    def objcollide(self):
        if self in state.objects:
            for thing in state.objects:
                if type(thing).__name__ != "drawlayer" and thing != self and thing.layer == self.layer:
                    if self.checkobjcollide(self,thing):
                        thing.collidefunction(self)
    
    def collidefunction(self,trigger):
        pass

    def damagetake(self,dmg):
        pass
                
    #Draw the sprite to the canvas in the correct position
    def render(self):
        parallaxmod = self.parallax - state.cam.depth
        if self.direction == 1:
            state.display.blit(self.sprite,[(self.pos[0]-state.cam.pos[0]*parallaxmod)*state.scaleamt,(self.pos[1]-state.cam.pos[1]*parallaxmod)*state.scaleamt])
        else:
            state.display.blit(pygame.transform.flip(self.sprite,True,False),[(self.pos[0]-state.cam.pos[0]*parallaxmod)*state.scaleamt,(self.pos[1]-state.cam.pos[1]*parallaxmod)*state.scaleamt])

class spawner(gameObject):
    def __init__(self,locus,depth,parallax,name, layer, extras):
        super().__init__(locus,depth,parallax, layer, extras)
        self.name = name
        self.data = state.objectsource[name]
        self.size = [0,0]
        self.getpoints()
        
        self.delcond = self.data.get("DeleteCondition")
        self.spawncond = self.data.get("SpawnCondition")
        self.spawntype = self.data.get("Spawntype")
        self.spawnees = self.data.get("Objlist")
        self.spawnedobjs = []

    def render(self):
        parallaxmod = self.parallax - state.cam.depth
        pygame.draw.rect(state.display,(255,255,0),((self.pos[0]-state.cam.pos[0]*parallaxmod)*state.scaleamt,(self.pos[1]-state.cam.pos[1]*parallaxmod)*state.scaleamt,20*state.scaleamt,20*state.scaleamt))
        
    def update(self):
        #super().update()
        for item in self.spawnedobjs:
            if item not in state.objects:
                self.spawnedobjs.remove(item)
        self.spawncheck()
        self.deletecheck()

    def collidefunction(self,trigger):
        pass
        
    def deletecheck(self):
        if self.delcond == "offcamera":
            #if within camera x
            if not(state.cam.pos[0]+state.screensize[0]>=self.pos[0]+self.size[0]>=state.cam.pos[0] or state.cam.pos[0]+state.screensize[0]>=self.pos[0]>=state.cam.pos[0]):
                #if within camera y
                if not(state.cam.pos[1]+state.screensize[1]>=self.pos[1]+self.size[1]>=state.cam.pos[1] or state.cam.pos[1]+state.screensize[1]>=self.pos[1]>=state.cam.pos[1]):
                    for item in self.spawnedobjs:
                        if item in state.objects:
                            item.delete()
                        
    def spawncheck(self):
        if self.spawncond == "entercamera":
            #if within camera x
            if state.cam.pos[0]+state.screensize[0]>=self.pos[0]+self.size[0]>=state.cam.pos[0] or state.cam.pos[0]+state.screensize[0]>=self.pos[0]>=state.cam.pos[0]:
                #if within camera y
                if state.cam.pos[1]+state.screensize[1]>=self.pos[1]+self.size[1]>=state.cam.pos[1] or state.cam.pos[1]+state.screensize[1]>=self.pos[1]>=state.cam.pos[1]:
                    #if not within x last frame
                    if not (state.cam.lastpos[0]+state.screensize[0]>=self.pos[0]+self.size[0]>=state.cam.lastpos[0] or state.cam.lastpos[0]+state.screensize[0]>=self.pos[0]>=state.cam.lastpos[0]) or  not (state.cam.lastpos[1]+state.screensize[1]>=self.pos[1]+self.size[1]>=state.cam.lastpos[1] or state.cam.lastpos[1]+state.screensize[1]>=self.pos[1]>=state.cam.lastpos[1]):
                        #if not within y last frame
                            #spawn things
                            self.spawn()
    def spawn(self):
        if self.spawntype == "random":
            index = random.randint(0,len(self.spawnees)-1)
            for item in self.spawnees[index]:
                if item[3] == "parent":
                    item[3] = self.depth
                if item[4] == "parent":
                    item[4] = self.parallax
                self.spawnedobjs.append(globals()[item[0]]([item[2][0]+self.pos[0],item[2][1]+self.pos[1]],item[3],item[4],item[1],item[5]))

class Sign(character):
    def __init__(self,locus,depth,parallax,name, layer, extras):
        super().__init__(locus,depth,parallax,name, layer, extras)
        if "text" in extras.keys():
            self.text = extras["text"]
        else:
            self.text = "TEST"
        #self.sprite.fill((100,100,0))
    def update(self):
        super().update()
        self.animationupdate()
        self.sprite.blit(state.font.render(self.text,False,(255,255,180)),(40*state.scaleamt,40*state.scaleamt))
    
        
class Platform(character):
    def __init__(self,locus,depth,parallax,name, layer, extras):
        super().__init__(locus,depth,parallax,name, layer, extras)
        self.gravity = 0
        #self.sprite.fill((100,0,0))
        #pygame.draw.rect(self.sprite,(255,0,0),(0,0,self.size[0],20))

    def collide(self):
        pass
    
    def update(self):
        super().update()
        self.animationupdate()
        
    def collidefunction(self,trigger):
        if trigger.lastbottom[1] <= self.top[1] and trigger.speed[1] >= 0:
            trigger.grounded = True
            trigger.speed[1] = 0
            trigger.movement[1] = 0
            trigger.pos[1] = self.top[1] - trigger.size[1]

class CollapsingPlatform(Platform):
    def __init__(self,locus,depth,parallax,name, layer, extras):
        super().__init__(locus,depth,parallax,name, layer, extras)
        self.collapsing = False
    
    def update(self):
        super().update()
        self.animationupdate()

    #force the platform to collapse when shot
    def damagetake(self,amount):
        self.animname = "Break"
        self.actionqueue.append([6,["collapsestart",None],["self","collapsing",True]])
        self.actionqueue.append([60,["diePlat","WoodPlank"],[None,None,True]])
        
    def collidefunction(self,trigger):
        if trigger.lastbottom[1] <= self.top[1] and trigger.speed[1] >= 0 and self.collapsing == False and type(trigger) == Player:
            #self.sprite.fill((0,0,100))
            #pygame.draw.rect(self.sprite,(0,0,255),(0,0,self.size[0],20))
            self.animname = "Break"
            trigger.grounded = True
            trigger.speed[1] = 0
            trigger.movement[1] = 0
            trigger.pos[1] = self.top[1] - trigger.size[1]
            self.actionqueue.append([6,["collapsestart",None],["self","collapsing",True]])
            self.actionqueue.append([60,["diePlat","WoodPlank"],[None,None,True]])
            
class Hitbox(gameObject):
    def __init__(self,locus,depth,parallax, layer, extras):
        self.offset = locus
        self.size = extras["size"]
        self.mode = extras["type"]
        self.amt = extras["amt"]
        self.lifespan = extras["lifespan"]
        self.parent = extras["parent"]
        self.allegience = self.parent.allegience
        if self.parent == None:
            super().__init__([self.offset[0],self.offset[1]],depth,parallax, layer, extras)
        else:
            super().__init__([self.parent.pos[0]+self.offset[0],self.parent.pos[1]+self.offset[1]],depth,parallax, layer, extras)
        self.hitobjects = []
        self.parent.children.append(self)
        self.getpoints()
    #calcualte the points to use in collision detection
    def getpoints(self):
        self.left = [self.pos[0],int(self.pos[1]+self.size[1]/2)]
        self.right = [self.pos[0]+self.size[0],int(self.pos[1]+self.size[1]/2)]
        self.top = [int(self.pos[0]+self.size[0]/2),self.pos[1]]
        self.bottom = [int(self.pos[0]+self.size[0]/2),self.pos[1]+self.size[1]]
    def update(self):
        #update the lifespan timer, and remove the object if it's number is up.
        if type(self.lifespan) in [int,float]:
            self.lifespan -= state.deltatime
            if self.lifespan <= 0:
                self.parent.children.remove(self)
                self.delete()
        if self.parent.direction == 1:
            self.pos[0] = self.parent.pos[0]+self.offset[0]
        elif self.parent.direction == -1:
            self.pos[0] = self.parent.pos[0]-(self.offset[0])
        self.getpoints()
        self.render()

    def render(self):
        if self.mode == "dmg":
            color = [200,50,50]
        elif self.mode == "block":
            color = [50,50,200]
        elif self.mode == "triggerfunc":
            color = [200,150,50]
        elif self.mode == "split":
            color = [50,200,50]
        parallaxmod = self.parallax - state.cam.depth
        pygame.draw.rect(state.display,color,((self.pos[0]-state.cam.pos[0]*parallaxmod)*state.scaleamt,(self.pos[1]-state.cam.pos[1]*parallaxmod)*state.scaleamt,self.size[0]*state.scaleamt,self.size[1]*state.scaleamt))

    def collidefunction(self,trigger):
        if trigger != self.parent:
            if self.mode == "dmg":
                if trigger.allegience != self.allegience and trigger not in self.hitobjects:
                    hit = True
                    for obj in trigger.children:
                        if type(obj) == Hitbox and obj.mode == "block":
                            if self.checkobjcollide(self,obj):
                                hit = False
                    #deal damage
                    if hit and hasattr(trigger,"damagetake"):
                        trigger.damagetake(self.amt)
                    self.hitobjects.append(trigger)
            elif self.mode == "block":
                if type(trigger)==Projectile:
                    trigger.delete()
            elif self.mode == "triggerfunc":
                if trigger.allegience != self.allegience:
                    getattr(self.parent,self.amt)()
            elif self.mode == "split":
                if type(trigger) == Enemy and trigger.iframes <= 0:
                    #print(self.amt)
                    moves.split(trigger,self.amt)
                elif type(trigger) == Boss and trigger.iframes <= 0:
                    trigger.damagetake(trigger.health/2)

class collectGoal(character):
    def __init__(self,locus,depth,parallax,name, layer, extras):
        super().__init__(locus,depth,parallax,name, layer, extras)
        self.sprite.fill((0,0,100))
        self.gotten = False
    def collidefunction(self,trigger):
        if type(trigger).__name__ == "Player" and self.gotten == False:
            trigger.stun = True
            trigger.speed[0] = 0
            trigger.animname = "Win"
            trigger.requestanim = True
            self.gotten = True
            self.actionqueue.append([120,["loadnextstate",["cutscene","outro"]],[None,None,True]])

class Projectile(character):
    def __init__(self,locus,depth,parallax,name, layer, extras):
        self.weapon_type = name
        self.gun = extras["parent"]
        super().__init__([self.gun.pos[0]+locus[0],self.gun.pos[1]+locus[1]],depth,parallax,name,layer,extras)
        
        self.gravity = 0
        self.blockable = True
        self.allegience = self.gun.allegience
        if "flip" not in self.extras.keys():
            self.direction = self.gun.direction
        self.damage = self.data["dmg"]
        self.angle = -extras["angle"]
        self.persistence = False
        if "lifespan" in self.data.keys():
            self.lifespan = self.data.get("lifespan")
        else:
            self.lifespan = 60
        self.gun.bulletCounts[self.weapon_type] += 1
        if "Movedata" in self.data.keys():
            data = deepcopy(self.data["Movedata"])
            for item in data:
                if type(item[1][1]) == list:
                    item[1][1][0] = item[1][1][0] * self.direction
                self.actionqueue.append(item)
        else:
            self.actionqueue.append([0,["setforce",[50*self.direction,0]],["time",self.lifespan,False]])

    def update(self):
        #print("Chugging from ", self)
        #super().update()
        self.lastanim = self.animname
        self.lastpos = self.pos.copy()
        self.lastbottom = self.bottom.copy()
        self.lasttop = self.top.copy()
        self.lastleft = self.left.copy()
        self.lastright = self.right.copy()
        self.lastdir = self.direction
        
        self.getpoints()
        if self.iframes > 0:
            self.iframes -= state.deltatime
        else:
            self.iframes = 0
        if self in state.objects:
            #self.physics()
            self.movement[0] = (self.speed[0]*math.cos(math.radians(self.angle*self.direction))+self.speed[1]*math.sin(math.radians(self.angle)))*state.deltatime
            self.movement[1] = (self.speed[0]*math.sin(math.radians(self.angle*self.direction))+self.speed[1]*math.cos(math.radians(self.angle)))*state.deltatime
            #self.movement = [self.speed[0]*state.deltatime,self.speed[1]*state.deltatime]
            while self.movement != [0,0]:
                self.move()
                self.collide()
                self.objcollide()
            self.objcollide()
            self.collide()
            self.render()
        self.actionupdate()
        for item in self.children:
            item.pos[0] = item.pos[0]+(self.pos[0]-self.lastpos[0])
            item.pos[1] = item.pos[1]+(self.pos[1]-self.lastpos[1])
        self.speed[0] += self.nextspeedadj[0]
        self.speed[1] += self.nextspeedadj[1]
        self.nextspeedadj = [0,0]
        
        self.animationupdate()
        
        #update the lifespan timer, and remove the object if it's number is up.
        if type(self.lifespan) in (int,float):
            self.lifespan -= state.deltatime
            if self.lifespan <= 0:
                self.gun.bulletCounts[self.weapon_type] -= 1
                self.delete()
        if self.leftblock or self.rightblock or self.topblock or self.grounded:
            if not self.persistence:
                self.gun.bulletCounts[self.weapon_type] -= 1
                self.delete()
                #print(self.pos)
            
    def collidefunction(self,trigger):
        #if type(trigger) == Player:
        #    print("gottem")
        if self.allegience != trigger.allegience:
            #print(type(trigger))#.allegience)
            if hasattr(trigger,"damagetake"):
                trigger.damagetake(self.damage)
            if not self.persistence:
                self.gun.bulletCounts[self.weapon_type] -= 1
                self.delete()
            
class Player(character):
    def __init__(self,locus,depth,parallax,name,layer,extras):
        super().__init__(locus,depth,parallax,name,layer,extras)
        if "Powers" in self.data.keys():
            self.abilities = self.data["Powers"]
        else:
            self.abilities = ["Default"]
        self.weap = "Default"
        self.maxhealth = 100
        self.health = self.maxhealth
        self.allegience = "Hero"
        #make the camera focus on this object
        if state.gamemode != "edit":
            state.cam.focusobj = self
        #self.sprite.fill((255,0,0))
        #pygame.draw.rect(self.sprite,(255,255,255),((self.size[0]-20),self.size[1]/4,20,20))
    #this update is the same as the one for generic characters, but it allows the player to control it.
    def update(self):
        if state.gamemode != "edit":
            self.lastanim = self.animname
            self.lastpos = self.pos.copy()
            self.lastbottom = self.bottom.copy()
            self.lasttop = self.top.copy()
            self.lastleft = self.left.copy()
            self.lastright = self.right.copy()
            self.lastdir = self.direction
            self.physics()
            if self.iframes > 0:
                self.iframes -= state.deltatime
            else:
                self.iframes = 0
            #print(self.speed)
            self.movement = [self.speed[0]*state.deltatime,self.speed[1]*state.deltatime]
            while self.movement != [0,0]:
                self.move()
                self.collide()
                self.groundsnap()
                self.objcollide()
            self.collide()
            self.groundsnap()
            self.objcollide()
            if not self.stun:
                self.playerControl()
            self.actionupdate()
        for item in self.children:
            item.pos[0] = item.pos[0]+(self.pos[0]-self.lastpos[0])
            item.pos[1] = item.pos[1]+(self.pos[1]-self.lastpos[1])
        #print("Before:",self.speed)
        self.speed[0] += self.nextspeedadj[0]
        self.speed[1] += self.nextspeedadj[1]
        #print("After:",self.speed)
        self.nextspeedadj = [0,0]
        state.HUD.blit(state.font.render(f"HP:{self.health}",False,[255,255,255],[0,0,0]),(30*state.scaleamt,30*state.scaleamt))
        if self.health <= 0:
            state.HUD.blit(state.font.render(f"Game Over",False,[255,0,0],[0,0,0]),(1800*state.scaleamt,1800*state.scaleamt))
        if hasattr(animHandlers,f"{self.name}animationPick"):
            getattr(animHandlers,f"{self.name}animationPick")(self)
        self.animationupdate()
        self.render()

    #perform moves from the moves library based on the status of input
    def playerControl(self):
        #run the jump function if the spacebar is down
        if state.keys[pygame.K_SPACE]:
            if pygame.K_SPACE in state.newkeys and self.grounded == True:
                #moves.jump(self,120)
                self.actionqueue.append([0,["jump",80],[None,None,True]])
            else:
                self.actionqueue.append([0,["jumpstall",100],[None,None,True]])
        #walk left or right if the a or d keys are pressed. Swap directions accordingly unless the shift key is held.
        if state.keys[pygame.K_a]:
            if not state.keys[pygame.K_LSHIFT] and not state.keys[pygame.K_RSHIFT]:
                self.direction = -1
            moves.walk(self,-15)
        if state.keys[pygame.K_d]:
            if not state.keys[pygame.K_LSHIFT] and not state.keys[pygame.K_RSHIFT]:
                self.direction = 1
            moves.walk(self,15)
        if pygame.K_q in state.newkeys:
            self.actionqueue.append([0,["cyclepower",-1],[None,None,True]])
        if pygame.K_e in state.newkeys:
            self.actionqueue.append([0,["cyclepower",1],[None,None,True]])
        if pygame.K_f in state.newkeys:
            self.actionqueue.append([0,[f"weap{self.weap}",None],[None,None,True]])
        #test damage
        if pygame.K_m in state.newkeys:
            self.damagetake(10)
            #state.particleManager.particles[self.layer].append([self.pos,[[0,0,120,120,0,0,0,1]],[0,-20],[0,5],[120,120],0,0,60])

    def damagetake(self,dmg):
        if self.health > 0:
            if self.iframes <= 0:
                self.health -= dmg
                self.animname = "Fall"
                self.requestanim = True
                self.iframes = 90
                self.actionqueue.append([0,["walk",10],[None,None,True]])
                self.actionqueue.append([0,["jump",20],[None,None,True]])
                self.actionqueue.append([0,["stun",dmg],[None,None,True]])
                self.actionqueue.append([30,["destun",dmg],[None,None,True]])
                #apply stun pallate after a while. Maybe we replace this with a flicker function?
                self.actionqueue.append([35,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([40,["deTempPallate",None],[None,None,True]])
                self.actionqueue.append([45,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([50,["deTempPallate",None],[None,None,True]])
                self.actionqueue.append([55,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([60,["deTempPallate",None],[None,None,True]])
                self.actionqueue.append([65,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([70,["deTempPallate",None],[None,None,True]])
                self.actionqueue.append([75,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([80,["deTempPallate",None],[None,None,True]])
                self.actionqueue.append([85,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([90,["deTempPallate",None],[None,None,True]])
            if self.health <= 0:
                self.kill() 

class Enemy(character):
    def __init__(self,locus,depth,parallax,name,layer,extras):
        super().__init__(locus,depth,parallax,name,layer,extras)
        #print(self.data.keys())
        if "Behavior" in self.data.keys():
            self.behavior = state.aisource[self.data["Behavior"]]
        else:
            self.behavior = [[0,["nothing","nothing"],[None,None,False]]]
        if "Pallate" in self.data.keys():
            self.pallate = self.data["Pallate"]
        else:
            self.pallate = "Default"
        if "Pallate" in self.data.keys():
            self.pallate = self.data["Pallate"]
        else:
            self.pallate = "Default"
        self.maxhealth = self.data["HP"]
        if "healthDivide" in self.extras.keys():
            self.health = int(self.maxhealth/self.extras["healthDivide"])
        else:
            self.health = self.maxhealth
        self.gravity = 7
        self.grounded = False
        #find player to target
        self.target = None
        # pygame.draw.rect(self.sprite,(255,255,255),((self.size[0]-20),self.size[1]/4,20,20))

    def update(self):
        #gather info about prior frame
        self.lastanim = self.animname
        self.lastpos = self.pos.copy()
        self.lastbottom = self.bottom.copy()
        self.lasttop = self.top.copy()
        self.lastleft = self.left.copy()
        self.lastright = self.right.copy()
        self.lastdir = self.direction

        for obj in state.objects:
            if type(obj).__name__== "Player":
                self.target = obj

        #refresh the actionqueue
        if self.iframes > 0:
            self.iframes -= state.deltatime
        if not self.stun:
            if self.actionqueue == []:
                self.actionqueue = deepcopy(self.behavior)
        #perform movement and check collisions
        self.movement = [self.speed[0]*state.deltatime,self.speed[1]*state.deltatime]
        while self.movement != [0,0]:
            self.move()
            self.collide()
            self.groundsnap()
            self.objcollide()
        self.objcollide()
        self.collide()
        self.groundsnap()
        #adjust postitions of any child objs
        for item in self.children:
            item.pos[0] = item.pos[0]+(self.pos[0]-self.lastpos[0])
            item.pos[1] = item.pos[1]+(self.pos[1]-self.lastpos[1])
        
        self.physics()
        self.actionupdate()
        self.nextspeedadj = [0,0]
        #update animations
        if hasattr(animHandlers,f"{self.name}animationPick"):
            getattr(animHandlers,f"{self.name}animationPick")(self)
        self.animationupdate()
        self.render()
        #adjust speed for the next frame--complex deltatime stuffs 
        self.speed[0] += self.nextspeedadj[0]
        self.speed[1] += self.nextspeedadj[1]
        
    def collidefunction(self,trigger):
        if trigger.allegience != self.allegience:
            if hasattr(trigger, "damagetake"):
                trigger.damagetake(10)
            
    # eventually add a check statement like "hp -= dmg. if hp < 0 then Die"
    def damagetake(self,dmg):
        self.actionqueue = []
        self.actionqueue.append([0,["stun",dmg],[None,None,True]])
        self.actionqueue.append([30,["destun",dmg],[None,None,True]])
        self.health -= dmg
        if self.health <= 0:
            self.kill()
            
class roomLock(gameObject):
    def __init__(self,locus,depth,parallax,name, layer, extras):
        super().__init__(locus,depth,parallax, layer, extras)
        self.name = name
        self.data = state.objectsource[name]
        self.triggers = []
        if "Size" in self.data.keys():
            self.size = self.data["Size"]
        else:
            self.size = state.screensize
        self.getpoints()

    def render(self):
        if state.gamemode == "edit":
            parallaxmod = self.parallax - state.cam.depth
            pygame.draw.rect(state.display,(200,100,50),((self.pos[0]-state.cam.pos[0]*parallaxmod)*state.scaleamt,(self.pos[1]-state.cam.pos[1]*parallaxmod)*state.scaleamt,self.size[0]*state.scaleamt,self.size[1]*state.scaleamt),int(state.tilesize*state.scaleamt/2))
        
    def update(self):
        self.render()
        self.getpoints()

    def collidefunction(self,trigger):
        self.triggers.append(trigger)
        if type(trigger) == Player:
            state.cam.pos = self.pos.copy()
            if self not in state.cam.locks:
                state.cam.locks.append(self)
            for item in state.objects:
                if hasattr(item,"fightStart") and self.checkobjcollide(self,item) and not item.active:
                    item.fightStart()
    
class Boss(Enemy):
    def __init__(self,locus,depth,parallax,name,layer,extras):
        super().__init__(locus,depth,parallax,name,layer,extras)
        self.trueBehavior = self.behavior.copy()
        self.behavior = state.aisource["BossWait"]
        self.active = False
        
    def update(self):
        super().update()
        if self.behavior == self.trueBehavior:
            state.HUD.blit(state.font.render(f"Boss HP:{self.health}",False,[255,0,100],[0,0,0]),(30*state.scaleamt,150*state.scaleamt))
        if self.iframes > 0:
            self.iframes -= state.deltatime

    def fightStart(self):
        self.actionqueue = [[0,["nothing",None],["time",120,0]]]
        self.behavior = self.trueBehavior
        self.stun = False
        self.animname = "Intro"
        self.requestanim = True
        self.active = True
        
    def damagetake(self,dmg):
        if self.health > 0:
            if self.iframes <= 0:
                self.health -= dmg
                self.animname = "Hurt"
                self.requestanim = True
                self.iframes = 90
                self.actionqueue.append([0,["walk",10*self.direction],[None,None,True]])
                self.actionqueue.append([0,["jump",20],[None,None,True]])
                self.actionqueue.append([0,["stun",dmg],[None,None,True]])
                self.actionqueue.append([30,["destun",dmg],[None,None,True]])
                #apply stun pallate after a while. Maybe we replace this with a flicker function?
                self.actionqueue.append([35,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([40,["deTempPallate",None],[None,None,True]])
                self.actionqueue.append([45,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([50,["deTempPallate",None],[None,None,True]])
                self.actionqueue.append([55,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([60,["deTempPallate",None],[None,None,True]])
                self.actionqueue.append([65,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([70,["deTempPallate",None],[None,None,True]])
                self.actionqueue.append([75,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([80,["deTempPallate",None],[None,None,True]])
                self.actionqueue.append([85,["tempPallate","Stun"],[None,None,True]])
                self.actionqueue.append([90,["deTempPallate",None],[None,None,True]])
            if self.health <= 0:
                self.kill()
class oneWay(gameObject):
    def __init__(self,locus,depth,parallax,name,layer,extras):
        super().__init__(locus,depth,parallax,layer,extras)
        if hasattr(self.extras,"size"):
            self.size = self.extras["size"]
        else:
            self.size = [120,3600]
        self.name = name
        if hasattr(self.extras,"axis"):
            self.axis = self.extras["axis"]
        else:
            self.axis = "left"
        self.getpoints()

    def update(self):
        self.getpoints()
        self.render()
        
    def collidefunction(self,trigger):
        match self.axis:
            case "left":
                if trigger.right[0] >= self.left[0] and trigger.left[0] <= self.left[0] and trigger.speed[0] > 0:
                    trigger.pos[0] = self.left[0] - trigger.size[0]
                    trigger.blockedright = True
            case "right":
                if trigger.left[0] <= self.right[0] and trigger.right[0] >= self.right[0] and trigger.speed[0] < 0:
                    trigger.pos[0] = self.right[0]
                    trigger.blockedleft = True
    def render(self):
        pass
        #parallaxmod = self.parallax - state.cam.depth
        #pygame.draw.rect(state.display,(100,50,100),(self.pos[0]-state.cam.pos[0]*parallaxmod,self.pos[1]-state.cam.pos[1]*parallaxmod,self.size[0],self.size[1]))
        
