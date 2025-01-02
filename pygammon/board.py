from PIL import Image, ImageDraw
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPolygonF
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsView


def create_backgammon_board(save_path="backgammon_board.png"):
    # Dimensions
    board_width, board_height = 800, 400
    triangle_width, triangle_height = board_width // 12, board_height // 2

    # Create a blank image
    board = Image.new("RGB", (board_width, board_height), "saddlebrown")
    draw = ImageDraw.Draw(board)

    # Draw dividing line
    draw.line([(board_width // 2, 0), (board_width // 2, board_height)], fill="black", width=3)

    # Draw triangles (alternating colors)
    colors = ["white", "black"]
    for i in range(12):
        # Top triangles
        x1 = i * triangle_width
        x2 = x1 + triangle_width
        points = [(x1, 0), (x2, 0), ((x1 + x2) // 2, triangle_height)]
        draw.polygon(points, fill=colors[i % 2])

        # Bottom triangles
        points = [(x1, board_height), (x2, board_height), ((x1 + x2) // 2, board_height - triangle_height)]
        draw.polygon(points, fill=colors[i % 2])

    # Save the board as an image
    board.save(save_path)
    print(f"Backgammon board saved to {save_path}")


def create_backgammon_board2():
    # Board settings
    board_width = 800
    board_height = 400
    point_width = board_width / 14  # 12 points + gutters
    point_height = board_height / 2

    # Colors
    color_dark = QColor("#8B4513")  # Dark triangles
    color_light = QColor("#FFD700")  # Light triangles
    color_board = QColor("#D2B48C")  # Board background
    color_checker = QColor("#000000")  # Checker color

    # Create scene
    scene = QGraphicsScene()
    scene.setBackgroundBrush(color_board)
    scene.setSceneRect(0, 0, board_width, board_height)  # Scene size

    # Draw points (triangles)
    for i in range(12):  # 12 points on each side
        x_start = (i + 1) * point_width
        triangle = QPolygonF([
            QPointF(x_start, 0 if i % 2 == 0 else point_height),
            QPointF(x_start + point_width, 0 if i % 2 == 0 else point_height),
            QPointF(x_start + point_width / 2, point_height if i % 2 == 0 else 0),
        ])
        color = color_dark if i % 2 == 0 else color_light
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
        checker.setBrush(color_checker)
        scene.addItem(checker)

    # Create and show view
    view = QGraphicsView(scene)
    view.setScene(scene)
    #view.setRenderHint(view.RenderHint.Antialiasing)
    view.setFixedSize(board_width + 20, board_height + 20)
    #view.show()
    return view
