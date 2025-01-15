from PySide6.QtWidgets import QApplication, QGraphicsView

from pygammon.game import Game
from pygammon.boards.board2 import PygammonScene
from pygammon.conf import settings
from pygammon.window import BackgammonWindow


if __name__ == "__main__":
    # Create the application
    app = QApplication([])
    window = BackgammonWindow()

    # Create a Game
    game = Game()

    # Create the scene based on the board in the game
    bg_scene = PygammonScene(board=game.board)
    bg_scene.draw_board()
    bg_scene.draw_checkers()

    view = QGraphicsView(bg_scene)
    view.setScene(bg_scene)
    view.setFixedSize(settings.board_width + 20, settings.board_height + 20)
    window.setCentralWidget(view)

    window.show()
    app.exec()
