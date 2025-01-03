from PySide6.QtWidgets import QMainWindow


class BackgammonWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Pygammon")
        self.resize(800, 400)  # Initial window size (resizable)


class BackgammonApp(QMainWindow):  # For loading an image
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