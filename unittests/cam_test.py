import unittest
from unittest.mock import MagicMock
import GameData as state
from Cam import cam 

class TestCam(unittest.TestCase):
    #Initialization test to make sure all is good
    def test_initialization(self):
        state.screensize = [800, 600]
        #get class
        camera = cam()

        #simple assertion
        #get center camera
        self.assertEqual(camera.focus, [400, 300])  
        self.assertEqual(camera.pos, (0, 0))
        self.assertEqual(camera.lastpos, (0, 0))
        self.assertEqual(camera.depth, 0)
        self.assertIsNone(camera.focusobj)

    def test_update_no_focus(self):
        state.screensize = [800, 600]
        #test play
        state.gamemode = "play" 
        #no objects 
        state.objects = []
        camera = cam()
        
        camera.update()

        #test if camera position changes
        self.assertEqual(camera.pos, (0, 0))
        self.assertEqual(camera.lastpos, (0, 0))

    def test_focus_objects(self):
        state.screensize = [800, 600]
        state.gamemode = "play"
        state.objects = []

        mock_focus_object = MagicMock()
        mock_focus_object.pos = [1000, 800]
        mock_focus_object.parallax = 1  # Default parallax

        camera = cam()
        camera.focusobj = mock_focus_object
        camera.update()

        # The camera should center on the focus object
        self.assertEqual(camera.focus, [1000, 800])
        self.assertEqual(camera.pos, (600, 500))  # Adjusted for screen size
    

unittest.main()