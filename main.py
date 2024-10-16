"""
Filename: main.py
Author(s): Taliesin Reese
Verion: 1.5
Date: 10/16/2024
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

#initialize pygame stuffs
pygame.init()
#the tilesize is a lynchpin. All measures in the game save for the final render size are based on the tile (or, they will be in the final product. Not all of them are right now)
state.tilesize = 120
#size to actually display stuff
state.displaysize = 800
#anyway set up pygame stuff
state.screensize = (state.tilesize*30,state.tilesize*30)
state.window = pygame.display.set_mode((state.displaysize,state.displaysize))
state.display = pygame.Surface(state.screensize)
state.font = pygame.font.SysFont("Lucida Console",100)

#initialize timer
clock = pygame.time.Clock()

#initialize game stuffs
state.gamemode = "play"
state.invis = (255,0,255)
state.movetickamount = 120
state.deltatime = 1
state.adjustdeltatime = True
state.writer = pygame.font.SysFont("Arial",150)
state.tilesource = json.load(open("tiles.json"))
state.tilesheet = pygame.image.load("Assets/images/tiles.png").convert()
state.spritesheet = pygame.image.load("Assets/images/CharSprites.png").convert()
state.objectsource = json.load(open("objects.json"))
state.objects = []
state.fpsTarget = 60
state.cam = Cam.cam()

#to start with, load menu stuffs
menufuncs.loadmenu("test")

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
    #update world
    state.cam.update()
    for thing in state.objects:
        thing.update()

    #display
    state.window.blit(pygame.transform.scale(state.display,(state.displaysize,state.displaysize)),(0,0))
    pygame.display.flip()
    clock.tick()
