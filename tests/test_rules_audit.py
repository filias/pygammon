"""
Rules-audit tests.

These pin backgammon rules that aren't obviously covered elsewhere, or that
we explicitly want to lock in as the engine evolves. Tests marked `xfail` are
known rule-gaps documented for the team — if one starts passing, flip it to a
regular test.
"""

import pytest
from unittest.mock import patch

from pygammon.logic.game_engine import GameEngine, GamePhase
from pygammon.logic.models import Board, Color, Direction, Game, Player
from pygammon.logic.move import get_valid_moves
from pygammon.logic.position import get_win_type, has_winner


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture
def light_player():
    return Player(name="L", color=Color.LIGHT, direction=Direction.DECREASING)


@pytest.fixture
def dark_player():
    return Player(name="D", color=Color.DARK, direction=Direction.INCREASING)


@pytest.fixture
def engine():
    game = Game()
    game.current_player = game.player1  # DARK, INCREASING
    e = GameEngine(game)
    e.phase = GamePhase.ROLLING
    return e


def _only_dark_on(points_to_count):
    """Build a position dict with dark checkers on given points {point: count}."""
    return {p: [Color.DARK] * n for p, n in points_to_count.items()}


# --------------------------------------------------------------------------- #
# CRITICAL RULE GAP: "must play higher die when only one can be played"
# --------------------------------------------------------------------------- #


class TestMustPlayHigherDie:
    """
    Rule: If a player can play one die but not both, and a choice exists,
    they MUST play the higher die.
    """

    def test_must_play_higher_when_only_one_playable(self, dark_player):
        # Single dark checker on 15. Dice [6, 2].
        # die=6: 15→21 ok. die=2: 15→17 blocked. Only 6 playable → must use 6.
        # After 15→21 (6), no checkers left → can't use die=2. Only one die total.
        position = {
            15: [Color.DARK],
            17: [Color.LIGHT, Color.LIGHT],  # blocks die=2
        }
        moves = get_valid_moves(dark_player, position, [6, 2], bar=[])
        dies_used = {m[2] for m in moves}
        assert 2 not in dies_used, f"Low die offered despite higher playable: {moves}"
        assert 6 in dies_used

    def test_when_both_dice_blocked_no_moves(self, dark_player):
        # Single checker, both targets blocked.
        position = {
            10: [Color.DARK],
            13: [Color.LIGHT, Color.LIGHT],  # blocks die=3
            15: [Color.LIGHT, Color.LIGHT],  # blocks die=5
        }
        moves = get_valid_moves(dark_player, position, [3, 5], bar=[])
        assert moves == []

    def test_must_play_both_dice_when_possible(self, dark_player):
        # Two groups of checkers, both dice playable in sequence.
        position = {
            10: [Color.DARK] * 7,
            15: [Color.DARK] * 8,
        }
        moves = get_valid_moves(dark_player, position, [3, 5], bar=[])
        dies_used = {m[2] for m in moves}
        assert 3 in dies_used
        assert 5 in dies_used

    def test_only_higher_when_neither_sequence_uses_both(self, dark_player):
        # Single dark checker on 10. Dice [2, 5].
        # 10→12 (2) ok, then 12→17 (5) blocked → only 1 die.
        # 10→15 (5) ok, then 15→17 (2) blocked → only 1 die.
        # Neither sequence uses both → must play higher (5).
        position = {
            10: [Color.DARK],
            17: [Color.LIGHT, Color.LIGHT],  # blocks all follow-ups
        }
        moves = get_valid_moves(dark_player, position, [2, 5], bar=[])
        dies_used = {m[2] for m in moves}
        assert dies_used == {5}, f"Expected only higher die (5), got {moves}"

    def test_prefer_sequence_using_both_over_single_higher(self, dark_player):
        # Two groups of checkers, ample room. All first moves lead to both used.
        position = {
            5: [Color.DARK] * 8,
            10: [Color.DARK] * 7,
        }
        moves = get_valid_moves(dark_player, position, [3, 6], bar=[])
        dies_used = {m[2] for m in moves}
        assert 3 in dies_used
        assert 6 in dies_used

    def test_filter_first_move_that_blocks_second(self, dark_player):
        # Dark on 10 and 13 (only). Dice [3, 5].
        # All 4 first moves lead to using both → all offered.
        position = {10: [Color.DARK], 13: [Color.DARK]}
        moves = get_valid_moves(dark_player, position, [3, 5], bar=[])
        assert len(moves) == 4  # 2 checkers * 2 dice


# --------------------------------------------------------------------------- #
# Forfeit turn when no legal moves
# --------------------------------------------------------------------------- #


class TestForfeitTurn:
    def test_no_legal_moves_transitions_to_turn_complete(self, engine):
        # Dark is INCREASING → enters from bar (point 0) onto points 1..6.
        # Block all entry points with 2+ light checkers.
        engine.board.position = {p: [Color.LIGHT, Color.LIGHT] for p in range(1, 7)}
        engine.board.bar = [Color.DARK]
        with patch("pygammon.logic.game_engine.roll", return_value=(3, 5)):
            engine.roll_dice()
        assert engine.phase == GamePhase.TURN_COMPLETE
        assert engine.get_valid_moves() == []


# --------------------------------------------------------------------------- #
# Gammon / Backgammon scoring
# --------------------------------------------------------------------------- #


class TestWinTypeScoring:
    def test_single_when_loser_has_borne_off(self):
        board = Board(off_dark=[Color.DARK] * 15, off_light=[Color.LIGHT])
        assert has_winner(board) == Color.DARK
        assert get_win_type(board, loser=Color.LIGHT) == "single"

    def test_gammon_when_loser_has_no_checkers_off(self):
        board = Board(off_dark=[Color.DARK] * 15, off_light=[])
        # Clear light from dark's home (19..24) and bar — put them all on point 13.
        board.position = {13: [Color.LIGHT] * 15}
        board.bar = []
        assert get_win_type(board, loser=Color.LIGHT) == "gammon"

    def test_backgammon_when_loser_on_bar(self):
        board = Board(off_dark=[Color.DARK] * 15, off_light=[])
        board.bar = [Color.LIGHT]
        assert get_win_type(board, loser=Color.LIGHT) == "backgammon"

    def test_backgammon_when_loser_in_winners_home(self):
        # Dark wins; light has a checker in dark's home (19..24)
        board = Board(off_dark=[Color.DARK] * 15, off_light=[])
        # Light's starting position already has LIGHT on point 19? Let's check:
        # Default board has LIGHT on 6, 8 (light), 13 (dark), 17 (dark), 19 (dark), 24 (light)
        # so point 24 has LIGHT → that's in dark's home (19..24). Backgammon.
        assert get_win_type(board, loser=Color.LIGHT) == "backgammon"

    def test_game_result_multipliers(self):
        game = Game()
        game.board = Board(off_dark=[Color.DARK] * 15, off_light=[Color.LIGHT])
        game.cube.value = 2
        engine = GameEngine(game)
        winner, points, desc = engine.get_game_result()
        assert winner == Color.DARK
        assert desc == "single"
        assert points == 2  # 2 (cube) * 1 (single)

    def test_gammon_doubles_cube(self):
        # Clear board so loser has no off checkers and no backgammon condition
        game = Game()
        game.board = Board(off_dark=[Color.DARK] * 15, off_light=[])
        # Remove all light checkers from points in dark's home and bar
        game.board.position = {13: [Color.LIGHT] * 15}
        game.board.bar = []
        game.cube.value = 4
        engine = GameEngine(game)
        winner, points, desc = engine.get_game_result()
        assert desc == "gammon"
        assert points == 8  # 4 * 2


# --------------------------------------------------------------------------- #
# Bear-off: intermediate die must move within home if possible
# --------------------------------------------------------------------------- #


class TestBearOffIntermediate:
    def test_die_smaller_than_exact_must_move_within_home(self, dark_player):
        # Dark home is 19..24 (INCREASING). All 15 dark in home.
        # Checker on 20, die=3 → target 23 (in-home move, not bear-off).
        position = {p: [] for p in range(1, 25)}
        position[20] = [Color.DARK] * 15
        moves = get_valid_moves(dark_player, position, [3], bar=[])
        # Should offer the in-home move (20→23), not a bear-off.
        assert (20, 23, 3) in moves
        # No bear-off offered because target is inside the board
        assert all(m[1] != dark_player.bear_off for m in moves)


# --------------------------------------------------------------------------- #
# Cube: caps and ownership after accept
# --------------------------------------------------------------------------- #


class TestCubeRules:
    def test_cube_cap_respected(self, engine):
        engine.game.cube.value = 64
        assert engine.can_double is False

    def test_accept_transfers_ownership_to_receiver(self, engine):
        # Dark proposes, light accepts → light owns the cube afterwards.
        engine.propose_double()
        engine.respond_to_double(accepted=True)
        assert engine.game.cube.owner == Color.LIGHT
        assert engine.game.cube.value == 2
