"""TD-Gammon 198-feature board encoding. Pure numpy, no TF dependency."""

import numpy as np

from pygammon.logic.models import Board, Color


def encode_board(board: Board, current_player: Color) -> np.ndarray:
    """
    Encode board state into 198-feature vector (TD-Gammon style).

    For each of the 24 points, for each player (2), encode 4 features:
    - 1 checker present (0 or 1)
    - 2 checkers present (0 or 1)
    - 3 checkers present (0 or 1)
    - (n - 3) / 2 if n >= 3, else 0 (extra checkers)

    That's 24 * 2 * 4 = 192 features.

    Plus:
    - bar count for each player / 2 (2 features)
    - borne-off count for each player / 15 (2 features)
    - current player indicator (1 feature for dark, 1 for light)

    Total: 192 + 2 + 2 + 2 = 198
    """
    features = np.zeros(198, dtype=np.float32)

    for point in range(1, 25):
        checkers = board.position.get(point, [])
        if not checkers:
            continue

        color = checkers[0]
        n = len(checkers)

        # Offset: dark features at index 0-95, light at 96-191
        if color == Color.DARK:
            base = (point - 1) * 4
        else:
            base = 96 + (point - 1) * 4

        features[base] = 1.0 if n >= 1 else 0.0
        features[base + 1] = 1.0 if n >= 2 else 0.0
        features[base + 2] = 1.0 if n >= 3 else 0.0
        features[base + 3] = (n - 3) / 2.0 if n > 3 else 0.0

    # Bar (indices 192-193)
    dark_bar = sum(1 for c in board.bar if c == Color.DARK)
    light_bar = sum(1 for c in board.bar if c == Color.LIGHT)
    features[192] = dark_bar / 2.0
    features[193] = light_bar / 2.0

    # Borne off (indices 194-195)
    features[194] = len(board.off_dark) / 15.0
    features[195] = len(board.off_light) / 15.0

    # Current player indicator (indices 196-197)
    features[196] = 1.0 if current_player == Color.DARK else 0.0
    features[197] = 1.0 if current_player == Color.LIGHT else 0.0

    return features
