from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPolygonF, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPolygonItem

from pygammon.checker import MovableChecker
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

    def draw_checkers(self):
        for point_index, checkers in self.board.position.items():
            print(f"Drawing checkers at point {point_index}")

            for checker_index in range(1, len(checkers) + 1):
                print(f"Drawing checker at point {point_index} and checker {checker_index}")

                # Top checkers
                x_checker = (
                    (point_index - 1) * settings.point_width
                    + settings.point_width / 2
                    - settings.checker_radius
                )
                if point_index > 6:
                    # print(
                    #     f"Adjusting x for point {point_index} from {x_checker} to {x_checker + 10 * settings.point_width}"
                    # )
                    x_checker += settings.point_width
                y_checker = settings.board_height - (
                    checker_index * settings.checker_radius * 2
                )

                # Mirror checkers for the bottom side
                x_mirror_checker = (
                    (point_index - 1) * settings.point_width
                    + settings.point_width / 2
                    - settings.checker_radius
                )
                if point_index > 6:
                    # print(
                    #     f"Adjusting x for point {point_index} from {x_checker} to {x_checker + 10 * settings.point_width}"
                    # )
                    x_mirror_checker += settings.point_width
                y_mirror_checker = (
                    checker_index * settings.checker_radius * 2
                    - settings.checker_radius * 2
                )

                # Set the color
                if point_index in (1, 12):
                    checker_color = QColor(settings.color_light_checker)
                    mirror_checker_color = QColor(settings.color_dark_checker)
                else:
                    checker_color = QColor(settings.color_dark_checker)
                    mirror_checker_color = QColor(settings.color_light_checker)

                # Add checkers to the scene
                print(
                    f"Adding top checker to the scene with {x_checker}, {y_checker}, {point_index} and {checker_index}"
                )
                checker = MovableChecker(
                    x_checker, y_checker, settings.checker_radius * 2, checker_color
                )

                print(
                    f"Adding bottom checker to the scene with {x_mirror_checker}, {y_mirror_checker}, {point_index} and {checker_index}"
                )
                mirror_checker = MovableChecker(
                    x_mirror_checker,
                    y_mirror_checker,
                    settings.checker_radius * 2,
                    mirror_checker_color,
                )

                self.addItem(checker)
                self.addItem(mirror_checker)


def _get_color(index: int) -> QColor:
    if index % 2 == 0:
        return QColor(settings.color_dark_triangle)

    return QColor(settings.color_light_triangle)

def _toggle_color(color: QColor) -> QColor:
    if color == QColor(settings.color_dark_triangle):
        return QColor(settings.color_light_triangle)

    return QColor(settings.color_dark_triangle)
