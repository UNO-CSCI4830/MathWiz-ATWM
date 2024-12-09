"""
Filename: level.py
Author(s): Taliesin Reese
Verion: 1.14
Date: 11/23/2024
Purpose: Level class and functions for "MathWiz!"
"""
import pygame
import json
import menufuncs
#import objects
import GameData as state
import random

#this class defines the levels that the player will traverse.
class level:
    """
    A class to represent a level in the game.

    Attributes:
    name : str
        The name of the level.
    datafile : dict
        The JSON data of the level.
    depths : list
        The depth of each layer in the level.
    parallaxes : list
        The parallax values of each layer in the level.
    loops : list
        The loop settings of each layer in the level.
    tilemap : list
        The tile map of the level.
    flipmap : list
        The flip map of the level.
    spinmap : list
        The rotation map of the level.
    pallatemap : list
        The palette map of the level.
    objs : list
        The objects in the level.
    animationlist : list
        The animations in the level.
    """
    def __init__(self,name):
        """
        Initializes the level with the given name.

        Parameters:
        name : str
            The name of the level.
        """
        self.name = name
        self.datafile = json.load(open(f"Leveldata/{name}.json"))
        self.depths = self.datafile["layerdepths"]
        self.parallaxes = self.datafile["layerparallaxes"]
        self.loops = self.datafile["layerloops"]
        #to accurately load levels with old-style loops
        for entry in range(len(self.loops)):
            if type(self.loops[entry]) == bool:
                if self.loops[entry]:
                    self.loops[entry] = [None,None]
                    self.loops[entry][0] = True
                    self.loops[entry][1] = True
                else:
                    self.loops[entry] = [None,None]
                    self.loops[entry][0] = False
                    self.loops[entry][1] = False
        self.tilemap = self.datafile["tiles"]
        self.flipmap = self.datafile["flips"]
        self.spinmap = self.datafile["rotates"]
        self.pallatemap = self.datafile["pallates"]
        self.objs = self.datafile["objects"]
        self.animationlist = self.datafile["animations"]
        for layer in range(len(self.tilemap)):
            drawlayer(self,layer)
        #spawn objects that are assigned to the level
        for item in self.objs:
            #getattr(objects,item[0])(item[2],item[3],item[4],item[1],item[5])
            if len(item) > 5:
                state.maker.make_obj(item[0],(item[2],item[3],item[4],item[1],item[5],item[6]))
            else:
                state.maker.make_obj(item[0],(item[2],item[3],item[4],item[1],item[5]))
            if state.gamemode == "edit":
                state.editobjs.append(item)
        #state.player = objects.Player([50,50],(0), "MathWiz")
        state.level = self
        
#This class is used for the rendering of levels. Each one represents a depth layer of a level that will be rendered in the appropriate order
class drawlayer:
    """
    A class to represent a depth layer of a level for rendering.

    Attributes:
    level : level
        The level to which this layer belongs.
    layernum : int
        The layer number.
    longest : int
        The longest row in the layer.
    tallest : int
        The tallest column in the layer.
    width : int
        The width of the layer in pixels.
    height : int
        The height of the layer in pixels.
    workcanvas : pygame.Surface
        The surface to draw the layer on.
    brush : pygame.Surface
        The surface to draw individual tiles on.
    colorbrush : pygame.Surface
        The surface to apply color changes to tiles.
    brushval : int
        The current tile value of the brush.
    brushpal : int
        The current palette value of the brush.
    flipx : bool
        Whether the brush is flipped horizontally.
    flipy : bool
        Whether the brush is flipped vertically.
    rotate : int
        The rotation of the brush in degrees.
    loop : bool
        Whether the layer loops.
    depth : int
        The depth of the layer.
    parallax : float
        The parallax value of the layer.
    animationlist : list
        The animations in the layer.
    animtimers : list
        The timers for each animation.
    animframes : list
        The current frame of each animation.
    """
    def __init__(self,level,layernum):
        """
        Initializes the drawlayer with the given level and layer number.

        Parameters:
        level : level
            The level to which this layer belongs.
        layernum : int
            The layer number.
        """
        self.level = level
        self.layernum = layernum
        self.calcsize()

        self.animlistrecalc()
            
        self.brush = pygame.Surface((state.tilesize*state.scaleamt,state.tilesize*state.scaleamt)).convert_alpha()
        self.brush.fill(state.invis)
        if state.gamemode == "edit":
            self.brush.set_colorkey(state.invis)
        
        self.colorbrush = pygame.Surface((state.tilesize*state.scaleamt,state.tilesize*state.scaleamt)).convert_alpha()
        self.colorbrush.fill(state.invis)
        self.colorbrush.set_colorkey(state.invis)
        
        self.brushval = 0
        self.brushpal = 0
        self.flipx = False
        self.flipy = False
        self.rotate = 0
        if state.gamemode == "edit":
            self.loop = [False,False]
        else:
            self.loop = self.level.loops[self.layernum]
        #the depth will be useful to add parallax scrolling
        self.depth = self.level.depths[layernum]
        self.parallax = self.level.parallaxes[layernum]
        #whenever a new thing is added to the object list, the list has to be sorted so that things are in the correct order
        state.objects.append(self)
        state.objects.sort(key = lambda item: item.depth, reverse = True)
        self.render()
        
    def render(self):
        """
        Renders the layer by drawing each tile to the workcanvas.
        """
        self.workcanvas.fill((0,0,0))
        #iterate through every row of tiles, and every tile.
        for row in range(len(self.level.tilemap[self.layernum])):
            for tile in range(len(self.level.tilemap[self.layernum][row])):
                #get the number of the tile in that slot, and information about its collision data
                tilenum = self.level.tilemap[self.layernum][row][tile]
                pallatenum = self.level.pallatemap[self.layernum][row][tile]
                tileinfo = state.tilesource["tiles"][str(tilenum)]
                self.tileupdate(row,tile,tileinfo,tilenum,pallatenum)

    def calcsize(self):
        """
        Calculates the size of the layer in pixels.
        """
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
        self.workcanvas = pygame.Surface((self.width*state.scaleamt,self.height*state.scaleamt)).convert_alpha()
        if state.gamemode == "play":
            self.workcanvas.set_colorkey(state.invis)
            
    def tileupdate(self,row,tile,tileinfo,tilenum,pallatenum):
        """
        Updates the tile at the given position with the given information.

        Parameters:
        row : int
            The row of the tile.
        tile : int
            The column of the tile.
        tileinfo : dict
            The information of the tile.
        tilenum : int
            The number of the tile.
        pallatenum : int
            The palette number of the tile.
        """
        if tilenum != self.brushval or pallatenum != self.brushpal:
            self.brush.fill(state.invis)
            #print(row,tile,tileinfo,tilenum,pallatenum)
            self.brush.blit(state.tilesheet, (tileinfo[3][0]*state.scaleamt,tileinfo[3][1]*state.scaleamt), (tileinfo[1][0]*state.scaleamt,tileinfo[1][1]*state.scaleamt,tileinfo[2][0]*state.scaleamt,tileinfo[2][1]*state.scaleamt))
            
            """#this is a temporary rendering system. It should ultimately be replaced with graphics pulled from files based on tilenum.
            #also, only changes the brush when the tilenum is different. This hopefully saves on execution time.
            #FOR DEBUGGING PURPOSES
            if tilenum == 1:
                self.brush.fill((0,0,255))
            elif tilenum == 2:
                pygame.draw.polygon(self.brush, (0,255,255), ([0,state.tilesize],[state.tilesize,0],[state.tilesize,state.tilesize]))
            elif tilenum == 3:
                pygame.draw.polygon(self.brush, (255,255,0), ([0,state.tilesize],[state.tilesize,state.tilesize/2],[state.tilesize,state.tilesize]))
            elif tilenum == 4:
                pygame.draw.polygon(self.brush, (255,255,0), ([0,state.tilesize],[0,state.tilesize/2],[state.tilesize,0],[state.tilesize,state.tilesize]))
            elif tilenum == 5:
                pygame.draw.polygon(self.brush, (255,0,0), ([0,state.tilesize],[0,state.tilesize/2],[state.tilesize,state.tilesize/2],[state.tilesize,state.tilesize]))"""
                
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
            if state.gamemode == "edit":
                self.brush.set_colorkey(state.invis)
            else:
                self.brush.set_colorkey(None)

        #apply flips and rotation based on the level data
        self.rotate = (self.level.spinmap[self.layernum][row][tile])*90
        flipval = self.level.flipmap[self.layernum][row][tile]
        if flipval == 1:
            self.flipx = True
            self.flipy = False
        elif flipval == 2:
            self.flipx = True
            self.flipy = True
        elif flipval == 3:
            self.flipy = True
            self.flipx = False
        else:
            self.flipx = False
            self.flipy = False
        #render layer
        self.workcanvas.blit(pygame.transform.flip(pygame.transform.rotate(self.brush,self.rotate),self.flipx,self.flipy),(tile*state.tilesize*state.scaleamt,row*state.tilesize*state.scaleamt))

    def animlistrecalc(self):
        """
        Recalculates the animation list for the layer.
        """
        self.animationlist = self.level.animationlist[self.layernum]
        self.animtimers = []
        self.animframes = []
        for sequence in self.animationlist:
            self.animtimers.append(0)
            self.animframes.append(0)
            
    def update(self):
        """
        Updates the layer, including tile animations and parallax scrolling.
        """
        #update tile animations
        #print(self.animationlist)
        for timer in range(len(self.animtimers)):
            self.animtimers[timer] += state.deltatime
        for sequencenum in range(len(self.animationlist)):
            if self.animtimers[sequencenum] >= self.animationlist[sequencenum][3][self.animframes[sequencenum]][1]:
                self.animtimers[sequencenum] = 0
                if self.animframes[sequencenum] >= len(self.animationlist[sequencenum][3])-1:
                    self.animframes[sequencenum] = 0
                else:
                    self.animframes[sequencenum] += 1
                if state.gamemode != "edit":
                    getattr(self.level,self.animationlist[sequencenum][0])[self.layernum][self.animationlist[sequencenum][2]][self.animationlist[sequencenum][1]] = self.animationlist[sequencenum][3][self.animframes[sequencenum]][0]
                    row = self.animationlist[sequencenum][2]
                    tile = self.animationlist[sequencenum][1]
                    tilenum = self.level.tilemap[self.layernum][row][tile]
                    pallatenum = self.level.pallatemap[self.layernum][row][tile]
                    tileinfo = state.tilesource["tiles"][str(tilenum)]
                    self.tileupdate(row,tile,tileinfo,tilenum,pallatenum)
            if state.gamemode == "edit":
                col = int(255*self.animtimers[sequencenum]/self.animationlist[sequencenum][3][self.animframes[sequencenum]][1])
                row = self.animationlist[sequencenum][2]
                tile = self.animationlist[sequencenum][1]
                pygame.draw.rect(self.workcanvas, (0,col,col,50), (tile*state.tilesize*state.scaleamt,row*state.tilesize*state.scaleamt,state.tilesize*state.scaleamt,state.tilesize*state.scaleamt))
        #this modifier determines how much the offset of an object should be affected by it's distance from the camera in z space...sort of.
        parallaxmod = self.parallax-state.cam.depth
        
        screenplacemod = [0,0]
        if self.loop[0] == True:
            screenplacemod[0] = ((state.cam.pos[0]*parallaxmod)//self.width)*self.width
        if self.loop[1] == True:
            screenplacemod[1] = ((state.cam.pos[1]*parallaxmod)//self.height)*self.height
            
        drawspot = (screenplacemod[0]-state.cam.pos[0]*parallaxmod,
                    screenplacemod[1]-state.cam.pos[1]*parallaxmod)
        state.display.blit(self.workcanvas,(drawspot[0]*state.scaleamt,drawspot[1]*state.scaleamt))

        if self.loop[0] == True:
            if abs(state.cam.pos[0])+state.screensize[0] > (drawspot[0]+self.longest*state.tilesize):
                state.display.blit(self.workcanvas,((drawspot[0]+self.width)*state.scaleamt,drawspot[1]*state.scaleamt))
                
        if self.loop[1] == True:
            if abs(state.cam.pos[1])+state.screensize[1] > len(self.level.tilemap[self.layernum])*state.tilesize:
                state.display.blit(self.workcanvas,((drawspot[0])*state.scaleamt,(drawspot[1]+self.height)*state.scaleamt))

        if self.loop[0] and self.loop[1] and abs(state.cam.pos[0]) > (drawspot[0]+self.longest*state.tilesize) and abs(state.cam.pos[1])+state.screensize[1] > len(self.level.tilemap[self.layernum])*state.tilesize:
            state.display.blit(self.workcanvas,((drawspot[0]+self.width)*state.scaleamt,(drawspot[1]+self.height)*state.scaleamt))