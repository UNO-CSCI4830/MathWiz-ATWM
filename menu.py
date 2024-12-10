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
        self.canvas = pygame.Surface([self.size[0]*state.scaleamt,self.size[1]*state.scaleamt])
        self.graphics = pygame.Surface([self.size[0]*state.scaleamt,self.size[1]*state.scaleamt])
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
        # somewhere I removed the code that removes the main background menu art. this is another revolutionary bandaid fix
        if self.text == "":
            self.onHover()
        #if mouse is within button borders, render differently
        if (state.mouse[0] >= self.pos[0]-state.cam.pos[0] and state.mouse[0] <= self.pos[0]-state.cam.pos[0]+self.size[0]) and (state.mouse[1] <= self.pos[1]-state.cam.pos[1]+self.size[1] and state.mouse[1] >= self.pos[1]-state.cam.pos[1]):
        # check when the mouse button is being held down, but only run self.onClick() when the mouse button is released
        # a click is a click; you can't run a function when it's only half.
            if (state.click[0] and pygame.MOUSEBUTTONUP in state.event_types) or (pygame.K_RETURN in state.newkeys):
                self.onClick()
            elif pygame.MOUSEMOTION in state.event_types and self.text != "":
                state.menu_button_focus = self
        else:
            if self.graphicsdata != None:
                #self.graphics = pygame.Surface([self.graphicsdata[2]*state.scaleamt,self.graphicsdata[3]*state.scaleamt])
                self.graphics.blit(state.menusheet,(0,0),[self.graphicsdata[0]*state.scaleamt,self.graphicsdata[1]*state.scaleamt,self.graphicsdata[2]*state.scaleamt,self.graphicsdata[3]*state.scaleamt])
                self.canvas.blit(pygame.transform.scale(self.graphics,[self.size[0]*state.scaleamt,self.size[1]*state.scaleamt]),(0,0))
            else:
                self.canvas.fill((0,255,0))
        state.display.blit(self.canvas,((self.pos[0]-state.cam.pos[0])*state.scaleamt,(self.pos[1]-state.cam.pos[1])*state.scaleamt))
        text = state.font.render(self.text,False,(0,0,90))

        # allow traversal through the menus with arrow keys
        if pygame.MOUSEMOTION not in state.event_types:
            # if there was a button previously being hovered, search from that button
            if state.menu_button_focus != None:
                found_button = None
                if state.keys[pygame.K_UP] or state.keys[pygame.K_w]:
                    found_button = menufuncs.search([state.menu_button_focus.pos[0] + state.menu_button_focus.size[0]/2, state.menu_button_focus.pos[1]]) # upmost center point
                elif state.keys[pygame.K_LEFT] or state.keys[pygame.K_a]:
                    found_button = menufuncs.search([state.menu_button_focus.pos[0], state.menu_button_focus.pos[1] + state.menu_button_focus.size[1]/2]) # leftmost center point
                elif state.keys[pygame.K_RIGHT] or state.keys[pygame.K_d]:
                    found_button = menufuncs.search([state.menu_button_focus.pos[0] + state.menu_button_focus.size[0], state.menu_button_focus.pos[1] + state.menu_button_focus.size[1]/2]) # rightmost center point
                elif state.keys[pygame.K_DOWN] or state.keys[pygame.K_s]:
                    found_button = menufuncs.search([state.menu_button_focus.pos[0] + state.menu_button_focus.size[0]/2, state.menu_button_focus.pos[1] + state.menu_button_focus.size[1]]) # bottommost center point
            else: # if not (aka: mouse was not on anything), attempt to search from the center of the screen
                found_button = menufuncs.search([state.screensize[0]/2, state.screensize[1]/2])
            if found_button:
                    state.menu_button_focus = found_button
                    pygame.mouse.set_pos([(found_button.pos[0] + found_button.size[0]/2)/(state.screensize[0]/800), (found_button.pos[1] + found_button.size[1]/2)/(state.screensize[1]/800)])

        #draw to the canvas
        state.display.blit(text,(((self.pos[0]-state.cam.pos[0])*state.scaleamt+(self.size[0]*state.scaleamt/2)-(text.get_width()*state.scaleamt/2)),((self.pos[1]-state.cam.pos[1])*state.scaleamt+(self.size[1]*state.scaleamt/2)-(text.get_height()*state.scaleamt/2))))
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
            #self.graphics = pygame.Surface([self.graphicsdata[6]*state.scaleamt,self.graphicsdata[7]*state.scaleamt])
            self.graphics.blit(state.menusheet,(0,0),[self.graphicsdata[4]*state.scaleamt,self.graphicsdata[5]*state.scaleamt,self.graphicsdata[6]*state.scaleamt,self.graphicsdata[7]*state.scaleamt])
            self.canvas.blit(pygame.transform.scale(self.graphics,[self.size[0]*state.scaleamt,self.size[1]*state.scaleamt]),(0,0))
        else:
            self.canvas.fill((255,0,0))

