"""Smoke tests for UI components. Requires PySide6 + a display server."""

import pytest

try:
    from PySide6.QtWidgets import QApplication

    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False

pytestmark = pytest.mark.skipif(not HAS_PYSIDE6, reason="PySide6 not installed")


@pytest.fixture(scope="session")
def qapp():
    """Create a single QApplication for all UI tests."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def board():
    from pygammon.logic.models import Board

    return Board()


@pytest.fixture
def scene(qapp, board):
    from pygammon.ui.board import PygammonScene

    return PygammonScene(board=board)


class TestPygammonScene:
    def test_draw_board(self, scene):
        scene.draw_board()
        # Should have 24 triangle items (12 top + 12 bottom)
        assert len(scene.items()) == 24

    def test_draw_checkers_creates_items(self, scene):
        from pygammon.ui.checker import CheckerItem

        scene.draw_board()
        scene.draw_checkers()
        # 30 checkers (15 per player)
        assert len(scene.checker_items) == 30
        assert all(isinstance(c, CheckerItem) for c in scene.checker_items)

    def test_draw_checkers_stores_point_index(self, scene):
        scene.draw_board()
        scene.draw_checkers()
        point_indices = {c.point_index for c in scene.checker_items}
        # Initial position has checkers at these points
        assert point_indices == {1, 6, 8, 12, 13, 17, 19, 24}

    def test_refresh_board_replaces_checkers(self, scene):
        scene.draw_board()
        scene.draw_checkers()
        old_items = list(scene.checker_items)
        scene.refresh_board()
        assert scene.checker_items != old_items
        assert len(scene.checker_items) == 30

    def test_highlight_valid_sources(self, scene):
        scene.draw_board()
        scene.draw_checkers()
        moves = [(1, 4, 3), (12, 15, 3)]
        scene.highlight_valid_sources(moves)

        highlighted = [c for c in scene.checker_items if c.point_index in (1, 12)]
        assert len(highlighted) > 0

    def test_highlight_valid_destinations(self, scene):
        scene.draw_board()
        scene.draw_checkers()
        moves = [(1, 4, 3), (1, 6, 5)]
        scene.highlight_valid_destinations(moves)
        # Should create 2 highlight circles
        assert len(scene.highlight_items) == 2

    def test_highlight_destinations_skips_bear_off(self, scene):
        scene.draw_board()
        scene.draw_checkers()
        moves = [(24, 25, 1)]  # Bear-off destination
        scene.highlight_valid_destinations(moves)
        assert len(scene.highlight_items) == 0

    def test_clear_highlights(self, scene):
        scene.draw_board()
        scene.draw_checkers()
        scene.highlight_valid_destinations([(1, 4, 3)])
        assert len(scene.highlight_items) == 1
        scene.clear_highlights()
        assert len(scene.highlight_items) == 0

    def test_draw_bar_checkers(self, scene):
        from pygammon.logic.models import Color

        scene.board.bar = [Color.DARK, Color.LIGHT]
        scene.draw_board()
        scene.draw_checkers()
        assert len(scene.bar_items) == 2


class TestPointFromPosition:
    def test_top_left_is_point_1(self, scene):
        from PySide6.QtCore import QPointF
        from pygammon.conf import settings

        pos = QPointF(settings.point_width * 0.5, settings.board_height * 0.25)
        assert scene._point_from_position(pos) == 1

    def test_top_right_is_point_12(self, scene):
        from PySide6.QtCore import QPointF
        from pygammon.conf import settings

        x = 11 * settings.point_width + settings.point_width + settings.point_width * 0.5
        pos = QPointF(x, settings.board_height * 0.25)
        assert scene._point_from_position(pos) == 12

    def test_bottom_left_is_point_24(self, scene):
        from PySide6.QtCore import QPointF
        from pygammon.conf import settings

        pos = QPointF(settings.point_width * 0.5, settings.board_height * 0.75)
        assert scene._point_from_position(pos) == 24

    def test_bottom_right_is_point_13(self, scene):
        from PySide6.QtCore import QPointF
        from pygammon.conf import settings

        x = 11 * settings.point_width + settings.point_width + settings.point_width * 0.5
        pos = QPointF(x, settings.board_height * 0.75)
        assert scene._point_from_position(pos) == 13

    def test_bar_returns_none(self, scene):
        from PySide6.QtCore import QPointF
        from pygammon.conf import settings

        bar_x = 6 * settings.point_width + settings.point_width * 0.5
        pos = QPointF(bar_x, settings.board_height * 0.25)
        assert scene._point_from_position(pos) is None


class TestBackgammonWindow:
    def test_window_creates(self, qapp):
        from pygammon.ui.window import BackgammonWindow

        window = BackgammonWindow()
        assert window.windowTitle() == "Pygammon"
        assert window.roll_button is not None
        assert window.roll_button.isEnabled() is False

    def test_set_scene(self, qapp):
        from pygammon.logic.models import Board
        from pygammon.ui.board import PygammonScene
        from pygammon.ui.window import BackgammonWindow

        window = BackgammonWindow()
        board = Board()
        scene = PygammonScene(board=board)
        scene.draw_board()
        window.set_scene(scene)
        assert window.view is not None

    def test_update_labels(self, qapp):
        from pygammon.ui.window import BackgammonWindow

        window = BackgammonWindow()
        window.update_player_label("Alice", "dark")
        assert "Alice" in window.current_player_label.text()

        window.update_dice_label(3, 5)
        assert "3" in window.dice_label.text()
        assert "5" in window.dice_label.text()

        window.update_off_counts(2, 7)
        assert "2" in window.off_dark_label.text()
        assert "7" in window.off_light_label.text()


class TestCheckerItem:
    def test_checker_stores_point_index(self, qapp):
        from PySide6.QtGui import QColor
        from pygammon.ui.checker import CheckerItem

        checker = CheckerItem(0, 0, 20, QColor("#ff0000"), point_index=5)
        assert checker.point_index == 5

    def test_set_highlighted(self, qapp):
        from PySide6.QtGui import QColor
        from pygammon.ui.checker import CheckerItem

        checker = CheckerItem(0, 0, 20, QColor("#ff0000"), point_index=5)
        checker.set_highlighted(True)
        assert checker.pen().widthF() == 3.0
        checker.set_highlighted(False)
        assert checker.pen().widthF() != 3.0
