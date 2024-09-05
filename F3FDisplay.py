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
import collections
from argparse import ArgumentParser
from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, QTimer, pyqtSignal
from Utils import is_running_on_pi
from epaper import Epaper, Epaper42, Epaper75
from tcpClient import tcpClient
from Utils import getnetwork_info
import ConfigReader
from weather import weather


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
        self.round = None
        self.bestimelist = None
        self.pilotlist = None
        self.roundtimeslist = None
        self.weathertick = 0
        try:
            logging.info("F3FDisplay init")
            if ConfigReader.config.conf['display_type'] == 4.2:
                print("launch Epaper42")
                self.epaper = Epaper42(self.slot_btn_shutdown, self.slot_btn_page, self.slot_down_page)
            elif ConfigReader.config.conf['display_type'] == 7.5:
                print("launch Epaper75")
                self.epaper = Epaper75(self.slot_btn_shutdown, self.slot_btn_page, self.slot_down_page)
            else:
                print("launch Epaper")
                self.epaper = Epaper(self.slot_btn_shutdown, self.slot_btn_page, self.slot_down_page)
            self.weather = weather()
            self.weather.weatherNbData_signal.connect(self.epaper.weather_signalconnect())
            self.weather.weather_signal.connect(self.slot_weather)
            self.tcp = tcpClient()
            self.tcp.order_sig.connect(self.setorderdataanddisplaypilot)
            self.tcp.contestNotRunning_sig.connect(self.contestNotRunning)
            self.tcp.notConnected_sig.connect(self.displayWaitingMsg)
            self.displayWaitingMsg()

        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")

    def setorderdataanddisplaypilot(self, round, besttimelist, pilotlist, roundtimeslist):
        if self.mode is not mode.contest_weather:
            self.mode = mode.contest_pilotlist

        self.status = status.contest_inprogress
        self.round = round
        self.bestimelist = besttimelist
        self.pilotlist = pilotlist
        self.roundtimeslist = roundtimeslist
        if self.status == status.contest_inprogress and self.mode == mode.contest_pilotlist:
            self.epaper.displayPilot(self.round, self.weather.getLastSpeed(), self.weather.getLastDir(),
                                     self.bestimelist, self.pilotlist, None)
        elif self.mode == mode.contest_roundtime:
            print("page contest current round time")
            '''self.epaper.displayRemaining_RoundTime(self.round, self.weather.getLastSpeedMoy(),
                                                   self.weather.getLastDirMoy(),
                                                   self.bestimelist, self.pilotlist, self.roundtimeslist)
            '''

    def contestNotRunning(self):
        self.status = status.contest_notstarted
        if self.mode is not mode.contest_weather:
            self.epaper.displayContestNotRunning(self.weather.getLastSpeed(), self.weather.getLastDir())
            self.mode = mode.contest_None

    def displayWaitingMsg(self):
        ip, gw = getnetwork_info()
        self.epaper.displayWaitingMsg(ip, gw)
        self.status = status.notconnected
        self.mode = mode.contest_None

    def slot_btn_page(self):
        print("slot btn_page")
        if self.status == status.contest_notstarted:
            if self.mode == mode.contest_None:
                print("page weather")
                self.mode = mode.contest_weather
                self.epaper.displayWeather(self.weather.getLastSpeed(), self.weather.getLastDir(),
                               self.weather.createGraph(self.epaper.epd.width, self.epaper.epd.height-73))
            else:
                print("page contest not running")

                self.mode = mode.contest_None
                self.epaper.displayContestNotRunning(self.weather.getLastSpeed(), self.weather.getLastDir())
        if self.status == status.contest_inprogress:
            self.incMode()
            if self.mode == mode.contest_pilotlist:
                print("page remaining pilot")

                self.epaper.displayPilot(self.round, self.weather.getLastSpeed(), self.weather.getLastDir(),
                                         self.bestimelist, self.pilotlist, None)
            elif self.mode == mode.contest_weather:
                print("page weather")
                self.epaper.displayWeather(self.weather.getLastSpeed(), self.weather.getLastDir(),
                               self.weather.createGraph(self.epaper.epd.width, self.epaper.epd.height-73))
            elif self.mode == mode.contest_ranking:
                print("page contest ranking")
                self.epaper.displayRanking()
            elif self.mode == mode.contest_roundtime:
                print("page contest current round time")
                self.epaper.displayRemaining_RoundTime(self.round, self.weather.getLastSpeed(),
                                                       self.weather.getLastDir(),
                                                       self.bestimelist, self.pilotlist, self.roundtimeslist)

    def slot_down_page(self):
        print("slot_down_page")

    def slot_btn_shutdown(self):
        print("slot shuntdown")
        self.epaper.close()
        self.weather.close()
        if is_running_on_pi():
            os.system("sudo shutdown now")
        exit()

    def slot_weather(self):
        self.weathertick += 1
        if self.weathertick > 1:
            if self.mode is not mode.contest_weather:
                if self.status == status.contest_notstarted:
                    self.epaper.displayContestNotRunning(self.weather.getLastSpeed(), self.weather.getLastDir())
                if self.status == status.contest_inprogress:
                    #elif self.mode == mode.contest_pilotlist:
                    self.epaper.displayPilot(self.round, self.weather.getLastSpeed(), self.weather.getLastDir(),
                                             self.bestimelist, self.pilotlist, None)
            else:
                self.epaper.displayWeather(self.weather.getLastSpeed(), self.weather.getLastDir(),
                               self.weather.createGraph(self.epaper.epd.width, self.epaper.epd.height-73))

            self.weather.weathertofile()
            self.weathertick = 0

    def incMode(self):
        #self.mode = self.mode+1
        if self.mode == mode.contest_pilotlist:
            self.mode = mode.contest_weather
        else:
            self.mode = mode.contest_pilotlist


class weather_only():
    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.INFO)
        self.width = ConfigReader.config.conf['weatherBmpWidht']
        self.height = ConfigReader.config.conf['weatherBmpHeight']
        self.weather = weather(ConfigReader.config.conf['weather_log'])
        self.weather.weather_signal.connect(self.slot_weather)

    def slot_weather(self):
        self.weather.createGraph(self.width, self.height, asFile=True)

if __name__ == '__main__':
    parser = ArgumentParser(prog='chrono')
    parser.add_argument('--weather-only', action="store_true")
    args = parser.parse_args()

    import os

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    ConfigReader.init()
    ConfigReader.config = ConfigReader.Configuration(dname + '/config.json')

    if args.weather_only:
        app = QCoreApplication(sys.argv)
        weatherCtrl = weather_only()
    else:
        if not is_running_on_pi():
            app = QtWidgets.QApplication(sys.argv)
        else:
            app = QCoreApplication(sys.argv)
        displayCtrl = f3fdisplay_ctrl()
    sys.exit(app.exec_())
