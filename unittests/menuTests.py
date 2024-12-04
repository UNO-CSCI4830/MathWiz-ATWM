import sys

sys.path.append("../MathWiz-ATWM")

import unittest
import json
import Cam
# import menus
import level
import maker
import menufuncs
import pygame
import GameData as state

pygame.init()

state.menudata = json.load(open("menus.json"))
state.displaysize = 800
state.window = pygame.display.set_mode((800,800))
state.tilesheet = pygame.image.load("Assets/images/tiles.png").convert()
state.menusheet = pygame.image.load("Assets/images/menuassets.png").convert()
state.tilesize = 120
state.screensize = (state.tilesize*30,state.tilesize*30)
state.cam = Cam.cam()
state.mouse = [0,0]
state.display = pygame.Surface(state.screensize)
state.font = pygame.font.SysFont("Lucida Console",75)
state.gamemode = "play"
state.maker = maker.maker()
state.invis = (255,0,255)
state.objectsource = json.load(open("objects.json"))
state.infosource = json.load(open("entityinfo.json"))
state.aisource = json.load(open("behaviours.json"))
state.tilesource = json.load(open("tiles.json"))

class menuTests(unittest.TestCase):
    def setUp(self):
        menufuncs.loadmenu("test")  # start each test case from the title menu

    def testMenuObjCount(self):
        self.assertEqual(len(state.objects), 3)
        menufuncs.loadmenu("test2")
        self.assertEqual(len(state.objects), 1)

    def testOnHoverMainMenu(self):
        state.mouse = [100,100]
        state.objects[0].update() # I had to add some attributes that makes a screen pop up
                                  # It's harmless, but if someone can come up with a way to get rid of it while keeping this test good please let me know
        self.assertNotEqual(state.objects[0].graphics, None) # main menu background has graphics

    def testOnHoverButton(self):
        state.objects[1].update()
        self.assertEqual(state.objects[1].canvas.get_at((1000,250)), (0,255,0,255))
        state.mouse = [1800, 2750]
        state.click = pygame.mouse.get_pressed() # it yells at me if I don't assign state.click to something
        state.objects[1].update()   # should call onHover()
        self.assertEqual(state.objects[1].canvas.get_at((1000,250)), (255,0,0,255))

    def testOnClickStartGame(self):
        with self.assertRaises(AttributeError):
            state.currentlevel
        state.objects[1].update()
        state.objects[1].last = 0 # onClick() won't work without this
        state.objects[1].onClick()
        self.assertNotEqual(state.currentlevel, None) # Checking if the level directly equals expoFixed does not seem to work

    def testOnClickToMenuTwo(self):
        state.objects[2].update()
        state.objects[2].last = 0
        state.objects[2].onClick()
        self.assertEqual(len(state.objects), 1) # went to other menu

    def testOnClickToMenuOne(self):
        menufuncs.loadmenu("test2")
        state.objects[0].update()
        state.objects[0].last = 0
        state.objects[0].onClick()
        self.assertEqual(len(state.objects), 3) # went to main menu

unittest.main()
pygame.quit()