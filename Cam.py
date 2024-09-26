"""
Filename: Cam.py
Author(s): Taliesin Reese
Verion: 1.1
Date: 9/26/2024
Purpose: Camera functions and class for "MathWiz!"
"""
import GameData as state
class cam:
    def __init__(self):
        self.focus = [state.screensize[0]/2,state.screensize[1]/2]
        self.pos = (0,0)
        self.depth = 0
    def update(self):
        self.pos = (self.focus[0]-state.screensize[0]/2, self.focus[1]-state.screensize[1]/2)
