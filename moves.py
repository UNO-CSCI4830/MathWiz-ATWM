"""
Filename: moves.py
Author(s): Taliesin Reese
Version: 1.8
Date: 11/10/2024
Purpose: moves to be used in "MathWiz!"
"""
import GameData as state
import pygame
import menufuncs

#set vertical velocity to the jumpspeed
def jump(caller, height):
    """
    Sets vertical velocity to the jump speed.

    Parameters:
    caller : object
        The object calling the function.
    height : int
        The height of the jump.
    """
    caller.speed[1] = -height
            
def jumpstall(caller,height):
    """
    Reduces the upward speed of the caller if they are moving upwards.

    Parameters:
    caller : object
        The object calling the function.
    height : int
        The height of the jump.
    """
    if caller.speed[1] < 0:
        caller.speed[1] -= (caller.gravity/2)*state.deltatime

#add the walk speed to the character, unless the speed exceeds maxspeed.
def walk(caller,speed):
    """
    Adds the walk speed to the character, unless the speed exceeds max speed.

    Parameters:
    caller : object
        The object calling the function.
    speed : int
        The speed of walking.
    """
    caller.speed[0] += speed*state.deltatime
    if abs(caller.speed[0]) > caller.maxspeed:
        caller.speed[0] = caller.maxspeed*(caller.speed[0]/abs(caller.speed[0]))
        
def setforce(caller,force):
    """
    Sets the force on the caller.

    Parameters:
    caller : object
        The object calling the function.
    force : tuple
        The force to set on the caller.
    """
    if force[0] != None:
        caller.speed[0]=force[0]
    if force[1] != None:
        caller.speed[1]=force[1]
    
def cyclepower(caller,indexval):
    """
    Cycles through the caller's abilities.

    Parameters:
    caller : object
        The object calling the function.
    indexval : int
        The index value to cycle through.
    """
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
    """
    Adds force to the caller.

    Parameters:
    caller : object
        The object calling the function.
    force : tuple
        The force to add to the caller.
    """
    caller.speed[0]+=force[0]*state.deltatime
    caller.speed[1]+=force[1]*state.deltatime

def collapsestart(caller,Nix):
    """
    Starts the collapsing process for the caller.

    Parameters:
    caller : object
        The object calling the function.
    Nix : any
        Placeholder parameter.
    """
    caller.collapsing = True
    
def delete(caller,burner):
    """
    Deletes the caller.

    Parameters:
    caller : object
        The object calling the function.
    burner : any
        Placeholder parameter.
    """
    caller.delete()

def loadnextstate(caller,data):
    """
    Loads the next state.

    Parameters:
    caller : object
        The object calling the function.
    data : list
        The data for the next state.
    """
    getattr(menufuncs,f"load{data[0]}")(data[1])

def hitboxon(caller,data):
    """
    Turns on the hitbox for the caller.

    Parameters:
    caller : object
        The object calling the function.
    data : list
        The data for the hitbox.
    """
    if data[4][4] == "spawner":
        data[4][4] = caller
    if data[1] == "spawner":
        data[1] = caller.depth-1
    if data[2] == "spawner":
        data[2] = caller.parallax
    if data[3] == "spawner":
        data[3] = caller.layer
    state.maker.make_obj("Hitbox",data)

def firebullet(caller,data):
    """
    Fires a bullet from the caller.

    Parameters:
    caller : object
        The object calling the function.
    data : list
        The data for the bullet.
    """
    state.maker.make_obj("Projectile",data)

def stun(caller,data):
    """
    Stuns the caller.

    Parameters:
    caller : object
        The object calling the function.
    data : any
        Placeholder parameter.
    """
    if not caller.stun:
        caller.stun = True
        caller.storepal = caller.pallate
        caller.pallate = "Stun"
    
def destun(caller,data):
    """
    Removes the stun from the caller.

    Parameters:
    caller : object
        The object calling the function.
    data : any
        Placeholder parameter.
    """
    caller.pallate = caller.storepal
    caller.stun = False

def nothing(caller, nothing):
    pass

#attacks
def weapDefault(caller,Burner):
    """
    Default weapon attack.

    Parameters:
    caller : object
        The object calling the function.
    Burner : any
        Placeholder parameter.
    """
    caller.requestanim = True
    caller.animname = "Moonwalk"
    caller.actionqueue.append([5,["hitboxon",[[120,0],caller.depth,caller.parallax,caller.layer,[[240,240],"dmg",10,30,caller]]],[None,None,True]])

def weapMMissile(caller,Burner):
    """
    Missile weapon attack.

    Parameters:
    caller : object
        The object calling the function.
    Burner : any
        Placeholder parameter.
    """
    #caller.actionqueue.append([0,["jump",10],["keys",pygame.K_f,False]])
    caller.actionqueue.append([5,["firebullet",[[120,0],caller.depth,caller.parallax,"Missile",caller.layer,[caller]]],[None,None,True]])
    
def weapdirtycheaterpower(caller,Burner):
    """
    Cheater power weapon attack.

    Parameters:
    caller : object
        The object calling the function.
    Burner : any
        Placeholder parameter.
    """
    caller.requestanim = True
    caller.animname = "Moonwalk"
    print("I LOL'D")

def explode_and_split(caller, data):
    """
    Explodes the caller and spawns new objects.

    Parameters:
    caller : object
        The object calling the function.
    data : list
        The data for the new objects.
    """
    caller.delete()

    for obj_data in data:
        obj_type = obj_data.get("type","Projectile")
        position = obj_data.get("position", caller.pos)
        name = obj_data.get("name",obj_type)
        state.maker.make_obj(obj_type,[position, name])
#death functions
def dieDefault(caller,Burner):
    """
    Default death function.

    Parameters:
    caller : object
        The object calling the function.
    Burner : any
        Placeholder parameter.
    """
    for child in caller.children:
        child.delete()
    caller.delete()

def diePlayer(caller,Burner):
    """
    Player death function.

    Parameters:
    caller : object
        The object calling the function.
    Burner : any
        Placeholder parameter.
    """
    caller.actionqueue = [[120,["loadnextstate",["level",state.level.name]],[None,None,True]],[30,["stun",None],[None,None,True]]]
    caller.stun = True
    caller.animname = "Fall"
    caller.requestanim = True
    

