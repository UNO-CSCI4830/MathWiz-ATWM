"""
Filename: menufuncs.py
Author(s): Taliesin Reese
Version: 1.3
Date: 11/06/2024
Purpose: functions for menus in "MathWiz!"
"""
import json
import pygame
import GameData as state

#contrary to the name, these functions are used outside of menus as well
menudata = json.load(open("menus.json"))

#load a menu as prescribed by the json file
def loadmenu(menuname):
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

# with arrow keys, search for other buttons in the menu
def search(search_pos):
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
                    print("found up")
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
                    print("found down")
                    return button
    
#nothing
def nothing(nothing):
    pass
