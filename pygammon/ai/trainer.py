"""TD(lambda) self-play trainer for backgammon."""

import numpy as np
import tensorflow as tf

from pygammon.ai.model import TDGammonModel
from pygammon.engine.api import BackgammonAPI
from pygammon.engine.encoding import encode_board
from pygammon.logic.game_engine import GamePhase
from pygammon.logic.models import Color


class TDTrainer:
    """Self-play TD(lambda) trainer using eligibility traces."""

    def __init__(
        self,
        model: TDGammonModel,
        learning_rate: float = 0.1,
        lamda: float = 0.7,
    ):
        self.model = model
        self.lr = learning_rate
        self.lamda = lamda
        self.api = BackgammonAPI()

    def train_episode(self) -> dict:
        """Play one self-play game and train the model. Returns stats."""
        self.api.reset()

        # Build model if needed (first call)
        dummy = np.zeros((1, 198), dtype=np.float32)
        self.model(dummy)

        # Initialize eligibility traces
        traces = [tf.zeros_like(w) for w in self.model.trainable_variables]

        move_count = 0
        prev_value = None

        while self.api.phase != GamePhase.GAME_OVER:
            # Roll phase
            if self.api.phase == GamePhase.ROLLING:
                self.api.roll()

            # No moves available
            if self.api.phase == GamePhase.TURN_COMPLETE:
                self.api.end_turn()
                continue

            # Moving phase — pick greedy move
            if self.api.phase == GamePhase.MOVING:
                actions = self.api.get_legal_actions()
                if not actions:
                    if self.api.phase == GamePhase.TURN_COMPLETE:
                        self.api.end_turn()
                    continue

                # Evaluate current state
                board = self.api.engine.board
                current_color = self.api.current_player_color
                encoded = encode_board(board, current_color)
                x = tf.constant(encoded.reshape(1, -1))

                with tf.GradientTape() as tape:
                    current_value = self.model(x)

                gradients = tape.gradient(
                    current_value, self.model.trainable_variables
                )

                # Update traces
                traces = [
                    self.lamda * trace + grad
                    for trace, grad in zip(traces, gradients)
                ]

                # TD update (if we have a previous value)
                if prev_value is not None:
                    td_error = current_value.numpy()[0, 0] - prev_value
                    for var, trace in zip(self.model.trainable_variables, traces):
                        var.assign_add(self.lr * td_error * trace)

                prev_value = current_value.numpy()[0, 0]

                # Choose best move (greedy)
                best_action = self._choose_best_action(actions)
                result = self.api.step(*best_action)
                move_count += 1

                if result["done"]:
                    break

                if result["turn_complete"]:
                    self.api.end_turn()

        # Terminal update
        winner = self.api.engine.winner
        if winner is not None and prev_value is not None:
            # Final reward: 1 if dark wins, 0 if light wins (from dark's perspective)
            final_value = 1.0 if winner == Color.DARK else 0.0
            td_error = final_value - prev_value
            for var, trace in zip(self.model.trainable_variables, traces):
                var.assign_add(self.lr * td_error * trace)

        return {
            "winner": str(winner) if winner else None,
            "moves": move_count,
        }

    def _choose_best_action(self, actions):
        """Choose the action that leads to highest value for current player."""
        best_value = -float("inf")
        best_action = actions[0]

        current_color = self.api.current_player_color

        for action in actions:
            # Simulate the move
            value = self._evaluate_action(action, current_color)
            if value > best_value:
                best_value = value
                best_action = action

        return best_action

    def _evaluate_action(self, action, current_color):
        """Evaluate a hypothetical action by simulating it on a copy of the board."""
        # For efficiency, just use the current value + a small random noise
        # (dice provide natural exploration in backgammon)
        # A full lookahead would copy the board state — we use the simpler approach
        board = self.api.engine.board
        position_copy = {k: list(v) for k, v in board.position.items()}
        bar_copy = list(board.bar)
        off_dark_copy = list(board.off_dark)
        off_light_copy = list(board.off_light)

        # Simulate move on copy
        from pygammon.logic.move import move_checker
        from pygammon.logic.models import Board

        temp_board = Board()
        temp_board.position = position_copy
        temp_board.bar = bar_copy
        temp_board.off_dark = off_dark_copy
        temp_board.off_light = off_light_copy

        player = self.api.engine.current_player
        from_pt, to_pt, die_val = action

        # Handle bar entry
        if from_pt == player.bar:
            if any(c == player.color for c in temp_board.bar):
                temp_board.bar.remove(player.color)
                temp_board.position.setdefault(from_pt, []).insert(0, player.color)

        try:
            opponent, borne_off = move_checker(
                from_pt, to_pt, player, temp_board.position
            )
            if opponent:
                temp_board.bar.append(opponent)
            if borne_off:
                if player.color == Color.DARK:
                    temp_board.off_dark.append(player.color)
                else:
                    temp_board.off_light.append(player.color)
        except ValueError:
            return -float("inf")

        encoded = encode_board(temp_board, current_color)
        x = tf.constant(encoded.reshape(1, -1))
        value = self.model(x).numpy()[0, 0]

        # If current player is light, flip value (model outputs from dark's perspective)
        if current_color == Color.LIGHT:
            value = 1.0 - value

        return value
