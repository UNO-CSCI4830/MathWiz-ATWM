"""
Filename: Cam.py
Author(s): Taliesin Reese, Vladislav Plotnikov
Verion: 1.4
Date: 10/26/2024
Purpose: Camera functions and class for "MathWiz!"
"""
import GameData as state
class cam:
    def __init__(self):
        self.focus = [state.screensize[0]/2,state.screensize[1]/2]
        self.pos = (0,0)
        self.lastpos = (0,0)
        self.depth = 0
        self.focusobj = None
        self.locks = []
    def update(self):
        self.lastpos = self.pos
        #set focus and depth such that the focus object will always be in the center
        if self.focusobj != None:
            self.focus = self.focusobj.pos
            self.depth = self.focusobj.parallax-1
        #set position so focus object is centered.
        #if objects are locking the camera, it should not move.
        if self.locks == []:
            self.pos = (self.focus[0]-state.screensize[0]/2, self.focus[1]-state.screensize[1]/2)
        #do not pan the camera if doing so would expose void.
        if state.gamemode != "edit":
            for item in state.objects:
                if type(item).__name__ == "drawlayer":
                    if item.loop == False:
                        parallaxmod = item.parallax-self.depth
                        if self.pos[0]*parallaxmod < 0:
                            self.pos = (0,self.pos[1])
                        elif (self.pos[0]+state.screensize[0])*parallaxmod > item.width:
                            self.pos = (item.width-state.screensize[0],self.pos[1])
                        if self.pos[1]*parallaxmod < 0:
                            self.pos = (self.pos[0],0)
                        elif (self.pos[1]+state.screensize[1])*parallaxmod > item.height:
                            self.pos = (self.pos[0],item.height-state.screensize[1])

