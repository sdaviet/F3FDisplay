
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

import threading
import socket
import time
import logging
import re
import json

from PyQt5.QtCore import QThread, pyqtSignal

INITMSG = "Init"
EVENTMSG = "Event"
RACEORDERMSG = "Order"


class udpreceive(QThread):
    # parameters : value, unit
    windspeed_signal = pyqtSignal(float, str)
    # parameters : direction, accu voltage
    winddir_signal = pyqtSignal(float, float)

    def __init__(self, udpport):
        super().__init__()
        self.__debug = False
        self.port = udpport


        self.msg = ""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))
        self.start()


    def __del__(self):
        self.wait()

    def run(self):
        while (not self.isFinished()):
            # wait until somebody throws an event
            try:
                data, address_temp = self.sock.recvfrom(65536)
                address = list(address_temp)
                if self.__debug:
                    print(data, address)
                dt = time.time()
                m = data.decode('utf-8').split()
                if (m[0] == 'terminated'):
                    self.terminate()
                    break
                if m[0] == 'wind_speed':
                    self.windspeed_signal.emit(float(m[1]), str(m[2]))
                elif m[0] == 'wind_dir':
                    self.winddir_signal.emit(float(m[1]), float(m[2]))

            except socket.error as msg:
                print('udp receive error {}'.format(msg))
                logging.warning('udp receive error {}'.format(msg))
                continue

if __name__ == '__main__':
    UDP_PORT = 4445
    print("Main start")
    udpreceive = udpreceive(UDP_PORT, None, None, None)
    udpreceive.start()
    while (not udpreceive.isFinished()):
        # udpreceive.event.set ()
        time.sleep(1)
