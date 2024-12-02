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
    def __init__(self, pos, size, graphics, depth, text, funcname, assets):
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
        #if mouse is within button borders, render differently
        if (state.mouse[0] >= self.pos[0]-state.cam.pos[0] and state.mouse[0] <= self.pos[0]-state.cam.pos[0]+self.size[0]) and (state.mouse[1] <= self.pos[1]-state.cam.pos[1]+self.size[1] and state.mouse[1] >= self.pos[1]-state.cam.pos[1]):
        # check when the mouse button is being held down, but only run self.onClick() when the mouse button is released
        # a click is a click; you can't run a function when it's only half.
            if state.click[0]:
                    if pygame.MOUSEBUTTONUP in state.event_types:
                        self.onClick()
            else:
                if self.text != "":
                    state.menu_button_focus = self
                else:
                    state.menu_button_focus = None
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

        # change buttons if the mouse isn't moving and arrow keys are pressed
        # if nothing is initially selected (hovered), start from the center of the screen and find a button based on the direction of the arrow key
        # if something is initially selected (hovered), start from the center of the button and find another button based on the direction of the arrow key
        # so really, i don't need to focus on a particular button. just on a particular part of the screen
        # how do I not fetch the same button? will search_pos need to be moved to the center of whatever side of a button?

        # try iterating through every object in the list and checking if it's a menu button. then pull data from there
        if pygame.MOUSEMOTION not in state.event_types:
            # print("taking inputs from keyboard to move the buttons...")
            # if there was not a button previously being hovered
            if state.menu_button_focus != None:
                state.menu_button_focus.onHover()   # make sure this works instead of self.onHover()
                search_pos = [state.menu_button_focus.pos[0] + state.menu_button_focus.size[0]/2, state.menu_button_focus.pos[1] + state.menu_button_focus.size[1]/2]
                found = False
                pixel_step_count = 5    # search 5 pixels at a time. buttons should never be smaller than that
                if state.keys[pygame.K_UP]:
                    while not found and 0 < search_pos[1]:
                        search_pos[1] -= pixel_step_count
                        # somehow, get all menu button positions. then check if they're on the same layer and then if the position is within their borders
                elif state.keys[pygame.K_LEFT]:
                    while not found and 0 < search_pos[0]:
                        search_pos[0] -= pixel_step_count
                elif state.keys[pygame.K_RIGHT]:
                    while not found and search_pos[0] < 3600:
                        search_pos[0] += pixel_step_count
                elif state.keys[pygame.K_DOWN]:
                    while not found and search_pos[1] < 3600:
                        search_pos[1] += pixel_step_count
        #draw to the canvas
        state.display.blit(text,((self.pos[0]-state.cam.pos[0]+(self.size[0]/2)-(text.get_width()/2)),(self.pos[1]-state.cam.pos[1]+(self.size[1]/2)-(text.get_height()/2))))
    def onClick(self):
        # so it turns out when you click a button the MOUSEBUTTONUP event is sent twice.
        # this event is required because you can just hold the button and the bug will happen
        # I don't know how to fix it so this is the next best thing I could come up with
        self.now = pygame.time.get_ticks()
        if self.now - self.last >= 200:
            self.last = pygame.time.get_ticks()
            #get the function bearing the name designated by self.func, and run it using the arguments passed in.
            getattr(menufuncs,self.func)(self.funcargs[0])
    def onHover(self):
        if self.graphicsdata != None:
            self.graphics = pygame.Surface(self.graphicsdata[6:])
            self.graphics.blit(state.menusheet,(0,0),self.graphicsdata[4:8])
            self.canvas.blit(pygame.transform.scale(self.graphics,self.size),(0,0))
        else:
            self.canvas.fill((255,0,0))

