"""
Filename: menufuncs.py
Author(s): Taliesin Reese
Version: 1.4
Date: 11/20/2024
Purpose: functions for menus in "MathWiz!"
"""
import json
import pygame
import GameData as state
import pygame

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
    state.menu_button_focus = None
    state.cam.locks = []
    #import statement down here to prevent import loop. Perhaps a better way to do this exists?
    import menu
    for entity in state.menudata[menuname]:
        menu.MenuObj(entity[0],entity[1],entity[2],entity[3],entity[4],entity[5], entity[6])
    if menuname in state.menudata["bgm"].keys():
        pygame.mixer.music.load(f"Assets\\sounds\\music\\{state.menudata['bgm'][menuname]}.wav")
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()
    state.clock.tick()
        
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
    state.cam.focus = [state.screensize[0]/2,state.screensize[1]/2]
    state.menu_button_focus = None
    state.cam.focusobj = None
    state.cam.locks = []
    #import statement down here to prevent import loop. Perhaps a better way to do this exists?
    import level
    state.currentlevel = level.level(levelname)
    state.particleManager.reset()
    #force every character to do a little wait
    for item in state.objects:
        if hasattr(item, "actionqueue"):
            item.actionqueue.append([0,[f"levelStart",None],["time",90,None]])
            item.stun = True
            item.actionqueue.append([90,["destun",None],[None,None,None]])
    if hasattr(state.currentlevel,"bgm"):
        pygame.mixer.music.load(f"Assets\\sounds\\music\\{state.currentlevel.bgm}.wav")
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()
    state.clock.tick()

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
    state.cam.focus = [state.screensize[0]/2,state.screensize[1]/2]
    state.cam.focusobj = None
    state.cam.locks = []
    import cutscene
    cutscene.cutscenePlayer(scenename)
    state.clock.tick()

def search(search_pos):
    """
    From a given position, searches for other menu buttons in a linear path depending on the arrow key pressed.

    Parameters:
    search_pos: [int, int]
        The initial position of the screen to start searching from.
    """
    menu_buttons = []
    for obj in state.objects:
        if type(obj).__name__ == "MenuObj" and obj.text != "":
            menu_buttons.append(obj)

    pixel_step_count = 5
    if state.keys[pygame.K_UP]:
        while 0 < search_pos[1]:
            search_pos[1] -= pixel_step_count
            for button in menu_buttons:
                if button.pos[0] < search_pos[0] < button.pos[0] + button.size[0] and button.pos[1] < search_pos[1] < button.pos[1] + button.size[1]:
                    return button
    elif state.keys[pygame.K_LEFT]:
        while 0 < search_pos[0]:
            search_pos[0] -= pixel_step_count
            for button in menu_buttons:
                if button.pos[0] < search_pos[0] < button.pos[0] + button.size[0] and button.pos[1] < search_pos[1] < button.pos[1] + button.size[1]:
                    return button
    elif state.keys[pygame.K_RIGHT]:
        while search_pos[0] < state.screensize[0]:
            search_pos[0] += pixel_step_count
            for button in menu_buttons:
                if button.pos[0] < search_pos[0] < button.pos[0] + button.size[0] and button.pos[1] < search_pos[1] < button.pos[1] + button.size[1]:
                    return button
    elif state.keys[pygame.K_DOWN]:
        while search_pos[1] < state.screensize[1]:
            search_pos[1] += pixel_step_count
            for button in menu_buttons:
                if button.pos[0] < search_pos[0] < button.pos[0] + button.size[0] and button.pos[1] < search_pos[1] < button.pos[1] + button.size[1]:
                    return button
    
#nothing
def nothing(nothing):
    pass
