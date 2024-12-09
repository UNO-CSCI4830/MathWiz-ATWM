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
pygame.init()
pygame.mixer.init()

jump_sound = pygame.mixer.Sound("Assets/sounds/SFX/Jump.mp3")
jump_sound.set_volume(.5)
basic_shot_sound = pygame.mixer.Sound("Assets/sounds/SFX/Magic Shot.mp3")
basic_shot_sound.set_volume(.5)
flaming_shot_sound = pygame.mixer.Sound("Assets/sounds/SFX/FireShot.mp3")
flaming_shot_sound.set_volume(.5)
explosion_sound = pygame.mixer.Sound("Assets/sounds/SFX/Explosion.mp3")
explosion_sound.set_volume(.5)
hit_sound = pygame.mixer.Sound("Assets/sounds/SFX/Magic Hit.mp3")
hit_sound.set_volume(.3)
enemy_defeat_sound = pygame.mixer.Sound("Assets/sounds/SFX/EnemyDeath.mp3")
enemy_defeat_sound.set_volume(.7)
from copy import deepcopy
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
    jump_sound.play()
    caller.grounded = False
            
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
        caller.speed[1] -= (caller.gravity/2)*state.deltatime/2
        caller.nextspeedadj[1] -= (caller.gravity/2)*state.deltatime/2

def flip(caller,Burner):
    caller.direction = caller.flip * -1

def setflip(caller,flipset):
    caller.direction = flipset

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
    caller.speed[0] += speed*state.deltatime/2
    caller.nextspeedadj[0] += speed*state.deltatime/2
    if abs(caller.speed[0]) > caller.maxspeed[0]:
        caller.speed[0] = caller.maxspeed[0]*(caller.speed[0]/abs(caller.speed[0]))

#like normal walk, but adjusts for direction
def walkdir(caller,speed):
    """
    Adds the walk speed to the character in the direction the object is facing, unless the speed exceeds max speed.

    Parameters:
    caller : object
        The object calling the function.
    speed : int
        The speed of walking.
    """
    caller.speed[0] += speed*caller.direction*state.deltatime/2
    caller.nextspeedadj[0] += speed*caller.direction*state.deltatime/2
    if abs(caller.speed[0]) > caller.maxspeed[0]:
        caller.speed[0] = caller.maxspeed[0]*caller.direction
        
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
    caller.speed[0]+=force[0]*state.deltatime/2
    caller.speed[1]+=force[1]*state.deltatime/2
    caller.nextspeedadj[0]+=force[0]*state.deltatime/2
    caller.nextspeedadj[1]+=force[1]*state.deltatime/2

def doiftargetleft(caller,data):
    """
    perform a function only if the target object of the caller is to the left of the caller (WARNING: REQUIRES THE PRESENCE OF A TARGET OBJECT).

    Parameters:
    caller : object
        The object calling the function.
    data : tuple
        the action to perform if the condition is true
    """
    if caller.target.right[0] < caller.left[0]:
        globals()[data[0]](caller,data[1])

def doiftargetright(caller,data):
    """
    perform a function only if the target object of the caller is to the right of the caller (WARNING: REQUIRES THE PRESENCE OF A TARGET OBJECT).

    Parameters:
    caller : object
        The object calling the function.
    data : tuple
        the action to perform if the condition is true
    """
    if caller.target.left[0] > caller.right[0]:
        globals()[data[0]](caller,data[1])

def doiftargetabove(caller,data):
    """
    perform a function only if the target object of the caller is above the caller (WARNING: REQUIRES THE PRESENCE OF A TARGET OBJECT).

    Parameters:
    caller : object
        The object calling the function.
    data : tuple
        the action to perform if the condition is true
    """
    if caller.target.bottom[1] < caller.top[1]:
        globals()[data[0]](caller,data[1])

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
    """
    Fires a bullet from the caller.

    Parameters:
    caller : object
        The object calling the function.
    data : list
        The data for the bullet.
    """
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
            caller.shoottimer = 30

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
        tempPallate(caller,"Stun")
        caller.stun = True
        hit_sound.play()

def split(caller,num):
    """
    Divides objects into multiple objects. Enemies will have reduced health, and Projectiles will have altered trajectories

    Parameters:
    caller : object
        The object calling the function.
    num : int
        Number of ways to split the object
    """
    if "healthDivide" in caller.extras.keys():
        caller.extras["healthDivide"] = caller.extras["healthDivide"]*num
        caller.extras["divIterations"] += 1
    else:
        caller.extras["healthDivide"] = num
        caller.extras["divIterations"] = 1
    if hasattr(caller.extras,"maxdiv"):
        max = caller.extras["maxdiv"]
    else:
        max = 3
    if caller.extras["divIterations"] <= max:
        for loop in range(num):
            if type(caller).__name__=="Enemy":
                newpos = [caller.pos[0] + caller.direction*caller.size[0]/num, caller.pos[1]]
                caller.direction = caller.direction * (-1 ** loop)
            elif type(caller).__name__ =="Projectile":
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
    """
    Removes the stun from the caller.

    Parameters:
    caller : object
        The object calling the function.
    data : any
        Placeholder parameter.
    """
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
        state.HUD.blit(state.font.render(f"Get Ready",False,[255,255,255],[0,0,0]),(1800*state.scaleamt,1800*state.scaleamt))

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

def timeslowset(caller,amt):
    state.timeslow = amt

#attacks
def weapGroove(caller,Burner):
    """
    Placeholder weapon attack.

    Parameters:
    caller : object
        The object calling the function.
    Burner : any
        Placeholder parameter.
    """
    caller.requestanim = True
    caller.animname = "Moonwalk"
    caller.actionqueue.append([5,["hitboxon",[[120,0],caller.depth,caller.parallax,caller.layer,{"size":[240,240],"type":"dmg","amt":100,"lifespan":30,"parent":caller}]],[None,None,True]])

def weapDefault(caller,Burner):
    """
    Default weapon attack.

    Parameters:
    caller : object
        The object calling the function.
    Burner : any
        Placeholder parameter.
    """
    caller.shoottimer = 30
    basic_shot_sound.play()
    caller.actionqueue.append([5,["firebullet",[[0,120],caller.depth,caller.parallax,"Bustershot",caller.layer,{"parent":caller}]],[None,None,True]])

def weapDivSlice(caller,Burner):
    """
    Division weapon attack.

    Parameters:
    caller : object
        The object calling the function.
    Burner : any
        Placeholder parameter.
    """
    caller.shoottimer = 30
    caller.actionqueue.append([5,["hitboxon",[[120,0],caller.depth,caller.parallax,caller.layer,{"size":[240,240],"type":"split","amt":2,"lifespan":30,"parent":caller}]],[None,None,True]])

def weapMMissile(caller,Burner):
    """
    Expoent weapon attack.

    Parameters:
    caller : object
        The object calling the function.
    Burner : any
        Placeholder parameter.
    """
    #caller.actionqueue.append([0,["jump",10],["keys",pygame.K_f,False]])caller.shoottimer = 30
    caller.shoottimer = 30
    flaming_shot_sound.play()
    caller.actionqueue.append([5,["firebullet",[[120,0],caller.depth,caller.parallax,"Missile",caller.layer,{"parent":caller}]],[None,None,True]])

def weapdirtycheaterpower(caller,Burner):
    """
    THIS WEAPON CONTAINS WIN

    Parameters:
    caller : object
        The object calling the function.
    Burner : any
        Placeholder parameter.
    """
    caller.requestanim = True
    caller.animname = "Moonwalk"
    print("I LOL'D")

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
    camunlock(caller,Burner)
    caller.delete()
    enemy_defeat_sound.play()

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
    camunlock(caller,Burner)

def dieBoss(caller,Burner):
    caller.actionqueue = [[0,["jump",50],[None,None,True]],[0,["timeslowset",4],[None,None,True]],[60,["timeslowset",1],[None,None,True]]]
    caller.behavior = state.aisource["BossWait"]

    if caller.target != None:
        caller.target.stun = True
        caller.target.speed[0] = 0
        caller.target.animname = "Win"
        caller.target.requestanim = True
        caller.target.actionqueue.append([120,["loadnextstate",["cutscene","outro"]],[None,None,True]])

def dieEnemy(caller,Burner):
    particleSpawn(caller,[caller.pos,
                      [["DieCloud1",0,0,0,5],
                       ["DieCloud2",0,0,0,10],
                       ["DieCloud3",0,0,0,15],
                       ["DieCloud4",0,0,0,5],
                       ["DieCloud5",0,0,0,5],
                       ["DieCloud6",0,0,0,5],
                       ["DieCloud7",0,0,0,10],
                       ["DieCloud8",0,0,0,15]],
                      [0,0],[0,0],[0,0],70])
    for child in caller.children:
        child.delete()
    camunlock(caller,Burner)
    caller.delete()
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
