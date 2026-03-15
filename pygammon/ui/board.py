from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPolygonF, QPen, QBrush
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsPolygonItem,
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsSceneMouseEvent,
    QGraphicsSimpleTextItem,
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
        self.tray_items = []
        self.setSceneRect(0, 0, settings.board_width, settings.board_height)

    # --- Layout helpers ---

    def _x_for_column(self, col: int) -> float:
        """X position for the left edge of a point column (0-11)."""
        x = col * settings.point_width
        if col >= 6:
            x += settings.bar_width
        return x

    @property
    def _bar_x(self) -> float:
        return 6 * settings.point_width

    @property
    def _tray_x(self) -> float:
        return 12 * settings.point_width + settings.bar_width

    # --- Drawing ---

    def draw_board(self):
        self.setBackgroundBrush(QColor(settings.color_board))
        self.setSceneRect(0, 0, settings.board_width, settings.board_height)

        # Draw bar
        bar_rect = QGraphicsRectItem(
            self._bar_x, 0, settings.bar_width, settings.board_height
        )
        bar_rect.setBrush(QBrush(QColor(settings.color_bar)))
        bar_rect.setPen(QPen(QColor(settings.color_bar)))
        self.addItem(bar_rect)

        # Draw bear-off tray
        tray_rect = QGraphicsRectItem(
            self._tray_x, 0, settings.tray_width, settings.board_height
        )
        tray_rect.setBrush(QBrush(QColor(settings.color_tray)))
        tray_rect.setPen(QPen(QColor(settings.color_tray)))
        self.addItem(tray_rect)

        # Tray divider line
        mid_y = settings.board_height / 2
        divider = QGraphicsRectItem(
            self._tray_x, mid_y - 0.5, settings.tray_width, 1
        )
        divider.setBrush(QBrush(QColor("#ffffff")))
        divider.setPen(QPen(QColor("#ffffff")))
        self.addItem(divider)

        # Draw triangles
        for i in range(12):
            triangle_color = _get_color(index=i)
            pen = QPen(triangle_color)
            x_start = self._x_for_column(i)

            # Top triangles (points 1-12)
            base_left = QPointF(x_start, 0)
            top_middle = QPointF(
                x_start + settings.point_width / 2, settings.point_height
            )
            base_right = QPointF(x_start + settings.point_width, 0)

            tri = QGraphicsPolygonItem(
                QPolygonF([base_left, top_middle, base_right])
            )
            tri.setPen(pen)
            tri.setBrush(triangle_color)
            self.addItem(tri)

            # Bottom triangles (points 13-24)
            mirror_color = _toggle_color(triangle_color)
            pen = QPen(mirror_color)

            base_left = QPointF(x_start, settings.board_height)
            top_middle = QPointF(
                x_start + settings.point_width / 2,
                settings.board_height - settings.point_height,
            )
            base_right = QPointF(x_start + settings.point_width, settings.board_height)

            tri_m = QGraphicsPolygonItem(
                QPolygonF([base_left, top_middle, base_right])
            )
            tri_m.setPen(pen)
            tri_m.setBrush(QColor(mirror_color))
            self.addItem(tri_m)

    def _calculate_x_checker(self, point_index: int) -> float:
        if point_index >= 13:
            col = 24 - point_index
        else:
            col = point_index - 1

        x = self._x_for_column(col)
        x += settings.point_width / 2 - settings.checker_radius
        return x

    def _calculate_y_checker(self, point_index: int, checker_index: int) -> float:
        checker_height = checker_index * settings.checker_radius * 2

        if point_index >= 13:
            return settings.board_height - checker_height
        else:
            return checker_height - settings.checker_radius * 2

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
            x = self._calculate_x_checker(point_index)

            for ci in range(1, len(checkers) + 1):
                y = self._calculate_y_checker(point_index, ci)
                item = CheckerItem(
                    x, y,
                    settings.checker_radius * 2,
                    QColor(checker_color),
                    point_index,
                )
                self.addItem(item)
                self.checker_items.append(item)

        self._draw_bar_checkers()
        self._draw_tray_checkers()

    def _draw_bar_checkers(self):
        for item in self.bar_items:
            self.removeItem(item)
        self.bar_items.clear()

        bar_cx = self._bar_x + settings.bar_width / 2 - settings.checker_radius
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
                bar_cx, y,
                settings.checker_radius * 2,
                QColor(color),
                point_index=25 if checker_color_val == Color.DARK else 0,
            )
            self.addItem(item)
            self.bar_items.append(item)

    def _draw_tray_checkers(self):
        for item in self.tray_items:
            self.removeItem(item)
        self.tray_items.clear()

        tray_cx = self._tray_x + settings.tray_width / 2 - settings.checker_radius
        r = settings.checker_radius
        small_h = r * 0.6  # Stack them tighter in tray

        # Dark borne off — bottom half of tray
        for i, _ in enumerate(self.board.off_dark):
            y = settings.board_height - (i + 1) * small_h
            item = QGraphicsEllipseItem(tray_cx, y, r * 2, small_h)
            item.setBrush(QBrush(QColor(settings.color_dark_checker)))
            item.setPen(QPen(QColor(settings.color_dark_checker)))
            item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
            self.addItem(item)
            self.tray_items.append(item)

        # Light borne off — top half of tray
        for i, _ in enumerate(self.board.off_light):
            y = i * small_h
            item = QGraphicsEllipseItem(tray_cx, y, r * 2, small_h)
            item.setBrush(QBrush(QColor(settings.color_light_checker)))
            item.setPen(QPen(QColor(settings.color_light_checker)))
            item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
            self.addItem(item)
            self.tray_items.append(item)

    # --- Dice ---

    def draw_dice(self, die1: int, die2: int, player_color: str):
        self.clear_dice()

        size = settings.die_size
        gap = size * 0.4
        dice_total_w = size * 2 + gap
        mid_y = settings.board_height / 2

        if player_color == Color.DARK:
            # Dark: right half (between bar and tray), bottom
            area_x = self._bar_x + settings.bar_width
            area_w = self._tray_x - area_x
            bg_color = settings.color_dark_checker
            pip_color = settings.color_light_checker
            y = mid_y + gap
        else:
            # Light: left half (left of bar), top
            area_x = 0
            area_w = self._bar_x
            bg_color = settings.color_light_checker
            pip_color = settings.color_dark_checker
            y = mid_y - gap - size

        x_start = area_x + (area_w - dice_total_w) / 2

        d1 = DieItem(x_start, y, die1, bg_color=bg_color, pip_color=pip_color)
        d2 = DieItem(x_start + size + gap, y, die2, bg_color=bg_color, pip_color=pip_color)
        self.addItem(d1)
        self.addItem(d2)
        self.dice_items.extend([d1, d2])

    def clear_dice(self):
        for item in self.dice_items:
            self.removeItem(item)
        self.dice_items.clear()

    # --- Highlights ---

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
            y_center = (
                settings.point_height
                if dest <= 12
                else settings.board_height - settings.point_height
            )
            r = settings.checker_radius
            highlight = QGraphicsEllipseItem(x, y_center - r, r * 2, r * 2)
            highlight.setBrush(QBrush(QColor(settings.color_highlight_dest)))
            highlight.setOpacity(0.4)
            highlight.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
            self.addItem(highlight)
            self.highlight_items.append(highlight)

    def clear_highlights(self):
        for item in self.highlight_items:
            self.removeItem(item)
        self.highlight_items.clear()
        for checker in self.checker_items:
            checker.set_highlighted(False)

    # --- Click handling ---

    def on_checker_clicked(self, point_index: int):
        if self.controller:
            self.controller.on_point_clicked(point_index)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        for item in self.items(event.scenePos()):
            if isinstance(item, CheckerItem):
                item.mousePressEvent(event)
                return

        point = self._point_from_position(event.scenePos())
        if point is not None and self.controller:
            self.controller.on_point_clicked(point)

    def _point_from_position(self, pos):
        """Convert a scene position to a board point index (1-24) or None."""
        x, y = pos.x(), pos.y()
        half_h = settings.board_height / 2
        is_top = y < half_h

        # Check if in bar or tray area
        if x >= self._bar_x and x <= self._bar_x + settings.bar_width:
            return None
        if x >= self._tray_x:
            return None

        # Left half (columns 0-5)
        if x < self._bar_x:
            col = int(x / settings.point_width)
            col = max(0, min(5, col))
        # Right half (columns 6-11)
        else:
            adjusted_x = x - self._bar_x - settings.bar_width
            col = int(adjusted_x / settings.point_width) + 6
            col = max(6, min(11, col))

        if is_top:
            return col + 1  # Points 1-12
        else:
            return 24 - col  # Points 24-13


def _get_color(index: int) -> QColor:
    if index % 2 == 0:
        return QColor(settings.color_dark_triangle)
    return QColor(settings.color_light_triangle)


def _toggle_color(color: QColor) -> QColor:
    if color == QColor(settings.color_dark_triangle):
        return QColor(settings.color_light_triangle)
    return QColor(settings.color_dark_triangle)
