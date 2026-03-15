import os

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from pygammon.logic.models import Color, Game
from pygammon.logic.game_engine import GameEngine, GamePhase
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
    controller.board_updated.connect(
        lambda: _on_board_updated(scene, game, window, controller)
    )
    controller.dice_rolled.connect(
        lambda d1, d2: _on_dice_rolled(scene, window, controller, d1, d2)
    )
    controller.turn_changed.connect(
        lambda name, color: _on_turn_changed(scene, window, controller, name, color)
    )
    controller.valid_moves_changed.connect(
        lambda moves: _on_valid_moves(scene, moves, controller)
    )
    controller.game_over.connect(
        lambda winner, points, desc: _on_game_over(window, winner, points, desc)
    )
    controller.no_moves_available.connect(
        lambda: window.dice_label.setText("No moves available!")
    )
    controller.turn_complete.connect(lambda: _on_turn_complete(window))
    controller.double_proposed.connect(
        lambda name: _on_double_proposed(window, controller, name)
    )
    controller.cube_updated.connect(
        lambda value, owner: scene.draw_cube(value, owner)
    )

    # Connect UI controls
    window.roll_button.clicked.connect(controller.on_roll_clicked)
    window.roll_button.setEnabled(True)
    window.undo_button.clicked.connect(controller.on_undo_clicked)
    window.confirm_button.clicked.connect(controller.on_confirm_clicked)
    window.double_button.clicked.connect(controller.on_double_clicked)

    controller.start_game()


def _on_board_updated(scene, game, window, controller):
    scene.refresh_board()
    window.update_off_counts(len(game.board.off_dark), len(game.board.off_light))
    window.undo_button.setEnabled(controller.engine.can_undo)
    window.confirm_button.setEnabled(
        controller.engine.phase == GamePhase.TURN_COMPLETE
    )
    window.double_button.setEnabled(controller.engine.can_double)


def _on_dice_rolled(scene, window, controller, d1, d2):
    window.update_dice_label(d1, d2)
    window.roll_button.setEnabled(False)
    window.double_button.setEnabled(False)
    scene.draw_dice(d1, d2, controller.engine.current_player.color)


def _on_turn_complete(window):
    window.confirm_button.setEnabled(True)


def _on_turn_changed(scene, window, controller, name, color):
    window.update_player_label(name, color)
    window.dice_label.setText("")
    window.roll_button.setEnabled(True)
    window.confirm_button.setEnabled(False)
    window.double_button.setEnabled(controller.engine.can_double)
    scene.clear_dice()


def _on_valid_moves(scene, moves, controller):
    if controller.selected_point is not None:
        scene.highlight_valid_destinations(moves)
    else:
        scene.highlight_valid_sources(moves)


def _on_game_over(window, winner, points, desc):
    window.roll_button.setEnabled(False)
    window.double_button.setEnabled(False)
    if desc == "forfeit":
        msg = f"{winner} wins by forfeit! ({points} point{'s' if points != 1 else ''})"
    else:
        msg = f"{winner} wins with a {desc}! ({points} point{'s' if points != 1 else ''})"
    QMessageBox.information(window, "Game Over", msg)


def _on_double_proposed(window, controller, proposer_name):
    # If AI proposed the double, show dialog for human to respond
    # If human proposed, AI responds automatically via controller
    if controller._is_ai_turn():
        # AI proposed — human must respond
        cube_value = controller.engine.cube.value
        new_value = cube_value * 2
        reply = QMessageBox.question(
            window,
            "Double Proposed",
            f"{proposer_name} proposes to double the stakes to {new_value}.\n\n"
            f"Accept or decline?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        controller.on_double_response(reply == QMessageBox.StandardButton.Yes)
    # else: human proposed, AI responds via controller._ai_respond_to_double


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
