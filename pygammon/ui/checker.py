from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtGui import QBrush, QColor, QMouseEvent, QPen

from pygammon.conf import settings


class CheckerItem(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, color, point_index: int):
        super().__init__(x, y, radius, radius)
        self.point_index = point_index
        self.base_color = color
        self.setBrush(QBrush(color))
        self.setPen(QPen(color))

    def set_highlighted(self, highlighted: bool):
        if highlighted:
            self.setPen(QPen(QColor(settings.color_selected), 3))
        else:
            self.setPen(QPen(self.base_color))

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        scene = self.scene()
        if scene and hasattr(scene, "on_checker_clicked"):
            scene.on_checker_clicked(self.point_index)
