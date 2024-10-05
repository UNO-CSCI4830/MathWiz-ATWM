"""
Filename: Editor.py
Author(s): Taliesin Reese
Version: 1.5
Date: 10/05/2024
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

#create variables
toolvar = 0
state.wasclick = [0,0,0,0,0]
#create stuff for level rendering
state.tilesize = 120
state.screensize = (state.tilesize*30,state.tilesize*30)
state.window = pygame.display.set_mode((800,800))
state.tilesource = json.load(open("tiles.json"))
state.tilesheet = pygame.image.load("Assets/images/tiles.png").convert()
state.display = pygame.Surface(state.screensize)
state.objectsource = json.load(open("objects.json"))
state.objects = []
state.cam = Cam.cam()

state.gamemode = "edit"
state.invis = (255,0,255)
state.level = level.level("blank")


#main loop
def main():
    #create stuff for modification
    state.layercount = len(state.level.tilemap)
    state.tools = createtoolbox()
    state.renderdepth = 0
    state.renderlayer = 0
    state.cam.depth = -(1-state.level.parallaxes[state.renderlayer])
    state.editobjs =[]
    state.groupselect = [[],[]]
    state.currentlayer = None
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
                    item.render()
                    item.update()
                    state.parallaxmod = item.parallax-state.cam.depth
            else:
                if item.depth == state.renderdepth:
                    item.update()
    
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
            case _:
                pass

        #display and prep for next update
        state.window.blit(pygame.transform.scale(state.display,(800,800)),(0,0))
        
        pygame.display.flip()
        state.cam.update()
        state.window.fill((0,0,0))
        state.display.fill((0,0,0))
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
    except Exception as e:
        print(e)
        print(state.toolvar)

#save levels
def save():
    writeTo = open((f"Leveldata\{state.Filename.get('1.0','end-1c')}.json"),'w')
    print(state.level.depths,state.level.parallaxes)
    writeThis = {"layerdepths":state.level.depths,
                 "layerparallaxes":state.level.parallaxes,
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
        state.layercount = len(state.level.tilemap)
        state.Layerswitch.config(to = state.layercount-1)
    except Exception as e:
        print(e)
        print("No such file!")
        
#new levels
def new():
    state.objects = []
    state.level = level.level("blank")

def setlayer():
    try:
        num = int(state.Layerswitch.get())
    except:
        num = 0
    print(num)
    print(state.objects)
    state.renderlayer = num
    state.renderdepth = state.level.depths[num]
    state.cam.depth = -(1-state.level.parallaxes[state.renderlayer])
    state.Depthswitch.delete(0,"end")
    state.Depthswitch.insert(0,state.renderdepth)
    state.Parallaxswitch.delete(0,"end")
    state.Parallaxswitch.insert(0,state.level.parallaxes[state.renderlayer])

def setlayerdepth():
    try:
        num = int(state.Depthswitch.get())
    except:
        num = 0
    state.level.depths[state.renderlayer] = num
    state.renderdepth = num

def setlayerparallax():
    try:
        num = int(state.Parallaxswitch.get())
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
        except:
            print("Cannot Place, Out of Bounds")
    elif state.click[2] == True:
        try:
            draw(state.level.tilemap,tile,0)
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
            elif check == 1:
                draw(state.level.flipmap,tile,0)
            elif check == 2:
                draw(state.level.flipmap,tile,3)
            elif check == 3:
                draw(state.level.flipmap,tile,2)
        except Exception as e:
            print("Cannot flip, Out of Bounds")
    elif state.click[2] and not state.wasclick[2]:
        try:
            check = state.level.flipmap[state.renderlayer][tile[1]][tile[0]]
            if check == 0:
                draw(state.level.flipmap,tile,3)
            elif check == 1:
                draw(state.level.flipmap,tile,2)
            elif check == 2:
                draw(state.level.flipmap,tile,1)
            elif check == 3:
                draw(state.level.flipmap,tile,0)
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

def coladdupdate():
    cols = int(state.addamt.get())
    tile = [int((state.mouse[0]+state.cam.pos[0]*state.parallaxmod)//state.tilesize),int((state.mouse[1]+state.cam.pos[1]*state.parallaxmod)//state.tilesize)]
    #print(tile)
    locusupdate = [int(state.mouse[0]//state.tilesize)*state.tilesize,int(state.mouse[1]//state.tilesize)*state.tilesize]
    pygame.draw.rect(state.display,(0,255,0),(locusupdate[0],-10,state.tilesize,state.screensize[1]+20),10)
    if state.click[0] and not state.wasclick[0]:
        addwidth(tile,cols)
        
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
        state.level.tilemap[state.renderlayer].insert(target[1],add)
        state.level.pallatemap[state.renderlayer].insert(target[1],add)
        state.level.spinmap[state.renderlayer].insert(target[1],add)
        state.level.flipmap[state.renderlayer].insert(target[1],add)

def addwidth(target, colstoadd):
    #add values into all the rows
    for row in range(len(state.level.tilemap[state.renderlayer])):
        for iteration in range(colstoadd):
            state.level.tilemap[state.renderlayer][row].insert(target[0],1)
            state.level.pallatemap[state.renderlayer][row].insert(target[0],1)
            state.level.spinmap[state.renderlayer][row].insert(target[0],1)
            state.level.flipmap[state.renderlayer][row].insert(target[0],1)

def addLayer():
    num = state.renderlayer
    for item in state.objects:
        if type(item) == level.drawlayer:
            if item.layernum >= state.renderlayer:
                item.layernum += 1
    state.objects.append(level.drawlayer(state.level,state.renderdepth))
    state.level.tilemap.insert(num,blank())
    state.level.pallatemap.insert(num,blank())
    state.level.spinmap.insert(num,blank())
    state.level.flipmap.insert(num,blank())
    state.level.depths.insert(num,state.renderdepth)
    state.layercount += 1
    state.Layerswitch.config(to = state.layercount)
    #state.renderlayer = num+1
    #state.renderdepth = state.level.depths[num+1]
    
main()
