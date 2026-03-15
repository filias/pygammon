from enum import StrEnum
from typing import List, Optional, Tuple

from pygammon.logic.dice import roll
from pygammon.logic.models import Board, Color, Game, Player
from pygammon.logic.move import get_valid_moves, move_checker
from pygammon.logic.position import has_winner


class GamePhase(StrEnum):
    NOT_STARTED = "not_started"
    ROLLING = "rolling"
    MOVING = "moving"
    TURN_COMPLETE = "turn_complete"
    GAME_OVER = "game_over"


class _Snapshot:
    """Snapshot of board state before a move, for undo."""

    def __init__(self, position, bar, off_dark, off_light, remaining_dice, phase):
        self.position = position
        self.bar = bar
        self.off_dark = off_dark
        self.off_light = off_light
        self.remaining_dice = remaining_dice
        self.phase = phase


class GameEngine:
    """State machine that orchestrates a backgammon game."""

    def __init__(self, game: Game):
        self.game = game
        self.phase = GamePhase.NOT_STARTED
        self.remaining_dice: List[int] = []
        self.move_count = 0
        self._undo_stack: List[_Snapshot] = []

    @property
    def current_player(self) -> Player:
        if self.game.current_player_index == 0:
            return self.game.player1
        return self.game.player2

    @property
    def board(self) -> Board:
        return self.game.board

    def start_game(self):
        """Start the game — first player begins rolling."""
        self.game.current_player_index = 0
        self.game.current_player = self.game.player1
        self.phase = GamePhase.ROLLING

    def roll_dice(self) -> Tuple[int, int]:
        """Roll dice and transition to MOVING phase."""
        if self.phase != GamePhase.ROLLING:
            raise ValueError(f"Cannot roll in phase {self.phase}")

        dice = roll()
        self.game.dice = dice

        # Doubles give 4 moves
        if dice[0] == dice[1]:
            self.remaining_dice = [dice[0]] * 4
        else:
            self.remaining_dice = list(dice)

        # Check if player has any valid moves
        valid = self.get_valid_moves()
        if valid:
            self.phase = GamePhase.MOVING
        else:
            # No valid moves — skip to turn complete
            self.phase = GamePhase.TURN_COMPLETE

        return dice

    def get_valid_moves(self) -> List[Tuple[int, int, int]]:
        """Get all valid moves for current state."""
        return get_valid_moves(
            self.current_player,
            self.board.position,
            self.remaining_dice,
            self.board.bar,
        )

    def execute_move(self, from_point: int, to_point: int, die_value: int):
        """Execute a single checker move."""
        if self.phase != GamePhase.MOVING:
            raise ValueError(f"Cannot move in phase {self.phase}")

        # Validate the move is legal
        valid_moves = self.get_valid_moves()
        if (from_point, to_point, die_value) not in valid_moves:
            raise ValueError(
                f"Illegal move: ({from_point}, {to_point}, {die_value})"
            )

        # Save snapshot for undo
        self._undo_stack.append(_Snapshot(
            position={k: list(v) for k, v in self.board.position.items()},
            bar=list(self.board.bar),
            off_dark=list(self.board.off_dark),
            off_light=list(self.board.off_light),
            remaining_dice=list(self.remaining_dice),
            phase=self.phase,
        ))

        player = self.current_player

        # Handle bar entry: remove checker from bar
        if from_point == player.bar:
            self.board.bar.remove(player.color)
            # Temporarily add to position for move_checker
            self.board.position.setdefault(from_point, []).insert(0, player.color)

        opponent_color, borne_off = move_checker(
            from_point, to_point, player, self.board.position
        )

        # Handle hit — send opponent to bar
        if opponent_color:
            self.board.bar.append(opponent_color)

        # Handle bearing off
        if borne_off:
            if player.color == Color.DARK:
                self.board.off_dark.append(player.color)
            else:
                self.board.off_light.append(player.color)

        # Consume the die
        self.remaining_dice.remove(die_value)
        self.move_count += 1

        # Check for winner
        winner = has_winner(self.board)
        if winner:
            self.phase = GamePhase.GAME_OVER
            return

        # Check if more moves available
        if not self.remaining_dice or not self.get_valid_moves():
            self.phase = GamePhase.TURN_COMPLETE
        # Otherwise stay in MOVING phase

    def undo_move(self) -> bool:
        """Undo the last move. Returns True if successful."""
        if not self._undo_stack:
            return False
        snapshot = self._undo_stack.pop()
        self.board.position = snapshot.position
        self.board.bar = snapshot.bar
        self.board.off_dark = snapshot.off_dark
        self.board.off_light = snapshot.off_light
        self.remaining_dice = snapshot.remaining_dice
        self.phase = snapshot.phase
        self.move_count -= 1
        return True

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def end_turn(self):
        """Switch to the other player and start their rolling phase."""
        if self.phase != GamePhase.TURN_COMPLETE:
            raise ValueError(f"Cannot end turn in phase {self.phase}")

        # Switch player
        self.game.current_player_index = 1 - self.game.current_player_index
        self.game.current_player = self.current_player
        self.remaining_dice = []
        self._undo_stack.clear()
        self.phase = GamePhase.ROLLING

    @property
    def winner(self) -> Optional[Color]:
        return has_winner(self.board)
