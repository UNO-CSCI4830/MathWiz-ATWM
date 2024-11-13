"""
Filename: objects.py
Author(s): Talieisn Reese, Vladislav Plotnikov, Drew Scebold, Zaid Kakish, Logan Jenison, John Millar
Version: 1.17
Date: 11/10/2024
Purpose: object classes for "MathWiz!"
"""
import pygame
import json
import tilecollisions
import moves
import random
from functools import partial
from copy import deepcopy

import GameData as state

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
            if state.camera.focusobj == self:
                state.camera.focusobj = None
        except:
            pass

#slightly less basic class to build characters on--players, enemies, moving platforms, bosses, etc.
class character(gameObject):
    def __init__(self,locus,depth,parallax,name, layer, extras):
        #extra data used for individual object types
        self.data = state.objectsource[name]
        super().__init__(locus,depth,parallax, layer, extras)
        #extra variables handle things unique to objects with more logic: movement, gravity, grounded state, etc.
        self.movement = [0,0]
        self.direction = 1
        self.lastdirection = 1
        self.maxfall = 50
        self.maxspeed = 20
        self.gravity = 10
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
        self.sprite = pygame.Surface(self.size)
        self.colorbrush = pygame.Surface(self.size)
        self.sprite.set_colorkey(state.invis)
        self.pallate = "Default"
        self.storepal = "Default"
        #stuff for animation
        self.animname = "Idle"
        self.lastanim = "Idle"
        self.animframe = 0
        self.animtime = 0
        self.requestanim = False
        if state.gamemode == "edit":
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
        #allegience value for projectile and damage collisions.
        self.allegience = "Enemy"

    #run every frame to update the character's logic    
    def update(self):
        self.lastanim = self.animname
        self.lastpos = self.pos.copy()
        self.lastbottom = self.bottom.copy()
        self.lasttop = self.top.copy()
        self.lastleft = self.left.copy()
        self.lastright = self.right.copy()
        self.lastdir = self.direction
        self.actionupdate()
        self.getpoints()
        if self in state.objects:
            self.physics()
            self.movement = [self.speed[0]*state.deltatime,self.speed[1]*state.deltatime]
            while self.movement != [0,0]:
                self.move()
                self.collide()
                self.objcollide()
            self.objcollide()
            self.collide()
            for item in self.children:
                item.pos[0] = item.pos[0]+(self.pos[0]-self.lastpos[0])
                item.pos[1] = item.pos[1]+(self.pos[1]-self.lastpos[1])
            self.render()

    def actionupdate(self):
        #iterate through every action in the queue.
        for action in self.actionqueue:
            #if the action has a starttimer above zero, iterate that down a peg.
            if action[0] > 0:
                action[0] -= state.deltatime
            #otherwise, do the thing.
            else:
                getattr(moves,action[1][0])(self, action[1][1])
                #if the action's popcondidtion is met, pull it from the queue and skip.
                match action[2][0]:
                    case "self":
                        if getattr(self,action[2][1]) == action[2][2]:
                            self.actionqueue.remove(action)
                    case "state":
                        if getattr(state,action[2][1]) == action[2][2]:
                            self.actionqueue.remove(action)
                    case "keys":
                        if state.keys[action[2][1]] == action[2][2]:
                            self.actionqueue.remove(action)
                    case "time":
                        if action[2][1] <= 0:
                            self.actionqueue.remove(action)
                        else:
                            action[2][1] -= state.deltatime
                    #remove the action immediately if the source isn't found
                    case _:
                        self.actionqueue.remove(action)

    def kill(self):
        if getattr(moves,f"die{self.deathtype}") != None:
            getattr(moves,f"die{self.deathtype}")(self,None)
        else:
            moves.dieDefault(self,None)
        
    def animationpick(self):
        #OVERRIDE: If specially requested, play that animation until completion.
        if self.requestanim == False:
            #if nonxero speed on x-axis and grounded, return the walking animation
            if self.grounded:
                if abs(self.speed[0]) > 0:
                    self.animname = "Walk"
                #by default, return the idle animation
                else:
                    self.animname = "Idle"
            #if not grounded and going up, retun jumping animation
            elif self.grounded == False:
                #if notgrounded and falling down, return falling animation
                if self.speed[1] >= 0:
                    self.animname = "Fall"
                else:
                    self.animname = "Jump"
        if self.animname != self.lastanim:
            self.animtime = 0
            self.animframe = 0
        
    def animationupdate(self):
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
            self.sprite.blit(state.spritesheet, self.info["Frames"][anim[self.animframe][0]][4:],(self.info["Frames"][anim[self.animframe][0]][:4]))
            self.sprite = pygame.transform.rotate(pygame.transform.flip(self.sprite,anim[self.animframe][1][0],anim[self.animframe][1][1]),anim[self.animframe][2])
            
            #get the sprite drawn with the correct palatte
            #optimize this later
            if self.pallate != "Default":
                for color in range(len(state.infosource[self.infoname]["Pallates"][self.pallate])):
                    self.colorbrush.fill(state.infosource[self.infoname]["Pallates"][self.pallate][color])
                    self.sprite.set_colorkey(state.infosource[self.infoname]["Pallates"]["Default"][color])
                    self.colorbrush.blit(self.sprite,(0,0))
                    self.sprite.blit(self.colorbrush,(0,0))
                self.sprite.set_colorkey(state.invis)
            
    #calcualte the points to use in collision detection
    def getpoints(self):
        self.left = [self.pos[0],int(self.pos[1]+self.size[1]/2)]
        self.right = [self.pos[0]+self.size[0],int(self.pos[1]+self.size[1]/2)]
        self.top = [int(self.pos[0]+self.size[0]/2),self.pos[1]]
        self.bottom = [int(self.pos[0]+self.size[0]/2),self.pos[1]+self.size[1]]

    #check if a point is colliding with the ground. Add logic for moving platforms later
    def pointcollide(self, point):
        #find layers to do collision on:
        for item in state.objects:
            if type(item).__name__ == "drawlayer" and item.layernum == self.layer:
                #get the tile that the point is positioned on
                tile = [int(point[0]//state.tilesize),int(point[1]//state.tilesize)]
                #get values from said tile
                #UNLESS the layer is supposed to loop--THEN simply loop the information from the list
                if item.loop == True:
                    tile = [tile[0]%(item.longest), tile[1]%(len(state.level.tilemap[item.layernum]))]
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
            if self.speed[1] < self.maxfall:
                self.speed[1] += self.gravity*state.deltatime
        #otherwise, don't add gravity at all. doing so would cause the player to gain fallspeed while they stood, and causes them to fall like a ton of bricks if the ground ceases to hold them (i.e. they walk off a ledge)
        else:
            self.speed[1] = 0
        #decrease move speed    
        if self.speed[0] > 0:
            self.speed[0] -= 4*state.deltatime
            if (self.speed[0]) < 1:
                self.speed[0] = 0
        elif self.speed[0] < 0:
            self.speed[0] += 4*state.deltatime
            if (self.speed[0]) > -1:
                self.speed[0] = 0
            
    #pretty self-explanitory: add the movement speed to the character        
    def move(self):
        if abs(self.movement[1]) > state.movetickamount:
            if self.movement[1] > 0:
                self.pos[1] += state.movetickamount
                self.movement[1]-=state.movetickamount
            elif self.movement[1] < 0:
                self.pos[1] -= state.movetickamount
                self.movement[1]+=state.movetickamount
            if abs(self.movement[1]) < 1:
                self.movement[1] = 0
        else:
            self.pos[1] += self.movement[1]
            self.movement[1] = 0

        if abs(self.movement[0]) > state.movetickamount:
            if self.movement[0] > 0:
                self.pos[0] += state.movetickamount
                self.movement[0]-=state.movetickamount
            elif self.movement[0] < 0:
                self.pos[0] -= state.movetickamount
                self.movement[0]+=state.movetickamount
            if abs(self.movement[0]) < 1:
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
        if self in state. objects:
            for thing in state.objects:
                if type(thing).__name__ != "drawlayer" and thing != self and thing.layer == self.layer:
                    if self.checkobjcollide(self,thing):
                        thing.collidefunction(self)
    
    def collidefunction(self,trigger):
        pass

    def damagetake(self,dmg):
        pass
                
    #Draw the player sprite to the canvas in the correct position
    def render(self):
        parallaxmod = self.parallax - state.cam.depth
        if self.direction == 1:
            state.display.blit(self.sprite,[self.pos[0]-state.cam.pos[0]*parallaxmod,self.pos[1]-state.cam.pos[1]*parallaxmod])
        else:
            state.display.blit(pygame.transform.flip(self.sprite,True,False),[self.pos[0]-state.cam.pos[0],self.pos[1]-state.cam.pos[1]])

class spawner(gameObject):
    def __init__(self,locus,depth,parallax,name, layer, extras):
        super().__init__(locus,depth,parallax, layer, extras)
        self.name = name
        self.data = state.objectsource[name]
        self.size = [0,0]
        character.getpoints(self)
        
        self.delcond = self.data.get("DeleteCondition")
        self.spawncond = self.data.get("SpawnCondition")
        self.spawntype = self.data.get("Spawntype")
        self.spawnees = self.data.get("Objlist")
        self.spawnedobjs = []

    def render(self):
        parallaxmod = self.parallax - state.cam.depth
        pygame.draw.rect(state.display,(255,255,0),(self.pos[0]-state.cam.pos[0]*parallaxmod,self.pos[1]-state.cam.pos[1]*parallaxmod,20,20))
        
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
        self.text = extras[0]
        #self.sprite.fill((100,100,0))
    def update(self):
        super().update()
        self.animationupdate()
        self.sprite.blit(state.font.render(self.text,False,(255,255,180)),(40,40))
    
        
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
        self.actionqueue.append([60,["delete",None],[None,None,True]])
        
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
            self.actionqueue.append([60,["delete",None],[None,None,True]])
            
class Hitbox(gameObject):
    def __init__(self,locus,depth,parallax, layer, extras):
        self.offset = locus
        self.size = extras[0]
        self.mode = extras[1]
        self.amt = extras[2]
        self.lifespan = extras[3]
        self.parent = extras[4]
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
        parallaxmod = self.parallax - state.cam.depth
        pygame.draw.rect(state.display,color,(self.pos[0]-state.cam.pos[0]*parallaxmod,self.pos[1]-state.cam.pos[1]*parallaxmod,self.size[0],self.size[1]))

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
        super().__init__([extras[0].pos[0]+locus[0],extras[0].pos[1]+locus[1]],depth,parallax,name,layer,extras)
        
        self.gravity = 0
        self.blockable = True
        self.allegience = extras[0].allegience
        self.direction = extras[0].direction
        self.damage = 10
        if extras[0].direction == 1:
            self.movespeed = [50,0]
        else:
            self.movespeed = [-50,0]
        self.persistence = False
        self.lifespan = 60

    def update(self):
        super().update()
        self.speed[0] = self.movespeed[0]
        #update the lifespan timer, and remove the object if it's number is up.
        if type(self.lifespan) in (int,float):
            self.lifespan -= state.deltatime
            if self.lifespan <= 0:
                self.delete()
        if self.leftblock or self.rightblock or self.topblock or self.grounded:
            if not self.persistence:
                self.delete()

    def render(self):
        parallaxmod = self.parallax - state.cam.depth
        pygame.draw.rect(state.display,(200,50,50),(self.pos[0]-state.cam.pos[0]*parallaxmod,self.pos[1]-state.cam.pos[1]*parallaxmod,self.size[0],self.size[1]))
                
    def collidefunction(self,trigger):
        if self.allegience != trigger.allegience:
            #print(type(trigger))#.allegience)
            if hasattr(trigger,"damagetake"):
                trigger.damagetake(self.damage)
            if not self.persistence:
                self.delete()
            
class Player(character):
    def __init__(self,locus,depth,parallax,name,layer,extras):
        super().__init__(locus,depth,parallax,name,layer,extras)
        self.abilities = ["Default","MMissile"]
        self.weap = "Default"
        self.health = 100
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
            if not self.stun:
                self.playerControl()
            self.actionupdate()
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
        for item in self.children:
            item.pos[0] = item.pos[0]+(self.pos[0]-self.lastpos[0])
            item.pos[1] = item.pos[1]+(self.pos[1]-self.lastpos[1])
        state.HUD.blit(state.font.render(f"HP:{self.health}",False,[255,255,255],[0,0,0]),(30,30))
        if self.health <= 0:
            state.HUD.blit(state.font.render(f"Game Over",False,[255,0,0],[0,0,0]),(1800,1800))
        self.animationpick()
        self.animationupdate()
        self.render()

    #perform moves from the moves library based on the status of input
    def playerControl(self):
        #run the jump function if the spacebar is down
        if state.keys[pygame.K_SPACE]:
            if pygame.K_SPACE in state.newkeys and self.grounded == True:
                #moves.jump(self,100)
                self.actionqueue.append([0,["jump",100],[None,None,True]])
            else:
                self.actionqueue.append([0,["jumpstall",100],[None,None,True]])
        #walk left or right if the a or d keys are pressed. Swap directions accordingly unless the shift key is held.
        if state.keys[pygame.K_a]:
            if not state.keys[pygame.K_LSHIFT] and not state.keys[pygame.K_RSHIFT]:
                self.direction = -1
            moves.walk(self,-20)
        if state.keys[pygame.K_d]:
            if not state.keys[pygame.K_LSHIFT] and not state.keys[pygame.K_RSHIFT]:
                self.direction = 1
            moves.walk(self,20)
        if pygame.K_q in state.newkeys:
            self.actionqueue.append([0,["cyclepower",-1],[None,None,True]])
        if pygame.K_e in state.newkeys:
            self.actionqueue.append([0,["cyclepower",1],[None,None,True]])
        if pygame.K_f in state.newkeys:
            self.actionqueue.append([0,[f"weap{self.weap}",None],[None,None,True]])
        #test damage
        if pygame.K_m in state.newkeys:
            self.damagetake(10)

    def damagetake(self,dmg):
        if self.health > 0:
            if not self.stun:
                self.health -= dmg
                self.animname = "Fall"
                self.requestanim = True
                self.actionqueue.append([0,["walk",10],[None,None,True]])
                self.actionqueue.append([0,["jump",20],[None,None,True]])
                self.actionqueue.append([0,["stun",dmg],[None,None,True]])
                self.actionqueue.append([30,["destun",dmg],[None,None,True]])
            if self.health <= 0:
                self.kill()

class Enemy(character):
    def __init__(self,locus,depth,parallax,name,layer,extras):
        super().__init__(locus,depth,parallax,name,layer,extras)
        if extras != [""]:
            self.behavior = state.aisource[extras[0]]
        else:
            self.behavior = [[0,["nothing","nothing"],[None,None,False]]]
        self.health = 100
        self.gravity = 50
        self.grounded = False
        self.pallate = "Shadow"
        #find player to target
        for obj in state.objects:
            if "Player" in str(obj):
                self.target = obj
        # pygame.draw.rect(self.sprite,(255,255,255),((self.size[0]-20),self.size[1]/4,20,20))

    def update(self):
        self.lastanim = self.animname
        self.lastpos = self.pos.copy()
        self.lastbottom = self.bottom.copy()
        self.lasttop = self.top.copy()
        self.lastleft = self.left.copy()
        self.lastright = self.right.copy()
        self.lastdir = self.direction
        self.physics()
        self.actionupdate()
        # the idea here for later on is enemy names will be tied to a different ai procedure
        # for instance, here the "test-enemy" is the "follow" AI, but a "crab" enemy could also have "follow"
        # at least, it was the idea but it seems each enemy has to be a different object in objects.json. oh well
        if not self.stun:
            if self.actionqueue == []:
                self.actionqueue = deepcopy(self.behavior)
        # also need to make the hitbox constant
        self.movement = [self.speed[0]*state.deltatime,self.speed[1]*state.deltatime]
        while self.movement != [0,0]:
            self.move()
            self.collide()
            self.groundsnap()
            self.objcollide()
        self.objcollide()
        self.collide()
        self.groundsnap()
        for item in self.children:
            item.pos[0] = item.pos[0]+(self.pos[0]-self.lastpos[0])
            item.pos[1] = item.pos[1]+(self.pos[1]-self.lastpos[1])
        self.animationpick()
        self.animationupdate()
        self.render()
        
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
            self.actionqueue = [[0,["dieDefault",None],[None,None,True]]]
            
