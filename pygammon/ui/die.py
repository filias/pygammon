from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem

from pygammon.conf import settings

DIE_SIZE = 36
PIP_RADIUS = 4
CORNER_RADIUS = 5

# Pip positions as fractions of die size, for values 1-6
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


class DieGraphic(QGraphicsRectItem):
    def __init__(self, x: float, y: float, value: int):
        super().__init__(x, y, DIE_SIZE, DIE_SIZE)
        self.setBrush(QBrush(QColor(settings.color_die_bg)))
        self.setPen(QPen(QColor(settings.color_die_pip), 1))

        pip_color = QColor(settings.color_die_pip)
        for px, py in _PIP_POSITIONS[value]:
            cx = x + px * DIE_SIZE - PIP_RADIUS
            cy = y + py * DIE_SIZE - PIP_RADIUS
            pip = QGraphicsEllipseItem(
                cx, cy, PIP_RADIUS * 2, PIP_RADIUS * 2, self
            )
            pip.setBrush(QBrush(pip_color))
            pip.setPen(QPen(pip_color))
