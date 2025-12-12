from pygammon.logic.models import Board, Color

from pygammon.logic.position import has_winner


def test_has_winner_no_winner():
    board = Board()
    assert has_winner(board) is None


def test_has_winner_light():
    # This is a hack test
    board = Board(off_light=[1,2,3,4,5,6,7,8,9,1,1,1,1,1,1], off_dark=[])
    assert has_winner(board) is Color.LIGHT
