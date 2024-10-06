"""
Filename: objects.py
Author(s): Talieisn Reese
Version: 1.2
Date: 10/2/2024
Purpose: object classes for "MathWiz!"
"""
import pygame
import GameData as state
import json
import tilecollisions
import moves
from functools import partial

#basic class to build other objects onto
class gameObject:
    def __init__(self, locus, depth, parallax):
        self.pos = locus
        self.lastpos = locus
        self.depth = depth
        self.parallax = parallax
        self.speed = [0,0]
        #add to list of objects that are updated every frame
        state.objects.append(self)
        #resort list to ensure objects are rendered in the correct order
        state.objects.sort(key = lambda item: item.depth, reverse = True)
    #remove self from object list
    def delete(self):
        state.objects.remove(self)

#slightly less basic class to build characters on--players, enemies, moving platforms, bosses, etc.
class character(gameObject):
    def __init__(self,locus,depth,parallax,name):
        super().__init__(locus,depth,parallax)
        #extra variables handle things unique to objects with more logic: movement, gravity, grounded state, etc.
        self.speed = [0,0]
        self.direction = 1
        self.maxfall = 50
        self.maxspeed = 20
        self.gravity = 10
        self.grounded = True
        self.actiontimer = 0
        self.name = name
        self.size = state.objectsource[name]["Sizes"]["Default"]
        #determine points for collision
        self.getpoints()
        self.lastbottom = self.bottom.copy()
        self.lasttop = self.top.copy()
        self.lastleft = self.left.copy()
        self.lastright = self.right.copy()
        #the action queue is used to hold the current action.
        self.actionqueue = []
        #a dictionary of hurtboxes that this object can spawn--a dictionary is used so that we can activate and deactivate them by name. Will likely be used more for enemies than for MathWiz himself
        self.hurtboxes = {}
        #sprite used to show player. Replace these calls with animation frame draws
        self.sprite = pygame.Surface(self.size)
        self.sprite.fill((255,0,0))
        pygame.draw.rect(self.sprite,(255,255,255),((self.size[0]-20),self.size[1]/4,20,20))

    #run every frame to update the character's logic    
    def update(self):
        self.actionupdate()
        self.physics()
        self.move()
        self.collide()
        self.render()
        self.lastpos = self.pos.copy()
        self.lastbottom = self.bottom.copy()
        self.lasttop = self.top.copy()
        self.lastleft = self.left.copy()
        self.lastright = self.right.copy()

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
                        if getattr(self,action[2][1]) == action[2][2]:
                            self.actionqueue.remove(action)
                    case "keys":
                        if state.keys[action[2][1]] == action[2][2]:
                            self.actionqueue.remove(action)
                    #remove the action immediately if the source isn't found
                    case _:
                        self.actionqueue.remove(action)
            
        
    #calcualte the points to use in collision detection
    def getpoints(self):
        self.left = [self.pos[0],self.pos[1]+self.size[1]/2]
        self.right = [self.pos[0]+self.size[0],self.pos[1]+self.size[1]/2]
        self.top = [self.pos[0]+self.size[0]/2,self.pos[1]]
        self.bottom = [self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]]

    #check if a point is colliding with the ground. Add logic for moving platforms later
    def pointcollide(self, point):
        #find layers to do collision on:
        for item in state.objects:
            if type(item).__name__ == "drawlayer" and item.parallax == self.parallax:
                #get the tile that the point is positioned on
                tile = [int(point[0]//state.tilesize),int(point[1]//state.tilesize)]
                #get values from said tile
                try:
                    #UNLESS the layer is supposed to loop--THEN simply loop the information from the list
                    if item.loop == True:
                        tile = [tile[0]%(item.longest), tile[1]%(len(state.level.tilemap[item.layernum]))]
                    tiletype = state.level.tilemap[item.layernum][tile[1]][tile[0]]
                    tileflip = state.level.flipmap[item.layernum][tile[1]][tile[0]]
                    tilerotate = state.level.spinmap[item.layernum][tile[1]][tile[0]]
                #unless it doesn't exist. Then, treat it as if it were solid to prevent out-of-bounds errors
                except:
                    tiletype = 1
                    tileflip = 0
                    tilerotate = 0
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

    #determine collision based on the vectors surrounding level geometry--this should become standard issue.
    #this could be far more efficient if we cull vectors based on ineligibility for collision.
    def vectorpointhandlecollide(self,vector,axis,polarity):
        for item in state.objects:
            #get the linedata of the layers that the player should collide with
            if type(item).__name__ == "drawlayer" and item.parallax == self.parallax:
                linedata = item.linemap
                for line in linedata:
                    #if the stage is set to loop, compensate for the player's position.
                    #this modifier determines how much the offset of an object should be affected by it's distance from the camera in z space...sort of.
                    if item.loop:
                        screenplacemod = [((self.pos[0])//item.width)*item.width,
                                        ((self.pos[1])//item.height)*item.height]
                    else:
                        screenplacemod = (0,0)
                    #print(screenplacemod)
                    line = [[line[0][0]+screenplacemod[0],line[0][1]+screenplacemod[1]],
                            [line[1][0]+screenplacemod[0],line[1][1]+screenplacemod[1]]]
                    collidepoint = self.vectorcollide(vector,line)
                    if collidepoint != None:
                        difference = [vector[1][0]-self.pos[0],vector[1][1]-self.pos[1]]
                        collidedif = vector[0][axis] - vector[1][axis]
                        try:
                            if polarity == collidedif/abs(collidedif):
                                self.pos[axis] = collidepoint[axis]-difference[axis]
                                vector = (vector[0],[collidepoint[0],collidepoint[1]])
                                self.getpoints()
                        except ZeroDivisionError:
                            pass

    #then,check collisions
    def vectorcollide(self,vector,line):
        #calculate the slopes of both lines
        #get offset of function. If it is a vertical line, offset behaves slightly different: it is the x value.
        try:
            moveslope = (vector[0][1]-vector[1][1])/(vector[0][0]-vector[1][0])
            moveoffset = vector[0][1]-moveslope*vector[0][0]
        except ZeroDivisionError:
            moveslope = "cringe"
            moveoffset = vector[0][0]
        try:
            lineslope = (line[0][1]-line[1][1])/(line[0][0]-line[1][0])
            lineoffset = line[0][1]-lineslope*line[0][0]
        except ZeroDivisionError:
            lineslope = "cringe"
            lineoffset = line[0][0]
        text = pygame.font.SysFont("Comic Sans MS", 100)
        state.display.blit(text.render(f"{lineslope}", 0, (255,0,0)),(line[0][0],line[0][1]))


        """if lineslope == 0 and line[0][1]==2520:
            print(round(vector[0][1]),vector[0][1])"""
            
        #find point that would lie on both lines if they were infinite
        if lineslope == "cringe":
            if moveslope == "cringe":
                #special contingency if both lines are vertical
                if lineoffset == moveoffset:
                    if line[0][1]>=vector[0][1] and line[0][1]<=vector[1][1]:
                        return (lineoffset,line[0][1])
                    elif line[1][1]>=vector[0][1] and line[1][1]<=vector[1][1]:
                        return (lineoffset,line[0][1])
                    else:
                        return None
                else:
                    return None
            else:
                y = lineoffset*moveslope+moveoffset
                point = (lineoffset,y)
                #if point is actually in both lines:
                if (point[1] <= line[0][1] and point[1] >= line[1][1]) or (point[1] >= line[0][1] and point[1] <= line[1][1]):
                    if (point[1] <= vector[0][1] and point[1] >= vector[1][1]) or (point[1] >= vector[0][1] and point[1] <= vector[1][1]):
                        if (point[0] <= line[0][0] and point[0] >= line[1][0]) or (point[0] >= line[0][0] and point[0] <= line[1][0]):
                            if (point[0] <= vector[0][0] and point[0] >= vector[1][0]) or (point[0] >= vector[0][0] and point[0] <= vector[1][0]):
                                #return that point
                                return point
                return None

        else:
            if moveslope == "cringe":
                #special contingency for vertical moveslope
                if moveoffset <= line[0][0] and moveoffset >= line [1][0] or moveoffset >= line[0][0] and moveoffset <= line [1][0]:
                    y = moveoffset*lineslope+lineoffset
                    if (y <= vector[0][1] and y >= vector[1][1]) or (y >= vector[0][1] and y <= vector[1][1]):
                        return (moveoffset,y)
                    else:
                        return None
                else:
                    return None
            else:
                if moveslope == lineslope:
                    #special contingency for two lines with the same slope
                    if moveoffset == lineoffset:
                        xtru,ytru = False,False
                        if (line[0][1]>=vector[0][1] and line[0][1]>=vector[1][1])or(line[1][1]>=vector[0][1] and line[1][1]>=vector[1][1]):
                            ytru = True
                        if (line[0][0]>=vector[0][0] and line[0][0]>=vector[1][0])or(line[1][0]>=vector[0][0] and line[1][0]>=vector[1][0]):
                            xtru = True
                        if xtru and ytru:
                            return (vector[1])
                        else:
                            return None
                    else:
                        return None
                else:
                    x = (lineoffset-moveoffset)/(moveslope-lineslope)
                    #contingency plan for horizontal lines
                    if lineslope == 0:
                        y = line[0][1]
                    else:
                        y = moveslope*x+moveoffset
                    point = (x,y)
                    #pygame.draw.rect(state.display,(0,255,0), [point[0]-8,point[1]-8,16,16])
                    #if point is actually in both lines:
                    if (point[1] <= line[0][1] and point[1] >= line[1][1]) or (point[1] >= line[0][1] and point[1] <= line[1][1]):
                        if (point[1] <= vector[0][1] and point[1] >= vector[1][1]) or (point[1] >= vector[0][1] and point[1] <= vector[1][1]):
                            if (point[0] <= line[0][0] and point[0] >= line[1][0]) or (point[0] >= line[0][0] and point[0] <= line[1][0]):
                                if (point[0] <= vector[0][0] and point[0] >= vector[1][0]) or (point[0] >= vector[0][0] and point[0] <= vector[1][0]):
                                    #return that point
                                    return point
                    #by default, return nothing
                    return None

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
        elif self.speed[0] < 0:
            self.speed[0] += 4*state.deltatime
        if abs(self.speed[0] < 1):
            self.speed[0] = 0
            
    #pretty self-explanitory: add the movement speed to the character        
    def move(self):
        self.pos[1] += self.speed[1]*state.deltatime
        self.pos[0] += self.speed[0]*state.deltatime
        self.pos = [round(self.pos[0]),round(self.pos[1])]

    #check for collisions on all four points. if a collision is found, find how far the point is into the ground and move it so that it is only 1px of less deep.  
    def collide(self):
        self.vectorpointhandlecollide((self.lastbottom,self.bottom),1,-1)
        self.getpoints()
        #if the bottom point is blocked, the player is on the ground
        self.grounded = self.pointcollide([self.bottom[0],self.bottom[1]])
        if self.grounded:
            dist = 1
            while True:
                if self.pointcollide([self.bottom[0],self.bottom[1]-dist]) == True:
                    dist += 1
                else:
                    self.pos[1] -= dist-1
                    self.getpoints()
                    break
        #this check is exclusive to the bottom point. If the distance to the ground is less than the current forwards momentum, snap player to the ground.
        else:
            dist = 1
            while dist < abs(self.speed[0]):
                if self.pointcollide([self.bottom[0],self.bottom[1]+dist]) != True:
                    dist += 1
                else:
                    if dist < abs(self.speed[0]):
                        self.pos[1] += dist-1
                        self.grounded = True
                        self.getpoints()
                    break

        #if the top point is blocked, the character is bumping into a ceiling
        self.vectorpointhandlecollide((self.lasttop,self.top),1,1)
        self.getpoints()
        self.topblock =  self.pointcollide(self.top)
        if self.topblock:
            dist = 1
            while True:
                if not self.pointcollide([self.top[0],self.top[1]+dist]):
                    self.pos[1]+=dist-1
                    self.getpoints()
                    break
                dist += 1
        #if the left or right points are blocked, the character is pressing against a wall on that side
        self.vectorpointhandlecollide((self.lastleft,self.left),0,1)
        self.getpoints()
        self.leftblock =  self.pointcollide(self.left)
        if self.leftblock:
            dist = 1
            while True:
                if not self.pointcollide([self.left[0]+dist,self.left[1]]):
                    self.pos[0]+=dist-1
                    self.getpoints()
                    break
                dist += 1
                
        self.vectorpointhandlecollide((self.lastright,self.right),0,-1)
        self.getpoints()
        self.rightblock =  self.pointcollide(self.right)
        if self.rightblock:
            dist = 1
            while True:
                if not self.pointcollide([self.right[0]-dist,self.right[1]]):
                    self.pos[0]-=dist-1
                    self.getpoints()
                    break
                dist += 1
                
    #Draw the player sprite to the canvas in the correct position
    def render(self):
        parallaxmod = self.parallax - state.cam.depth
        if True:#self.direction == 1:
            state.display.blit(self.sprite,[self.pos[0]-state.cam.pos[0]*parallaxmod,self.pos[1]-state.cam.pos[1]*parallaxmod])
        else:
            state.display.blit(pygame.transform.flip(self.sprite,True,False),[self.pos[0]-state.cam.pos[0],self.pos[1]-state.cam.pos[1]])
        
class Player(character):
    #this update is the same as the one for generic characters, but it allows the player to control it.
    def update(self):
        if state.gamemode != "edit":
            self.physics()
            self.playerControl()
            self.actionupdate()
            #print(self.speed)
            self.move()
            self.collide()
            #state.cam.focus = self.pos#(4250,3120)
        self.render()
        self.lastpos = self.pos.copy()
        self.lastbottom = self.bottom.copy()
        self.lasttop = self.top.copy()
        self.lastleft = self.left.copy()
        self.lastright = self.right.copy()

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
        if pygame.K_h in state.newkeys:
            self.actionqueue.append([60,["jump",150],["keys",pygame.K_h,True]])
            
