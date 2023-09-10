import typing
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
from os import path
import sys

FORM_CLASS,_ = uic.loadUiType(path.join(path.dirname(__file__),'pharmasy main.ui'))


class Mainapp(QMainWindow, FORM_CLASS):
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