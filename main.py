"""
Filename: main.py
Author(s): Taliesin Reese
Verion: 1.8
Date: 10/29/2024
Purpose: Core file for "MathWiz!"
"""
#premade library imports
import pygame
import json

import GameData as state
import Cam
import menu
import level
import objects
import menufuncs
import maker

#initialize pygame stuffs
pygame.init()

#Load settings
state.savedata = json.load(open("Save.json"))
state.savefile = 1

state.adjustdeltatime = state.savedata[str(state.savefile)]["adjustdeltatime"]
state.movetickamount = state.savedata[str(state.savefile)]["movetickamount"]
#size to actually display stuff
state.displaysize = state.savedata[str(state.savefile)]["displaysize"]
#the tilesize is a lynchpin. All measures in the game save for the final render size are based on the tile (or, they will be in the final product. Not all of them are right now)
state.tilesize = 120
#anyway set up pygame stuff
state.screensize = (state.tilesize*30,state.tilesize*30)
state.window = pygame.display.set_mode((state.displaysize,state.displaysize))
state.display = pygame.Surface(state.screensize)
state.HUD = pygame.Surface(state.screensize)
state.font = pygame.font.SysFont("Lucida Console",75)

#initialize timer
clock = pygame.time.Clock()

#load assets
state.tilesheet = pygame.image.load("Assets/images/tiles.png").convert()
state.spritesheet = pygame.image.load("Assets/images/CharSprites.png").convert()
state.menusheet = pygame.image.load("Assets/images/menuassets.png").convert()

state.objectsource = json.load(open("objects.json"))
state.aisource = json.load(open("behaviours.json"))
state.infosource = json.load(open("entityinfo.json"))

state.tilesource = json.load(open("tiles.json"))
state.cutscenesource = json.load(open("cutscenes.json"))

#initialize game stuffs
state.gamemode = "play"
state.maker = maker.maker()
state.invis = (255,0,255)
state.HUD.set_colorkey(state.invis)
state.deltatime = 1
state.fpsTarget = 60

state.objects = []
state.cam = Cam.cam()

#to start with, load menu stuffs
#menufuncs.loadmenu("test")
menufuncs.loadcutscene("Intro")

while True:
    #input handling--maybe throw this into it's own file for the sake of organization?
    #newkeys is a suprise tool that will help us later
    state.newkeys = []
    #position of the mouse cursor relative to the window. Adjusted for the scaling.
    state.mouse = pygame.mouse.get_pos()
    state.mouse = (state.mouse[0]*state.screensize[0]/800,state.mouse[1]*state.screensize[1]/800)
    #current state of the mouse buttons
    state.click = pygame.mouse.get_pressed()
    events = pygame.event.get()
    for event in events:
        #quit logic
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            #if a key is newly down on this frame, it's important. Add it to newkeys
            state.newkeys.append(event.key)
    #current state of keyboard keys
    state.keys = pygame.key.get_pressed()
    
    """FOR TESTING UNDER HEAVY LAG:"""
    #from time import sleep
    #sleep(0.25)

    #calculate deltatime. This is used to augment certain values and keep the speed of things independent from the framerate
    if state.adjustdeltatime:
        state.deltatime = state.fpsTarget*clock.get_time()/(1000)
    #print(state.deltatime)
    #reset display
    state.display.fill((0,0,255))
    state.HUD.fill((255,0,255))
    #update world
    state.cam.update()
    for thing in state.objects:
        thing.update()
    #draw HUD
    state.display.blit(state.HUD,(0,0))
    #display
    state.window.blit(pygame.transform.scale(state.display,(state.displaysize,state.displaysize)),(0,0))
    pygame.display.flip()
    clock.tick()
