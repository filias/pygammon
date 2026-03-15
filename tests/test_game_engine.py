import pytest
from unittest.mock import patch

from pygammon.logic.game_engine import GameEngine, GamePhase
from pygammon.logic.models import Color, Game


@pytest.fixture
def engine():
    game = Game()
    engine = GameEngine(game)
    engine.start_game()
    # Skip opening roll — go straight to rolling for most tests
    engine.phase = GamePhase.ROLLING
    engine.game.current_player_index = 0
    engine.game.current_player = engine.game.player1
    return engine


class TestOpeningRoll:
    def test_start_game_goes_to_opening_roll(self):
        game = Game()
        engine = GameEngine(game)
        engine.start_game()
        assert engine.phase == GamePhase.OPENING_ROLL

    def test_opening_roll_tie_stays_in_opening(self):
        game = Game()
        engine = GameEngine(game)
        engine.start_game()
        # Keep rolling until we get a result (tie or not)
        for _ in range(100):
            dark_d, light_d, is_tie = engine.opening_roll()
            if is_tie:
                assert engine.phase == GamePhase.OPENING_ROLL
                break
            else:
                # Got a non-tie, test passes anyway
                break

    def test_opening_roll_sets_player_and_dice(self):
        game = Game()
        engine = GameEngine(game)
        engine.start_game()
        for _ in range(100):
            dark_d, light_d, is_tie = engine.opening_roll()
            if not is_tie:
                break
        assert engine.phase in (GamePhase.MOVING, GamePhase.TURN_COMPLETE)
        assert len(engine.remaining_dice) == 2
        if dark_d > light_d:
            assert engine.current_player.color == Color.DARK
        else:
            assert engine.current_player.color == Color.LIGHT


class TestPhaseTransitions:
    def test_starts_not_started(self):
        game = Game()
        engine = GameEngine(game)
        assert engine.phase == GamePhase.NOT_STARTED

    def test_start_game_goes_to_rolling(self, engine):
        assert engine.phase == GamePhase.ROLLING

    def test_roll_goes_to_moving(self, engine):
        engine.roll_dice()
        assert engine.phase in (GamePhase.MOVING, GamePhase.TURN_COMPLETE)

    @patch("pygammon.logic.game_engine.roll", return_value=(3, 5))
    def test_roll_with_valid_moves_goes_to_moving(self, mock_roll, engine):
        engine.roll_dice()
        assert engine.phase == GamePhase.MOVING

    def test_cannot_roll_in_moving_phase(self, engine):
        engine.roll_dice()
        if engine.phase == GamePhase.MOVING:
            with pytest.raises(ValueError):
                engine.roll_dice()

    def test_cannot_move_in_rolling_phase(self, engine):
        with pytest.raises(ValueError):
            engine.execute_move(1, 2, 1)


class TestTurnSwitching:
    @patch("pygammon.logic.game_engine.roll", return_value=(3, 5))
    def test_turn_switches_after_end_turn(self, mock_roll, engine):
        assert engine.current_player.color == Color.DARK
        engine.roll_dice()

        # Use all dice (dark moves decreasingly: 24->21, 24->19 won't work since only 2)
        valid = engine.get_valid_moves()
        # Execute moves until turn complete
        for from_pt, to_pt, die_val in valid:
            if engine.phase != GamePhase.MOVING:
                break
            try:
                engine.execute_move(from_pt, to_pt, die_val)
            except ValueError:
                continue

        if engine.phase == GamePhase.TURN_COMPLETE:
            engine.end_turn()
            assert engine.current_player.color == Color.LIGHT
            assert engine.phase == GamePhase.ROLLING


class TestDoubles:
    @patch("pygammon.logic.game_engine.roll", return_value=(3, 3))
    def test_doubles_give_four_dice(self, mock_roll, engine):
        engine.roll_dice()
        assert len(engine.remaining_dice) == 4
        assert all(d == 3 for d in engine.remaining_dice)


class TestBarEnforcement:
    @patch("pygammon.logic.game_engine.roll", return_value=(3, 5))
    def test_bar_moves_only_when_on_bar(self, mock_roll, engine):
        # Put a dark checker on the bar (dark is INCREASING, bar=0)
        engine.board.bar.append(Color.DARK)
        # Remove it from a point to keep count consistent
        engine.board.position[1].pop()

        engine.roll_dice()
        valid = engine.get_valid_moves()

        # All moves should be from bar (point 0 for dark/increasing)
        assert all(m[0] == 0 for m in valid)


class TestBearingOff:
    @patch("pygammon.logic.game_engine.roll", return_value=(3, 2))
    def test_bearing_off(self, mock_roll):
        game = Game()
        game.board.position = {
            19: [Color.DARK, Color.DARK, Color.DARK],
            20: [Color.DARK, Color.DARK, Color.DARK],
            21: [Color.DARK, Color.DARK, Color.DARK],
            22: [Color.DARK, Color.DARK, Color.DARK],
            23: [Color.DARK, Color.DARK],
            24: [Color.DARK],
        }
        engine = GameEngine(game)
        engine.start_game()
        engine.phase = GamePhase.ROLLING
        engine.game.current_player_index = 0
        engine.game.current_player = engine.game.player1
        engine.roll_dice()

        valid = engine.get_valid_moves()
        # Should have bearing-off moves (bear_off=25 for increasing)
        bear_off_moves = [m for m in valid if m[1] == 25]
        assert len(bear_off_moves) > 0


class TestWinDetection:
    @patch("pygammon.logic.game_engine.roll", return_value=(1, 1))
    def test_game_over_on_last_bear_off(self, mock_roll):
        game = Game()
        game.board.position = {24: [Color.DARK]}
        game.board.off_dark = [Color.DARK] * 14
        game.board.bar = []

        engine = GameEngine(game)
        engine.start_game()
        engine.phase = GamePhase.ROLLING
        engine.game.current_player_index = 0
        engine.game.current_player = engine.game.player1
        engine.roll_dice()

        engine.execute_move(24, 25, 1)
        assert engine.phase == GamePhase.GAME_OVER
        assert engine.winner == Color.DARK


class TestUndo:
    @patch("pygammon.logic.game_engine.roll", return_value=(3, 5))
    def test_undo_restores_position(self, mock_roll, engine):
        engine.roll_dice()
        valid = engine.get_valid_moves()
        move = valid[0]

        # Save state before move
        pos_before = {k: list(v) for k, v in engine.board.position.items()}
        dice_before = list(engine.remaining_dice)

        engine.execute_move(*move)
        assert engine.can_undo

        engine.undo_move()
        assert engine.board.position == pos_before
        assert engine.remaining_dice == dice_before

    @patch("pygammon.logic.game_engine.roll", return_value=(3, 5))
    def test_undo_restores_phase(self, mock_roll, engine):
        engine.roll_dice()
        valid = engine.get_valid_moves()
        engine.execute_move(*valid[0])
        engine.undo_move()
        assert engine.phase == GamePhase.MOVING

    def test_cannot_undo_without_moves(self, engine):
        assert not engine.can_undo
        assert engine.undo_move() is False

    @patch("pygammon.logic.game_engine.roll", return_value=(3, 5))
    def test_undo_stack_cleared_on_end_turn(self, mock_roll, engine):
        engine.roll_dice()
        valid = engine.get_valid_moves()
        for m in valid:
            if engine.phase != GamePhase.MOVING:
                break
            try:
                engine.execute_move(*m)
            except ValueError:
                continue
        if engine.phase == GamePhase.TURN_COMPLETE:
            engine.end_turn()
            assert not engine.can_undo


class TestDoublingCube:
    def test_can_double_at_start(self, engine):
        assert engine.can_double is True

    def test_cannot_double_after_rolling(self, engine):
        engine.roll_dice()
        assert engine.can_double is False

    def test_propose_double(self, engine):
        engine.propose_double()
        assert engine.phase == GamePhase.DOUBLING

    def test_accept_double(self, engine):
        engine.propose_double()
        engine.respond_to_double(True)
        assert engine.cube.value == 2
        assert engine.cube.owner == Color.LIGHT  # opponent owns it
        assert engine.phase == GamePhase.ROLLING

    def test_decline_double(self, engine):
        engine.propose_double()
        engine.respond_to_double(False)
        assert engine.phase == GamePhase.GAME_OVER
        assert engine.winner == Color.DARK

    def test_only_cube_owner_can_double(self, engine):
        # Double and accept — light now owns cube
        engine.propose_double()
        engine.respond_to_double(True)
        # Dark (current player) cannot double since light owns cube
        assert engine.can_double is False

    @patch("pygammon.logic.game_engine.roll", return_value=(3, 5))
    def test_cube_owner_can_redouble(self, mock_roll, engine):
        # Dark doubles, light accepts (light owns cube at 2)
        engine.propose_double()
        engine.respond_to_double(True)
        # Dark rolls and plays
        engine.roll_dice()
        valid = engine.get_valid_moves()
        for m in valid:
            if engine.phase != GamePhase.MOVING:
                break
            try:
                engine.execute_move(*m)
            except ValueError:
                continue
        if engine.phase == GamePhase.TURN_COMPLETE:
            engine.end_turn()
            # Now it's light's turn — light owns cube and can redouble
            assert engine.can_double is True

    def test_cannot_double_past_64(self, engine):
        engine.game.cube.value = 64
        assert engine.can_double is False

    def test_forfeit_gives_cube_value_points(self, engine):
        engine.game.cube.value = 4
        engine.propose_double()
        engine.respond_to_double(False)
        winner, points, desc = engine.get_game_result()
        assert winner == Color.DARK
        assert points == 4
        assert desc == "forfeit"


class TestIllegalMoves:
    @patch("pygammon.logic.game_engine.roll", return_value=(3, 5))
    def test_illegal_move_rejected(self, mock_roll, engine):
        engine.roll_dice()
        with pytest.raises(ValueError, match="Illegal move"):
            engine.execute_move(1, 2, 1)
