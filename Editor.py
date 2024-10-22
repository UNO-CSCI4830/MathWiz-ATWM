"""
Filename: Editor.py
Author(s): Taliesin Reese
Version: 1.10
Date: 10/21/2024
Purpose: Level Editor for MathWiz!
"""

import pygame
pygame.init()
import tkinter
from tkinter import ttk
from functools import partial

import GameData as state
import level
import Cam
import menufuncs
import json
import objects

#create variables
toolvar = 0
state.wasclick = [0,0,0,0,0]
#create stuff for level rendering
state.tilesize = 120
state.screensize = (state.tilesize*30,state.tilesize*30)
state.window = pygame.display.set_mode((800,800))
state.tilesource = json.load(open("tiles.json"))
state.tilesheet = pygame.image.load("Assets/images/tiles.png").convert()
state.spritesheet = pygame.image.load("Assets/images/CharSprites.png").convert()
state.display = pygame.Surface(state.screensize)
state.objectsource = json.load(open("objects.json"))
state.objects = []
state.deltatime = 1
state.cam = Cam.cam()

state.gamemode = "edit"
state.invis = (255,0,255)
state.level = level.level("blank")


#main loop
def main():
    #create stuff for modification
    state.editloops = [False]
    state.layercount = len(state.level.tilemap)
    state.tools = createtoolbox()
    state.renderdepth = 0
    state.parallax = 1
    state.renderlayer = 0
    state.cam.depth = -(1-state.level.parallaxes[state.renderlayer])
    state.editobjs = []
    state.groupselect = [[],[]]
    state.currentlayer = None
    #whether or not the level has been altered since last frame
    state.levelchanged = False
    while True:
        #position of the mouse cursor relative to the window. Adjusted for the scaling.
        state.mouse = pygame.mouse.get_pos()
        state.mouse = (state.mouse[0]*state.screensize[0]/800,state.mouse[1]*state.screensize[1]/800)
        #current state of the mouse buttons
        state.click = pygame.mouse.get_pressed()
        #current state of keyboard keys
        state.keys = pygame.key.get_pressed()
        #render level
        for item in state.objects:
            if type(item) == level.drawlayer:
                if item.layernum == state.renderlayer:
                    if state.levelchanged:
                        item.render()
                    item.update()
                    state.parallaxmod = item.parallax-state.cam.depth
            else:
                if item.depth == state.renderdepth:
                    item.render()
        #reset the changed status for upcoming loops
        state.levelchanged = False
        #handle editor functions
        move()
        state.tools.update()
        updatetoolbar()
        match state.toolvarlast:
            case 0:
                blockdrawupdate()
            case 1:
                flipdrawupdate()
            case 2:
                spindrawupdate()
            case 3:
                colordrawupdate()
            case 4:
                rowaddupdate()
            case 5:
                coladdupdate()
            case 6:
                itemaddupdate()
            case 7:
                animaddupdate()
            case _:
                pass

        #display and prep for next update
        state.window.blit(pygame.transform.scale(state.display,(800,800)),(0,0))
        
        pygame.display.flip()
        state.cam.update()
        state.window.fill((0,0,0))
        state.display.fill((255,0,255))
        state.wasclick = state.click
            
        #quit
        for event in pygame.event.get():
            #quit logic
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
def move():
    if state.keys[pygame.K_a]:
        state.cam.focus[0] -= state.tilesize
    if state.keys[pygame.K_d]:
        state.cam.focus[0] += state.tilesize
    if state.keys[pygame.K_s]:
        state.cam.focus[1] += state.tilesize
    if state.keys[pygame.K_w]:
        state.cam.focus[1] -= state.tilesize
        
#create toolbox
def createtoolbox():
    toolbar = tkinter.Tk()
    toolbar.title("Toolbox")
    #populate toolbar with universal options
    toolsLabel = tkinter.Label(toolbar,text = "Tools:")
    toolsLabel.pack()
    state.toolvar = tkinter.IntVar(value = -1)
    Draw = ttk.Radiobutton(toolbar, text = "Draw Terrain", variable = state.toolvar, value = 0)
    Draw.pack()
    Flip = ttk.Radiobutton(toolbar, text = "Flip Terrain", variable = state.toolvar, value = 1)
    Flip.pack()
    Rotate = ttk.Radiobutton(toolbar, text = "Spin Terrain", variable = state.toolvar, value = 2)
    Rotate.pack()
    Pallate = ttk.Radiobutton(toolbar, text = "Recolor Terrain", variable = state.toolvar, value = 3)
    Pallate.pack()
    vertadd = ttk.Radiobutton(toolbar, text = "Add rows", variable = state.toolvar, value = 4)
    vertadd.pack()
    horadd = ttk.Radiobutton(toolbar, text = "Add columns", variable = state.toolvar, value = 5)
    horadd.pack()
    itemadd = ttk.Radiobutton(toolbar, text = "Add items", variable = state.toolvar, value = 6)
    itemadd.pack()
    animadd = ttk.Radiobutton(toolbar, text = "Add tile animations", variable = state.toolvar, value = 7)
    animadd.pack()
    switchLabel = tkinter.Label(toolbar,text = "Layer:")
    switchLabel.pack()
    state.Layerswitch = tkinter.Spinbox(toolbar, from_=0, to=state.layercount-1, repeatdelay=500, repeatinterval=100,command=setlayer)
    state.Layerswitch.pack()
    state.Layerswitch.delete(0,"end")
    state.Layerswitch.insert(0,0)
    dialLabel = tkinter.Label(toolbar,text = "Layer Depth:")
    dialLabel.pack()
    state.Depthswitch = tkinter.Spinbox(toolbar, format="%.2f",increment=0.1, from_=-500, to=500, repeatdelay=500, repeatinterval=100,command=setlayerdepth)
    state.Depthswitch.pack()
    state.Depthswitch.delete(0,"end")
    state.Depthswitch.insert(0,0)
    paraLabel = tkinter.Label(toolbar,text = "Layer Parallax:")
    paraLabel.pack()
    state.Parallaxswitch = tkinter.Spinbox(toolbar, format="%.2f", increment=0.1, from_=-500, to=500, repeatdelay=500, repeatinterval=100,command=setlayerparallax)
    state.Parallaxswitch.pack()
    state.Parallaxswitch.delete(0,"end")
    state.Parallaxswitch.insert(0,0)
    state.LoopBtn = tkinter.Checkbutton(toolbar,text = "Loop:",onvalue = True,offvalue = False,variable = state.editloops[state.layercount-1],command = setlayerloop)
    state.LoopBtn.pack()
    addLayerBtn = tkinter.Button(toolbar, text = "Add new Layer", compound = "left", padx = 10, pady = 5, command = partial(addLayer))
    addLayerBtn.pack()

    optionsLabel = tkinter.Label(toolbar,text = "Tool Options:")
    optionsLabel.pack()
    tooloptions = tkinter.Frame(toolbar)
    
    state.addamtlbl = tkinter.Label(tooloptions, text = "Number to add:")
    state.addamt = tkinter.Spinbox(tooloptions, from_=0, to=30, width=10, repeatdelay=500, repeatinterval=100)
    
    state.tileselect = tkinter.Listbox(tooloptions,selectmode = "single")
    for item in state.tilesource["tiles"].values():
        state.tileselect.insert("end",item)
    
    state.pallateselect = tkinter.Listbox(tooloptions,selectmode = "single")
    for item in state.tilesource["pallatecodes"].values():
        state.pallateselect.insert("end",item)
    
    state.objselect = tkinter.Listbox(tooloptions,selectmode = "single")
    for item in state.objectsource.keys():
        state.objselect.insert("end",item)
    
    state.animselect = tkinter.Listbox(tooloptions,selectmode = "single")
    for item in state.tilesource["anims"].keys():
        state.animselect.insert("end",item)
    
    tooloptions.pack()

    nameLabel = tkinter.Label(toolbar,text = "Name (.json will be appended):")
    nameLabel.pack()
    state.Filename = tkinter.Text(toolbar,height = 1, width = 20)
    state.Filename.pack()
    SaveBtn = tkinter.Button(toolbar, text = "Save", compound = "left", padx = 10, pady = 5, command = partial(save))
    SaveBtn.pack()
    LoadBtn = tkinter.Button(toolbar, text = "Load", compound = "left", padx = 10, pady = 5, command = partial(load))
    LoadBtn.pack()
    NewBtn = tkinter.Button(toolbar, text = "New Level", compound = "left", padx = 10, pady = 5, command = partial(new))
    NewBtn.pack()
    
    state.toolvarlast = -1
    return toolbar

def updatetoolbar():
    try:
        if state.toolvar.get() != state.toolvarlast:
            state.toolvarlast = state.toolvar.get()
            #add rows mode and add columns mode
            if state.toolvarlast == 0:
                state.tileselect.pack()
            else:
                state.tileselect.pack_forget()
            if state.toolvarlast == 3:
                state.pallateselect.pack()
            else:
                state.pallateselect.pack_forget()
            if state.toolvarlast == 4 or state.toolvarlast == 5:
                state.addamtlbl.pack()
                state.addamt.pack()
            else:
                state.addamtlbl.pack_forget()
                state.addamt.pack_forget()
            if state.toolvarlast == 6:
                state.objselect.pack()
            else:
                state.objselect.pack_forget()
            if state.toolvarlast == 7:
                state.animselect.pack()
            else:
                state.animselect.pack_forget()
    except Exception as e:
        print(e)
        print(state.toolvar)

#save levels
def save():
    writeTo = open((f"Leveldata\{state.Filename.get('1.0','end-1c')}.json"),'w')
    print(state.level.depths,state.level.parallaxes)
    writeThis = {"layerdepths":state.level.depths,
                 "layerparallaxes":state.level.parallaxes,
                 "layerloops":state.editloops,
                 "animations":state.level.animationlist,
                 "tiles":state.level.tilemap,
                 "flips":state.level.flipmap,
                 "rotates":state.level.spinmap,
                 "pallates":state.level.pallatemap,
                 "objects":state.editobjs}
    json.dump(writeThis,writeTo)
    print("Your Game--Saved!")
    
#load levels
def load():
    levelname = state.Filename.get('1.0','end-1c')
    state.cam.focus = [state.screensize[0]/2,state.screensize[1]/2]
    state.Layerswitch.delete(0,"end")
    state.Layerswitch.insert(0,0)
    setlayer()
    try:
        state.objects = []
        state.editobjs = []
        state.level = level.level(levelname)
        state.editloops = state.level.loops
        state.LoopBtn.config(variable = state.editloops[state.renderlayer])
        if state.editloops[state.renderlayer]:
            state.LoopBtn.select()
        else:
            state.LoopBtn.deselect()
        
        state.layercount = len(state.level.tilemap)
        state.Layerswitch.config(to = state.layercount-1)
    except Exception as e:
        raise e
        print("No such file!")
        
#new levels
def new():
    state.objects = []
    state.editobjs = []
    state.level = level.level("blank")
    state.editloops = state.level.loops
    state.LoopBtn.config(variable = state.editloops[state.renderlayer])
    if state.editloops[state.renderlayer]:
        state.LoopBtn.select()
    else:
        state.LoopBtn.deselect()

def setlayer():
    try:
        num = int(state.Layerswitch.get())
    except:
        num = 0
    print(num)
    print(state.objects)
    state.renderlayer = num
    state.renderdepth = state.level.depths[num]
    state.parallax = state.level.parallaxes[state.renderlayer]
    state.LoopBtn.config(variable = state.editloops[state.renderlayer])
    if state.editloops[state.renderlayer]:
        state.LoopBtn.select()
    else:
        state.LoopBtn.deselect()
    state.cam.depth = -(1-state.level.parallaxes[state.renderlayer])
    state.Depthswitch.delete(0,"end")
    state.Depthswitch.insert(0,state.renderdepth)
    state.Parallaxswitch.delete(0,"end")
    state.Parallaxswitch.insert(0,state.level.parallaxes[state.renderlayer])
    
def setlayerloop():
    if state.editloops[state.renderlayer]:
        state.editloops[state.renderlayer] = False
    else:
        state.editloops[state.renderlayer] = True
        
def setlayerdepth():
    print(state.renderdepth)
    try:
        num = int(float(state.Depthswitch.get()))
    except Exception as e:
        num = 0
    state.level.depths[state.renderlayer] = num
    state.renderdepth = num
    print(state.renderdepth)

def setlayerparallax():
    try:
        num = float(state.Parallaxswitch.get())
    except:
        num = 0
    state.level.parallaxes[state.renderlayer] = num
    state.cam.depth = -(1-num)


def draw(canvasarray,tile,value):
    canvasarray[state.renderlayer][tile[1]][tile[0]] = value
            
def blank():
    return [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
    
def blockdrawupdate():
    tile = [int((state.mouse[0]+state.cam.pos[0]*state.parallaxmod)//state.tilesize),int((state.mouse[1]+state.cam.pos[1]*state.parallaxmod)//state.tilesize)]
    #print(tile)
    locusupdate = [int(state.mouse[0]//state.tilesize)*state.tilesize,int(state.mouse[1]//state.tilesize)*state.tilesize]
    pygame.draw.rect(state.display,(0,255,0),(locusupdate[0],locusupdate[1],state.tilesize,state.tilesize),10)
    if state.click[0] == True:
        try:
        #change block type if list entry is clicked
            state.drawval = state.tileselect.curselection()[0]
        except:
            state.drawval = 1
            
        try:
            draw(state.level.tilemap,tile,state.drawval)
            state.levelchanged = True
        except:
            print("Cannot Place, Out of Bounds")
    elif state.click[2] == True:
        try:
            draw(state.level.tilemap,tile,0)
            state.levelchanged = True
        except:
            print("Cannot Erase, Out of Bounds")
    else:
        if state.click[1]:
            if not state.wasclick[1]:
                state.groupselect[0] = tile
                state.groupselect[1] = tile
            else:
                if tile[0] <= state.groupselect[0][0] or tile[1] <= state.groupselect[0][1]:
                    #state.groupselect[1] = state.groupselect[0].copy()
                    state.groupselect[0] = tile
                else:
                    state.groupselect[1] = tile
            pygame.draw.rect(state.display,(0,255,0),(state.groupselect[0][0]*state.tilesize,state.groupselect[0][1]*state.tilesize,(state.groupselect[1][0]-state.groupselect[0][0])*state.tilesize,(state.groupselect[1][1]-state.groupselect[0][1])*state.tilesize))
        elif state.wasclick[1]:
            for row in range(state.groupselect[1][1]-state.groupselect[0][1]):
                for tile in range(state.groupselect[1][0]-state.groupselect[0][0]):
                    try:
                    #change block type if list entry is clicked
                        state.drawval = state.tileselect.curselection()[0]
                    except:
                        state.drawval = 1
                    try:
                        draw(state.level.tilemap,[state.groupselect[0][0]+tile,state.groupselect[0][1]+row],state.drawval)
                        state.levelchanged = True
                    except:
                        print("Cannot Place, Out of Bounds")
            state.groupselect = [[],[]]

def colordrawupdate():
    tile = [int((state.mouse[0]+state.cam.pos[0]*state.parallaxmod)//state.tilesize),int((state.mouse[1]+state.cam.pos[1]*state.parallaxmod)//state.tilesize)]
    #print(tile)
    locusupdate = [int(state.mouse[0]//state.tilesize)*state.tilesize,int(state.mouse[1]//state.tilesize)*state.tilesize]
    pygame.draw.rect(state.display,(0,255,0),(locusupdate[0],locusupdate[1],state.tilesize,state.tilesize),10)
    if state.click[0] == True:
        try:
        #change pallate if list entry is clicked
            state.colorval = state.pallateselect.curselection()[0]
        except:
            state.colorval = 0
            
        try:
            draw(state.level.pallatemap,tile,state.colorval)
            state.levelchanged = True
        except:
            print("Cannot Color, Out of Bounds")
    else:
        if state.click[1]:
            if not state.wasclick[1]:
                state.groupselect[0] = tile
                state.groupselect[1] = tile
            else:
                if tile[0] <= state.groupselect[0][0] or tile[1] <= state.groupselect[0][1]:
                    #state.groupselect[1] = state.groupselect[0].copy()
                    state.groupselect[0] = tile
                else:
                    state.groupselect[1] = tile
            pygame.draw.rect(state.display,(0,255,0),(state.groupselect[0][0]*state.tilesize,state.groupselect[0][1]*state.tilesize,(state.groupselect[1][0]-state.groupselect[0][0])*state.tilesize,(state.groupselect[1][1]-state.groupselect[0][1])*state.tilesize))
        elif state.wasclick[1]:
            for row in range(state.groupselect[1][1]-state.groupselect[0][1]):
                for tile in range(state.groupselect[1][0]-state.groupselect[0][0]):
                    try:
                    #change block type if list entry is clicked
                        state.colorval = state.tileselect.curselection()[0]
                    except:
                        state.colorval = 0
                    try:
                        draw(state.level.pallatemap,[state.groupselect[0][0]+tile,state.groupselect[0][1]+row],state.colorval)
                        state.levelchanged = True
                    except:
                        print("Cannot Color, Out of Bounds")
            state.groupselect = [[],[]]

def flipdrawupdate():
    tile = [int((state.mouse[0]+state.cam.pos[0]*state.parallaxmod)//state.tilesize),int((state.mouse[1]+state.cam.pos[1]*state.parallaxmod)//state.tilesize)]
    locusupdate = [int(state.mouse[0]//state.tilesize)*state.tilesize,int(state.mouse[1]//state.tilesize)*state.tilesize]
    pygame.draw.rect(state.display,(0,255,0),(locusupdate[0],locusupdate[1],state.tilesize,state.tilesize),10)
    if state.click[0] and not state.wasclick[0]:
        try:
            check = state.level.flipmap[state.renderlayer][tile[1]][tile[0]]
            if check == 0:
                draw(state.level.flipmap,tile,1)
                state.levelchanged = True
            elif check == 1:
                draw(state.level.flipmap,tile,0)
                state.levelchanged = True
            elif check == 2:
                draw(state.level.flipmap,tile,3)
                state.levelchanged = True
            elif check == 3:
                draw(state.level.flipmap,tile,2)
                state.levelchanged = True
        except Exception as e:
            print("Cannot flip, Out of Bounds")
    elif state.click[2] and not state.wasclick[2]:
        try:
            check = state.level.flipmap[state.renderlayer][tile[1]][tile[0]]
            if check == 0:
                draw(state.level.flipmap,tile,3)
                state.levelchanged = True
            elif check == 1:
                draw(state.level.flipmap,tile,2)
                state.levelchanged = True
            elif check == 2:
                draw(state.level.flipmap,tile,1)
                state.levelchanged = True
            elif check == 3:
                draw(state.level.flipmap,tile,0)
                state.levelchanged = True
        except:
            print("Cannot flip, Out of Bounds")

def spindrawupdate():
    tile = [int((state.mouse[0]+state.cam.pos[0]*state.parallaxmod)//state.tilesize),int((state.mouse[1]+state.cam.pos[1]*state.parallaxmod)//state.tilesize)]
    locusupdate = [int(state.mouse[0]//state.tilesize)*state.tilesize,int(state.mouse[1]//state.tilesize)*state.tilesize]
    pygame.draw.rect(state.display,(0,255,0),(locusupdate[0],locusupdate[1],state.tilesize,state.tilesize),10)
    if state.click[0] and not state.wasclick[0]:
        try:
            check = state.level.spinmap[state.renderlayer][tile[1]][tile[0]]+1
            if check > 3:
                check = 0
            if check < 0:
                check = 3
            draw(state.level.spinmap,tile,check)
            state.levelchanged = True
        except Exception as e:
            print("Cannot spin, Out of Bounds")

def rowaddupdate():
    rows = int(state.addamt.get())
    tile = [int((state.mouse[0]+state.cam.pos[0]*state.parallaxmod)//state.tilesize),int((state.mouse[1]+state.cam.pos[1]*state.parallaxmod)//state.tilesize)]
    #print(tile)
    locusupdate = [int(state.mouse[0]//state.tilesize)*state.tilesize,int(state.mouse[1]//state.tilesize)*state.tilesize]
    pygame.draw.rect(state.display,(0,255,0),(-10,locusupdate[1],state.screensize[0]+20,state.tilesize),10)
    if state.click[0] and not state.wasclick[0]:
        addheight(tile,rows)
        state.levelchanged = True

def coladdupdate():
    cols = int(state.addamt.get())
    tile = [int((state.mouse[0]+state.cam.pos[0]*state.parallaxmod)//state.tilesize),int((state.mouse[1]+state.cam.pos[1]*state.parallaxmod)//state.tilesize)]
    #print(tile)
    locusupdate = [int(state.mouse[0]//state.tilesize)*state.tilesize,int(state.mouse[1]//state.tilesize)*state.tilesize]
    pygame.draw.rect(state.display,(0,255,0),(locusupdate[0],-10,state.tilesize,state.screensize[1]+20),10)
    if state.click[0] and not state.wasclick[0]:
        addwidth(tile,cols)
        state.levelchanged = True

def animaddupdate():
    tile = [int((state.mouse[0]+state.cam.pos[0]*state.parallaxmod)//state.tilesize),int((state.mouse[1]+state.cam.pos[1]*state.parallaxmod)//state.tilesize)]
    locusupdate = [int(state.mouse[0]//state.tilesize)*state.tilesize,int(state.mouse[1]//state.tilesize)*state.tilesize]
    pygame.draw.rect(state.display,(0,255,0),(locusupdate[0],locusupdate[1],state.tilesize,state.tilesize),10)
    state.addanimindex = state.animselect.curselection()
    if state.addanimindex != ():
        state.addanim = state.animselect.get(state.addanimindex[0])
    else:
        state.addanim = "testanim1"
    anim = state.tilesource["anims"][state.addanim]
    #if new leftclick:
    if state.click[0] and not state.wasclick[0]:
        #if there's a conflicting animation on that tile, remove it.
        for candidate in state.level.animationlist[state.renderlayer]:
            if tile[0]==candidate[1] and tile[1]==candidate[2] and anim[0]==candidate[0]:
                state.level.animationlist.remove(candidate)
                for item in state.objects:
                    if type(item).__name__=="drawlayer":
                        if item.depth==state.renderdepth:
                            item.animationlist.delete(candidate)
                            del item.animtimers[-1]
                            del item.animframes[-1]
                #if you find one, there will not be another.
                break
        #add animation to list
        state.level.animationlist[state.renderlayer].append([anim[0],tile[0],tile[1],anim[1]])
        for item in state.objects:
            if type(item).__name__=="drawlayer":
                if item.depth==state.renderdepth:
                    item.animtimers.append(0)
                    item.animframes.append(0)

def itemaddupdate():
    posadj = [state.mouse[0]+state.cam.pos[0]*state.parallaxmod,state.mouse[1]+state.cam.pos[1]*state.parallaxmod]
    extras = ["TEST"]
    #if new leftclick:
    if state.click[0] and not state.wasclick[0]:
        #place the selected object at that point
        state.addobjindex = state.objselect.curselection()[0]
        state.addobj = state.objselect.get(state.addobjindex)
        if state.addobj != None:
            added = getattr(objects,state.objectsource[state.addobj]["Type"])(posadj,state.renderdepth,state.parallax,state.addobj,extras)
            state.editobjs.append([state.objectsource[state.addobj]["Type"],state.addobj,posadj,state.renderdepth,state.parallax,extras])
            state.levelchanged = True
    #if new rightclick:
    elif state.click[2] and not state.wasclick[2]:
        #for object on layer:
        for obj in state.objects:
            #if mouse is between object points and object is not a layer or a hitbox:
            if obj.depth==state.renderdepth:
                if type(obj).__name__ == "spawner" and obj.pos[0]-10<=posadj[0]<=obj.pos[0]+10 and obj.pos[1]-10<=posadj[1]<=obj.pos[1]+10:
                    state.editobjs.remove([type(obj).__name__,obj.name,obj.pos,state.renderdepth,state.parallax,obj.extras])
                    for child in obj.children:
                        child.delete()
                    obj.delete()
                    state.levelchanged = True
                elif type(obj).__name__ not in ["drawlayer","Hitbox"]  and (obj.left[0]<=posadj[0]<=obj.right[0] and obj.top[1]<=posadj[1]<=obj.bottom[1]):
                    #destroy object and all it's children
                    state.editobjs.remove([type(obj).__name__,obj.name,obj.pos,state.renderdepth,state.parallax,obj.extras])
                    for child in obj.children:
                        child.delete()
                    obj.delete()
                    state.levelchanged = True
                    break

def addheight(target, rowstoadd):
    #find longest row in level tileset
    longest = 0
    for row in state.level.tilemap[state.renderlayer]:
        if len(row)>longest:
            longest = len(row)
    #add rows at length of longest row at the point listed
    add = []
    for zero in range(longest):
        add.append(1)
    for row in range(rowstoadd):
        state.level.tilemap[state.renderlayer].insert(target[1],add.copy())
        state.level.pallatemap[state.renderlayer].insert(target[1],add.copy())
        state.level.spinmap[state.renderlayer].insert(target[1],add.copy())
        state.level.flipmap[state.renderlayer].insert(target[1],add.copy())
    for object in state.objects:
        if type(object)==level.drawlayer and object.layernum == state.renderlayer:
            object.calcsize()

def addwidth(target, colstoadd):
    #add values into all the rows
    for row in range(len(state.level.tilemap[state.renderlayer])):
        for iteration in range(colstoadd):
            state.level.tilemap[state.renderlayer][row].insert(target[0],1)
            state.level.pallatemap[state.renderlayer][row].insert(target[0],1)
            state.level.spinmap[state.renderlayer][row].insert(target[0],1)
            state.level.flipmap[state.renderlayer][row].insert(target[0],1)
    for object in state.objects:
        if type(object)==level.drawlayer and object.layernum == state.renderlayer:
            object.calcsize()

def addLayer():
    num = state.renderlayer
    for item in state.objects:
        if type(item) == level.drawlayer:
            if item.layernum >= state.renderlayer:
                item.layernum += 1
    level.drawlayer(state.level,state.renderdepth)
    state.level.tilemap.insert(num,blank())
    state.level.pallatemap.insert(num,blank())
    state.level.spinmap.insert(num,blank())
    state.level.flipmap.insert(num,blank())
    state.editloops.insert(num,False)
    state.level.depths.insert(num,state.renderdepth)
    state.level.parallaxes.insert(num,state.renderdepth)
    state.layercount += 1
    state.Layerswitch.config(to = state.layercount)
    #state.renderlayer = num+1
    #state.renderdepth = state.level.depths[num+1]
    
main()
