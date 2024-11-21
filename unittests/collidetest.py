import sys
sys.path.append("../")

#MathWiz stuff
import json
import pygame
import level
import objects
import GameData as state
import maker
import Cam

import os
os.chdir('../')

pygame.init()
state.window = pygame.display.set_mode((1,1))
state.display = pygame.Surface((0,0))
state.savedata = json.load(open("Save.json"))
state.savefile = 1
state.adjustdeltatime = state.savedata[str(state.savefile)]["adjustdeltatime"]
state.movetickamount = state.savedata[str(state.savefile)]["movetickamount"]
state.tilesize = 120
state.screensize = (state.tilesize*30,state.tilesize*30)
clock = pygame.time.Clock()
state.tilesheet = pygame.image.load("Assets/images/tiles.png").convert()
state.spritesheet = pygame.image.load("Assets/images/CharSprites.png").convert()
state.menusheet = pygame.image.load("Assets/images/menuassets.png").convert()
state.objectsource = json.load(open("objects.json"))
state.aisource = json.load(open("behaviours.json"))
state.infosource = json.load(open("entityinfo.json"))
state.tilesource = json.load(open("tiles.json"))
state.cutscenesource = json.load(open("cutscenes.json"))
state.menudata = json.load(open("menus.json"))
state.gamemode = "play"
state.maker = maker.maker()
state.invis = (255,0,255)
state.deltatime = 1
state.fpsTarget = 60
state.objects = []
state.cam = Cam.cam()
state.currentlevel = level.level("Test")

#for testing purposes, we need to single out the player. Normally we wouldn't do this.
for obj in state.objects:
    if type(obj).__name__ == "Player":
        state.MainPlayer = obj
        break

#unittest stuff
import unittest
class manager(unittest.TestCase):
    #make sure object would correctly identify terrain types and collide correctly
    def testCollideTerrain(self):
        state.MainPlayer.pos = (0,240)
        state.MainPlayer.getpoints()
        self.assertFalse(state.MainPlayer.pointcollide(state.MainPlayer.bottom))
        
        state.MainPlayer.pos = (0,3120)
        state.MainPlayer.getpoints()
        self.assertTrue(state.MainPlayer.pointcollide(state.MainPlayer.bottom))
        
        state.MainPlayer.pos = (1800,2761)
        state.MainPlayer.getpoints()
        self.assertFalse(state.MainPlayer.pointcollide(state.MainPlayer.bottom))
        state.MainPlayer.pos = (1919,2761)
        state.MainPlayer.getpoints()
        self.assertTrue(state.MainPlayer.pointcollide(state.MainPlayer.bottom))
        
        state.MainPlayer.pos = (840,3061)
        state.MainPlayer.getpoints()
        self.assertFalse(state.MainPlayer.pointcollide(state.MainPlayer.bottom))
        state.MainPlayer.pos = (959,3061)
        state.MainPlayer.getpoints()
        self.assertTrue(state.MainPlayer.pointcollide(state.MainPlayer.bottom))
        
        state.MainPlayer.pos = (1080,3001)
        state.MainPlayer.getpoints()
        self.assertFalse(state.MainPlayer.pointcollide(state.MainPlayer.bottom))
        state.MainPlayer.pos = (1199,3001)
        state.MainPlayer.getpoints()
        self.assertTrue(state.MainPlayer.pointcollide(state.MainPlayer.bottom))
        
        state.MainPlayer.pos = (960,3059)
        state.MainPlayer.getpoints()
        self.assertFalse(state.MainPlayer.pointcollide(state.MainPlayer.bottom))
        state.MainPlayer.pos = (960,3060)
        state.MainPlayer.getpoints()
        self.assertTrue(state.MainPlayer.pointcollide(state.MainPlayer.bottom))
        
unittest.main(verbosity = 3)
pygame.quit()
