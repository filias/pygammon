from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from pygammon.board import create_backgammon_board


class BackgammonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Backgammon Board")
        self.setGeometry(100, 100, 800, 400)

        # Load the backgammon board image
        pixmap = QPixmap("backgammon_board.png")

        # Display the image in a QLabel
        label = QLabel(self)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)


if __name__ == "__main__":
    # Create the application
    app = QApplication([])

    # For board 1
    create_backgammon_board()
    window = BackgammonApp()
    window.show()

    # For board 2
    # view = create_backgammon_board2()
    # view.show()

    app.exec()
