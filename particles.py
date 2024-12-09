"""
Filename: particles.py
Author(s): Taliesin Reese
Version: 1.0
Date: 11/23/2024
Purpose: Particle System for "MathWiz!"
"""
import pygame

import GameData as state

class ParticleManager:
    def __init__(self):
        self.particles = [[]]
        self.storage = pygame.Surface(state.screensize).convert()
        self.storage.set_colorkey(state.invis)
    def updateLayer(self,layer):
        self.storage.fill(state.invis)
        index = 0
        #iterate through all particles on the current layer
        while index < len(self.particles[layer]):
            particle = self.particles[layer][index]
            #when inserted, particles are to be formatted thusly:
            """[
                [Location],
                [
                    [frame x, frame y, frame len, frame width, flipx, flipy, rotate, ticktime]
                ],
                [Current move vector],
                [Momentum change vector],
                [Terminal velocity],
                frame,
                timer,
                lifespan
            ]"""
            #draw graphics
            parallaxmod = state.level.parallaxes[layer]-state.cam.depth
            
            state.display.blit(state.spritesheet,
                               ((particle[0][0]+particle[2][0] - state.cam.pos[0]*parallaxmod)*state.scaleamt,
                                (particle[0][1]+particle[2][1] - state.cam.pos[1]*parallaxmod)*state.scaleamt),
                               [particle[1][particle[5]][0]*state.scaleamt,
                                particle[1][particle[5]][1]*state.scaleamt,
                                particle[1][particle[5]][2]*state.scaleamt,
                                particle[1][particle[5]][3]*state.scaleamt])
            #update the movement speed. Don't let them break TV, tho
            if particle[2][0] >= 0:
                if particle[2][0] <= particle[4][0]:
                    particle[2][0] += particle[3][0]*state.deltatime
                else:
                    particle[2][0] = particle[4][0]
            else:
                if particle[2][0] >= -particle[4][0]:
                    particle[2][0] += particle[3][0]*state.deltatime
                else:
                    particle[2][0] = -particle[4][0]
                    
            if particle[2][1] >= 0:
                if particle[2][1] <= particle[4][1]:
                    particle[2][1] += particle[3][1]*state.deltatime
                else:
                    particle[2][1] = particle[4][1]
            else:
                if particle[2][1] >= -particle[4][1]:
                    particle[2][1] += particle[3][1]*state.deltatime
                else:
                    particle[2][1] = -particle[4][1]
                    
            #update location
            particle[0][0] += particle[2][0]
            particle[0][1] += particle[2][1]
            #update timers
            particle[6]+=state.deltatime
            particle[7]-=state.deltatime
            #update frame if the current one's run it's course
            if particle[6] >= particle[1][particle[5]][7]:
                particle[6] = 0#particle[1][particle[5]][7]
                particle[5] += 1
            if particle[5] >= len(particle[1]):
                particle[5] = 0
            #delete the object if it's lifespan is up
            #print(particle)
            if particle[7] <= 0:
                self.particles[layer].remove(particle)
            else:
                index += 1
        #state.display.blit(self.storage,(0,0))
                
    def reset(self):
        self.particles = []
        for layer in state.level.loops:
            self.particles.append([])
