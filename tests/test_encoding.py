import pytest

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@pytest.mark.skipif(not HAS_NUMPY, reason="numpy not installed")
class TestEncoding:
    def test_output_shape(self):
        from pygammon.engine.encoding import encode_board
        from pygammon.logic.models import Board, Color

        board = Board()
        features = encode_board(board, Color.DARK)
        assert features.shape == (198,)
        assert features.dtype == np.float32

    def test_initial_position_dark_features(self):
        from pygammon.engine.encoding import encode_board
        from pygammon.logic.models import Board, Color

        board = Board()
        features = encode_board(board, Color.DARK)

        # Point 1 has 2 dark checkers -> base index = 0
        assert features[0] == 1.0
        assert features[1] == 1.0
        assert features[2] == 0.0
        assert features[3] == 0.0

    def test_initial_position_light_features(self):
        from pygammon.engine.encoding import encode_board
        from pygammon.logic.models import Board, Color

        board = Board()
        features = encode_board(board, Color.DARK)

        # Point 6 has 5 light checkers -> base index = 96 + (6-1)*4 = 116
        assert features[116] == 1.0
        assert features[117] == 1.0
        assert features[118] == 1.0
        assert features[119] == 1.0  # (5-3)/2 = 1.0

    def test_current_player_indicator(self):
        from pygammon.engine.encoding import encode_board
        from pygammon.logic.models import Board, Color

        board = Board()
        dark_features = encode_board(board, Color.DARK)
        assert dark_features[196] == 1.0
        assert dark_features[197] == 0.0

        light_features = encode_board(board, Color.LIGHT)
        assert light_features[196] == 0.0
        assert light_features[197] == 1.0

    def test_bar_encoding(self):
        from pygammon.engine.encoding import encode_board
        from pygammon.logic.models import Board, Color

        board = Board()
        board.bar = [Color.DARK, Color.DARK, Color.LIGHT]
        features = encode_board(board, Color.DARK)
        assert features[192] == 1.0  # 2 dark / 2
        assert features[193] == 0.5  # 1 light / 2

    def test_borne_off_encoding(self):
        from pygammon.engine.encoding import encode_board
        from pygammon.logic.models import Board, Color

        board = Board()
        board.off_dark = [Color.DARK] * 10
        board.off_light = [Color.LIGHT] * 5
        features = encode_board(board, Color.DARK)
        assert abs(features[194] - 10 / 15.0) < 1e-6
        assert abs(features[195] - 5 / 15.0) < 1e-6

    def test_empty_board(self):
        from pygammon.engine.encoding import encode_board
        from pygammon.logic.models import Board, Color

        board = Board()
        board.position = {}
        board.bar = []
        features = encode_board(board, Color.DARK)
        assert np.sum(features[:192]) == 0.0
