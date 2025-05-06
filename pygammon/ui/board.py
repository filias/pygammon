from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPolygonF, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPolygonItem

from pygammon.logic.pygammon import Color
from pygammon.ui.checker import MovableChecker
from pygammon.conf import settings


class PygammonScene(QGraphicsScene):

    def __init__(self, board):
        super().__init__()
        self.board = board
        self.setSceneRect(0, 0, settings.board_width, settings.board_height)

    def draw_board(self):
        self.setBackgroundBrush(QColor(settings.color_board))
        self.setSceneRect(
            0, 0, settings.board_width, settings.board_height
        )  # Scene size

        # Draw triangles (board points) (0,0 is up, left)
        for i in range(12):  # 12 points on each side
            #print(f"Setting up triangle {i}")

            # Setup colors
            triangle_color = _get_color(index=i)
            pen = QPen(triangle_color)

            x_start = i * settings.point_width
            if i >= 6:
                x_start += settings.point_width

            # Triangle points
            base_left = QPointF(x_start, 0)
            top_middle = QPointF(
                x_start + settings.point_width / 2, settings.point_height
            )
            base_right = QPointF(x_start + settings.point_width, 0)

            triangle = QPolygonF(
                [
                    base_left,
                    top_middle,
                    base_right,
                ]
            )

            # Draw the triangle
            #print(f"Drawing triangle {i}")
            triangle_polygon = QGraphicsPolygonItem(triangle)
            triangle_polygon.setPen(pen)  # Line color
            triangle_polygon.setBrush(triangle_color)  # Filling color
            self.addItem(triangle_polygon)

            # Triangle mirror for the other side of the board and change color
            mirror_triangle_color = _toggle_color(color=triangle_color)
            pen = QPen(mirror_triangle_color)

            base_left = QPointF(x_start, settings.board_height)
            top_middle = QPointF(
                x_start + settings.point_width / 2,
                settings.board_height - settings.point_height,
            )
            base_right = QPointF(x_start + settings.point_width, settings.board_height)

            triangle_mirror = QPolygonF(
                [
                    base_left,
                    top_middle,
                    base_right,
                ]
            )

            #print(f"Drawing mirror triangle {i}")
            triangle_polygon_mirror = QGraphicsPolygonItem(triangle_mirror)
            triangle_polygon_mirror.setPen(pen)  # Line color
            triangle_polygon_mirror.setBrush(
                QColor(mirror_triangle_color)
            )  # Filling color
            self.addItem(triangle_polygon_mirror)

    def _calculate_x_checker(self, point_index: int) -> float:
        if point_index >= 13:  # Bottom checkers
            point_index = 25 - point_index

        x_point = (point_index - 1) * settings.point_width  # Closer to 0
        x_middle_of_point = settings.point_width / 2
        x_checker = x_point + x_middle_of_point - settings.checker_radius

        if point_index > 6:  # Compensate for the bar
            x_checker += settings.point_width

        return x_checker

    def _calculate_y_checker(self, point_index, checker_index: int) -> float:
        checker_height = checker_index * settings.checker_radius * 2

        if point_index >= 13:  # Bottom checkers
            y_checker = settings.board_height - checker_height
        else: # Top checkers
            y_checker = checker_height - settings.checker_radius * 2

        return y_checker

    def draw_checkers(self):
        for point_index, checkers in self.board.position.items():
            print(f"Drawing {len(checkers)} checkers at point {point_index}")

            # Define the checker color
            checker_color = settings.color_dark_checker if checkers[0] == Color.DARK else settings.color_light_checker
            x_checker = self._calculate_x_checker(point_index)

            for checker_index in range(1, len(checkers) + 1):
                y_checker = self._calculate_y_checker(point_index, checker_index)

                # Add checkers to the scene
                print(f"Adding checker: {x_checker}, {y_checker}, {point_index} and {checker_index}")
                checker = MovableChecker(
                    x_checker, y_checker, settings.checker_radius * 2, checker_color
                )
                self.addItem(checker)

def _get_color(index: int) -> QColor:
    if index % 2 == 0:
        return QColor(settings.color_dark_triangle)

    return QColor(settings.color_light_triangle)

def _toggle_color(color: QColor) -> QColor:
    if color == QColor(settings.color_dark_triangle):
        return QColor(settings.color_light_triangle)

    return QColor(settings.color_dark_triangle)
