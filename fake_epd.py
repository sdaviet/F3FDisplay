#
# This file is part of the F3FDisplay distribution (https://github.com/sdaviet/F3FDisplay).
# Copyright (c) 2021 Sylvain DAVIET, Joel MARIN.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import logging
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap

from PIL.ImageQt import ImageQt

# Display resolution
EPD_WIDTH = 400
EPD_HEIGHT = 300


class fake_EPD(QtCore.QObject):
    signal_nextpage = QtCore.pyqtSignal()
    signal_downpage = QtCore.pyqtSignal()
    signal_shutdown = QtCore.pyqtSignal()

    def __init__(self, size):
        super().__init__()
        logging.basicConfig(level=logging.INFO)
        if size == 4.2:
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
        self.MainWindow = QtWidgets.QMainWindow()
        self.centralwidget = QtWidgets.QWidget(self.MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.MainWindow.setCentralWidget(self.centralwidget)
        self.btnPage = QtWidgets.QPushButton(self.centralwidget)
        self.btnPage.setObjectName("btn_page")
        self.btnPage.setText("Btn Page")
        self.gridLayout.addWidget(self.btnPage)
        self.btnDown = QtWidgets.QPushButton(self.centralwidget)
        self.btnDown.setObjectName("btn_down")
        self.btnDown.setText("Btn Down")
        self.gridLayout.addWidget(self.btnDown)
        self.btnShutDown = QtWidgets.QPushButton(self.centralwidget)
        self.btnShutDown.setObjectName("btn_shutdown")
        self.btnShutDown.setText("btn Shutdown")
        self.gridLayout.addWidget(self.btnShutDown)

        self.lbl = QtWidgets.QLabel(self.centralwidget)
        self.gridLayout.addWidget(self.lbl)

        self.btnShutDown.clicked.connect(self.btn_shutdown_clicked)
        self.btnPage.clicked.connect(self.btn_page_clicked)
        self.btnDown.clicked.connect(self.btn_down_clicked)
        self.MainWindow.show()

    def btn_shutdown_clicked(self):
        self.signal_shutdown.emit()

    def btn_page_clicked(self):
        self.signal_nextpage.emit()
    def btn_down_clicked(self):
        self.signal_downpage.emit()

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
