from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class QMarketGraphicsScene(QGraphicsScene):
    def __init__(self, scene, parent = None):
        super().__init__(parent)
        self.scene = scene
        # Настройки окна
        self._color_background = QColor("#f2f2f2")
        self.setBackgroundBrush(self._color_background)
        #self.drawBackground()

    def setGraphScene(self, width, height):
        self.setSceneRect(-width//2, -height//2, width, height)

