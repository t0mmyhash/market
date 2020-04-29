from market_scene import Scene, Market
from market_view import QMarketGraphicsView
from box_office import Box_Office
from customer import Customer
from constants import AD_NUM, BOX_OFFICE_INTERVAL, DAYS, START_BOX_OFFICE_POS_X, START_TIME_STAMP, DEBUG_MODE

import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import  *

class SuperWindow(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.styleSheet_filename = 'qss/style.qss'
        self.__loadStylesheet(self.styleSheet_filename)
        self.__initUI()

    def __initUI(self):
        """ Инициализация интерфейса она моделирования """
        # Начальные настройки окна
        self.setGeometry(250, 200, 800, 500)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setWindowTitle("PYATYOROCHKA")

        # Сетап сцены
        self.scene = Scene()

        # Сетап элементов управления моделированием
        param_box = self.__parametersViewSetup()
        res_box   = self.__statisticsViewSetup()
        hbox = QHBoxLayout(self)

        self.view = QMarketGraphicsView(self.scene.grScene, self)

        vertical_split = QSplitter(Qt.Horizontal)
        vertical_split.addWidget(self.view)
        vertical_split.addWidget(param_box)
        vertical_split.setSizes([600, 100])
        hbox.addWidget(vertical_split)

        horizontal_split = QSplitter(Qt.Vertical)
        horizontal_split.addWidget(vertical_split)
        horizontal_split.addWidget(res_box)
        horizontal_split.setSizes([1000, 200])
        hbox.addWidget(horizontal_split)
        self.setLayout(hbox)

        self.show()

    def __loadStylesheet(self, filename):
        """ Загрузка стилей элементов управления из файла """
        print('styles loaded: ', filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))

    def __parametersViewSetup(self):
        """
        Установки раздела параметров;
        :return: фрейм разметки.
        """
        frame = QFrame()
        vbox = QVBoxLayout()
        vbox.setSpacing(20)

        # Шаг
        step_tuple = self.__comboBoxSetup("Шаг : ", 10, 70, 10, 0)
        step_box, self.step_combo = step_tuple

        # Кассы
        boxes_tuple = self.__comboBoxSetup("Количество касс : ", 1, 8, 1, 0)
        box_office_frame, self.box_office_combo = boxes_tuple

        # Максимально допустимая длина очереди
        queue_tuple = self.__comboBoxSetup("Максимальная очередь : ", 5, 8, 1, 2)
        max_queue_box, self.queue_combo = queue_tuple

        # Скидка
        sale_tuple = self.__singleEditLineSetup("Процент скидки : ", 1)
        sale_percent, self.sale_per = sale_tuple

        # Реклама
        self.ads_check = QCheckBox('Реклама (7 тысяч рублей)', self)

        # Промежуток появления нового покупателя
        req_tuple = self.__rangeEditLineSetup("Промежуток : ", "мин.", 0, 7)
        need_freq_range, self.min_customer_frequency, self.max_customer_frequency = req_tuple

        # Промежуток обслуживания клиента
        service_time_tuple = self.__rangeEditLineSetup("Обслуживание : ", "мин.", 1, 7)
        service_time_range, self.min_service_time, self.max_service_time = service_time_tuple

        # Промежуток для чека
        check_tuple = self.__rangeEditLineSetup("Чек : ", "руб.", 30, 9000)
        check_range, self.min_check, self.max_check = check_tuple

        # Добавление элементов в основную разметку
        vbox.addLayout(step_box)
        vbox.addLayout(box_office_frame)
        vbox.addLayout(max_queue_box)
        vbox.addLayout(sale_percent)
        vbox.addWidget(self.ads_check)
        vbox.addLayout(check_range)
        vbox.addLayout(need_freq_range)
        vbox.addLayout(service_time_range)

        # Кнопки
        control_buttons = self.__controlButtonSetup()

        vbox.addLayout(control_buttons)
        frame.setLayout(vbox)
        return frame

    def __statisticsViewSetup(self):
        """
        Установки раздела статистики;
        :return: фрейм разметки.
        """
        frame = QFrame()
        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        hbox = QHBoxLayout()
        hbox.addStretch(1)

        # Нижняя строка
        customers_box = QHBoxLayout()
        customers_box.addStretch(1)

        # Обслуженные покупатели
        serve_lbl = QLabel('Количество обслуженных покупателей : ')
        customers_box.addWidget(serve_lbl)
        self.serviced_customers_text = QTextEdit(self)
        self.serviced_customers_text.setFixedHeight(30)
        self.serviced_customers_text.setFixedWidth(60)
        self.serviced_customers_text.setReadOnly(True)
        self.serviced_customers_text.setPlainText('0')
        customers_box.addWidget(self.serviced_customers_text)

        # Потерянные покупатели
        pass_lbl = QLabel('Покупателей потеряно : ')
        customers_box.addWidget(pass_lbl)
        self.lost_customers_text = QTextEdit(self)
        self.lost_customers_text.setFixedHeight(30)
        self.lost_customers_text.setFixedWidth(60)
        self.lost_customers_text.setReadOnly(True)
        self.lost_customers_text.setPlainText('0')
        customers_box.addWidget(self.lost_customers_text)

        # Верхняя строка
        grid = QHBoxLayout()
        grid.addStretch(5)

        # Средний чек
        sold_lbl = QLabel("Средний чек : ")
        grid.addWidget(sold_lbl)
        self.sold_average = QTextEdit(self)
        self.sold_average.setFixedHeight(30)
        self.sold_average.setFixedWidth(100)
        self.sold_average.setReadOnly(True)
        self.sold_average.setPlainText('0 руб.')
        grid.addWidget(self.sold_average)

        # Среднее время ожидания
        queue_length_average_time = QLabel("Среднее время ожидания в очереди : ")
        grid.addWidget(queue_length_average_time)
        self.queue_length_average_time = QTextEdit(self)
        self.queue_length_average_time.setFixedHeight(30)
        self.queue_length_average_time.setFixedWidth(100)
        self.queue_length_average_time.setReadOnly(True)
        self.queue_length_average_time.setPlainText('0.0 мин.')
        grid.addWidget(self.queue_length_average_time)

        # Средняя занятость касс
        box_offices_average = QLabel("Средняя занятость касс : ")
        grid.addWidget(box_offices_average)
        self.box_office_average_occupancy = QTextEdit(self)
        self.box_office_average_occupancy.setFixedHeight(30)
        self.box_office_average_occupancy.setFixedWidth(100)
        self.box_office_average_occupancy.setReadOnly(True)
        self.box_office_average_occupancy.setPlainText('0')
        grid.addWidget(self.box_office_average_occupancy)

        # Текущее время в магазине
        self.time_stamp = QLabel(START_TIME_STAMP)
        grid.addWidget(self.time_stamp)
        hbox.addLayout(grid)
        vbox.addLayout(hbox)

        # Выручка
        prof_lbl = QLabel('Общая выручка : ')
        customers_box.addWidget(prof_lbl)
        self.profit_text = QTextEdit(self)
        self.profit_text.setFixedHeight(30)
        self.profit_text.setFixedWidth(150)
        self.profit_text.setReadOnly(True)
        self.profit_text.setPlainText('0 руб.')
        self.profit = 0
        customers_box.addWidget(self.profit_text)

        vbox.addLayout(customers_box)
        frame.setLayout(vbox)
        return frame

    def __comboBoxSetup(self, label_title, min_val, max_val, step, def_val):
        """
        Установки строчки выпадающего списка.
        :param label_title: название выпадающего списка, размещается слева;
        :param min_val: минимальное значение списка;
        :param max_val: максимальное значение списка;
        :param step: шаг;
        :param def_val: значение, которое будет установлено списку по умолчанию;
        :return: фрейм с расстановкой, сам комбобокс.
        """
        hbox = QHBoxLayout()
        label = QLabel(label_title)
        hbox.addWidget(label)
        combo_box = QComboBox()
        for val in range(min_val, max_val, step):
            combo_box.addItem(str(val))
        combo_box.setCurrentIndex(def_val)
        hbox.addWidget(combo_box)
        return hbox, combo_box

    def __rangeEditLineSetup(self, label_title, measure, min_def, max_def):
        """
        Установки строчки отрезка с изменяемыми значениями полей
        :param label_title: названиие полей, размещается слева;
        :param measure: единица измерения;
        :param min_def: значение по умолчанию, размещаемое в поле "минимум";
        :param max_def: значение по умолчанию, размещаемое в поле "максимум"
        :return: фрейм с расстановкой, два поля.
        """
        hbox = QHBoxLayout()
        hbox.setSpacing(5)
        cur_lbl = QLabel(label_title)
        from_lbl = QLabel("от")
        from_text = QLineEdit()
        from_text.setText(str(min_def))
        to_lbl = QLabel("до")
        to_text = QLineEdit()
        to_text.setText(str(max_def))
        measure_lbl2 = QLabel(measure)

        hbox.addWidget(cur_lbl)
        hbox.addWidget(from_lbl)
        hbox.addWidget(from_text)
        hbox.addWidget(to_lbl)
        hbox.addWidget(to_text)
        hbox.addWidget(measure_lbl2)

        return hbox, from_text, to_text

    def __singleEditLineSetup(self, label_title, def_val):
        """
        Установки строчкии с одним полем редактирования.
        :param label_title: название поля, размещается слева;
        :param def_val: значениия поля по умолчанию;
        :return: фрейм с расстановкой, поле.
        """
        hbox = QHBoxLayout()
        hbox.setSpacing(5)
        cur_lbl = QLabel(label_title)
        equ_text = QLineEdit(str(def_val))
        hbox.addWidget(cur_lbl)
        hbox.addWidget(equ_text)
        return hbox, equ_text

    def __controlButtonSetup(self):
        """
        Кнопки управлениия.
        :return: фрейм разметки
        """
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        self.draw_button = QPushButton("Показать", self)
        self.draw_button.setFixedHeight(60)
        self.draw_button.clicked.connect(lambda : self.__layoutSetup())

        self.start_button = QPushButton("Старт", self)
        self.start_button.clicked.connect(lambda: self.startProcess())
        self.start_button.setEnabled(False)

        self.stop_button = QPushButton("Стоп", self)
        self.stop_button.setEnabled(False)

        vbox.addWidget(self.start_button)
        vbox.addWidget(self.stop_button)
        hbox.addWidget(self.draw_button)
        hbox.addLayout(vbox)
        return hbox

    def __layoutSetup(self):
        """
        Сетап всего моделирования.
        :return:
        """
        while (self.view.items()):
            cur_item = self.view.items()[0]
            self.view.grScene.removeItem(cur_item)
            del cur_item

        # Обнуление / установка / приисвоение начальных настроек моделирования

        # Время

        self.spawn_period = 1000
        self.time_hours = 0
        self.time_min = 0
        self.day = 0

        self.profit = 0 # Выручка

        # Инициализация значениями из полей
        self.min_freq = int(self.min_customer_frequency.text())
        self.max_freq = int(self.max_customer_frequency.text())
        self.min_check_val = int(self.min_check.text())
        self.max_check_val = int(self.max_check.text())
        self.min_time_buy =  int(self.min_service_time.text())
        self.max_time_buy = int(self.max_service_time.text())
        self.step_len = int(self.step_combo.currentText())
        self.sale_percent = int(self.sale_per.text())
        self.box_office_num = int(self.box_office_combo.currentText())
        self.ads = self.ads_check.isChecked()
        self.max_queue = int(self.queue_combo.currentText())


        self.profit -= AD_NUM * self.ads # Выручка с учетом включенной рекламы
        self.time_factor = 10 / float(self.step_len) # Множитель шага для таймеров

        # Значения к 0
        self.lost_customers_text.setPlainText('0')
        self.serviced_customers_text.setPlainText('0')
        self.sold_average.setPlainText('0 руб.')
        self.queue_length_average_time.setPlainText('0.0 мин.')
        self.time_stamp.setText(START_TIME_STAMP)
        self.box_office_average_occupancy.setPlainText('0.0')
        self.profit_text.setPlainText(str(self.profit) + ' руб.')

        # Инициализация магазина
        self.offices_dict = {}
        self.super_market = Market()

        pos = START_BOX_OFFICE_POS_X
        self.super_market.box_offices = []
        for ind in range(self.box_office_num):
            Box_Office(self, pos)
            pos -= BOX_OFFICE_INTERVAL

        self.start_button.setEnabled(True)
        self.draw_button.setEnabled(True)

    def startProcess(self):
        """
        Начало процесса моделирования
        :return:
        """
        self.start_button.setEnabled(False)
        self.draw_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Основной таймер
        self.main_time = int(float(7 * 24 * 60 * 60 * 1000) / (self.step_len * 6))
        self.main_timer = QTimeLine(self.main_time)
        self.main_timer.start()

        # Таймер часов магазина, привязан к скорости (шагу моделированиия)
        self.day_timer = QTimeLine(int(self.main_time * self.time_factor))
        self.day_timer.setUpdateInterval(int(self.step_len * 1000 * self.time_factor))
        self.day_timer.valueChanged.connect(self.__weekTimes)
        self.day_timer.finished.connect(lambda: self.stopModeling())
        self.day_timer.start()

        self.timer = QTimer()
        self.main_timer.finished.connect(lambda: self.timer.stop())
        self.stop_button.clicked.connect(lambda: self.stopModeling())
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.__createCustomer)
        self.timer.start(self.spawn_period)

    def stopModeling(self):
        """
        Остановка моделирования.
        :return:
        """
        self.main_timer.stop()
        self.timer.stop()
        self.day_timer.stop()
        self.draw_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def __weekTimes(self):
        """
        Вывод на экране времени, прошедшего с наала моделирования.
        :return:
        """
        self.time_min += self.step_len // 10
        if self.time_min > 5:
            self.time_hours +=1
            self.time_min = self.time_min % 6
        if self.time_hours > 23:
            self.time_hours = 0
            self.day += 1
        self.day %= 7
        self.time_stamp.setText(DAYS[self.day] + " " + ("0" if len(str(self.time_hours)) == 1 else "") + str(self.time_hours) + ":" + str(self.time_min) + "0")

    def __createCustomer(self):
        """
        Создание нового покупателя
        :return:
        """
        # Рассчет времени спавна следующего
        single_spawn_time_choice = random.choice(range(self.min_freq, self.max_freq + 1, 1)) # Выбор из промежутка
        self.spawn_period = int((single_spawn_time_choice * 1000) * self.time_factor) # Новое начальное значение таймера спавна

        self.spawn_time_with_ads = int(self.spawn_period * (1.0 - 0.1 * self.ads)) # С учетом рекламы
        self.spawn_time_with_ads_and_sales = int(self.spawn_time_with_ads * (1.0 - 0.005 * self.sale_percent)) # С учетом скидок
        if DEBUG_MODE: print("-- spawn new customer:", self.spawn_period / 1000)
        Customer(self) # Создаем нового покупателя
        self.timer.stop()
        self.timer.start(self.spawn_time_with_ads_and_sales) # Обновляем таймер с учетом нового времени

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()