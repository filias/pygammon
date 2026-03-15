"""Graphical dice items for the board scene."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsItemGroup, QGraphicsRectItem

from pygammon.conf import settings

# Pip positions for each die face, as (x_frac, y_frac) of die size
_PIP_POSITIONS = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
    6: [
        (0.25, 0.25), (0.75, 0.25),
        (0.25, 0.5), (0.75, 0.5),
        (0.25, 0.75), (0.75, 0.75),
    ],
}


class DieItem(QGraphicsItemGroup):
    """A single die graphic: rounded rectangle with pips."""

    def __init__(self, x, y, value, bg_color=None, pip_color=None, parent=None):
        super().__init__(parent)
        size = settings.die_size
        pip_radius = size * 0.09

        # Die body
        body = QGraphicsRectItem(x, y, size, size)
        body.setBrush(QBrush(QColor(bg_color or settings.color_die_bg)))
        body.setPen(QPen(QColor("#888888"), 1.5))
        self.addToGroup(body)

        # Pips
        pip_color = QColor(pip_color or settings.color_die_pip)
        for fx, fy in _PIP_POSITIONS.get(value, []):
            px = x + fx * size - pip_radius
            py = y + fy * size - pip_radius
            pip = QGraphicsEllipseItem(px, py, pip_radius * 2, pip_radius * 2)
            pip.setBrush(QBrush(pip_color))
            pip.setPen(QPen(pip_color))
            self.addToGroup(pip)

        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
