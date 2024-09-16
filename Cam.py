"""
Filename: Cam.py
Author(s): Taliesin Reese
Verion: 1.0
Date: 9/11/2024
Purpose: Camera functions and class for "MathWiz!"
"""
import GameData as state
class cam:
    def __init__(self):
        self.focus = [state.screensize[0]/2,state.screensize[1]/2]
        self.pos = (0,0)
    def update(self):
        self.pos = (self.focus[0]-state.screensize[0]/2, self.focus[1]-state.screensize[1]/2)
