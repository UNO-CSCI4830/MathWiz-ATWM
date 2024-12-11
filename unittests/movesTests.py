import unittest

import objects
import moves
import GameData as state
from unittest.mock import patch


#the tilesize is a lynchpin. All measures in the game save for the final render size are based on the tile (or, they will be in the final product. Not all of them are right now)
state.tilesize = 120
#anyway set up pygame stuff
state.screensize = (state.tilesize*30,state.tilesize*30)

#initialize game stuffs
state.gamemode = "play"
state.invis = (255,0,255)
state.deltatime = 1
state.fpsTarget = 60

state.objects = []

class movesTests(unittest.TestCase):

    def setUp(self):
        self.caller = objects.gameObject([10, 10], 1, 1,  1, 1)
        self.caller.speed = [10, 10]
        self.caller.gravity = 10
        self.caller.maxspeed = 15
        self.caller.stun = False
        self.caller.storepal = "foo"
        self.caller.pallate = "boo"

        self.fakeCaller = 5

    # jump test methods

    def test_jump(self):
        moves.jump(self.caller, 5)
        self.assertEqual(self.caller.speed[1], -5)

    def test_jump_throw_error(self):
        with self.assertRaises(AttributeError):
            moves.jump(self.fakeCaller, 5)

    # jumpstall test methods

    def test_jumpstall(self):
        moves.jumpstall(self.caller, 5)
        self.assertEqual(self.caller.speed[1], 10)

        #Test the if statement for when vertical speed is less than 0
        self.caller.speed[1] = -5
        moves.jumpstall(self.caller, 5)
        self.assertEqual(self.caller.speed[1], -10)


    def test_jumpstall_throw_error(self):
        with self.assertRaises(AttributeError):
            moves.jumpstall(self.fakeCaller, 5)

    # walk test methods

    def test_walk(self):
        moves.walk(self.caller, 2)
        self.assertEqual(self.caller.speed[0], 12)

        #Test the if branch for when horizontal speed is greater than max speed
        self.caller.speed[0] = 20
        moves.walk(self.caller, 5)
        self.assertEqual(self.caller.speed[0], 15)

    def test_walk_throw_error(self):
        with self.assertRaises(AttributeError):
            moves.walk(self.fakeCaller, 5)

    # setforce test methods

    def test_setforce(self):
        moves.setforce(self.caller, [5, 5])
        self.assertEqual(self.caller.speed[0], 5)
        self.assertEqual(self.caller.speed[1], 5)

        moves.setforce(self.caller, [10, 10])
        self.assertEqual(self.caller.speed[0], 10)
        self.assertEqual(self.caller.speed[1], 10)

        moves.setforce(self.caller, [-5, -5])
        self.assertEqual(self.caller.speed[0], -5)
        self.assertEqual(self.caller.speed[1], -5)

    # addforce test methods

    def test_addforce(self):
        moves.addforce(self.caller, [5, 5])
        self.assertEqual(self.caller.speed[0], 15)
        self.assertEqual(self.caller.speed[1], 15)

        # Add a negative force
        moves.addforce(self.caller, [-10, -10])
        self.assertEqual(self.caller.speed[0], 5)
        self.assertEqual(self.caller.speed[1], 5)

        # Add a huge force
        moves.addforce(self.caller, [10000, 10000])
        self.assertEqual(self.caller.speed[0], 10005)
        self.assertEqual(self.caller.speed[1], 10005)

    def test_addforce_throw_error(self):

        # throws error when force is not a number
        with self.assertRaises(TypeError):
            moves.addforce(self.caller, ["foo"])

        # throws error when force is not long enough
        with self.assertRaises(IndexError):
            moves.addforce(self.caller, [1])

        # throws error caller doesn't have attribute
        with self.assertRaises(AttributeError):
            moves.addforce(self.fakeCaller, [1, 1])

    # delete test methods

    @patch("objects.gameObject.delete")
    def test_delete(self, mock_delete):
        #Make sure the moves delete calls the objects delete
        moves.delete(self.caller, "foo")
        mock_delete.assert_called()


    def test_delete_throw_error(self):
        with self.assertRaises(AttributeError):
            moves.delete(self.fakeCaller, "foo")

    # stun test methods

    def test_stun(self):
        moves.stun(self.caller, "foo")
        self.assertTrue(self.caller.stun)
        self.assertEqual(self.caller.storepal, "boo")
        self.assertEqual(self.caller.pallate, "Stun")

    def test_stun_throw_error(self):
        with self.assertRaises(AttributeError):
            moves.stun(self.fakeCaller, "foo")

    # destun test methods

    def test_destun(self):
        moves.stun(self.caller, "foo")

        moves.destun(self.caller, "foo")
        self.assertFalse(self.caller.stun)
        self.assertEqual(self.caller.pallate, "boo")

    def test_destun_throw_error(self):
        with self.assertRaises(AttributeError):
            moves.destun(self.fakeCaller, "foo")






if __name__ == '__main__':
    unittest.main()