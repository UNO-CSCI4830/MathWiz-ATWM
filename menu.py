"""
Filename: menu.py
Author(s): Taliesin Reese
Version: 1.2
Date: 10/29/2024
Purpose: Menu elements and layouts for "MathWiz!"
"""
import pygame
import GameData as state
import menufuncs

#this class is for Menu Objects--the current functioality was made with buttons in mind, but could be extrapolated to other stuff too.
class MenuObj:
    """
    A class to represent a menu object.

    Attributes:
    pos : tuple
        The position of the menu object.
    size : tuple
        The size of the menu object.
    graphicsdata : list
        The graphics data for the menu object.
    depth : int
        The depth of the menu object for rendering order.
    text : str
        The text to display on the menu object.
    func : str
        The function to call when the menu object is clicked.
    funcargs : list
        The arguments to pass to the function when the menu object is clicked.
    canvas : pygame.Surface
        The surface to draw the menu object on.
    graphics : pygame.Surface
        The surface to draw the graphics on.
    now : int
        The current time in milliseconds.
    last : int
        The last time the menu object was clicked in milliseconds.
    """
    def __init__(self, pos, size, graphics, depth, text, funcname, assets):
        """
        Initializes the menu object with the given parameters.
        """
        self.pos = pos
        self.size = size
        self.graphicsdata = graphics
        self.depth = depth
        self.text = text
        self.func = funcname
        self.funcargs = assets
        self.canvas = pygame.Surface(self.size)
        self.graphics = pygame.Surface(self.size)
        self.now = 0
        self.last = pygame.time.get_ticks()
        #add self to list of objects to be rendered
        state.objects.append(self)
        #re-sort list to ensure things are rendered in the right order
        state.objects.sort(key = lambda item: item.depth)

    def update(self):
        """
        Updates the menu object, handling hover and click events.
        """
        #if mouse is within button borders, render differently
        if (state.mouse[0] >= self.pos[0]-state.cam.pos[0] and state.mouse[0] <= self.pos[0]-state.cam.pos[0]+self.size[0]) and (state.mouse[1] <= self.pos[1]-state.cam.pos[1]+self.size[1] and state.mouse[1] >= self.pos[1]-state.cam.pos[1]):
        # check when the mouse button is being held down, but only run self.onClick() when the mouse button is released
        # a click is a click; you can't run a function when it's only half.
            if state.click[0]:
                    for event in state.events:
                        if event.type == pygame.MOUSEBUTTONUP:
                            self.onClick()
            else:
                self.onHover()
        else:
            if self.graphicsdata != None:
                self.graphics = pygame.Surface(self.graphicsdata[2:4])
                self.graphics.blit(state.menusheet,(0,0),self.graphicsdata[:4])
                self.canvas.blit(pygame.transform.scale(self.graphics,self.size),(0,0))
            else:
                self.canvas.fill((0,255,0))
        state.display.blit(self.canvas,(self.pos[0]-state.cam.pos[0],self.pos[1]-state.cam.pos[1]))
        text = state.font.render(self.text,False,(0,0,90))
        #draw to the canvas
        state.display.blit(text,((self.pos[0]-state.cam.pos[0]+(self.size[0]/2)-(text.get_width()/2)),(self.pos[1]-state.cam.pos[1]+(self.size[1]/2)-(text.get_height()/2))))
    
    def onClick(self):
        """
        Handles the click event for the menu object.
        """
        # so it turns out when you click a button the MOUSEBUTTONUP event is sent twice.
        # this event is required because you can just hold the button and the bug will happen
        # I don't know how to fix it so this is the next best thing I could come up with
        self.now = pygame.time.get_ticks()
        if self.now - self.last >= 200:
            self.last = pygame.time.get_ticks()
            #get the function bearing the name designated by self.func, and run it using the arguments passed in.
            getattr(menufuncs,self.func)(self.funcargs[0])
    def onHover(self):
        """
        Handles the hover event for the menu object.
        """
        if self.graphicsdata != None:
            self.graphics = pygame.Surface(self.graphicsdata[6:])
            self.graphics.blit(state.menusheet,(0,0),self.graphicsdata[4:8])
            self.canvas.blit(pygame.transform.scale(self.graphics,self.size),(0,0))
        else:
            self.canvas.fill((255,0,0))

