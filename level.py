"""
Filename: level.py
Author(s): Taliesin Reese
Verion: 1.5
Date: 10/09/2024
Purpose: Level class and functions for "MathWiz!"
"""
import pygame
import json
import menufuncs
import objects
import GameData as state
import random

#this class defines the levels that the player will traverse.
class level:
    def __init__(self,name):
        self.datafile = json.load(open(f"Leveldata/{name}.json"))
        self.depths = self.datafile["layerdepths"]
        self.parallaxes = self.datafile["layerparallaxes"]
        self.tilemap = self.datafile["tiles"]
        self.flipmap = self.datafile["flips"]
        self.spinmap = self.datafile["rotates"]
        self.pallatemap = self.datafile["pallates"]
        self.objs = self.datafile["objects"]
        for layer in range(len(self.tilemap)):
            drawlayer(self,layer)
        #spawn objects that are assigned to the level
        objects.spawner([2220,1050],0,1,"ExponentQuestionSpawner",[])
        for item in self.objs:
            getattr(objects,item[0])(item[2],item[3],item[4],item[1],item[5])
            if state.gamemode == "edit":
                state.editobjs.append(item)
        #state.player = objects.Player([50,50],(0), "MathWiz")
        state.level = self
#This class is used for the rendering of levels. Each one represents a depth layer of a level that will be rendered in the appropriate order
class drawlayer:
    def __init__(self,level,layernum):
        self.level = level
        self.layernum = layernum
        self.calcsize()
        #map of lines to be used for updated collision detection
        self.linemap = []
            
        self.brush = pygame.Surface((state.tilesize,state.tilesize)).convert()
        self.brush.fill(state.invis)
        self.brush.set_colorkey(state.invis)
        
        self.colorbrush = pygame.Surface((state.tilesize,state.tilesize)).convert()
        self.colorbrush.fill(state.invis)
        self.colorbrush.set_colorkey(state.invis)
        
        self.brushval = 0
        self.brushpal = 0
        self.flipx = False
        self.flipy = False
        self.rotate = 0
        if state.gamemode == "edit":
            self.loop = False
        else:
            self.loop = True
        #the depth will be useful to add parallax scrolling
        self.depth = self.level.depths[layernum]
        self.parallax = self.level.parallaxes[layernum]
        #whenever a new thing is added to the object list, the list has to be sorted so that things are in the correct order
        state.objects.append(self)
        state.objects.sort(key = lambda item: item.depth, reverse = True)
        self.render()
        self.calclinemap()
        
    def render(self):
        self.workcanvas.fill((0,0,0))
        #iterate through every row of tiles, and every tile.
        for row in range(len(self.level.tilemap[0])):
            for tile in range(len(self.level.tilemap[self.layernum][row])):
                #get the number of the tile in that slot, and information about its collision data
                tilenum = self.level.tilemap[self.layernum][row][tile]
                pallatenum = self.level.pallatemap[self.layernum][row][tile]
                #this is a temporary rendering system. It should ultimately be replaced with graphics pulled from files based on tilenum.
                #also, only changes the brush when the tilenum is different. This hopefully saves on execution time.
                if tilenum != self.brushval or pallatenum != self.brushpal:
                    tileinfo = state.tilesource["tiles"][str(tilenum)]
                    self.brush.fill (state.invis)
                    self.brush.blit(state.tilesheet, (tileinfo[3][0],tileinfo[3][1]), (tileinfo[1][0],tileinfo[1][1],tileinfo[2][0],tileinfo[2][1]))
                    """
                    FOR DEBUGGING PURPOSES
                    if tilenum == 1:
                        self.brush.fill((0,0,255))
                    elif tilenum == 2:
                        pygame.draw.polygon(self.brush, (0,255,255), ([0,state.tilesize],[state.tilesize,0],[state.tilesize,state.tilesize]))
                    elif tilenum == 3:
                        pygame.draw.polygon(self.brush, (255,255,0), ([0,state.tilesize],[state.tilesize,state.tilesize/2],[state.tilesize,state.tilesize]))
                    elif tilenum == 4:
                        pygame.draw.polygon(self.brush, (255,255,0), ([0,state.tilesize],[0,state.tilesize/2],[state.tilesize,0],[state.tilesize,state.tilesize]))
                    elif tilenum == 5:
                        pygame.draw.polygon(self.brush, (255,0,0), ([0,state.tilesize],[0,state.tilesize/2],[state.tilesize,state.tilesize/2],[state.tilesize,state.tilesize]))
                        """
                    self.brushval = tilenum
                    #set pallate value to tile's default value
                    self.brushpal = tileinfo[4]

                    #apply pallate change if required
                    if pallatenum != self.brushpal:
                        pallatename = state.tilesource["pallatecodes"][str(self.brushpal)]
                        targetname = state.tilesource["pallatecodes"][str(pallatenum)]
                        for color in range(len(state.tilesource["pallates"][pallatename])):
                            self.colorbrush.fill(state.tilesource["pallates"][targetname][color])
                            self.brush.set_colorkey(state.tilesource["pallates"][pallatename][color])
                            self.colorbrush.blit(self.brush,(0,0))
                            self.brush.blit(self.colorbrush,(0,0))
                        self.brushpal = pallatenum
                    self.brush.set_colorkey(state.invis)

                #apply flips and rotation based on the level data
                self.rotate = (self.level.spinmap[self.layernum][row][tile])*90
                flipval = self.level.flipmap[self.layernum][row][tile]
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
                self.workcanvas.blit(pygame.transform.flip(pygame.transform.rotate(self.brush,self.rotate),self.flipx,self.flipy),(tile*state.tilesize,row*state.tilesize))
        #drop layer into display

    def calcsize(self):
        #find the longest row in the layer
        self.longest = 0
        for row in self.level.tilemap[self.layernum]:
            if len(row)>self.longest:
                self.longest = len(row)
        #get longest column
        self.tallest = len(self.level.tilemap[self.layernum])
        #width and height in pixels
        self.width = self.longest*state.tilesize
        self.height = self.tallest*state.tilesize
        #canvas on which the level is to be drawn
        self.workcanvas = pygame.Surface((self.width,self.height)).convert()
        if state.gamemode == "play":
            self.workcanvas.set_colorkey(state.invis)

    def calclinemap(self):
        for row in range(len(self.level.tilemap[self.layernum])):
            for tile in range(len(self.level.tilemap[self.layernum][row])):
                if self.level.tilemap[self.layernum][row][tile] != 0:
                    #full blocks--points will always be the same
                    if state.tilesource["tiles"][str(self.level.tilemap[self.layernum][row][tile])][5] == 1:
                        tl = [tile*state.tilesize,row*state.tilesize]
                        tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                        bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                        br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                    #45-degree blocks
                    elif state.tilesource["tiles"][str(self.level.tilemap[self.layernum][row][tile])][5] == 2:
                        orientation = (self.level.spinmap[self.layernum][row][tile],self.level.flipmap[self.layernum][row][tile])
                        if  orientation == (0,0) or orientation == (1,3) or orientation == (2,2) or orientation == (3,1):
                            tl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (0,1) or orientation == (1,2) or orientation == (2,3) or orientation == (3,0):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (0,2) or orientation == (1,1) or orientation == (2,0) or orientation == (3,3):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (0,3) or orientation == (1,0) or orientation == (2,1) or orientation == (3,2):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                       
                    #low 22-degree blocks
                    elif state.tilesource["tiles"][str(self.level.tilemap[self.layernum][row][tile])][5] == 3:
                        orientation = (self.level.spinmap[self.layernum][row][tile],self.level.flipmap[self.layernum][row][tile])
                        if  orientation == (0,0) or orientation == (2,2):
                            tl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize/2]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (0,1) or orientation == (2,3):
                            tl = [tile*state.tilesize,row*state.tilesize+state.tilesize/2]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (0,2) or orientation == (2,0):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize/2]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                        elif orientation == (0,3) or orientation == (2,1):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize/2]
                        elif  orientation == (1,0) or orientation == (3,2):
                            tl = [tile*state.tilesize+state.tilesize/2,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (1,1) or orientation == (3,3):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize/2,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (1,2) or orientation == (3,0):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize/2,row*state.tilesize+state.tilesize]
                        elif orientation == (1,3) or orientation == (3,1):
                            tl = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize+state.tilesize/2,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                    #high 22-degree blocks
                    elif state.tilesource["tiles"][str(self.level.tilemap[self.layernum][row][tile])][5] == 4:
                        orientation = (self.level.spinmap[self.layernum][row][tile],self.level.flipmap[self.layernum][row][tile])
                        if  orientation == (0,0) or orientation == (2,2):
                            tl = [tile*state.tilesize,row*state.tilesize+state.tilesize/2]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (0,1) or orientation == (2,3):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize/2]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (0,2) or orientation == (2,0):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize/2]
                        elif orientation == (0,3) or orientation == (2,1):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize/2]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif  orientation == (1,0) or orientation == (3,2):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize+state.tilesize/2,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (1,1) or orientation == (3,3):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize/2,row*state.tilesize+state.tilesize]
                        elif orientation == (1,2) or orientation == (3,0):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize/2,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (1,3) or orientation == (3,1):
                            tl = [tile*state.tilesize+state.tilesize/2,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                    #half blocks
                    elif state.tilesource["tiles"][str(self.level.tilemap[self.layernum][row][tile])][5] == 5:
                        orientation = (self.level.spinmap[self.layernum][row][tile],self.level.flipmap[self.layernum][row][tile])
                        if  orientation == (0,0) or orientation == (2,2):
                            tl = [tile*state.tilesize,row*state.tilesize+state.tilesize/2]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize/2]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (0,1) or orientation == (2,3):
                            tl = [tile*state.tilesize,row*state.tilesize+state.tilesize/2]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize/2]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (0,2) or orientation == (2,0):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize/2]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize/2]
                        elif orientation == (0,3) or orientation == (2,1):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize/2]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize/2]
                        elif  orientation == (1,0) or orientation == (3,2):
                            tl = [tile*state.tilesize+state.tilesize/2,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize+state.tilesize/2,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                        elif orientation == (1,1) or orientation == (3,3):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize/2,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize/2,row*state.tilesize+state.tilesize]
                        elif orientation == (1,2) or orientation == (3,0):
                            tl = [tile*state.tilesize,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize/2,row*state.tilesize]
                            bl = [tile*state.tilesize,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize/2,row*state.tilesize+state.tilesize]
                        elif orientation == (1,3) or orientation == (3,1):
                            tl = [tile*state.tilesize+state.tilesize/2,row*state.tilesize]
                            tr = [tile*state.tilesize+state.tilesize,row*state.tilesize]
                            bl = [tile*state.tilesize+state.tilesize/2,row*state.tilesize+state.tilesize]
                            br = [tile*state.tilesize+state.tilesize,row*state.tilesize+state.tilesize]
                    candidates = [[tl,tr],[tr,br],[br,bl],[bl,tl]]
                    for entry in candidates:
                        foundmatch = False
                        try:
                            entryslope = (entry[0][1]-entry[1][1])/(entry[0][0]-entry[1][0])
                        except:
                            entryslope = "cringe"
                        for line in self.linemap:
                            #test if the two lines share a common slope
                            try:
                                lineslope = (line[0][1]-line[1][1])/(line[0][0]-line[1][0])
                            except:
                                lineslope = "cringe"
                            if lineslope == entryslope:
                                if (line[0] == entry[0] and line[1] == entry[1]) or (line[0] == entry[1] and line[1] == entry[0]):
                                    self.linemap.remove(line)
                                    foundmatch = True
                                    break
                                if line[0] == entry[0]:
                                    line[0] = entry[1]
                                    foundmatch = True
                                    break
                                elif line[1] == entry[0]:
                                    line[1] = entry[1]
                                    foundmatch = True
                                    break
                                elif line[0] == entry[1]:
                                    line[0] = entry[0]
                                    foundmatch = True
                                    break
                                elif line[1] == entry[1]:
                                    line[1] = entry[0]
                                    foundmatch = True
                                    break
                        if foundmatch == False:
                            self.linemap.append(entry)


    def update(self):
        #this modifier determines how much the offset of an object should be affected by it's distance from the camera in z space...sort of.
        parallaxmod = self.parallax-state.cam.depth
        if self.loop == True:
            screenplacemod = [((state.cam.pos[0]*parallaxmod)//self.width)*self.width,
                             ((state.cam.pos[1]*parallaxmod)//self.height)*self.height]
        else:
            screenplacemod = [0,0]
        drawspot = (screenplacemod[0]-state.cam.pos[0]*parallaxmod,
                    screenplacemod[1]-state.cam.pos[1]*parallaxmod)
        state.display.blit(self.workcanvas,drawspot)
        if self.loop == True:
            match (abs(state.cam.pos[0])+state.screensize[0] > (drawspot[0]+self.longest*state.tilesize), 
                  abs(state.cam.pos[1])+state.screensize[1] > len(self.level.tilemap[self.layernum])*state.tilesize):
                case (True, False):
                    state.display.blit(self.workcanvas,(drawspot[0]+self.longest*state.tilesize,drawspot[1]))
                case (True, True):
                    state.display.blit(self.workcanvas,(drawspot[0]+self.longest*state.tilesize,drawspot[1]))
                    state.display.blit(self.workcanvas,(drawspot[0]+self.longest*state.tilesize,drawspot[1]+len(self.level.tilemap[self.layernum])*state.tilesize))
                    state.display.blit(self.workcanvas,(drawspot[0],drawspot[1]+len(self.level.tilemap[self.layernum])*state.tilesize))
                case (False, True):
                    state.display.blit(self.workcanvas,(drawspot[0],drawspot[1]+len(self.level.tilemap[self.layernum])*state.tilesize))
        #for segment in self.linemap:
        #    colval = random.randint(0,255)
        #    pygame.draw.line(state.display,(colval,colval,0),(segment[0][0]+drawspot[0],segment[0][1]+drawspot[1]),(segment[1][0]+drawspot[0],segment[1][1]+drawspot[1]),15)
