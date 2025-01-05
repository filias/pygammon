from PySide6.QtWidgets import QApplication, QGraphicsView

from pygammon.boards.board2 import BOARD_WIDTH, BOARD_HEIGHT
from pygammon.boards.board2 import add_initial_position, create_backgammon_board
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
    view.setFixedSize(BOARD_WIDTH + 20, BOARD_HEIGHT + 20)
    window.setCentralWidget(view)

    window.show()
    app.exec()
