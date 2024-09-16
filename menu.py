"""
Filename: menu.py
Author(s): Taliesin Reese
Version: 1.0
Date: 9/8/2024
Purpose: Menu elements and layouts for "MathWiz!"
"""
import pygame
import GameData as state
import menufuncs

#this class is for Menu Objects--the current functioality was made with buttons in mind, but could be extrapolated to other stuff too.
class MenuObj:
    def __init__(self, pos, size, depth, text, funcname, assets):
        self.pos = pos
        self.size = size
        self.depth = depth
        self.text = text
        self.func = funcname
        self.funcargs = assets
        #add self to list of objects to be rendered
        state.objects.append(self)
        #re-sort list to ensure things are rendered in the right order
        state.objects.sort(key = lambda item: item.depth)
    def update(self):
        #if mouse is within button borders, render differently
        if (state.mouse[0] >= self.pos[0]-state.cam.pos[0] and state.mouse[0] <= self.pos[0]-state.cam.pos[0]+self.size[0]) and (state.mouse[1] <= self.pos[1]-state.cam.pos[1]+self.size[1] and state.mouse[1] >= self.pos[1]-state.cam.pos[1]):
            pygame.draw.rect(state.display, (255,0,0), (self.pos[0]-state.cam.pos[0],self.pos[1]-state.cam.pos[1],self.size[0],self.size[1]))
            #if the mouse button 1 is down, run the function assigned to this object
            if state.click[0]:
                self.onClick()
        else:
            pygame.draw.rect(state.display, (0,255,0), (self.pos[0]-state.cam.pos[0],self.pos[1]-state.cam.pos[1],self.size[0],self.size[1]))
        text = state.font.render(self.text,False,(0,0,90))
        #draw to the canvas
        state.display.blit(text,((self.pos[0]-state.cam.pos[0]+(self.size[0]/2)-(text.get_width()/2)),(self.pos[1]-state.cam.pos[1]+(self.size[1]/2)-(text.get_height()/2))))
    def onClick(self):
        #get the function bearing the name designated by self.func, and run it using the arguments passed in.
        getattr(menufuncs,self.func)(self.funcargs[0])
