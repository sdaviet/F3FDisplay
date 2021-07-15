import logging
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap

from PIL.ImageQt import ImageQt

# Display resolution
EPD_WIDTH = 400
EPD_HEIGHT = 300


class EPD:
    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.INFO)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        #self.MainWindow = QtWidgets.QMainWindow()
        #self.MainWindow.resize(2*self.width, 2*self.height)
        #self.centralwidget = QtWidgets.QWidget(self.MainWindow)
        #self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        #self.lbl = QtWidgets.QLabel(self.centralwidget)
        #self.lbl.setFixedSize(2*EPD_WIDTH, 2*EPD_HEIGHT)
        #self.lbl.resize(2*EPD_WIDTH, 2*EPD_HEIGHT)
        #self.MainWindow.show()

        self.lbl = QtWidgets.QLabel()


    def reset(self):
        logging.info("reset")

    def init(self):
        logging.info("init")

    def getbuffer(self, image):
        return image

    def Clear(self):
        logging.info("clear")

    def sleep(self):
        logging.info("sleep")

    def display(self, image):
        logging.info("display")
        qimage = ImageQt(image)
        self.lbl.setPixmap(QtGui.QPixmap.fromImage(qimage))
        self.lbl.show()
