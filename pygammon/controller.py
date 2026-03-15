from PySide6.QtCore import QObject, QTimer, Signal

from pygammon.logic.game_engine import GameEngine, GamePhase


class GameController(QObject):
    """Qt signal bridge between GameEngine and UI."""

    board_updated = Signal()
    dice_rolled = Signal(int, int)  # die1, die2
    turn_changed = Signal(str, str)  # player_name, player_color
    valid_moves_changed = Signal(list)  # list of (from, to, die) tuples
    game_over = Signal(str)  # winner color
    no_moves_available = Signal()

    def __init__(self, engine: GameEngine, ai_player=None, ai_color=None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.selected_point = None
        self.ai_player = ai_player
        self.ai_color = ai_color

    def start_game(self):
        self.engine.start_game()
        player = self.engine.current_player
        self.turn_changed.emit(player.name, player.color)
        self.board_updated.emit()

    def _is_ai_turn(self) -> bool:
        return (
            self.ai_player is not None
            and self.ai_color is not None
            and self.engine.current_player.color == self.ai_color
        )

    def on_roll_clicked(self):
        if self.engine.phase != GamePhase.ROLLING:
            return

        die1, die2 = self.engine.roll_dice()
        self.dice_rolled.emit(die1, die2)

        if self.engine.phase == GamePhase.TURN_COMPLETE:
            self.no_moves_available.emit()
            self._finish_turn()
            return

        valid = self.engine.get_valid_moves()
        self.valid_moves_changed.emit(valid)
        self.board_updated.emit()

        # AI auto-move
        if self._is_ai_turn():
            self._ai_play_moves()

    def on_point_clicked(self, point_index: int):
        if self.engine.phase != GamePhase.MOVING:
            return

        if self.selected_point is None:
            # First click — select source
            valid = self.engine.get_valid_moves()
            valid_sources = set(m[0] for m in valid)
            if point_index in valid_sources:
                self.selected_point = point_index
                # Filter destinations for this source
                destinations = [m for m in valid if m[0] == point_index]
                self.valid_moves_changed.emit(destinations)
        else:
            # Second click — select destination
            valid = self.engine.get_valid_moves()
            matching = [
                m for m in valid
                if m[0] == self.selected_point and m[1] == point_index
            ]
            if matching:
                move = matching[0]
                self.engine.execute_move(move[0], move[1], move[2])
                self.selected_point = None
                self.board_updated.emit()

                if self.engine.phase == GamePhase.GAME_OVER:
                    self.game_over.emit(str(self.engine.winner))
                elif self.engine.phase == GamePhase.TURN_COMPLETE:
                    self._finish_turn()
                else:
                    # Still moving — show new valid moves
                    valid = self.engine.get_valid_moves()
                    self.valid_moves_changed.emit(valid)
            else:
                # Invalid destination — deselect
                self.selected_point = None
                valid = self.engine.get_valid_moves()
                self.valid_moves_changed.emit(valid)

    def _finish_turn(self):
        self.engine.end_turn()
        self.selected_point = None
        player = self.engine.current_player
        self.turn_changed.emit(player.name, player.color)
        self.valid_moves_changed.emit([])
        self.board_updated.emit()

        # If next turn is AI, auto-roll after a short delay
        if self._is_ai_turn():
            QTimer.singleShot(500, self.on_roll_clicked)

    def _ai_play_moves(self):
        """Let the AI play all moves for the current turn."""
        while self.engine.phase == GamePhase.MOVING:
            legal = self.engine.get_valid_moves()
            if not legal:
                break
            best = self.ai_player.choose_move(
                self.engine.board, self.engine.current_player, legal
            )
            if best is None:
                break
            self.engine.execute_move(*best)
            self.board_updated.emit()

        if self.engine.phase == GamePhase.GAME_OVER:
            self.game_over.emit(str(self.engine.winner))
        elif self.engine.phase == GamePhase.TURN_COMPLETE:
            self._finish_turn()
