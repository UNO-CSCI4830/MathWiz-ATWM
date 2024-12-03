"""
Filename: animHandlers.py
Author(s): Taliesin Reese
Version: 1.0
Date: 12/1/2024
Purpose: Entity Animation Handlers for "MathWiz!"
"""
def MathWizanimationPick(caller):
        framecontinue = False
        #OVERRIDE: If specially requested, play that animation until completion.
        if caller.requestanim == False:
            #if nonxero speed on x-axis and grounded, return the walking animation
            if caller.grounded:
                if abs(caller.speed[0]) > 0:
                    if caller.shoottimer > 0:
                        if caller.lastanim =="Walk":
                            framecontinue = True
                        caller.animname = "WalkShoot"
                    else:
                        caller.animname = "Walk"
                #by default, return the idle animation
                else:
                    if caller.shoottimer > 0:
                        caller.animname = "Shoot"
                    else:
                        caller.animname = "Idle"
            #if not grounded and going up, retun jumping animation
            elif caller.grounded == False:
                #if notgrounded and falling down, return falling animation
                if caller.shoottimer > 0:
                    caller.animname = "AirShoot1"
                else:
                    if caller.speed[1] >= 0:
                        caller.animname = "Fall"
                    else:
                        caller.animname = "Jump"
        if caller.animname != caller.lastanim and not framecontinue:
            caller.animtime = 0
            caller.animframe = 0
def ExponianimationPick(caller):
    caller.animname = "Base1"
