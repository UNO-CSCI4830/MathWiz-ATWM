"""
Filename: level.py
Author(s): Taliesin Reese
Verion: 1.0
Date: 9/8/2024
Purpose: Level class and functions for "MathWiz!"
"""
import pygame
import json
import menufuncs
import objects
import GameData as state

#this class defines the levels that the player will traverse.
class level:
    def __init__(self,name):
        self.datafile = json.load(open(f"Leveldata/{name}.json"))
        self.tilemap = self.datafile["tiles"]
        self.flipmap = self.datafile["flips"]
        self.spinmap = self.datafile["rotates"]
        self.pallatemap = self.datafile["pallates"]
        self.objs = self.datafile["objects"]
        for layer in range(len(self.tilemap)):
            state.objects.append(drawlayer(self,layer))
        #this line of code spawns in a player object. This should eventually be cut in favor of a dynamic system for object spawning
        state.player = objects.Player([50,50],(0), "MathWiz")
        state.level = self
#This class is used for the rendering of levels. Each one represents a depth layer of a level that will be rendered in the appropriate order
class drawlayer:
    def __init__(self,level,layernum):
        self.level = level
        self.workcanvas = pygame.Surface(state.screensize).convert()
        self.workcanvas.set_colorkey((0,0,10))
        self.brush = pygame.Surface((state.tilesize,state.tilesize)).convert()
        self.brush.fill((0,0,10))
        self.brushval = 0
        self.flipx = False
        self.flipy = False
        self.rotate = 0
        #the depth will be useful to add parallax scrolling
        self.depth = self.level.datafile["layerdepths"][layernum]
        self.layernum = layernum
        #whenever a new thing is added to the object list, the list has to be sorted so that things are in the correct order
        state.objects.sort(key = lambda item: item.depth)
    def update(self):
        #iterate through every row of tiles, and every tile.
        for row in range(len(self.level.tilemap[0])):
            for tile in range(len(self.level.tilemap[self.layernum][row])):
                #get the number of the tile in that slot, and information about its collision data
                tilenum = self.level.tilemap[self.depth][row][tile]
                tiletype = state.tilesource["terraintypes"][tilenum]
                #this is a temporary rendering system. It should ultimately be replaced with graphics pulled from files based on tilenum.
                #also, only changes the brush when the tilenum is different. This hopefully saves on execution time.
                if tiletype != self.brushval:
                    self.brush.fill((0,0,10))
                    if tiletype == 1:
                        self.brush.fill((0,0,255))
                    elif tiletype == 2:
                        pygame.draw.polygon(self.brush, (0,255,255), ([0,state.tilesize],[state.tilesize,0],[state.tilesize,state.tilesize]))
                    elif tiletype == 3:
                        pygame.draw.polygon(self.brush, (255,255,0), ([0,state.tilesize],[state.tilesize,state.tilesize/2],[state.tilesize,state.tilesize]))
                    elif tiletype == 4:
                        pygame.draw.polygon(self.brush, (255,255,0), ([0,state.tilesize],[0,state.tilesize/2],[state.tilesize,0],[state.tilesize,state.tilesize]))
                    elif tiletype == 5:
                        pygame.draw.polygon(self.brush, (255,0,255), ([0,state.tilesize],[0,state.tilesize/2],[state.tilesize,state.tilesize/2],[state.tilesize,state.tilesize]))
                    self.brushval = tiletype

                #apply flips and rotation based on the level data
                self.rotate = (self.level.spinmap[self.depth][row][tile])*90
                flipval = self.level.flipmap[self.depth][row][tile]
                if flipval == 1:
                    self.flipx = True
                elif flipval == 2:
                    self.flipx = True
                    self.flipy = True
                elif flipval == 3:
                    self.flipy = True
                else:
                    self.flipx = False
                    self.flipy = False
                #render layer
                self.workcanvas.blit(pygame.transform.flip(pygame.transform.rotate(self.brush,self.rotate),self.flipx,self.flipy),(tile*state.tilesize-state.cam.pos[0],row*state.tilesize-state.cam.pos[1]))
        #drop layer into display
        state.display.blit(self.workcanvas,(0,0))
        self.workcanvas.fill((0,0,0))
