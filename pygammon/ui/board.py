from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPolygonF, QPen, QBrush
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsPolygonItem,
    QGraphicsEllipseItem,
    QGraphicsSceneMouseEvent,
    QGraphicsTextItem,
)

from pygammon.logic.models import Color
from pygammon.ui.checker import CheckerItem
from pygammon.ui.dice import DieItem
from pygammon.conf import settings


class PygammonScene(QGraphicsScene):
    def __init__(self, board, controller=None):
        super().__init__()
        self.board = board
        self.controller = controller
        self.checker_items = []
        self.highlight_items = []
        self.bar_items = []
        self.dice_items = []
        self.setSceneRect(0, 0, settings.board_width, settings.board_height)

    def draw_board(self):
        self.setBackgroundBrush(QColor(settings.color_board))
        self.setSceneRect(0, 0, settings.board_width, settings.board_height)

        for i in range(12):
            triangle_color = _get_color(index=i)
            pen = QPen(triangle_color)

            x_start = i * settings.point_width
            if i >= 6:
                x_start += settings.point_width

            # Top triangles
            base_left = QPointF(x_start, 0)
            top_middle = QPointF(
                x_start + settings.point_width / 2, settings.point_height
            )
            base_right = QPointF(x_start + settings.point_width, 0)

            triangle = QPolygonF([base_left, top_middle, base_right])
            triangle_polygon = QGraphicsPolygonItem(triangle)
            triangle_polygon.setPen(pen)
            triangle_polygon.setBrush(triangle_color)
            self.addItem(triangle_polygon)

            # Bottom (mirror) triangles
            mirror_triangle_color = _toggle_color(color=triangle_color)
            pen = QPen(mirror_triangle_color)

            base_left = QPointF(x_start, settings.board_height)
            top_middle = QPointF(
                x_start + settings.point_width / 2,
                settings.board_height - settings.point_height,
            )
            base_right = QPointF(
                x_start + settings.point_width, settings.board_height
            )

            triangle_mirror = QPolygonF([base_left, top_middle, base_right])
            triangle_polygon_mirror = QGraphicsPolygonItem(triangle_mirror)
            triangle_polygon_mirror.setPen(pen)
            triangle_polygon_mirror.setBrush(QColor(mirror_triangle_color))
            self.addItem(triangle_polygon_mirror)

    def _calculate_x_checker(self, point_index: int) -> float:
        if point_index >= 13:
            point_index = 25 - point_index

        x_point = (point_index - 1) * settings.point_width
        x_middle_of_point = settings.point_width / 2
        x_checker = x_point + x_middle_of_point - settings.checker_radius

        if point_index > 6:
            x_checker += settings.point_width

        return x_checker

    def _calculate_y_checker(self, point_index, checker_index: int) -> float:
        checker_height = checker_index * settings.checker_radius * 2

        if point_index >= 13:
            y_checker = settings.board_height - checker_height
        else:
            y_checker = checker_height - settings.checker_radius * 2

        return y_checker

    def draw_checkers(self):
        for item in self.checker_items:
            self.removeItem(item)
        self.checker_items.clear()

        for point_index, checkers in self.board.position.items():
            if not checkers:
                continue

            checker_color = (
                settings.color_dark_checker
                if checkers[0] == Color.DARK
                else settings.color_light_checker
            )
            x_checker = self._calculate_x_checker(point_index)

            for checker_index in range(1, len(checkers) + 1):
                y_checker = self._calculate_y_checker(point_index, checker_index)

                checker = CheckerItem(
                    x_checker,
                    y_checker,
                    settings.checker_radius * 2,
                    QColor(checker_color),
                    point_index,
                )
                self.addItem(checker)
                self.checker_items.append(checker)

        # Draw bar checkers
        self._draw_bar_checkers()

    def _draw_bar_checkers(self):
        for item in self.bar_items:
            self.removeItem(item)
        self.bar_items.clear()

        bar_x = settings.point_width * 6  # Middle of board
        dark_count = 0
        light_count = 0

        for checker_color_val in self.board.bar:
            if checker_color_val == Color.DARK:
                dark_count += 1
                color = settings.color_dark_checker
                y = settings.board_height / 2 - dark_count * settings.checker_radius * 2
            else:
                light_count += 1
                color = settings.color_light_checker
                y = settings.board_height / 2 + (light_count - 1) * settings.checker_radius * 2

            item = CheckerItem(
                bar_x,
                y,
                settings.checker_radius * 2,
                QColor(color),
                point_index=25 if checker_color_val == Color.DARK else 0,
            )
            self.addItem(item)
            self.bar_items.append(item)

    def draw_dice(self, die1: int, die2: int, player_color: str):
        """Draw two dice on the right side of the board for the given player."""
        self.clear_dice()

        size = settings.die_size
        gap = size * 0.3
        # Right margin: after the 12 points + bar
        x_start = 13 * settings.point_width + gap

        if player_color == Color.DARK:
            # Dark plays on bottom half — dice in bottom-right
            y = settings.board_height * 0.5 + gap
        else:
            # Light plays on top half — dice in top-right
            y = settings.board_height * 0.5 - gap - size

        d1 = DieItem(x_start, y, die1)
        d2 = DieItem(x_start + size + gap, y, die2)
        self.addItem(d1)
        self.addItem(d2)
        self.dice_items.extend([d1, d2])

    def clear_dice(self):
        for item in self.dice_items:
            self.removeItem(item)
        self.dice_items.clear()

    def refresh_board(self):
        self.clear_highlights()
        self.draw_checkers()

    def highlight_valid_sources(self, valid_moves):
        self.clear_highlights()
        source_points = set(m[0] for m in valid_moves)
        for checker in self.checker_items:
            if checker.point_index in source_points:
                checker.set_highlighted(True)

    def highlight_valid_destinations(self, moves):
        self.clear_highlights()
        for m in moves:
            dest = m[1]
            if dest < 1 or dest > 24:
                continue
            x = self._calculate_x_checker(dest)
            y_center = settings.point_height if dest <= 12 else settings.board_height - settings.point_height
            r = settings.checker_radius
            highlight = QGraphicsEllipseItem(x, y_center - r, r * 2, r * 2)
            highlight.setBrush(QBrush(QColor(settings.color_highlight_dest)))
            highlight.setOpacity(0.4)
            highlight.setAcceptedMouseButtons(Qt.MouseButton.NoButton)  # Click-through
            self.addItem(highlight)
            self.highlight_items.append(highlight)

    def clear_highlights(self):
        for item in self.highlight_items:
            self.removeItem(item)
        self.highlight_items.clear()
        for checker in self.checker_items:
            checker.set_highlighted(False)

    def on_checker_clicked(self, point_index: int):
        if self.controller:
            self.controller.on_point_clicked(point_index)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        # Check if a CheckerItem was clicked — let it handle via on_checker_clicked
        for item in self.items(event.scenePos()):
            if isinstance(item, CheckerItem):
                item.mousePressEvent(event)
                return

        # No checker at click position — resolve as a point click
        point = self._point_from_position(event.scenePos())
        if point is not None and self.controller:
            self.controller.on_point_clicked(point)

    def _point_from_position(self, pos):
        """Convert a scene position to a board point index (1-24) or None."""
        x, y = pos.x(), pos.y()
        half_h = settings.board_height / 2

        # Determine if top half (points 1-12) or bottom half (points 13-24)
        is_top = y < half_h

        # Calculate which column (0-12) the click is in
        # Account for the bar gap between columns 5 and 6
        bar_left = 6 * settings.point_width
        bar_right = bar_left + settings.point_width

        if bar_left <= x <= bar_right:
            return None  # Clicked on bar

        if x < bar_left:
            col = int(x / settings.point_width)
            if col > 5:
                col = 5
        elif x > bar_right:
            col = int((x - settings.point_width) / settings.point_width)
            if col < 6:
                col = 6
            if col > 11:
                col = 11
        else:
            return None

        if is_top:
            # Top row: left to right = points 1-12
            return col + 1
        else:
            # Bottom row: left to right = points 24, 23, ..., 13
            return 24 - col


def _get_color(index: int) -> QColor:
    if index % 2 == 0:
        return QColor(settings.color_dark_triangle)
    return QColor(settings.color_light_triangle)


def _toggle_color(color: QColor) -> QColor:
    if color == QColor(settings.color_dark_triangle):
        return QColor(settings.color_light_triangle)
    return QColor(settings.color_dark_triangle)
