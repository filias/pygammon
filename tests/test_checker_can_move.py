import copy
from pygammon.logic.models import Player, Color
from pygammon.logic.position import initial_position
from pygammon.logic.move import checker_can_move


def test_light_can_move_to_empty_point():
    light = Player(name="L", color=Color.LIGHT)
    pos = copy.deepcopy(initial_position)
    can_move, target = checker_can_move(1, 3, light, pos)
    assert can_move is True
    assert target == 4


def test_dark_can_move_to_empty_point():
    dark = Player(name="D", color=Color.DARK)
    pos = copy.deepcopy(initial_position)
    can_move, target = checker_can_move(24, 2, dark, pos)
    assert can_move is True
    assert target == 22


def test_can_hit_single_opponent():
    dark = Player(name="D", color=Color.DARK)
    pos = copy.deepcopy(initial_position)
    pos[10] = [Color.LIGHT]  # single opponent to hit
    can_move, target = checker_can_move(12, 2, dark, pos)
    assert can_move is True
    assert target == 10


def test_blocked_by_two_opponents():
    dark = Player(name="D", color=Color.DARK)
    pos = copy.deepcopy(initial_position)
    pos[10] = [Color.LIGHT, Color.LIGHT]  # two opponents block
    can_move, target = checker_can_move(12, 2, dark, pos)
    assert can_move is False
    assert target is None


def test_can_move_to_same_color():
    light = Player(name="L", color=Color.LIGHT)
    pos = copy.deepcopy(initial_position)
    # Light has checkers at point 12 in initial position
    can_move, target = checker_can_move(1, 11, light, pos)
    assert can_move is True
    assert target == 12


def test_bear_off_allowed_when_past_board():
    light = Player(name="L", color=Color.LIGHT)
    pos = {23: [Color.LIGHT]}
    can_move, target = checker_can_move(23, 3, light, pos)
    assert can_move is True
    assert target == 26  # past board edge
