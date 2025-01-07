from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPolygonF, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPolygonItem

from pygammon.checker import MovableChecker
from pygammon.conf import settings


# Initial position
INITIAL_POSITION = [
        (1, 1),
        (1, 2),
        (6, 1),
        (6, 2),
        (6, 3),
        (6, 4),
        (6, 5),
        (8, 1),
        (8, 2),
        (8, 3),
        (12, 1),
        (12, 2),
        (12, 3),
        (12, 4),
        (12, 5),
    ]

def create_backgammon_board() -> QGraphicsScene:
    scene = QGraphicsScene()
    scene.setBackgroundBrush(QColor(settings.color_board))
    scene.setSceneRect(0, 0, settings.board_width, settings.board_height)  # Scene size

    # Draw points (triangles)
    for i in range(12):  # 12 points on each side
        if i == 0:
            x_start = 0
        else:
            x_start = i * settings.point_width

        # Triangle points
        base_left = QPointF(x_start, 0)
        top_middle = QPointF(x_start + settings.point_width / 2, settings.point_height)
        base_right = QPointF(x_start + settings.point_width, 0)

        triangle = QPolygonF([
            base_left,
            top_middle,
            base_right,
        ])
        triangle_color = settings.color_dark_triangle if i % 2 == 0 else settings.color_light_triangle
        triangle_polygon = QGraphicsPolygonItem(triangle)

        # Line color
        pen = QPen(QColor(triangle_color))
        triangle_polygon.setPen(pen)

        # Filling color
        triangle_polygon.setBrush(QColor(triangle_color))

        scene.addItem(triangle_polygon)

        # Triangle mirror for the other side of the board and change color
        # Triangle points
        base_left = QPointF(x_start, settings.board_height)
        top_middle = QPointF(x_start + settings.point_width / 2, settings.board_height - settings.point_height)
        base_right = QPointF(x_start + settings.point_width, settings.board_height)

        triangle_mirror = QPolygonF([
            base_left,
            top_middle,
            base_right,
        ])
        triangle_polygon_mirror = QGraphicsPolygonItem(triangle_mirror)
        mirror_triangle_color = QColor(settings.color_light_triangle) if i % 2 == 0 else QColor(settings.color_dark_triangle)

        # Line color
        pen_mirror = QPen(QColor(mirror_triangle_color))
        triangle_polygon.setPen(pen_mirror)

        # Filling color
        triangle_polygon_mirror.setBrush(QColor(mirror_triangle_color))

        scene.addItem(triangle_polygon_mirror)

    return scene


def add_initial_position(scene: QGraphicsScene) -> QGraphicsScene:
    for point_index, checker_index in INITIAL_POSITION:
        print(f"Drawing checker at point {point_index} and checker {checker_index}")
        # Bottom checkers
        x_checker = (point_index - 1) * settings.point_width + settings.point_width / 2 - settings.checker_radius
        y_checker = settings.board_height - (checker_index * settings.checker_radius * 2)

        # Mirror checkers for the top side
        x_mirror_checker = (
            (point_index - 1) * settings.point_width + settings.point_width / 2 - settings.checker_radius
        )
        y_mirror_checker = checker_index * settings.checker_radius * 2 - settings.checker_radius * 2

        # Set the color
        if point_index in (1, 12):
            checker_color = QColor(settings.color_light_checker)
            mirror_checker_color = QColor(settings.color_dark_checker)
        else:
            checker_color = QColor(settings.color_dark_checker)
            mirror_checker_color = QColor(settings.color_light_checker)

        checker = MovableChecker(
            x_checker, y_checker, settings.checker_radius * 2, checker_color
        )
        mirror_checker = MovableChecker(
            x_mirror_checker, y_mirror_checker, settings.checker_radius * 2, mirror_checker_color
        )

        scene.addItem(checker)
        scene.addItem(mirror_checker)

    return scene
