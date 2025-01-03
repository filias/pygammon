from PySide6.QtWidgets import QApplication

from pygammon.boards.board2 import create_backgammon_board
from pygammon.window import BackgammonWindow


if __name__ == "__main__":
    # Create the application
    app = QApplication([])
    window = BackgammonWindow()

    # For board 2
    view = create_backgammon_board()
    window.setCentralWidget(view)

    window.show()
    app.exec()
