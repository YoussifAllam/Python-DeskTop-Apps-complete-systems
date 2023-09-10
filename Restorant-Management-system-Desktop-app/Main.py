
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from os import path
import sys
import matplotlib.pyplot as plt 

#!
import numpy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg  as  FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
import matplotlib.patches as patches
from Restorant1 import Ui_Frame

'''
class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=12, height=2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()


    def plot(self):
        data = [random.random() for i in range(10)]
        
        
        ax = self.figure.add_subplot(111)
        ax.plot(data, '--')
        ax.plot(data, 'b-')
        bg_rect = patches.Rectangle((0, 0), 1, 1, facecolor='#ffffff')

        # Set the `facecolor` attribute of the `Rectangle` object to the desired background color.
        bg_rect.facecolor = '#ffffff'

        # Add the `Rectangle` object to the plot.
        ax.add_patch(bg_rect)
        self.draw()
        '''

class Mainapp(QFrame, Ui_Frame):
    #QWidget
    def __init__(self, parent=None):
        super(Mainapp, self).__init__(parent)
        QFrame.__init__(self)
        self.setupUi(self)
        ''' m = PlotCanvas(self, width=3.5, height=1.9)
        m.move(50,437)
        self.show()'''
        
    def plot(self):
          
        # random data
        data = [random.random() for i in range(10)]
  
        # clearing old figure
        self.figure.clear()
  
        # create an axis
        ax = self.figure.add_subplot(111)
  
        # plot data
        ax.plot(data, '*-')
  
        # refresh canvas
        self.canvas.draw()


def main():
    app = QApplication(sys.argv)
    window = Mainapp()
    window.show()
    app.exec_()
   


if __name__ == "__main__":
    main()