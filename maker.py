"""
Filename: maker.py
Author(s): Taliesin Reese
Version: 1.0
Date: 10/28/2024
Purpose: Support class for "MathWiz!"
"""
import objects
import level
import menu

#a class that makes instances of other classes. To prevent import loops, mostly
class maker:
    def make_obj(self,classname,info):
        if len(info) > 5:
            getattr(objects,classname)(info[0],info[1],info[2],info[3],info[4],info[5])
        else:
            getattr(objects,classname)(info[0],info[1],info[2],info[3],info[4])
