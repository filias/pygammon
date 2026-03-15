from pygammon.engine.api import BackgammonAPI
from pygammon.logic.game_engine import GamePhase


class TestBackgammonAPI:
    def test_reset_returns_state(self):
        api = BackgammonAPI()
        state = api.reset()
        assert "position" in state
        assert "bar" in state
        assert "current_player" in state
        # After reset, opening roll is done so we're in moving or turn_complete
        assert state["phase"] in ("moving", "turn_complete")

    def test_reset_has_dice(self):
        api = BackgammonAPI()
        state = api.reset()
        assert len(state["remaining_dice"]) == 2

    def test_legal_actions_after_reset(self):
        api = BackgammonAPI()
        api.reset()
        if api.phase == GamePhase.MOVING:
            actions = api.get_legal_actions()
            assert len(actions) > 0

    def test_step_executes_move(self):
        api = BackgammonAPI()
        api.reset()
        if api.phase == GamePhase.MOVING:
            actions = api.get_legal_actions()
            result = api.step(*actions[0])
            assert "state" in result
            assert "done" in result
            assert isinstance(result["done"], bool)

    def test_end_turn_switches_player(self):
        api = BackgammonAPI()
        api.reset()
        first_player = api.current_player_color

        # Play all moves
        while api.phase == GamePhase.MOVING:
            actions = api.get_legal_actions()
            if not actions:
                break
            api.step(*actions[0])

        if api.phase == GamePhase.TURN_COMPLETE:
            api.end_turn()
            assert api.current_player_color != first_player

    def test_roll_after_end_turn(self):
        api = BackgammonAPI()
        api.reset()

        while api.phase == GamePhase.MOVING:
            actions = api.get_legal_actions()
            if not actions:
                break
            api.step(*actions[0])

        if api.phase == GamePhase.TURN_COMPLETE:
            api.end_turn()
            assert api.phase == GamePhase.ROLLING
            api.roll()
            assert api.phase in (GamePhase.MOVING, GamePhase.TURN_COMPLETE)
