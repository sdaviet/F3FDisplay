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
from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, QTimer, pyqtSignal
from Utils import is_running_on_pi
from epaper import Epaper, Epaper42, Epaper75
from tcpClient import tcpClient
from UDPReceive import udpreceive
from Utils import getnetwork_info
import ConfigReader
from filewriter import filewriter


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
            self.udp = udpreceive(4445)
            self.udp.winddir_signal.connect(self.weather.slot_winddir)
            self.udp.windspeed_signal.connect(self.weather.slot_windspeed)
            self.file = filewriter()
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
            x, min, moy, max, dir = self.weather.getData()
            self.epaper.displayPilot(round, self.weather.getLastSpeedMoy(), self.weather.getLastDirMoy(),
                                     self.bestimelist, self.pilotlist, x, min, max, moy, dir)
        elif self.mode == mode.contest_roundtime:
            print("page contest current round time")
            self.epaper.displayRemaining_RoundTime(self.round, self.weather.getLastSpeedMoy(), self.weather.getLastDirMoy(),
                                         self.bestimelist, self.pilotlist, self.roundtimeslist)

    def contestNotRunning(self):
        self.status = status.contest_notstarted
        if self.mode is not mode.contest_weather:
            x, min, moy, max, dir = self.weather.getData()
            self.epaper.displayContestNotRunning(x, min, moy, max, dir)
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
                x, min, moy, max, dir = self.weather.getData()
                self.epaper.displayWeather(x, min, moy, max, dir)
            else:
                print("page contest not running")
                x, min, moy, max, dir = self.weather.getData()
                self.mode = mode.contest_None
                self.epaper.displayContestNotRunning(x, min, moy, max, dir)

        if self.status == status.contest_inprogress:
            self.incMode()
            if self.mode == mode.contest_pilotlist:
                print("page remaining pilot")
                x, min, moy, max, dir = self.weather.getData()
                self.epaper.displayPilot(self.round, self.weather.getLastSpeedMoy(), self.weather.getLastDirMoy(),
                                         self.bestimelist, self.pilotlist, x, min, max, moy, dir)
            elif self.mode == mode.contest_weather:
                print("page weather")
                x, min, moy, max, dir = self.weather.getData()
                self.epaper.displayWeather(x, min, moy, max, dir)
            elif self.mode == mode.contest_ranking:
                print("page contest ranking")
                self.epaper.displayRanking()
            elif self.mode == mode.contest_roundtime:
                print("page contest current round time")
                self.epaper.displayRemaining_RoundTime(self.round, self.weather.getLastSpeedMoy(), self.weather.getLastDirMoy(),
                                             self.bestimelist, self.pilotlist, self.roundtimeslist)

    def slot_down_page(self):
        print("slot_down_page")

    def slot_btn_shutdown(self):
        print("slot shuntdown")
        self.epaper.close()
        self.file.close()
        if is_running_on_pi():
            os.system("sudo shutdown now")
        exit()

    def slot_weather(self):
        self.weathertick += 1
        if self.weathertick > 1:
            x, min, moy, max, dir = self.weather.getData()
            if self.status == status.contest_notstarted:
                self.epaper.displayContestNotRunning(x, min, moy, max, dir)

            if self.status == status.contest_inprogress:
                if self.mode == mode.contest_weather:
                    self.epaper.displayWeather(x, min, moy, max, dir)
                elif self.mode == mode.contest_pilotlist:
                    self.epaper.displayPilot(self.round, self.weather.getLastSpeedMoy(), self.weather.getLastDirMoy(),
                                             self.bestimelist, self.pilotlist, x, min, max, moy, dir)

            if len(min)>0:
                self.file.write_weather(min[-1], moy[-1], max[-1], dir[-1])
            self.weathertick = 0

    def incMode(self):
        #self.mode = self.mode+1
        if self.mode == mode.contest_pilotlist:
            self.mode = mode.contest_weather
        else:
            self.mode = mode.contest_pilotlist


class weather(QTimer):
    weather_signal = pyqtSignal()
    weatherNbData_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.timerinterval = ConfigReader.config.conf['weather_timer_s']
        self.maxweatherdata = ConfigReader.config.conf['max_weather_data']
        self.newdata()
        self.timeout.connect(self.slot_timer)
        self.start(self.timerinterval*1000)
        self.list = []
        self.speed = 0
        self.dir = 0
        self.data = [500, 0, 0, 0, 0, 0]

    def slot_windspeed(self, speed, unit):
        if self.data[0] > speed:
            self.data[0] = speed
        if self.data[3] < speed:
            self.data[3] = speed
        self.data[1] += speed
        self.data[2] += 1
        self.speed = speed

    def slot_winddir(self, dir, accu):
        self.data[4] += dir
        self.data[5] +=1
        self.dir = dir

    def newdata(self):
        #[windmin, windsum, nbwind, windmax, dirsum, nbdir]
        self.data = [500, 0, 0, 0, 0, 0]

    def slot_timer(self):
        print("weather slot timer")
        if self.data[3] > 0:
            self.list.append(self.data)
        if len(self.list) > self.maxweatherdata:
            del self.list[0]

        self.weatherNbData_signal.emit(self.data[3])
        self.newdata()
        self.weather_signal.emit()

    def getData(self):
        time = 0
        x = []
        min = []
        moy = []
        max = []
        dir = []
        for i in self.list:
            x.append(time * self.timerinterval/60)
            time += 1
            min.append(i[0])
            moy.append(i[1]/i[2])
            max.append(i[3])
            if i[5] > 0:
                dir.append(i[4]/i[5])
        return x, min, moy, max, dir

    def getLastSpeedMoy(self):
        if len(self.list) > 0:
            return self.list[-1][1]/self.list[-1][2]
        else:
            return 0
    def getLastDirMoy(self):
        if len(self.list) > 0:
            if self.list[-1][5] > 0:
                return self.list[-1][4] / self.list[-1][5]
        return 0

if __name__ == '__main__':
    import os
    if not is_running_on_pi():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QCoreApplication(sys.argv)
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    ConfigReader.init()
    ConfigReader.config = ConfigReader.Configuration(dname + '/config.json')
    displayCtrl = f3fdisplay_ctrl()
    sys.exit(app.exec_())
    display.close()
    display.sleep()

