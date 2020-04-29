from constants import CUSTOMER_QUEUE_INTERVAL, BOX_OFFICE_WIDTH, BOX_OFFICE_HEIGHT, ZERO_POS_Y, \
                      END_POS_Y, DEBUG_MODE, CUSTOMER_SIZE_X

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Box_Office():
    def __init__(self, modeling, cur_pos):
        # Добавление кассы в модель
        self.queue = []
        self.pos = cur_pos
        modeling.super_market.box_offices.append(self)

        # Отображение кассы
        self.model = QGraphicsRectItem(cur_pos, ZERO_POS_Y, BOX_OFFICE_WIDTH, BOX_OFFICE_HEIGHT)
        self.model.setBrush(QColor().fromRgb(QRandomGenerator.global_().generate()))
        modeling.view.grScene.addItem(self.model)

    def queueStep(self, modeling):
        """
        Смещает очередь при выходе первого покупателя из магазина
        :param modeling: текущая модель
        :return:
        """
        if len(self.queue) != 0:
            # Оформляем выход
            leaving_customer = self.queue[0]
            time_for_leaving = int(1000 * modeling.time_factor)
            leaving_timer = QTimeLine(time_for_leaving) # Таймер выхода
            modeling.stop_button.clicked.connect(lambda: leaving_timer.stop()) # остоновка по кнопке
            leaving_customer.hpos = END_POS_Y
            leaving_timer.valueChanged.connect(leaving_customer.animateMove)
            leaving_timer.finished.connect(lambda: modeling.view.grScene.removeItem(leaving_customer.model))
            leaving_timer.start()
            del self.queue[0] # Убираем из очереди

            # Меняем позиции в очереди
            for current_customer in self.queue:
                current_customer.average_time_count(modeling)
                modeling.stop_button.clicked.connect(lambda: current_customer.move_timer.stop())
                if not current_customer.stop_flag:
                    if DEBUG_MODE: print("--- Else case: just default move to another pos.")
                    last_customer = current_customer.hpos
                    current_customer.hpos = last_customer - (CUSTOMER_SIZE_X + CUSTOMER_QUEUE_INTERVAL)
                    if DEBUG_MODE: print("---- last_t:", last_customer, "current_customer:", current_customer.hpos)
                    current_customer.initMove(modeling)
                else:
                    if DEBUG_MODE: print("--- Case of changing pos in queue while stopped.")
                    current_customer.hpos -= (CUSTOMER_SIZE_X + CUSTOMER_QUEUE_INTERVAL)
                    current_customer.initMove(modeling)

