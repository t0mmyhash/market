from super_window import SuperWindow
from PyQt5.QtWidgets import *
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SuperWindow()
    sys.exit(app.exec_())
