"""Gym-style headless API for backgammon, reusing GameEngine."""

from typing import List, Optional, Tuple

from pygammon.logic.game_engine import GameEngine, GamePhase
from pygammon.logic.models import Color, Game


class BackgammonAPI:
    """Headless backgammon environment for AI training."""

    def __init__(self):
        self.engine: Optional[GameEngine] = None

    def reset(self) -> dict:
        """Start a new game and return initial state."""
        game = Game()
        self.engine = GameEngine(game)
        self.engine.start_game()
        # Do opening roll (re-roll on ties)
        while self.engine.phase == GamePhase.OPENING_ROLL:
            self.engine.opening_roll()
        return self.get_state()

    def get_state(self) -> dict:
        """Return current game state as a dict."""
        board = self.engine.board
        return {
            "position": {k: list(v) for k, v in board.position.items()},
            "bar": list(board.bar),
            "off_dark": len(board.off_dark),
            "off_light": len(board.off_light),
            "current_player": str(self.engine.current_player.color),
            "phase": str(self.engine.phase),
            "remaining_dice": list(self.engine.remaining_dice),
            "dice": self.engine.game.dice,
        }

    def get_legal_actions(self) -> List[Tuple[int, int, int]]:
        """Return legal moves as (from_point, to_point, die_value) tuples."""
        if self.engine.phase != GamePhase.MOVING:
            return []
        return self.engine.get_valid_moves()

    def roll(self) -> Tuple[int, int]:
        """Roll dice. Returns the dice values."""
        return self.engine.roll_dice()

    def step(self, from_point: int, to_point: int, die_value: int) -> dict:
        """
        Execute a move and return result dict.

        Returns:
            {
                "state": current state dict,
                "done": bool (game over),
                "winner": Color or None,
                "turn_complete": bool (all dice used or no more moves),
            }
        """
        self.engine.execute_move(from_point, to_point, die_value)

        done = self.engine.phase == GamePhase.GAME_OVER
        turn_complete = self.engine.phase == GamePhase.TURN_COMPLETE

        return {
            "state": self.get_state(),
            "done": done,
            "winner": self.engine.winner,
            "turn_complete": turn_complete,
        }

    def end_turn(self):
        """End the current turn and switch players."""
        self.engine.end_turn()

    @property
    def phase(self) -> GamePhase:
        return self.engine.phase

    @property
    def current_player_color(self) -> Color:
        return self.engine.current_player.color
