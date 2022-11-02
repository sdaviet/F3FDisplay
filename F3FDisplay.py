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
#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
import json


import unicodedata
from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, QTimer

from Utils import is_running_on_pi


from UDPReceive import udpreceive
from epaper import Epaper
from tcpClient import tcpClient
from Utils import getnetwork_info


class status:
    notconnected = 0
    contest_notstarted = 1
    contest_inprogress = 2
class mode:
    contest_None = 0
    contest_pilotlist = 1
    contest_weather = 2
    contest_roundtime = 3
    contest_ranking = 4

class f3fdisplay_ctrl:
    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.INFO)
        self.mode = mode.contest_None
        self.status = status.notconnected
        self.pagenumber = 0
        try:
            logging.info("F3FDisplay init")

            self.epaper = Epaper(self.slot_btn_shutdown, self.slot_btn_page, self.slot_down_page)

            self.tcp = tcpClient()
            self.tcp.order_sig.connect(self.setorderdataanddisplaypilot)
            self.tcp.contestNotRunning_sig.connect(self.contestNotRunning)
            self.tcp.notConnected_sig.connect(self.displayWaitingMsg)
            self.displayWaitingMsg()

        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")
    def setorderdataanddisplaypilot(self, round, weather, besttimelist, pilotlist):
        if self.status != status.contest_inprogress:
            self.mode = mode.contest_pilotlist
            self.status = status.contest_inprogress

        self.round = round
        self.weather = weather
        self.bestimelist = besttimelist
        self.pilotlist = pilotlist
        self.epaper.displayPilot(round, weather, besttimelist, pilotlist, self.pagenumber)

    def contestNotRunning(self):
        self.epaper.contestNotRunning()
        self.status = status.contest_notstarted
        self.mode = mode.contest_None
    def displayWaitingMsg(self):
        ip, gw = getnetwork_info()
        self.epaper.displayWaitingMsg(ip, gw)
        self.status = status.notconnected
        self.mode = mode.contest_None
    def slot_btn_page(self):
        print("slot btn_page")
        if self.status == status.contest_inprogress:
            self.incMode()
            if self.mode == mode.contest_pilotlist:
                self.epaper.displayPilot(self.round, self.weather, self.bestimelist, self.pilotlist)
            elif self.mode == mode.contest_weather:
                self.epaper.displayWeather()
            elif self.mode == mode.contest_ranking:
                self.epaper.displayRanking()
            elif self.mode == mode.contest_roundtime:
                self.epaper.displayRoundTime()
    def slot_down_page(self):
        print("slot_down_page")
    def slot_btn_shutdown(self):
        print("slot shuntdown")
        self.epaper.close()

    def incMode(self):
        self.mode = self.mode+1
        if self.mode > mode.contest_ranking:
            self.mode = mode.contest_pilotlist

if __name__ == '__main__':

    if not is_running_on_pi():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QCoreApplication(sys.argv)
    displayCtrl = f3fdisplay_ctrl()

    sys.exit(app.exec_())
    display.close()
    display.sleep()

