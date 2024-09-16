"""
Filename: moves.py
Author(s): Taliesin Reese
Version: 1.0
Date: 9/9/2024
Purpose: moves to be used in "MathWiz!"
"""
import GameData as state
import pygame

#set vertical velocity to the jumpspeed
def jump(caller, height):
    if caller.grounded:
        #alter this check later to allow for controller support, if that happens
        if pygame.K_SPACE in state.newkeys:
            caller.speed[1] = -height
    else:
        if caller.speed[1] < 0:
            caller.speed[1] -= (caller.gravity/2)*state.deltatime

#add the walk speed to the character, unless the speed exceeds maxspeed.
def walk(caller,speed):
    caller.speed[0] += speed*state.deltatime
    if abs(caller.speed[0]) > caller.maxspeed:
        caller.speed[0] = caller.maxspeed*(caller.speed[0]/abs(caller.speed[0]))
