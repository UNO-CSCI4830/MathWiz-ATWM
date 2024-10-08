"""
Filename: menufuncs.py
Author(s): Taliesin Reese
Version: 1.0
Date: 9/8/2024
Purpose: functions for menus in "MathWiz!"
"""
import json
import GameData as state

#contrary to the name, these functions are used outside of menus as well
menudata = json.load(open("menus.json"))

#load a menu as prescribed by the json file
def loadmenu(menuname):
    #clear all objects, resulting in their removal from memory after a while
    state.objects = []
    #import statement down here to prevent import loop. Perhaps a better way to do this exists?
    import menu
    for entity in menudata[menuname]:
        menu.MenuObj(entity[0],entity[1],entity[2],entity[3],entity[4],entity[5])
        
#load a level as prescribed by the json file
def loadlevel(levelname):
    #clear all objects, resulting in their removal from memory after a while
    state.objects = []
    #import statement down here to prevent import loop. Perhaps a better way to do this exists?
    import level
    state.currentlevel = level.level(levelname)
    #add object-spawning code down here
