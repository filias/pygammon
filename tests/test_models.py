import pytest
from pydantic import ValidationError
from pygammon.logic.models import (
    Color,
    Die,
    Player,
    CheckerMove,
    BackgammonMove,
    Board,
    BAR,
    BEAR_OFF,
)


class TestDie:
    def test_die_valid_values(self):
        for value in range(1, 7):
            die = Die(value=value)
            assert die.value == value

    def test_die_invalid_value_zero(self):
        with pytest.raises(ValidationError):
            Die(value=0)

    def test_die_invalid_value_seven(self):
        with pytest.raises(ValidationError):
            Die(value=7)

    def test_die_roll_returns_valid_value(self):
        die = Die(value=1)
        for _ in range(100):
            result = die.roll()
            assert 1 <= result <= 6
            assert die.value == result


class TestPlayer:
    def test_player_creation(self):
        player = Player(name="Alice", color=Color.LIGHT)
        assert player.name == "Alice"
        assert player.color == Color.LIGHT

    def test_player_dark(self):
        player = Player(name="Bob", color=Color.DARK)
        assert player.color == Color.DARK


class TestCheckerMove:
    def test_checker_move_normal(self):
        move = CheckerMove(from_point=1, to_point=4, die_value=3)
        assert move.from_point == 1
        assert move.to_point == 4
        assert move.die_value == 3

    def test_checker_move_from_bar(self):
        move = CheckerMove(from_point=BAR, to_point=3, die_value=3)
        assert move.from_point == 0
        assert move.to_point == 3

    def test_checker_move_bear_off(self):
        move = CheckerMove(from_point=22, to_point=BEAR_OFF, die_value=3)
        assert move.from_point == 22
        assert move.to_point == 25

    def test_checker_move_invalid_die_value(self):
        with pytest.raises(ValidationError):
            CheckerMove(from_point=1, to_point=8, die_value=7)

    def test_checker_move_invalid_point(self):
        with pytest.raises(ValidationError):
            CheckerMove(from_point=26, to_point=1, die_value=1)


class TestBackgammonMove:
    def test_backgammon_move_single_checker(self):
        checker_move = CheckerMove(from_point=1, to_point=4, die_value=3)
        move = BackgammonMove(checker_moves=[checker_move], dice=(3, 5))
        assert len(move.checker_moves) == 1
        assert move.dice == (3, 5)

    def test_backgammon_move_two_checkers(self):
        moves = [
            CheckerMove(from_point=1, to_point=4, die_value=3),
            CheckerMove(from_point=12, to_point=17, die_value=5),
        ]
        move = BackgammonMove(checker_moves=moves, dice=(3, 5))
        assert len(move.checker_moves) == 2

    def test_backgammon_move_doubles(self):
        moves = [
            CheckerMove(from_point=1, to_point=4, die_value=3),
            CheckerMove(from_point=4, to_point=7, die_value=3),
            CheckerMove(from_point=7, to_point=10, die_value=3),
            CheckerMove(from_point=10, to_point=13, die_value=3),
        ]
        move = BackgammonMove(checker_moves=moves, dice=(3, 3))
        assert len(move.checker_moves) == 4


class TestBoard:
    def test_board_initial_position(self):
        board = Board()
        assert len(board.bar) == 0
        assert len(board.off_dark) == 0
        assert len(board.off_light) == 0

    def test_board_initial_position_has_correct_checkers(self):
        board = Board()
        # Check some key positions
        assert len(board.position[1]) == 2
        assert board.position[1][0] == Color.DARK
        assert len(board.position[24]) == 2
        assert board.position[24][0] == Color.LIGHT


class TestConstants:
    def test_bar_constant(self):
        assert BAR == 0

    def test_bear_off_constant(self):
        assert BEAR_OFF == 25
