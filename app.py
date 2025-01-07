from PySide6.QtWidgets import QApplication, QGraphicsView

from pygammon.boards.board2 import add_initial_position, create_backgammon_board
from pygammon.conf import settings
from pygammon.window import BackgammonWindow


if __name__ == "__main__":
    # Create the application
    app = QApplication([])
    window = BackgammonWindow()

    # Create a board and add the intial position
    scene = create_backgammon_board()
    scene = add_initial_position(scene)
    view = QGraphicsView(scene)
    view.setScene(scene)
    view.setFixedSize(settings.board_width + 20, settings.board_height + 20)
    window.setCentralWidget(view)

    window.show()
    app.exec()
