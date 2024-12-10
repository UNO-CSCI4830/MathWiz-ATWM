"""
Filename: Cam.py
Author(s): Taliesin Reese, Vladislav Plotnikov
Verion: 1.6
Date: 11/23/2024
Purpose: Camera functions and class for "MathWiz!"
"""
import GameData as state
class cam:
    """
    A class to represent the camera in the game.

    Attributes:
    focus: list
        The focus point of the camera.
    pos: tuple
        Current position of the camera.
    lastpos: tuple
        Previous position of the camera.
    depth: int
        The depth of the camera.
    focusobj: object
        The object that the camera is focused on.
    """

    def __init__(self):
        """
        Initializes the camera with default values.
        """
        self.focus = [state.screensize[0]/2,state.screensize[1]/2]
        self.pos = (0,0)
        self.lastpos = (0,0)
        self.depth = 0
        self.focusobj = None
        self.locks = []
    def update(self):
        """
        Updates the camera's position and focus based on the focus object.
        Ensures that the camera does not expose void areas.
        """
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
                if type(item).__name__ == "drawlayer" and item.parallax == self.depth + 1:
                    parallaxmod = item.parallax-self.depth
                    if item.loop[0] == False:
                        if self.pos[0]*parallaxmod < 0:
                            self.pos = (0,self.pos[1])
                        elif (self.pos[0]+state.screensize[0])*parallaxmod > item.width:
                            self.pos = (item.width-state.screensize[0],self.pos[1])
                    if item.loop[1] == False:
                        if self.pos[1]*parallaxmod < 0:
                            self.pos = (self.pos[0],0)
                        elif (self.pos[1]+state.screensize[1])*parallaxmod > item.height:
                            self.pos = (self.pos[0],item.height-state.screensize[1])

