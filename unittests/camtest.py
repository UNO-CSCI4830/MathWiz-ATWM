import unittest
import sys
sys.path.append("../MathWiz-ATWM")
#create objects
from unittest.mock import MagicMock
import GameData as state
from Cam import cam 

class TestCam(unittest.TestCase):
    #camera setup
    def test_setup(self):
        #set up screen, i made it 500x500 for ease
        state.screensize = [500, 500]
        #actually set up cam
        camera = cam()

        #simple assertion
        #get center camera
        #focuse on half
        self.assertEqual(camera.focus, [250, 250])  
        #make sure its center
        self.assertEqual(camera.pos, (0, 0))
        self.assertEqual(camera.depth, 0)

    def test_no_focus(self):
        #set a small screen
        state.screensize = [800, 600]
        #put it in play gamemode instead of edit
        state.gamemode = "play" 
        #no objects 
        state.objects = []
        camera = cam()
        #update settings
        camera.update()

        #test if camera position changes
        self.assertEqual(camera.pos, (0, 0))   #this is just to make sure its position is in center
        self.assertEqual(camera.lastpos, (0, 0))

    def test_focus_objects_regular(self):
        #screen size random nums to test
        state.screensize = [600, 600]
        state.gamemode = "play"
        state.objects = []

        #create mock object like earlier
        mock_focus_object = MagicMock()
        #add a position to focus, can be any value I just chose 800,400
        mock_focus_object.pos = [800, 400]
        #set up cam
        camera = cam()
        camera.focusobj = mock_focus_object
        #update
        camera.update()

        #okay, test to see if there is focus on the object
        self.assertEqual(camera.focus, [800, 400])  #should be same nums as object position
        #calculate cam position
        #focus[0] - screensize[0]/2 = 800 - 600/2 = 500
        #focus[1] - screensize[1]/2 = 400 - 600/2 = 100
        #make sure the nums match
        self.assertEqual(camera.pos, (500, 100))  
        #success

    #Focus on a negative position, handle negative numbers
    def test_focus_objects_negative(self):
        #same nums as above
        state.screensize = [600, 600]
        state.gamemode = "play"
        state.objects = []

        #create mock object like earlier
        mock_focus_object = MagicMock()
        #add a position to focus, this time 200 for second, so we can get a negative num, explained in a sec
        mock_focus_object.pos = [800, 200]
       
        #set cam
        camera = cam()
        camera.focusobj = mock_focus_object
        camera.update()

        #obj position
        self.assertEqual(camera.focus, [800, 200])
        #as in test above
        # 800 - 600/2 = 500
        # 200 - 600/2 = -100 
        #test to see if it pans -100
        self.assertEqual(camera.pos, (500, -100))
        #success

    #testing edit mode
    def test_edit(self):
        #set screen size
        state.screensize = [600, 600]
        #set gamemode to edit
        state.gamemode = "edit"
        state.objects = []

        camera = cam()
        camera.focus = [400, 500]
        camera.update()

        #same equation 
        #400 - 600/2 = 100
        # 500 - 600/2 = 200
        #testing
        self.assertEqual(camera.pos, (100, 200))  
        #success

    #test object parallax
    def test_with_parallax(self):
        state.screensize = [600, 600]
        state.gamemode = "play"

        #mock object
        mock_focus_object = MagicMock()
        mock_focus_object.pos = [400, 500]
        #set up parallax to tes depth
        mock_focus_object.parallax = 4 

        camera = cam()
        camera.focusobj = mock_focus_object
        camera.update()

        #first depth
        # 4 - 1 = 3
        #test depth of 3
        self.assertEqual(camera.depth, 3)
        #success
        #test cam position same equation
        self.assertEqual(camera.pos, (100, 200))
        #success 
    

unittest.main()