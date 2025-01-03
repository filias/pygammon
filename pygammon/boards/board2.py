from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPolygonF
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsView


def create_backgammon_board():
    # Board settings
    board_width = 800
    board_height = board_width * 10 / 14  # Calculated this with a square paper and based on a real board
    point_width = board_width / 14  # 12 points + gutters
    point_height = point_width * 4

    # Colors
    color_dark_triangle = QColor("#3662cb")  # Dark triangles
    color_light_triangle = QColor("#618dd6")  # Light triangles
    color_board = QColor("#3e72d8")  # Board background
    color_dark_checker = QColor("#2e2da2")  # Dark checker color
    color_light_checker = QColor("#d2d8f2")  # Light checker color

    # Create scene
    scene = QGraphicsScene()
    scene.setBackgroundBrush(color_board)
    scene.setSceneRect(0, 0, board_width, board_height)  # Scene size

    # Draw points (triangles)
    for i in range(12):  # 12 points on each side
        if i == 0:
            x_start = 0
        else:
            x_start = i * point_width

        # Triangle points
        base_left = QPointF(x_start, 0)
        top_middle = QPointF(x_start + point_width / 2, point_height)
        base_right = QPointF(x_start + point_width, 0)

        triangle = QPolygonF([
            base_left,
            top_middle,
            base_right,
        ])
        triangle_color = color_dark_triangle if i % 2 == 0 else color_light_triangle
        point = QGraphicsPolygonItem(triangle)
        point.setBrush(triangle_color)
        scene.addItem(point)

        # Triangle mirror for the other side of the board and change color
        # Triangle points
        base_left = QPointF(x_start, board_height)
        top_middle = QPointF(x_start + point_width / 2, board_height - point_height)
        base_right = QPointF(x_start + point_width, board_height)

        triangle_mirror = QPolygonF([
            base_left,
            top_middle,
            base_right,
        ])
        point_mirror = QGraphicsPolygonItem(triangle_mirror)
        mirror_triangle_color = color_light_triangle if i % 2 == 0 else color_dark_triangle
        point_mirror.setBrush(mirror_triangle_color)
        scene.addItem(point_mirror)

    # Draw checkers (example positions)
    checker_radius = point_width * 0.4
    checker_positions = [
        (1, 1), (1, 2),
        (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
        (8, 1), (8, 2), (8, 3),
        (12, 1), (12, 2), (12, 3), (12, 4), (12, 5),
        (13, 1), (13, 2), (13, 3), (13, 4), (13, 5),
        (17, 1), (17, 2), (17, 3),
        (19, 1), (19, 2), (19, 3), (19, 4), (19, 5),
        (24, 1), (24, 2),
    ]
    for point_index, checker_index in checker_positions:
        # Bottom checkers
        if point_index <= 12:
            x_checker = (point_index - 1)  * point_width + point_width / 2 - checker_radius
            y_checker = board_height - (checker_index * checker_radius * 2)
        else:  # Top checkers
            x_checker = board_height + point_index * point_width + point_width / 2 + checker_radius
            y_checker = (
                checker_index * checker_radius * 2
                if point_index <= 6
                else board_height - (checker_index * checker_radius * 2)
            )

        checker = QGraphicsEllipseItem(x_checker, y_checker, checker_radius * 2, checker_radius * 2)

        # Set the color
        if point_index in (1, 12, 17, 19):
            checker.setBrush(color_light_checker)
        else:
            checker.setBrush(color_dark_checker)

        scene.addItem(checker)

    # Create and show view
    view = QGraphicsView(scene)
    view.setScene(scene)
    view.setFixedSize(board_width + 20, board_height + 20)
    return view
