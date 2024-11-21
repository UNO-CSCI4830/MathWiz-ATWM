"""
Filename: menufuncs.py
Author(s): Taliesin Reese
Version: 1.4
Date: 11/20/2024
Purpose: functions for menus in "MathWiz!"
"""
import json
import GameData as state

#load a menu as prescribed by the json file
def loadmenu(menuname):
    #clear all objects, resulting in their removal from memory after a while
    state.objects = []
    state.cam.focus = [state.screensize[0]/2,state.screensize[1]/2]
    state.cam.focusobj = None
    state.deltatime = 1
    #import statement down here to prevent import loop. Perhaps a better way to do this exists?
    import menu
    for entity in state.menudata[menuname]:
        menu.MenuObj(entity[0],entity[1],entity[2],entity[3],entity[4],entity[5], entity[6])
        
#load a level as prescribed by the json file
def loadlevel(levelname):
    #clear all objects, resulting in their removal from memory after a while
    """print(state.objects)
    for item in range(len(state.objects)):
        state.objects = state.objects[1:]
        print(state.objects)
    print(state.objects)"""
    state.objects = []
    state.deltatime = 1
    state.cam.focus = [state.screensize[0]/2,state.screensize[1]/2]
    #import statement down here to prevent import loop. Perhaps a better way to do this exists?
    import level
    state.currentlevel = level.level(levelname)
    #add object-spawning code down here

#load the cutscene player
def loadcutscene(scenename):
    #clear all objects, resulting in their removal from memory after a while
    state.objects = []
    state.deltatime = 1
    state.cam.focus = [state.screensize[0]/2,state.screensize[1]/2]
    import cutscene
    cutscene.cutscenePlayer(scenename)
    
#nothing
def nothing(nothing):
    pass
