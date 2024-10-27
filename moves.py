"""
Filename: moves.py
Author(s): Taliesin Reese
Version: 1.4
Date: 10/26/2024
Purpose: moves to be used in "MathWiz!"
"""
import GameData as state
import pygame
import menufuncs

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
    
def cyclepower(caller,indexval):
    #cannot switch while firing
    if not state.keys[pygame.K_f]:
        if caller.weap in caller.abilities:
            #get new power
            newindex = caller.abilities.index(caller.weap)+indexval
            if newindex > len(caller.abilities)-1:
                newindex = 0
            caller.weap = caller.abilities[newindex]
        else:
            caller.weap = "dirtycheaterpower"
        caller.pallate = caller.weap
        
def addforce(caller,force):
    caller.speed[0]+=force[0]*state.deltatime
    caller.speed[1]+=force[1]*state.deltatime

def collapsestart(caller,Nix):
    caller.collapsing = True
    
def delete(caller,burner):
    caller.delete()

def loadnextstate(caller,data):
    getattr(menufuncs,f"load{data[0]}")(data[1])

def hitboxon(caller,hitboxname):
    caller.hitboxes[hitboxname].active = True
    
def hitboxoff(caller,hitboxname):
    caller.hitboxes[hitboxname].active = False
    caller.hitboxes[hitboxname].hitobjects = []

def weapDefault(caller,Burner):
    caller.requestanim = True
    caller.animname = "Moonwalk"
    caller.actionqueue.append([5,["hitboxon","testpunch"],[None,None,True]])
    caller.actionqueue.append([65,["hitboxoff","testpunch"],[None,None,True]])

def weapMMissile(caller,Burner):
    caller.actionqueue.append([0,["jump",10],["keys",pygame.K_f,False]])
    
def weapdirtycheaterpower(caller,Burner):
    print("I LOL'D")
