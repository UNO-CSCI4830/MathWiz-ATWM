import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Cam
import pytest
import state


class MockFocusObject:
    def __init__(self, pos, parallax):
        self.pos = pos
        self.parallax = parallax

@pytest.fixture
def camera():
    return Cam.cam()

def test_initialization(camera):
    assert camera.focus == [state.screensize[0]/2, state.screensize[1]/2]
    assert camera.pos == (0, 0)
    assert camera.lastpos == (0, 0)
    assert camera.depth == 0
    assert camera.focusobj is None

def test_update_focus_object(camera):
    focus_obj = MockFocusObject((100, 100), 2)
    camera.focusobj = focus_obj
    camera.update()
    assert camera.focus == (100, 100)
    assert camera.depth == 1

def test_update_position(camera):
    focus_obj = MockFocusObject((100, 100), 2)
    camera.focusobj = focus_obj
    camera.update()
    assert camera.pos == (100 - state.screensize[0]/2, 100 - state.screensize[1]/2)

def test_update_no_focus_object(camera):
    camera.update()
    assert camera.pos == (camera.focus[0] - state.screensize[0]/2, camera.focus[1] - state.screensize[1]/2)

def test_update_avoid_void(camera):
    state.gamemode = "play"
    state.objects = [MockFocusObject((0, 0), 1)]
    focus_obj = MockFocusObject((100, 100), 2)
    camera.focusobj = focus_obj
    camera.update()
    assert camera.pos[0] >= 0
    assert camera.pos[1] >= 0
