import typing
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from os import path
import sys
from pharmasy_main_ui import Ui_Frame



class Mainapp(QMainWindow, Ui_Frame):
    #QWidget
    def __init__(self, parent=None):
        super(Mainapp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)


def main():
    app = QApplication(sys.argv)
    window = Mainapp()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()