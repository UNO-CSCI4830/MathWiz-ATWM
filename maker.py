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
    """
    A class that makes instances of other classes to prevent import loops.

    Methods:
    make_obj(classname, info):
        Creates an instance of the specified class with the given information.
    """
    def make_obj(self,classname,info):
        """
        Creates an instance of the specified class with the given information.

        Parameters:
        classname : str
            The name of the class to instantiate.
        info : list
            The information to pass to the class constructor.
        """
        if len(info) > 5:
            getattr(objects,classname)(info[0],info[1],info[2],info[3],info[4],info[5])
        else:
            getattr(objects,classname)(info[0],info[1],info[2],info[3],info[4])
