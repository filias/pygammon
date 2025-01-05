from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPolygonF, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPolygonItem, QGraphicsEllipseItem


# Board settings
BOARD_WIDTH = 800
BOARD_HEIGHT = BOARD_WIDTH * 10 / 14  # Calculated this with a square paper and based on a real board
POINT_WIDTH = BOARD_WIDTH / 14  # 12 points + gutters
POINT_HEIGHT = POINT_WIDTH * 4
CHECKER_RADIUS = POINT_WIDTH * 0.4

# Colors
COLOR_DARK_TRIANGLE = QColor("#3662cb")  # Dark triangles
COLOR_LIGHT_TRIANGLE = QColor("#618dd6")  # Light triangles
COLOR_BOARD = QColor("#3e72d8")  # Board background
COLOR_DARK_CHECKER = QColor("#2e2da2")  # Dark checker color
COLOR_LIGHT_CHECKER = QColor("#d2d8f2")  # Light checker color

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
    scene.setBackgroundBrush(COLOR_BOARD)
    scene.setSceneRect(0, 0, BOARD_WIDTH, BOARD_HEIGHT)  # Scene size

    # Draw points (triangles)
    for i in range(12):  # 12 points on each side
        if i == 0:
            x_start = 0
        else:
            x_start = i * POINT_WIDTH

        # Triangle points
        base_left = QPointF(x_start, 0)
        top_middle = QPointF(x_start + POINT_WIDTH / 2, POINT_HEIGHT)
        base_right = QPointF(x_start + POINT_WIDTH, 0)

        triangle = QPolygonF([
            base_left,
            top_middle,
            base_right,
        ])
        triangle_color = COLOR_DARK_TRIANGLE if i % 2 == 0 else COLOR_LIGHT_TRIANGLE
        triangle_polygon = QGraphicsPolygonItem(triangle)

        # Line color
        pen = QPen(triangle_color)
        triangle_polygon.setPen(pen)

        # Filling color
        triangle_polygon.setBrush(triangle_color)

        scene.addItem(triangle_polygon)

        # Triangle mirror for the other side of the board and change color
        # Triangle points
        base_left = QPointF(x_start, BOARD_HEIGHT)
        top_middle = QPointF(x_start + POINT_WIDTH / 2, BOARD_HEIGHT - POINT_HEIGHT)
        base_right = QPointF(x_start + POINT_WIDTH, BOARD_HEIGHT)

        triangle_mirror = QPolygonF([
            base_left,
            top_middle,
            base_right,
        ])
        triangle_polygon_mirror = QGraphicsPolygonItem(triangle_mirror)
        mirror_triangle_color = COLOR_LIGHT_TRIANGLE if i % 2 == 0 else COLOR_DARK_TRIANGLE

        # Line color
        pen_mirror = QPen(mirror_triangle_color)
        triangle_polygon.setPen(pen_mirror)

        # Filling color
        triangle_polygon_mirror.setBrush(mirror_triangle_color)

        scene.addItem(triangle_polygon_mirror)

    return scene


def add_initial_position(scene: QGraphicsScene) -> QGraphicsScene:
    for point_index, checker_index in INITIAL_POSITION:
        # Bottom checkers
        x_checker = (point_index - 1) * POINT_WIDTH + POINT_WIDTH / 2 - CHECKER_RADIUS
        y_checker = BOARD_HEIGHT - (checker_index * CHECKER_RADIUS * 2)

        # Mirror checkers for the top side
        x_mirror_checker = (
            (point_index - 1) * POINT_WIDTH + POINT_WIDTH / 2 - CHECKER_RADIUS
        )
        y_mirror_checker = checker_index * CHECKER_RADIUS * 2 - CHECKER_RADIUS * 2

        checker = QGraphicsEllipseItem(
            x_checker, y_checker, CHECKER_RADIUS * 2, CHECKER_RADIUS * 2
        )
        mirror_checker = QGraphicsEllipseItem(
            x_mirror_checker, y_mirror_checker, CHECKER_RADIUS * 2, CHECKER_RADIUS * 2
        )

        # Set the color
        if point_index in (1, 12):
            checker.setBrush(COLOR_LIGHT_CHECKER)
            mirror_checker.setBrush(COLOR_DARK_CHECKER)
        else:
            checker.setBrush(COLOR_DARK_CHECKER)
            mirror_checker.setBrush(COLOR_LIGHT_CHECKER)

        scene.addItem(checker)
        scene.addItem(mirror_checker)

        return scene
