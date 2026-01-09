import copy
import pytest
from pygammon.logic.models import Player, Color
from pygammon.logic.position import initial_position
from pygammon.logic.move import move_checker


def test_normal_move_to_empty_point():
    light = Player(name="L", color=Color.LIGHT)
    pos = copy.deepcopy(initial_position)

    opponent, borne_off = move_checker(1, 4, light, pos)

    assert opponent is None
    assert borne_off is False
    assert Color.LIGHT in pos.get(4, [])


def test_hit_single_opponent():
    dark = Player(name="D", color=Color.DARK)
    pos = copy.deepcopy(initial_position)
    pos[10] = [Color.LIGHT]  # single opponent to hit
    pos[12] = [Color.DARK]   # dark checker to move

    opponent, borne_off = move_checker(12, 10, dark, pos)

    assert opponent == Color.LIGHT
    assert borne_off is False
    assert pos[10] == [Color.DARK]


def test_bear_off():
    light = Player(name="L", color=Color.LIGHT)
    pos = {23: [Color.LIGHT]}

    opponent, borne_off = move_checker(23, 25, light, pos)

    assert opponent is None
    assert borne_off is True
    assert pos.get(23) == []


def test_move_nonexistent_checker_raises():
    light = Player(name="L", color=Color.LIGHT)
    pos = {}

    with pytest.raises(ValueError):
        move_checker(1, 4, light, pos)


def test_move_wrong_color_checker_raises():
    light = Player(name="L", color=Color.LIGHT)
    pos = {1: [Color.DARK]}

    with pytest.raises(ValueError):
        move_checker(1, 4, light, pos)


def test_move_to_same_color_stacks():
    light = Player(name="L", color=Color.LIGHT)
    pos = {1: [Color.LIGHT], 4: [Color.LIGHT]}

    opponent, borne_off = move_checker(1, 4, light, pos)

    assert opponent is None
    assert borne_off is False
    assert pos[4] == [Color.LIGHT, Color.LIGHT]
