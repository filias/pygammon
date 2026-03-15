from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
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

        self.off_dark_label = QLabel("Dark off: 0")
        self.off_light_label = QLabel("Light off: 0")
        info_bar.addWidget(self.off_dark_label)
        info_bar.addWidget(self.off_light_label)

        self.main_layout.addLayout(info_bar)

        # Board view placeholder (set by set_scene)
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

        controls.addStretch()
        self.main_layout.addLayout(controls)

        # Menu bar
        menu_bar = self.menuBar()
        game_menu = menu_bar.addMenu("Game")
        self.new_game_action = game_menu.addAction("New Game")
        self.play_vs_ai_action = game_menu.addAction("Play vs AI")

    def set_scene(self, scene):
        if self.view:
            self.main_layout.removeWidget(self.view)
            self.view.deleteLater()
        self.view = QGraphicsView(scene)
        self.view.setFixedSize(settings.board_width + 20, settings.board_height + 20)
        # Insert before the controls layout (index 1, after info bar)
        self.main_layout.insertWidget(1, self.view)
        self.resize(settings.board_width + 40, settings.board_height + 120)

    def update_player_label(self, name: str, color: str):
        self.current_player_label.setText(f"Current: {name} ({color})")

    def update_dice_label(self, die1: int, die2: int):
        self.dice_label.setText(f"Dice: {die1}, {die2}")

    def update_off_counts(self, dark_off: int, light_off: int):
        self.off_dark_label.setText(f"Dark off: {dark_off}")
        self.off_light_label.setText(f"Light off: {light_off}")
