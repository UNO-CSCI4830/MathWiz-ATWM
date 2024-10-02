"""
Filename: moves.py
Author(s): Taliesin Reese
Version: 1.1
Date: 10/02/2024
Purpose: moves to be used in "MathWiz!"
"""
import GameData as state
import pygame

#set vertical velocity to the jumpspeed
def jump(caller, height):
    #alter this check later to allow for controller support, if that happens
    caller.speed[1] = -height
            
def jumpstall(caller,height):
    if caller.speed[1] < 0:
        caller.speed[1] -= (caller.gravity/2)*state.deltatime

#add the walk speed to the character, unless the speed exceeds maxspeed.
def walk(caller,speed):
    caller.speed[0] += speed*state.deltatime
    if abs(caller.speed[0]) > caller.maxspeed:
        caller.speed[0] = caller.maxspeed*(caller.speed[0]/abs(caller.speed[0]))
        
def setforce(caller,force):
    if force[0] != None:
        caller.speed[0]=force[0]
    if force[1] != None:
        caller.speed[1]=force[1]
        
def addforce(caller,force):
    caller.speed[0]+=force[0]*state.deltatime
    caller.speed[1]+=force[1]*state.deltatime
