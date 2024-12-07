import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock
import moves
import GameData as state

@pytest.fixture
def mock_caller():
    caller = MagicMock()
    caller.speed = [0, 0]
    caller.gravity = 9.8
    caller.maxspeed = 10
    caller.abilities = ["ability1", "ability2"]
    caller.weap = "ability1"
    caller.pallate = "default"
    caller.stun = False
    caller.children = []
    return caller

def test_stun(mock_caller):
    moves.stun(mock_caller, None)
    assert mock_caller.stun == True
    assert mock_caller.pallate == "Stun"

def test_dieDefault(mock_caller):
    child = MagicMock()
    mock_caller.children = [child]
    moves.dieDefault(mock_caller, None)
    child.delete.assert_called_once()
    mock_caller.delete.assert_called_once()


def test_weapDefault(mock_caller):
    moves.weapDefault(mock_caller, None)
    assert mock_caller.requestanim == True
    assert mock_caller.animname == "Moonwalk"

def test_destun(mock_caller):
    mock_caller.storepal = "default"
    moves.destun(mock_caller, None)
    assert mock_caller.stun == False
    assert mock_caller.pallate == "default"