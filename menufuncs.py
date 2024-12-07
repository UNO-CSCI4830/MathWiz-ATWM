"""
Filename: menufuncs.py
Author(s): Taliesin Reese
Version: 1.3
Date: 11/06/2024
Purpose: functions for menus in "MathWiz!"
"""
import json
import GameData as state

#contrary to the name, these functions are used outside of menus as well
menudata = json.load(open("menus.json"))

#load a menu as prescribed by the json file
def loadmenu(menuname):
    """
    Loads a menu as prescribed by the JSON file.

    Parameters:
    menuname : str
        The name of the menu to load.
    """
    #clear all objects, resulting in their removal from memory after a while
    state.objects = []
    state.cam.focus = [state.screensize[0]/2,state.screensize[1]/2]
    state.cam.focusobj = None
    state.deltatime = 1
    #import statement down here to prevent import loop. Perhaps a better way to do this exists?
    import menu
    for entity in menudata[menuname]:
        menu.MenuObj(entity[0],entity[1],entity[2],entity[3],entity[4],entity[5], entity[6])
        
#load a level as prescribed by the json file
def loadlevel(levelname):
    """
    Loads a level as prescribed by the JSON file.

    Parameters:
    levelname : str
        The name of the level to load.
    """
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
    """
    Loads the cutscene player with the given scene name.

    Parameters:
    scenename : str
        The name of the cutscene to load.
    """
    #clear all objects, resulting in their removal from memory after a while
    state.objects = []
    state.deltatime = 1
    state.cam.focus = [state.screensize[0]/2,state.screensize[1]/2]
    import cutscene
    cutscene.cutscenePlayer(scenename)
    
#nothing
def nothing(nothing):
    pass
