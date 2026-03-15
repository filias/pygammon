import pytest

from pygammon.logic.models import Color, Direction, Player
from pygammon.logic.move import all_checkers_in_home, get_valid_moves


@pytest.fixture
def light_player():
    return Player(name="Light", color=Color.LIGHT, direction=Direction.INCREASING)


@pytest.fixture
def dark_player():
    return Player(name="Dark", color=Color.DARK, direction=Direction.DECREASING)


class TestAllCheckersInHome:
    def test_initial_position_not_in_home(self, light_player):
        from pygammon.logic.models import Board

        board = Board()
        assert all_checkers_in_home(light_player, board.position, board.bar) is False

    def test_all_in_home(self, light_player):
        position = {
            19: [Color.LIGHT, Color.LIGHT, Color.LIGHT],
            20: [Color.LIGHT, Color.LIGHT, Color.LIGHT],
            21: [Color.LIGHT, Color.LIGHT, Color.LIGHT],
            22: [Color.LIGHT, Color.LIGHT, Color.LIGHT],
            23: [Color.LIGHT, Color.LIGHT],
            24: [Color.LIGHT],
        }
        assert all_checkers_in_home(light_player, position, []) is True

    def test_checker_on_bar_not_in_home(self, light_player):
        position = {19: [Color.LIGHT] * 14}
        assert all_checkers_in_home(light_player, position, [Color.LIGHT]) is False

    def test_dark_all_in_home(self, dark_player):
        position = {
            1: [Color.DARK, Color.DARK, Color.DARK],
            2: [Color.DARK, Color.DARK, Color.DARK],
            3: [Color.DARK, Color.DARK, Color.DARK],
            4: [Color.DARK, Color.DARK, Color.DARK],
            5: [Color.DARK, Color.DARK],
            6: [Color.DARK],
        }
        assert all_checkers_in_home(dark_player, position, []) is True


class TestGetValidMoves:
    def test_empty_dice_no_moves(self, light_player):
        position = {1: [Color.LIGHT]}
        moves = get_valid_moves(light_player, position, [], [])
        assert moves == []

    def test_simple_move(self, light_player):
        position = {1: [Color.LIGHT]}
        moves = get_valid_moves(light_player, position, [3], [])
        assert (1, 4, 3) in moves

    def test_blocked_destination(self, light_player):
        position = {
            1: [Color.LIGHT],
            4: [Color.DARK, Color.DARK],
        }
        moves = get_valid_moves(light_player, position, [3], [])
        assert (1, 4, 3) not in moves

    def test_can_hit_single_opponent(self, light_player):
        position = {
            1: [Color.LIGHT],
            4: [Color.DARK],
        }
        moves = get_valid_moves(light_player, position, [3], [])
        assert (1, 4, 3) in moves

    def test_bar_entry_required(self, light_player):
        position = {10: [Color.LIGHT]}
        bar = [Color.LIGHT]
        moves = get_valid_moves(light_player, position, [3], bar)
        # Must enter from bar (point 0), can't move point 10
        assert all(m[0] == 0 for m in moves)

    def test_bar_entry_blocked(self, light_player):
        position = {
            3: [Color.DARK, Color.DARK],
            10: [Color.LIGHT],
        }
        bar = [Color.LIGHT]
        moves = get_valid_moves(light_player, position, [3], bar)
        assert moves == []

    def test_bearing_off_exact(self, dark_player):
        position = {3: [Color.DARK]}
        moves = get_valid_moves(dark_player, position, [3], [])
        # Can bear off: point 3 - die 3 = 0 (bear off for decreasing)
        assert (3, 0, 3) in moves

    def test_bearing_off_overshoot_highest_checker(self, dark_player):
        position = {2: [Color.DARK]}
        moves = get_valid_moves(dark_player, position, [5], [])
        # Can bear off with overshoot since no checker is farther
        assert (2, 0, 5) in moves

    def test_bearing_off_overshoot_blocked_by_farther_checker(self, dark_player):
        position = {
            2: [Color.DARK],
            5: [Color.DARK],
        }
        moves = get_valid_moves(dark_player, position, [3], [])
        # Point 2 can't overshoot bear off (die 3 -> target -1) because point 5 has checker farther away
        # But point 5 can move to point 2 normally
        assert (5, 2, 3) in moves
        assert (2, 0, 3) not in moves

    def test_no_bearing_off_when_not_all_home(self, dark_player):
        position = {
            3: [Color.DARK],
            10: [Color.DARK],  # Outside home
        }
        moves = get_valid_moves(dark_player, position, [3], [])
        # Point 3 can't bear off (checker outside home), but can move to point 10
        assert (3, 0, 3) not in moves
        assert (10, 7, 3) in moves

    def test_multiple_dice_values(self, light_player):
        position = {1: [Color.LIGHT]}
        moves = get_valid_moves(light_player, position, [3, 5], [])
        assert (1, 4, 3) in moves
        assert (1, 6, 5) in moves

    def test_dark_simple_move(self, dark_player):
        position = {24: [Color.DARK]}
        moves = get_valid_moves(dark_player, position, [4], [])
        assert (24, 20, 4) in moves
