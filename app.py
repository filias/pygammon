from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from pygammon.logic.models import Color, Game
from pygammon.logic.game_engine import GameEngine, GamePhase
from pygammon.controller import GameController
from pygammon.ui.board import PygammonScene
from pygammon.ui.window import BackgammonWindow


# Global match state (persists across games in a match)
_match_state = {
    "scores": {Color.DARK: 0, Color.LIGHT: 0},
    "match_length": 0,
    "ai_player": None,
    "ai_color": None,
}


def create_game(window: BackgammonWindow, match_length=0, ai_player=None, ai_color=None,
                reset_scores=True):
    """Create and wire up a new game."""
    if reset_scores:
        _match_state["scores"] = {Color.DARK: 0, Color.LIGHT: 0}
    _match_state["match_length"] = match_length
    _match_state["ai_player"] = ai_player
    _match_state["ai_color"] = ai_color

    game = Game(match_length=match_length)
    game.scores = dict(_match_state["scores"])
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
        lambda name, color: _on_turn_changed(scene, window, controller, game, name, color)
    )
    controller.valid_moves_changed.connect(
        lambda moves: _on_valid_moves(scene, moves, controller)
    )
    controller.game_over.connect(
        lambda winner, points, desc: _on_game_over(window, game, winner, points, desc)
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

    # Disconnect old button signals before reconnecting
    for btn in [window.roll_button, window.undo_button, window.confirm_button,
                window.double_button]:
        try:
            btn.clicked.disconnect()
        except RuntimeError:
            pass

    # Connect UI controls
    window.roll_button.clicked.connect(controller.on_roll_clicked)
    window.roll_button.setEnabled(True)
    window.undo_button.clicked.connect(controller.on_undo_clicked)
    window.confirm_button.clicked.connect(controller.on_confirm_clicked)
    window.double_button.clicked.connect(controller.on_double_clicked)

    controller.start_game()
    _update_panel(scene, game, controller)


def _update_panel(scene, game, controller):
    scene.draw_panel(
        dark_name=game.player1.name,
        light_name=game.player2.name,
        dark_score=_match_state["scores"][Color.DARK],
        light_score=_match_state["scores"][Color.LIGHT],
        match_length=_match_state["match_length"],
        current_color=controller.engine.current_player.color,
    )


def _on_board_updated(scene, game, window, controller):
    scene.refresh_board()
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


def _on_turn_changed(scene, window, controller, game, name, color):
    window.update_player_label(name, color)
    window.dice_label.setText("")
    window.roll_button.setEnabled(True)
    window.confirm_button.setEnabled(False)
    window.double_button.setEnabled(controller.engine.can_double)
    scene.clear_dice()
    _update_panel(scene, game, controller)


def _on_valid_moves(scene, moves, controller):
    if controller.selected_point is not None:
        scene.highlight_valid_destinations(moves)
    else:
        scene.highlight_valid_sources(moves)


def _on_game_over(window, game, winner, points, desc):
    window.roll_button.setEnabled(False)
    window.double_button.setEnabled(False)

    # Update match scores
    winner_color = Color(winner)
    _match_state["scores"][winner_color] += points

    ml = _match_state["match_length"]

    if desc == "forfeit":
        msg = f"{winner} wins by forfeit! (+{points} pt{'s' if points != 1 else ''})"
    else:
        msg = f"{winner} wins with a {desc}! (+{points} pt{'s' if points != 1 else ''})"

    dark_s = _match_state["scores"][Color.DARK]
    light_s = _match_state["scores"][Color.LIGHT]
    msg += f"\n\nScore: Dark {dark_s} - Light {light_s}"

    # Check if match is won
    match_won = False
    if ml > 0:
        if dark_s >= ml:
            msg += f"\n\nDark wins the match to {ml}!"
            match_won = True
        elif light_s >= ml:
            msg += f"\n\nLight wins the match to {ml}!"
            match_won = True

    if match_won or ml == 0:
        QMessageBox.information(window, "Game Over", msg)
    else:
        reply = QMessageBox.information(
            window, "Game Over", msg + "\n\nStarting next game...",
        )
        # Start next game in the match
        create_game(
            window,
            match_length=ml,
            ai_player=_match_state["ai_player"],
            ai_color=_match_state["ai_color"],
            reset_scores=False,
        )


def _on_double_proposed(window, controller, proposer_name):
    if controller._is_ai_turn():
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


def _play_vs_ai(window):
    model_path, _ = QFileDialog.getOpenFileName(
        window, "Select AI Model Checkpoint", "checkpoints", "All Files (*)",
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
    for length, action in window.match_actions.items():
        action.triggered.connect(lambda checked=False, ml=length: create_game(window, match_length=ml))

    window.show()
    app.exec()
