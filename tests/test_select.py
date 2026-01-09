from pygammon.logic.models import Player, Color
from pygammon.logic.position import initial_position
from pygammon.logic.move import select_checker_to_play


def test_select_checker_light_picks_point_1():
    light = Player(name="L", color=Color.LIGHT)
    assert select_checker_to_play(light, initial_position) == 1


def test_select_checker_dark_picks_point_24():
    dark = Player(name="D", color=Color.DARK)
    assert select_checker_to_play(dark, initial_position) == 24


def test_select_checker_returns_none_when_no_checkers():
    light = Player(name="L", color=Color.LIGHT)
    empty_position = {}
    assert select_checker_to_play(light, empty_position) is None
