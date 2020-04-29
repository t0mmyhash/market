from constants import CUSTOMER_SIZE_X, CUSTOMER_SIZE_Y

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class QGraphicsCustomer(QGraphicsItem):
    """ Графическое изображение покупателя """
    def __init__(self, model, parent = None):
        super().__init__(parent)

        self.outline_width = 1.0
        self.pos_x = model.pos_x
        self.pos_y = model.pos_y

        self._color_background = QColor().fromRgb(QRandomGenerator.global_().generate())
        self._color_outline = QColor("#FF000000")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)

    def paint(self, painter, QStyleOptionGraphicsItem, widget = None):
        """ Отрисовка покупателя """
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawRect(self.pos_x, self.pos_y, CUSTOMER_SIZE_X, CUSTOMER_SIZE_Y)

    def boundingRect(self):
        """ Обновление каркасного прямоугольника"""
        return QRectF(self.pos_x, self.pos_y, CUSTOMER_SIZE_X, CUSTOMER_SIZE_Y)
