from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pygammon.conf import settings


class BackgammonWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pygammon")

        # Central widget with layout
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)

        # Top info bar
        info_bar = QHBoxLayout()
        self.current_player_label = QLabel("Press New Game to start")
        self.current_player_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        info_bar.addWidget(self.current_player_label)

        self.dice_label = QLabel("")
        self.dice_label.setStyleSheet("font-size: 16px;")
        info_bar.addWidget(self.dice_label)

        info_bar.addStretch()
        self.main_layout.addLayout(info_bar)

        # Board view placeholder
        self.view = None

        # Bottom controls
        controls = QHBoxLayout()
        self.roll_button = QPushButton("Roll Dice")
        self.roll_button.setStyleSheet("font-size: 14px; padding: 8px 16px;")
        self.roll_button.setEnabled(False)
        controls.addWidget(self.roll_button)

        self.undo_button = QPushButton("Undo")
        self.undo_button.setStyleSheet("font-size: 14px; padding: 8px 16px;")
        self.undo_button.setEnabled(False)
        controls.addWidget(self.undo_button)

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setStyleSheet("font-size: 14px; padding: 8px 16px;")
        self.confirm_button.setEnabled(False)
        controls.addWidget(self.confirm_button)

        controls.addStretch()

        self.double_button = QPushButton("Double")
        self.double_button.setStyleSheet("font-size: 14px; padding: 8px 16px;")
        self.double_button.setEnabled(False)
        controls.addWidget(self.double_button)
        self.main_layout.addLayout(controls)

        # Menu bar
        menu_bar = self.menuBar()
        game_menu = menu_bar.addMenu("Game")
        self.new_game_action = game_menu.addAction("New Game (unlimited)")
        self.play_vs_ai_action = game_menu.addAction("Play vs AI")
        match_menu = menu_bar.addMenu("Match")
        self.match_actions = {}
        for length in [3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:
            action = match_menu.addAction(f"Match to {length}")
            self.match_actions[length] = action

    def set_scene(self, scene):
        if self.view:
            self.main_layout.removeWidget(self.view)
            self.view.deleteLater()
        self.view = QGraphicsView(scene)
        self.view.setFixedSize(settings.board_width + 20, settings.board_height + 20)
        self.main_layout.insertWidget(1, self.view)
        self.resize(settings.board_width + 40, settings.board_height + 120)

    def update_player_label(self, name: str, color: str):
        self.current_player_label.setText(f"Current: {name} ({color})")

    def update_dice_label(self, die1: int, die2: int):
        self.dice_label.setText(f"Dice: {die1}, {die2}")
