from PySide6.QtCore import QObject, QTimer, Signal

from pygammon.logic.game_engine import GameEngine, GamePhase


class GameController(QObject):
    """Qt signal bridge between GameEngine and UI."""

    board_updated = Signal()
    dice_rolled = Signal(int, int)  # die1, die2
    turn_changed = Signal(str, str)  # player_name, player_color
    valid_moves_changed = Signal(list)  # list of (from, to, die) tuples
    game_over = Signal(str, int, str)  # winner_color, points, description
    no_moves_available = Signal()
    turn_complete = Signal()  # all dice used, waiting for confirm
    double_proposed = Signal(str)  # proposer name
    cube_updated = Signal(int, object)  # value, owner (Color or None)
    opening_rolled = Signal(int, int, bool)  # dark_die, light_die, is_tie

    def __init__(self, engine: GameEngine, ai_player=None, ai_color=None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.selected_point = None
        self.ai_player = ai_player
        self.ai_color = ai_color

    def start_game(self):
        self.engine.start_game()
        self.cube_updated.emit(self.engine.cube.value, self.engine.cube.owner)
        self.board_updated.emit()

    def on_opening_roll(self):
        if self.engine.phase != GamePhase.OPENING_ROLL:
            return
        dark_die, light_die, is_tie = self.engine.opening_roll()
        self.opening_rolled.emit(dark_die, light_die, is_tie)

        if not is_tie:
            player = self.engine.current_player
            self.turn_changed.emit(player.name, player.color)
            self.dice_rolled.emit(dark_die, light_die)
            self.board_updated.emit()

            if self._is_ai_turn():
                self._ai_play_moves()
            else:
                valid = self.engine.get_valid_moves()
                self.valid_moves_changed.emit(valid)

    def _is_ai_turn(self) -> bool:
        return (
            self.ai_player is not None
            and self.ai_color is not None
            and self.engine.current_player.color == self.ai_color
        )

    def _is_ai_opponent(self) -> bool:
        return (
            self.ai_player is not None
            and self.ai_color is not None
            and self.engine.opponent.color == self.ai_color
        )

    # --- Doubling ---

    def on_double_clicked(self):
        if not self.engine.can_double:
            return
        self.engine.propose_double()
        proposer = self.engine.current_player
        self.double_proposed.emit(proposer.name)

        # If AI is the opponent, let it respond after a delay
        if self._is_ai_opponent():
            QTimer.singleShot(800, self._ai_respond_to_double)

    def on_double_response(self, accepted: bool):
        if self.engine.phase != GamePhase.DOUBLING:
            return
        self.engine.respond_to_double(accepted)
        self.cube_updated.emit(self.engine.cube.value, self.engine.cube.owner)

        if self.engine.phase == GamePhase.GAME_OVER:
            winner, points, desc = self.engine.get_game_result()
            self.game_over.emit(str(winner), points, desc)
        # Accepted — back to ROLLING, update UI
        else:
            self.board_updated.emit()

    def _ai_respond_to_double(self):
        accepted = True
        if hasattr(self.ai_player, "should_accept_double"):
            accepted = self.ai_player.should_accept_double(
                self.engine.board, self.engine.opponent
            )
        self.on_double_response(accepted)

    # --- Rolling and moving ---

    def on_roll_clicked(self):
        if self.engine.phase != GamePhase.ROLLING:
            return

        die1, die2 = self.engine.roll_dice()
        self.dice_rolled.emit(die1, die2)

        if self.engine.phase == GamePhase.TURN_COMPLETE:
            self.no_moves_available.emit()
            self._finish_turn()
            return

        self.board_updated.emit()

        # AI auto-move
        if self._is_ai_turn():
            self._ai_play_moves()
            return

        valid = self.engine.get_valid_moves()
        self.valid_moves_changed.emit(valid)

    def on_point_clicked(self, point_index: int):
        if self.engine.phase != GamePhase.MOVING:
            return

        if self.selected_point is None:
            valid = self.engine.get_valid_moves()
            valid_sources = set(m[0] for m in valid)
            if point_index in valid_sources:
                self.selected_point = point_index
                destinations = [m for m in valid if m[0] == point_index]
                self.valid_moves_changed.emit(destinations)
        else:
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
                    winner, points, desc = self.engine.get_game_result()
                    self.game_over.emit(str(winner), points, desc)
                elif self.engine.phase == GamePhase.TURN_COMPLETE:
                    self.turn_complete.emit()
                else:
                    valid = self.engine.get_valid_moves()
                    self.valid_moves_changed.emit(valid)
            else:
                self.selected_point = None
                valid = self.engine.get_valid_moves()
                self.valid_moves_changed.emit(valid)

    def on_confirm_clicked(self):
        if self.engine.phase != GamePhase.TURN_COMPLETE:
            return
        self._finish_turn()

    def on_undo_clicked(self):
        if not self.engine.can_undo:
            return
        self.engine.undo_move()
        self.selected_point = None
        self.board_updated.emit()
        valid = self.engine.get_valid_moves()
        self.valid_moves_changed.emit(valid)

    def _finish_turn(self):
        self.engine.end_turn()
        self.selected_point = None
        player = self.engine.current_player
        self.turn_changed.emit(player.name, player.color)
        self.valid_moves_changed.emit([])
        self.board_updated.emit()

        if self._is_ai_turn():
            # AI might want to double before rolling
            QTimer.singleShot(500, self._ai_turn_start)

    def _ai_turn_start(self):
        """AI considers doubling, then rolls."""
        if self.engine.phase != GamePhase.ROLLING:
            return

        # Check if AI wants to double
        if self.engine.can_double and hasattr(self.ai_player, "should_double"):
            if self.ai_player.should_double(
                self.engine.board, self.engine.current_player
            ):
                self.engine.propose_double()
                self.double_proposed.emit(self.engine.current_player.name)
                # Human responds via dialog — don't auto-roll
                return

        self.on_roll_clicked()

    def _ai_play_moves(self):
        self._ai_play_next_move()

    def _ai_play_next_move(self):
        if self.engine.phase != GamePhase.MOVING:
            if self.engine.phase == GamePhase.GAME_OVER:
                winner, points, desc = self.engine.get_game_result()
                self.game_over.emit(str(winner), points, desc)
            elif self.engine.phase == GamePhase.TURN_COMPLETE:
                QTimer.singleShot(800, self._finish_turn)
            return

        legal = self.engine.get_valid_moves()
        if not legal:
            if self.engine.phase == GamePhase.TURN_COMPLETE:
                QTimer.singleShot(800, self._finish_turn)
            return

        best = self.ai_player.choose_move(
            self.engine.board, self.engine.current_player, legal
        )
        if best is None:
            return

        self.engine.execute_move(*best)
        self.board_updated.emit()

        QTimer.singleShot(600, self._ai_play_next_move)
