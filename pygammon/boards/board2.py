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
        color = color_dark_triangle if i % 2 == 0 else color_light_triangle
        point = QGraphicsPolygonItem(triangle)
        point.setBrush(color)
        scene.addItem(point)

        # Mirror the triangle for the other side of the board
        triangle_mirror = QPolygonF([
            QPointF(x_start, board_height if i % 2 == 0 else point_height),
            QPointF(x_start + point_width, board_height if i % 2 == 0 else point_height),
            QPointF(x_start + point_width / 2, point_height if i % 2 == 0 else board_height),
        ])
        point_mirror = QGraphicsPolygonItem(triangle_mirror)
        point_mirror.setBrush(color)
        scene.addItem(point_mirror)

    # Draw checkers (example positions)
    checker_radius = point_width * 0.4
    checker_positions = [
        (1, 1), (1, 2), (1, 3),  # First point has 3 checkers
        (6, 1),  # Sixth point has 1 checker
        (12, 1), (12, 2),  # Twelfth point has 2 checkers
    ]
    for point_index, checker_index in checker_positions:
        x_checker = point_index * point_width + point_width / 2 - checker_radius
        y_checker = checker_index * checker_radius * 2 if point_index <= 6 else board_height - (checker_index * checker_radius * 2)
        checker = QGraphicsEllipseItem(x_checker, y_checker, checker_radius * 2, checker_radius * 2)
        checker.setBrush(color_dark_checker)
        scene.addItem(checker)

    # Create and show view
    view = QGraphicsView(scene)
    view.setScene(scene)
    #view.setRenderHint(view.RenderHint.Antialiasing)
    view.setFixedSize(board_width + 20, board_height + 20)
    return view