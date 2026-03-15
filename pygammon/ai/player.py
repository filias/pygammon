"""AI player that uses a trained TD-Gammon model to select moves."""

import copy

import numpy as np
import tensorflow as tf

from pygammon.ai.model import TDGammonModel
from pygammon.engine.encoding import encode_board
from pygammon.logic.models import Board, Color
from pygammon.logic.move import move_checker


class AIPlayer:
    """Loads a trained model and picks the best move by evaluating all legal positions."""

    def __init__(self, model_path: str, hidden_size: int = 80):
        self.model = TDGammonModel(hidden_size=hidden_size)
        # Build and load
        self.model(tf.zeros((1, 198)))
        self.model.load_weights(model_path)

    def _win_probability(self, board, player):
        """Get win probability for the given player."""
        encoded = encode_board(board, player.color)
        x = tf.constant(encoded.reshape(1, -1))
        value = self.model(x).numpy()[0, 0]
        if player.color == Color.LIGHT:
            value = 1.0 - value
        return value

    def should_double(self, board, player) -> bool:
        """Propose doubling if win probability > 70%."""
        return self._win_probability(board, player) > 0.70

    def should_accept_double(self, board, player) -> bool:
        """Accept a double if win probability > 25%."""
        return self._win_probability(board, player) > 0.25

    def choose_move(self, board, player, legal_moves):
        """
        Evaluate all legal moves and return the best (from_pt, to_pt, die_val).
        Evaluates from the perspective of the current player.
        """
        if not legal_moves:
            return None

        best_value = -float("inf")
        best_move = legal_moves[0]

        for from_pt, to_pt, die_val in legal_moves:
            value = self._evaluate_move(board, player, from_pt, to_pt, die_val)
            if value > best_value:
                best_value = value
                best_move = (from_pt, to_pt, die_val)

        return best_move

    def _evaluate_move(self, board, player, from_pt, to_pt, die_val):
        """Simulate a move on a copy and evaluate the resulting position."""
        temp_board = Board()
        temp_board.position = {k: list(v) for k, v in board.position.items()}
        temp_board.bar = list(board.bar)
        temp_board.off_dark = list(board.off_dark)
        temp_board.off_light = list(board.off_light)

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

        encoded = encode_board(temp_board, player.color)
        x = tf.constant(encoded.reshape(1, -1))
        value = self.model(x).numpy()[0, 0]

        # Model outputs dark win prob; flip for light
        if player.color == Color.LIGHT:
            value = 1.0 - value

        return value
