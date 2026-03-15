import os

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from pygammon.logic.models import Color, Game
from pygammon.logic.game_engine import GameEngine
from pygammon.controller import GameController
from pygammon.ui.board import PygammonScene
from pygammon.ui.window import BackgammonWindow


def create_game(window: BackgammonWindow, ai_player=None, ai_color=None):
    """Create and wire up a new game."""
    game = Game()
    engine = GameEngine(game)
    controller = GameController(engine, ai_player=ai_player, ai_color=ai_color)

    scene = PygammonScene(board=game.board, controller=controller)
    scene.draw_board()
    scene.draw_checkers()

    window.set_scene(scene)

    # Connect signals
    controller.board_updated.connect(lambda: _on_board_updated(scene, game, window, controller))
    controller.dice_rolled.connect(
        lambda d1, d2: (window.update_dice_label(d1, d2), window.roll_button.setEnabled(False))
    )
    controller.turn_changed.connect(
        lambda name, color: _on_turn_changed(window, name, color)
    )
    controller.valid_moves_changed.connect(
        lambda moves: _on_valid_moves(scene, moves, controller)
    )
    controller.game_over.connect(lambda winner: _on_game_over(window, winner))
    controller.no_moves_available.connect(
        lambda: window.dice_label.setText("No moves available!")
    )
    controller.turn_complete.connect(
        lambda: _on_turn_complete(window)
    )

    # Connect UI controls
    window.roll_button.clicked.connect(controller.on_roll_clicked)
    window.roll_button.setEnabled(True)
    window.undo_button.clicked.connect(controller.on_undo_clicked)
    window.confirm_button.clicked.connect(controller.on_confirm_clicked)

    controller.start_game()


def _on_board_updated(scene, game, window, controller):
    from pygammon.logic.game_engine import GamePhase

    scene.refresh_board()
    window.update_off_counts(len(game.board.off_dark), len(game.board.off_light))
    window.undo_button.setEnabled(controller.engine.can_undo)
    window.confirm_button.setEnabled(controller.engine.phase == GamePhase.TURN_COMPLETE)


def _on_turn_complete(window):
    window.confirm_button.setEnabled(True)


def _on_turn_changed(window, name, color):
    window.update_player_label(name, color)
    window.dice_label.setText("")
    window.roll_button.setEnabled(True)
    window.confirm_button.setEnabled(False)


def _on_valid_moves(scene, moves, controller):
    if controller.selected_point is not None:
        scene.highlight_valid_destinations(moves)
    else:
        scene.highlight_valid_sources(moves)


def _on_game_over(window, winner):
    window.roll_button.setEnabled(False)
    QMessageBox.information(window, "Game Over", f"{winner} wins!")


def _play_vs_ai(window):
    """Start a game against a trained AI model."""
    model_path, _ = QFileDialog.getOpenFileName(
        window,
        "Select AI Model Checkpoint",
        "checkpoints",
        "All Files (*)",
    )
    if not model_path:
        return

    try:
        from pygammon.ai.player import AIPlayer

        ai = AIPlayer(model_path)
        create_game(window, ai_player=ai, ai_color=Color.LIGHT)
    except Exception as e:
        QMessageBox.warning(window, "Error", f"Failed to load AI model:\n{e}")


if __name__ == "__main__":
    app = QApplication([])
    window = BackgammonWindow()

    create_game(window)

    # Menu actions
    window.new_game_action.triggered.connect(lambda: create_game(window))
    window.play_vs_ai_action.triggered.connect(lambda: _play_vs_ai(window))

    window.show()
    app.exec()
