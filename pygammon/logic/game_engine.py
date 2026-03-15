from enum import StrEnum
from typing import List, Optional, Tuple

from pygammon.logic.dice import roll
from pygammon.logic.models import Board, Color, Game, Player
from pygammon.logic.move import get_valid_moves, move_checker
from pygammon.logic.position import WinType, get_win_type, has_winner


class GamePhase(StrEnum):
    NOT_STARTED = "not_started"
    ROLLING = "rolling"
    DOUBLING = "doubling"
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
        self.forfeit_color: Optional[Color] = None

    @property
    def current_player(self) -> Player:
        if self.game.current_player_index == 0:
            return self.game.player1
        return self.game.player2

    @property
    def opponent(self) -> Player:
        if self.game.current_player_index == 0:
            return self.game.player2
        return self.game.player1

    @property
    def board(self) -> Board:
        return self.game.board

    @property
    def cube(self):
        return self.game.cube

    def start_game(self):
        """Start the game — first player begins rolling."""
        self.game.current_player_index = 0
        self.game.current_player = self.game.player1
        self.phase = GamePhase.ROLLING

    # --- Doubling cube ---

    @property
    def can_double(self) -> bool:
        """Can the current player propose a double?"""
        if self.phase != GamePhase.ROLLING:
            return False
        if self.cube.value >= 64:
            return False
        # Centered cube: either player can double
        # Owned cube: only the owner can double
        return self.cube.owner is None or self.cube.owner == self.current_player.color

    def propose_double(self):
        """Current player proposes to double the stakes."""
        if not self.can_double:
            raise ValueError("Cannot double right now")
        self.phase = GamePhase.DOUBLING

    def respond_to_double(self, accepted: bool):
        """Opponent responds to a double proposal."""
        if self.phase != GamePhase.DOUBLING:
            raise ValueError(f"Cannot respond to double in phase {self.phase}")

        if accepted:
            self.cube.value *= 2
            # The player who was doubled now owns the cube
            self.cube.owner = self.opponent.color
            # Back to rolling — same player still needs to roll
            self.phase = GamePhase.ROLLING
        else:
            # Opponent declines — they forfeit at current stakes
            self.forfeit_color = self.opponent.color
            self.phase = GamePhase.GAME_OVER

    def get_game_result(self) -> Tuple[Color, int, str]:
        """Returns (winner, points, description)."""
        if self.forfeit_color:
            winner = Color.DARK if self.forfeit_color == Color.LIGHT else Color.LIGHT
            points = self.cube.value
            return winner, points, "forfeit"

        winner = has_winner(self.board)
        if winner is None:
            return None, 0, ""

        loser = Color.LIGHT if winner == Color.DARK else Color.DARK
        win_type = get_win_type(self.board, loser)
        multiplier = {"single": 1, "gammon": 2, "backgammon": 3}[win_type]
        points = self.cube.value * multiplier
        return winner, points, win_type

    # --- Dice and movement ---

    def roll_dice(self) -> Tuple[int, int]:
        """Roll dice and transition to MOVING phase."""
        if self.phase != GamePhase.ROLLING:
            raise ValueError(f"Cannot roll in phase {self.phase}")

        dice = roll()
        self.game.dice = dice

        if dice[0] == dice[1]:
            self.remaining_dice = [dice[0]] * 4
        else:
            self.remaining_dice = list(dice)

        valid = self.get_valid_moves()
        if valid:
            self.phase = GamePhase.MOVING
        else:
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

        valid_moves = self.get_valid_moves()
        if (from_point, to_point, die_value) not in valid_moves:
            raise ValueError(
                f"Illegal move: ({from_point}, {to_point}, {die_value})"
            )

        self._undo_stack.append(_Snapshot(
            position={k: list(v) for k, v in self.board.position.items()},
            bar=list(self.board.bar),
            off_dark=list(self.board.off_dark),
            off_light=list(self.board.off_light),
            remaining_dice=list(self.remaining_dice),
            phase=self.phase,
        ))

        player = self.current_player

        if from_point == player.bar:
            self.board.bar.remove(player.color)
            self.board.position.setdefault(from_point, []).insert(0, player.color)

        opponent_color, borne_off = move_checker(
            from_point, to_point, player, self.board.position
        )

        if opponent_color:
            self.board.bar.append(opponent_color)

        if borne_off:
            if player.color == Color.DARK:
                self.board.off_dark.append(player.color)
            else:
                self.board.off_light.append(player.color)

        self.remaining_dice.remove(die_value)
        self.move_count += 1

        winner = has_winner(self.board)
        if winner:
            self.phase = GamePhase.GAME_OVER
            return

        if not self.remaining_dice or not self.get_valid_moves():
            self.phase = GamePhase.TURN_COMPLETE

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

        self.game.current_player_index = 1 - self.game.current_player_index
        self.game.current_player = self.current_player
        self.remaining_dice = []
        self._undo_stack.clear()
        self.phase = GamePhase.ROLLING

    @property
    def winner(self) -> Optional[Color]:
        if self.forfeit_color:
            return Color.DARK if self.forfeit_color == Color.LIGHT else Color.LIGHT
        return has_winner(self.board)
