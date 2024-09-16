"""
Filename: objects.py
Author(s): Talieisn Reese
Version: 1.0
Date: 9/9/2024
Purpose: object classes for "MathWiz!"
"""
import pygame
import GameData as state
import json
import tilecollisions
import moves

#basic class to build other objects onto
class gameObject:
    def __init__(self, locus, depth):
        self.pos = locus
        self.depth = depth
        self.speed = [0,0]
        #add to list of objects that are updated every frame
        state.objects.append(self)
        #resort list to ensure objects are rendered in the correct order
        state.objects.sort(key = lambda item: item.depth)
    #remove self from object list
    def delete(self):
        state.objects.remove(self)

#slightly less basic class to build characters on--players, enemies, moving platforms, bosses, etc.
class character(gameObject):
    def __init__(self,locus,depth,name):
        super().__init__(locus,depth)
        #extra variables handle things unique to objects with more logic: movement, gravity, grounded state, etc.
        self.speed = [0,0]
        self.direction = 1
        self.maxfall = 150
        self.maxspeed = 20
        self.gravity = 15
        self.grounded = True
        self.actiontimer = 0
        self.name = name
        self.size = state.objectsource[name]["Sizes"]["Default"]
        #sprite used to show player. Replace these calls with animation frame draws
        self.sprite = pygame.Surface(self.size)
        self.sprite.fill((255,0,0))
        pygame.draw.rect(self.sprite,(255,255,255),((self.size[0]-20),self.size[1]/4,20,20))

    #run every frame to update the character's logic    
    def update(self):
        self.physics()
        self.move()
        self.collide()
        self.render()
        
    #calcualte the points to use in collision detection
    def getpoints(self):
        self.left = [self.pos[0],self.pos[1]+self.size[1]/2]
        self.right = [self.pos[0]+self.size[0],self.pos[1]+self.size[1]/2]
        self.top = [self.pos[0]+self.size[0]/2,self.pos[1]]
        self.bottom = [self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]]

    #check if a point is colliding with the ground. Add logic for moving platforms later
    def pointcollide(self, point):
        #get the tile that the point is positioned on
        tile = [int(point[0]//state.tilesize),int(point[1]//state.tilesize)]
        #get values from said tile
        try:
            tiletype = state.level.tilemap[self.depth][tile[1]][tile[0]]
            tileflip = state.level.flipmap[self.depth][tile[1]][tile[0]]
            tilerotate = state.level.spinmap[self.depth][tile[1]][tile[0]]
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
        if state.tilesource["terraintypes"][tiletype] == 1:
            return tilecollisions.solid((x,y))
        elif state.tilesource["terraintypes"][tiletype] == 2:
            return tilecollisions.fortyfive((x,y))
        elif state.tilesource["terraintypes"][tiletype] == 3:
            return tilecollisions.lowtwentytwo((x,y))
        elif state.tilesource["terraintypes"][tiletype] == 4:
            return tilecollisions.hightwentytwo((x,y))
        elif state.tilesource["terraintypes"][tiletype] == 5:
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
        elif self.speed[0] < 0:
            self.speed[0] += 4*state.deltatime
        if abs(self.speed[0] < 1):
            self.speed[0] = 0
            
    #pretty self-explanitory: add the movement speed to the character        
    def move(self):
        self.pos[1]+= self.speed[1]*state.deltatime
        self.pos[0]+= self.speed[0]*state.deltatime

    #check for collisions on all four points. if a collision is found, find how far the point is into the ground and move it so that it is only 1px of less deep.  
    def collide(self):
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
            while True:
                if self.pointcollide([self.bottom[0],self.bottom[1]+dist]) != True:
                    dist += 1
                else:
                    if dist < abs(self.speed[0]):
                        self.pos[1] += dist-1
                        self.grounded = True
                        self.getpoints()
                    break
        #if the top point is blocked, the character is bumping into a ceiling    
        self.topblock =  self.pointcollide(self.top)
        if self.topblock:
            dist = 1
            while True:
                if not self.pointcollide([self.top[0],self.top[1]+dist]):
                    self.pos[1]+=dist-1
                    self.getpoints()
                    break
                dist += 1
        #if rthe left or right points are blocked, the character is pressing against a wall on that side
        self.leftblock =  self.pointcollide(self.left)
        if self.leftblock:
            dist = 1
            while True:
                if not self.pointcollide([self.left[0]+dist,self.left[1]]):
                    self.pos[0]+=dist-1
                    self.getpoints()
                    break
                dist += 1
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
        if self.direction == 1:
            state.display.blit(self.sprite,[self.pos[0]-state.cam.pos[0],self.pos[1]-state.cam.pos[1]])
        else:
            state.display.blit(pygame.transform.flip(self.sprite,True,False),[self.pos[0]-state.cam.pos[0],self.pos[1]-state.cam.pos[1]])
        
class Player(character):
    #this update is the same as the one for generic characters, but it allows the player to control it.
    def update(self):
        self.physics()
        self.playerControl()
        #print(self.speed)
        self.move()
        self.collide()
        self.render()
    #perform moves from the moves library based on the status of input
    def playerControl(self):
        #run the jump function if the spacebar is down
        if state.keys[pygame.K_SPACE] or pygame.K_SPACE in state.newkeys:
            moves.jump(self,125)
        #walk left or right if the a or d keys are pressed. Swap directions accordingly unless the shift key is held.
        if state.keys[pygame.K_a]:
            if not state.keys[pygame.K_LSHIFT] and not state.keys[pygame.K_RSHIFT]:
                self.direction = -1
            moves.walk(self,-150)
        if state.keys[pygame.K_d]:
            if not state.keys[pygame.K_LSHIFT] and not state.keys[pygame.K_RSHIFT]:
                self.direction = 1
            moves.walk(self,150)
            
