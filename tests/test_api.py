from unittest.mock import patch

from pygammon.engine.api import BackgammonAPI
from pygammon.logic.game_engine import GamePhase


class TestBackgammonAPI:
    def test_reset_returns_state(self):
        api = BackgammonAPI()
        state = api.reset()
        assert "position" in state
        assert "bar" in state
        assert "current_player" in state
        assert state["phase"] == "rolling"

    def test_roll_transitions_to_moving(self):
        api = BackgammonAPI()
        api.reset()
        api.roll()
        assert api.phase in (GamePhase.MOVING, GamePhase.TURN_COMPLETE)

    @patch("pygammon.logic.game_engine.roll", return_value=(3, 5))
    def test_legal_actions_after_roll(self, mock_roll):
        api = BackgammonAPI()
        api.reset()
        api.roll()
        actions = api.get_legal_actions()
        assert len(actions) > 0

    @patch("pygammon.logic.game_engine.roll", return_value=(3, 5))
    def test_step_executes_move(self, mock_roll):
        api = BackgammonAPI()
        api.reset()
        api.roll()
        actions = api.get_legal_actions()
        result = api.step(*actions[0])
        assert "state" in result
        assert "done" in result
        assert isinstance(result["done"], bool)

    @patch("pygammon.logic.game_engine.roll", return_value=(3, 5))
    def test_end_turn_switches_player(self, mock_roll):
        api = BackgammonAPI()
        api.reset()
        first_player = api.current_player_color
        api.roll()

        # Play all moves
        while api.phase == GamePhase.MOVING:
            actions = api.get_legal_actions()
            if not actions:
                break
            api.step(*actions[0])

        if api.phase == GamePhase.TURN_COMPLETE:
            api.end_turn()
            assert api.current_player_color != first_player

    def test_no_legal_actions_before_roll(self):
        api = BackgammonAPI()
        api.reset()
        assert api.get_legal_actions() == []
