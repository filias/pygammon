from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtGui import QBrush, QMouseEvent


class MovableChecker(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, radius)
        self.setBrush(QBrush(color))
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)  # Enable movement
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable)  # Optional: Selectable
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)  # Update on move

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)  # Call parent method
        print(f"Checker clicked at: {self.scenePos()}")  # Debugging

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        print(f"Checker released at: {self.scenePos()}")
