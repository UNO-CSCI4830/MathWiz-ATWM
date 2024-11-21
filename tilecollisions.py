"""
Filename: tilecollisions.py
Author(s): Taliesin Reese
Verion: 1.0
Date: 9/9/2024
Purpose: Equtations for tile collisions in "MathWiz!"
"""
import GameData as state
import pygame
def solid(pos):
    return True
def fortyfive(pos):
    if pos[0] >= state.tilesize-(pos[1]):
        return True
    else:
        return False
def slab(pos):
    if pos[1] >= state.tilesize/2:
        return True
    else:
        return False
def lowtwentytwo(pos):
    if pos[0] >= (state.tilesize-pos[1])*2:
        return True
    else:
        return False
def hightwentytwo(pos):
    if pos[0] >= (state.tilesize-pos[1]-state.tilesize/2)*2:
        return True
    else:
        return False
