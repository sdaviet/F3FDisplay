# vim: set et sw=4 sts=4 fileencoding=utf-8:

#
# This file is part of the F3FChrono distribution (https://github.com/jomarin38/F3FChrono).
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


from time import perf_counter
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
from gpiozero import Button, LED
from PyQt5.QtCore import QObject, pyqtSignal
from F3FChrono.chrono import ConfigReader




class f3fDisplay_gpio(QObject):
    signal_nextpage = pyqtSignal()
    signal_shutdown = pyqtSignal()

    def __init__(self, rpi):
        super().__init__()
        self.__debug = True
        self.btn_enableEvent = True
        if rpi:
            self.btn = Button(ConfigReader.config.conf['btn'])
            self.btn.when_pressed = self.btn_pressed
            self.btn.when_released = self.btn_released
            self.btn_restart_time = ConfigReader.config.conf['btn_restart_time']
            self.lasttimer = None


    def btn_pressed(self):
        if self.__debug:
            print("gpio btnNext_pressed")
        if self.btn_enableEvent:
            self.btn_enableEvent = False
            self.lasttimer = perf_counter()

    def btn_released(self):
        self.btn_enableEvent = True
        if perf_counter()-self.lasttimer<self.btn_restart_time:
            self.signal_nextpage.emit()
        else:
            self.signal_shutdown.emit()
        if self.__debug:
            print("gpio signal btn_next_released")



if __name__ == '__main__':
    import sys
    from F3FChrono.Utils import is_running_on_pi
    from PyQt5.QtCore import pyqtSignal, QObject, QTimer, QThread, QCoreApplication
    
    ConfigReader.init()
    ConfigReader.config = ConfigReader.Configuration('../../config.json')
    rpi = f3fDisplay_gpio(rpi = is_running_on_pi())

    rpi.signal_btn_next.connect(rpi.event_signal)
    app = QCoreApplication(sys.argv)
    
    sys.exit(app.exec())

    del (rpi)
