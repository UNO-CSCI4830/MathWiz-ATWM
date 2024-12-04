"""
Filename: moves.py
Author(s): Taliesin Reese
Version: 1.10
Date: 12/4/2024
Purpose: moves to be used in "MathWiz!"
"""
import GameData as state
import pygame
import menufuncs

from copy import deepcopy

#set vertical velocity to the jumpspeed
def jump(caller, height):
    #alter this check later to allow for controller support, if that happens
    caller.speed[1] = -height
    caller.grounded = False
            
def jumpstall(caller,height):
    pass
    if caller.speed[1] < 0:
        caller.speed[1] -= (caller.gravity/2)*state.deltatime/2
        caller.nextspeedadj[1] -= (caller.gravity/2)*state.deltatime/2

#add the walk speed to the character, unless the speed exceeds maxspeed.
def walk(caller,speed):
    caller.speed[0] += speed*state.deltatime/2
    caller.nextspeedadj[0] += speed*state.deltatime/2
    if abs(caller.speed[0]) > caller.maxspeed[0]:
        caller.speed[0] = caller.maxspeed[0]*(caller.speed[0]/abs(caller.speed[0]))
        
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
    caller.speed[0]+=force[0]*state.deltatime/2
    caller.speed[1]+=force[1]*state.deltatime/2
    caller.nextspeedadj[0]+=force[0]*state.deltatime/2
    caller.nextspeedadj[1]+=force[1]*state.deltatime/2

def collapsestart(caller,Nix):
    caller.collapsing = True
    
def delete(caller,burner):
    caller.delete()

def loadnextstate(caller,data):
    getattr(menufuncs,f"load{data[0]}")(data[1])

def hitboxon(caller,data):
    print(data)
    if data[4]["parent"] == "spawner":
        data[4]["parent"] = caller
    if data[1] == "spawner":
        data[1] = caller.depth-1
    if data[2] == "spawner":
        data[2] = caller.parallax
    if data[3] == "spawner":
        data[3] = caller.layer
    state.maker.make_obj("Hitbox",data)

def firebullet(caller,data):
    if data[5]["parent"] == "spawner":
        data[5]["parent"] = caller
    if "angle" not in data[5].keys():
        data[5]["angle"] = 0
    if data[1] == "spawner":
        data[1] = caller.depth-1
    if data[2] == "spawner":
        data[2] = caller.parallax
    if data[4] == "spawner":
        data[4] = caller.layer
    if caller.shotLimits.get(data[3])!= None:
        if caller.bulletCounts[data[3]] < caller.shotLimits[data[3]]:
            state.maker.make_obj("Projectile",data)

def stun(caller,data):
    if not caller.stun:
        tempPallate(caller,"Stun")
        caller.stun = True

def split(caller,num):
    if "healthDivide" in caller.extras.keys():
        caller.extras["healthDivide"] = caller.extras["healthDivide"]*num
        caller.extras["divIterations"] += 1
    else:
        caller.extras["healthDivide"] = num
        caller.extras["divIterations"] = 1
    if caller.extras["divIterations"] <= 3:
        for loop in range(num):
            if type(caller).__name__!="Projectile":
                newpos = [caller.pos[0] + caller.direction*caller.size[0]/num, caller.pos[1]]
                caller.direction = caller.direction * (-1 ** loop)
            else:
                newpos = [caller.pos[0]-caller.gun.pos[0],caller.pos[1]-caller.gun.pos[1]]
                caller.extras["angle"] = (90-(180/num*(loop+1))+(180/(num*2)))/2
                caller.extras["flip"] = caller.direction
            if hasattr(caller,"name"):
                obj = state.maker.make_obj(type(caller).__name__, [newpos,caller.depth,caller.parallax,caller.name,caller.layer,caller.extras.copy()])
            else:
                obj = state.maker.make_obj(type(caller).__name__, [newpos,caller.depth,caller.parallax,caller.extras.copy()])
            if type(caller).__name__!="Projectile":
                obj.actionqueue=[[0,["nothing",None],["time",10*loop,True]]]
                obj.iframes = 60
                obj.damagetake(0)
        caller.lifespan = 0
    
def destun(caller,data):
    deTempPallate(caller,"Stun")
    caller.stun = False
    
def tempPallate(caller,name):
    if caller.storepal == None:
        caller.storepal = caller.pallate
        caller.pallate = name

def deTempPallate(caller,Burner):
    if caller.storepal != None:
        caller.pallate = caller.storepal
        caller.storepal = None
    
def camlock(caller,Burner):
    if caller not in state.cam.locks:
        state.cam.locks.append(caller)

def camunlock(caller,Burner):
    if caller in state.cam.locks:
        state.cam.locks.remove(caller)
        
def cammove(caller,pos):
    state.cam.pos = pos
    
def nothing(caller, nothing):
    pass

def levelStart(caller,Burner):
    if type(caller).__name__ == "Player":
        state.HUD.blit(state.font.render(f"Get Ready",False,[255,255,255],[0,0,0]),(1800,1800))

def particleSpawn(caller,data):
    #when inserting particles using this function, format thusly:
    """[
        Location,
        [
           [Particle Data Name, flipx,flipy,rotate,frametime]
        ],
        Init Speed,
        Update Speed,
        Max Speed,
        Lifespan
    ]"""
    fullparticles = []
    for frame in range(len(data[1])):
        fullparticles.append([])
        if data[1][frame][0] in state.particlesource["Graphics"].keys():
            particleinfo = deepcopy(state.particlesource["Graphics"][data[1][frame][0]])
        else:
            particleinfo = [1203,620,120,101]
        particleinfo.extend(data[1][frame][1:])
        fullparticles[frame] = particleinfo
    state.particleManager.particles[caller.layer].append(deepcopy([data[0],fullparticles,data[2],data[3],data[4],0,0,data[5]]))
    
    
#attacks
def weapGroove(caller,Burner):
    caller.requestanim = True
    caller.animname = "Moonwalk"
    caller.actionqueue.append([5,["hitboxon",[[120,0],caller.depth,caller.parallax,caller.layer,{"size":[240,240],"type":"dmg","amt":100,"lifespan":30,"parent":caller}]],[None,None,True]])

def weapDefault(caller,Burner):
    caller.shoottimer = 30
    caller.actionqueue.append([5,["hitboxon",[[120,0],caller.depth,caller.parallax,caller.layer,{"size":[240,240],"type":"split","amt":2,"lifespan":30,"parent":caller}]],[None,None,True]])
    #caller.actionqueue.append([5,["firebullet",[[0,120],caller.depth,caller.parallax,"Bustershot",caller.layer,{"parent":caller}]],[None,None,True]])

def weapMMissile(caller,Burner):
    #caller.actionqueue.append([0,["jump",10],["keys",pygame.K_f,False]])
    caller.actionqueue.append([5,["firebullet",[[120,0],caller.depth,caller.parallax,"Missile",caller.layer,{"parent":caller}]],[None,None,True]])

def weapdirtycheaterpower(caller,Burner):
    caller.requestanim = True
    caller.animname = "Moonwalk"
    print("I LOL'D")
#death functions
def dieDefault(caller,Burner):
    for child in caller.children:
        child.delete()
    camunlock(caller,Burner)
    caller.delete()

def diePlayer(caller,Burner):
    caller.actionqueue = [[120,["loadnextstate",["level",state.level.name]],[None,None,True]],[30,["stun",None],[None,None,True]]]
    caller.stun = True
    caller.animname = "Fall"
    caller.requestanim = True
    camunlock(caller,Burner)

def dieBoss(caller,Burner):
    if caller.target != None:
        caller.target.stun = True
        caller.target.speed[0] = 0
        caller.target.animname = "Win"
        caller.target.requestanim = True
        caller.target.actionqueue.append([120,["loadnextstate",["cutscene","outro"]],[None,None,True]])

def diePlat(caller,particlename):
    particleSpawn(caller,[[caller.left[0],caller.top[1]],
                      [[particlename,0,0,0,10],
                       [particlename,0,0,90,10],
                       [particlename,0,0,180,10],
                       [particlename,0,0,270,10]],
                      [-10,-10],[0,20],[50,100],60])
    particleSpawn(caller,[[caller.left[0],caller.bottom[1]],
                      [[particlename,0,0,0,10],
                       [particlename,0,0,90,10],
                       [particlename,0,0,180,10],
                       [particlename,0,0,270,10]],
                      [-5,-10],[0,20],[50,100],60])
    particleSpawn(caller,[[caller.right[0],caller.top[1]],
                      [[particlename,0,0,0,10],
                       [particlename,0,0,90,10],
                       [particlename,0,0,180,10],
                       [particlename,0,0,270,10]],
                      [10,-10],[0,20],[50,100],60])
    particleSpawn(caller,[[caller.right[0],caller.bottom[1]],
                      [[particlename,0,0,0,10],
                       [particlename,0,0,90,10],
                       [particlename,0,0,180,10],
                       [particlename,0,0,270,10]],
                      [5,-10],[0,20],[50,100],60])
    camunlock(caller,None)
    caller.delete()
