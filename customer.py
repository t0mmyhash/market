from customer_graphics import QGraphicsCustomer
from constants import CUSTOMER_QUEUE_INTERVAL, X_INTERVAL_FROM_BOX_OFFICE, ZERO_POS_Y, \
                      CUSTOMER_SIZE_X, PRE_BUY_TIME, CUSTOMER_ANIMATION_TIME, DEBUG_MODE

from PyQt5.QtCore import *
import random

class Customer():
    def __init__(self, modeling):
        self.pos_x = 0
        self.pos_y = 0
        self.modeling = modeling
        self.stop_flag = False
        self.speed = int(modeling.step_len / 10) # Скорость перемещения
        self.reach_flag = True
        self.time_waiting = 0
        self.model = QGraphicsCustomer(self) # Графика для покупателя

        self.check = random.choice(range(modeling.min_check_val, modeling.max_check_val, 1)) # выбор суммы покупок
        self.time_service = random.choice(range(modeling.min_time_buy, modeling.max_time_buy, 1)) # выбор времени обслуживания
        self.buy_time = self.time_service * 1000
        self.time_in_queue_with_service = self.buy_time + PRE_BUY_TIME # время у кассы

        self.__chooseBoxOffice(modeling)

    def __chooseBoxOffice(self, modeling):
        """
        Выбор кассы.
        :param modeling: текущая модель.
        :return:
        """
        if not modeling.super_market.box_offices:
            self.lostCustomer(modeling)
            return
        offices_list = modeling.super_market.box_offices
        min_queue = len(offices_list[0].queue)
        min_ind = 0
        for key in range(len(offices_list)): # Выбор минимальной очереди
            if min_queue > len(offices_list[key].queue):
                min_queue = len(offices_list[key].queue)
                min_ind = key
        if min_queue >= modeling.max_queue: # Если не влезает -- отправляется в потерянных
            self.lostCustomer(modeling)
            return
        else:
            target = offices_list[min_ind]
            self.hpos = len(target.queue) * (CUSTOMER_SIZE_X + CUSTOMER_QUEUE_INTERVAL) + ZERO_POS_Y
            self.pos_x = target.pos + X_INTERVAL_FROM_BOX_OFFICE

            self.office = target
            self.__customerAppearance(modeling) # Размещение покупателя на сцене

    def setPos(self, x, y):
        self.model.setPos(x, y)

    def __customerAppearance(self, modeling):
        """ Анимация покупателя и изменениие некоторых статистических полей модели"""

        self.model.setPos(self.pos_x, self.pos_y) # Установка позиции
        move_time = int(CUSTOMER_ANIMATION_TIME * modeling.time_factor)
        self.move_timer = QTimeLine(move_time)
        modeling.stop_button.clicked.connect(lambda: self.move_timer.stop())

        modeling.view.grScene.addItem(self.model) # Появление на сцене

        active_customers = 1
        customer_list = modeling.super_market.box_offices
        for key in range(len(customer_list)): # Выисление времени до кассы для этого покупателя, также вычисляется среднее колиество людей в очередях
            active_customers += len(customer_list[key].queue)
            for iter in range(len(customer_list[key].queue)):
                self.time_waiting += customer_list[key].queue[iter].time_in_queue_with_service
        active_customers = int(active_customers * 100 / len(customer_list)) / 100

        modeling.box_office_average_occupancy.clear()
        modeling.box_office_average_occupancy.insertPlainText(str(active_customers)) # Средняя занятость касс

        self.office.queue.append(self) # Добавление в оччередь
        self.average_time_count(modeling) # Вычисление среднего времени в очередях
        self.move_timer.valueChanged.connect(self.animateMove)
        self.move_timer.start()

    def initMove(self, modeling):
        """ Перемещение в очереди """
        self.move_timer.stop()
        self.move_timer = QTimeLine(CUSTOMER_ANIMATION_TIME)
        modeling.stop_button.clicked.connect(self.move_timer.stop)
        self.move_timer.valueChanged.connect(self.animateMove)
        self.stop_flag = False
        self.move_timer.start()

    def animateMove(self):
        """ Анимация движения покупателя"""
        if (self.pos_y > self.hpos + self.speed): # Идет со скоростью шага модели до определенной точки
            self.pos_y -= self.speed
            if DEBUG_MODE: print(self.model.pos().y())
            self.model.setPos(self.pos_x, self.pos_y)
            self.model.update()
        elif (self.pos_y > self.hpos + 1) and (self.reach_flag == True): # Доходит до места спокойно
            self.pos_y -= 1
            if DEBUG_MODE: print(self.model.pos().y())
            self.model.setPos(self.pos_x, self.pos_y)
            self.model.update()
        elif (self.pos_y <= -99 + self.speed) and (self.reach_flag == True): # Перемещение на первую позицию в очереди
                self.model.setPos(self.pos_x, -100)
                self.model.update()
                self.__purchase(self.modeling)
                self.reach_flag = False
        else :
            self.stop_flag = True


    def lostCustomer(self, modeling):
        """ Обработка потерянных покупателей """
        self.pos_x = 0
        self.model.setPos(self.pos_x, 200)
        lost_customer_time = int(CUSTOMER_ANIMATION_TIME * modeling.time_factor)
        self.lost_timer = QTimeLine(lost_customer_time)
        modeling.stop_button.clicked.connect(lambda: self.lost_timer.stop())
        self.lost_timer.start()
        self.customerLostEnd(modeling)

    def changeText(self, text_edit, val_to_add):
        """ Добавление числа к значению поля"""
        num = int(text_edit.toPlainText())
        text_edit.clear()
        text_edit.insertPlainText(str(num + val_to_add))

    def customerLostEnd(self, modeling):
        """ Изменение счетчика"""
        self.changeText(modeling.lost_customers_text, 1)

    def __purchase(self, modeling):
        """ Процесс покупок """
        if DEBUG_MODE: print("service:", self.buy_time / 1000)
        purchase_time = int(self.buy_time * modeling.time_factor)
        self.purchase_timer = QTimeLine(purchase_time)
        modeling.stop_button.clicked.connect(lambda: self.purchase_timer.stop())
        self.purchase_timer.finished.connect(lambda: self.purchaseSuccess(modeling))
        self.purchase_timer.start()

    def average_time_count(self, modeling):
        """ Вычисление среднего времени ожиданиия в очереди """
        average_time_in_queue = 0
        customer_list = modeling.super_market.box_offices
        for key in range(len(customer_list)):
            time_in_queues = 0
            for cust in range(len(customer_list[key].queue)):
                time_in_queues += customer_list[key].queue[cust].time_waiting
            average_time_in_queue = int((time_in_queues) / ((len(customer_list[key].queue) if len(customer_list[key].queue) > 0 else 1) * 10)) / 100
        if DEBUG_MODE: print(len(customer_list), average_time_in_queue)
        average_time_in_queue = int((average_time_in_queue) * 100 / (len(customer_list) )) / 100
        if DEBUG_MODE: print("``````time in queue: ", average_time_in_queue)
        modeling.queue_length_average_time.clear()
        modeling.queue_length_average_time.insertPlainText(str(average_time_in_queue) + " мин.")

    def purchaseSuccess(self, modeling):
        """ Обработка уходящего покупателя, изменение среднего чека и общей выручки """
        self.office.queueStep(modeling)

        self.changeText(modeling.serviced_customers_text, 1)

        new_profit = self.check * (1 - modeling.sale_percent / 100)
        modeling.profit = int((modeling.profit + new_profit) * 100) / 100
        modeling.profit_text.clear()
        modeling.profit_text.insertPlainText(str(modeling.profit)+" руб.")

        average_check = int(modeling.profit / int(modeling.serviced_customers_text.toPlainText()) * 10) / 10
        modeling.sold_average.clear()
        modeling.sold_average.insertPlainText(str(average_check)+' руб.')



