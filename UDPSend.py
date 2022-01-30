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

import socket
import time
import logging
import sys
import json
from PyQt5.QtCore import QObject, QTimer
from PyQt5 import QtWidgets


INITMSG = "Init"
EVENTMSG = "Event"
RACEORDERMSG = "Order"

class udpSend(QObject):
    def __init__(self, udpip, udpport):
        super(QObject, self).__init__()
        self.udpip = udpip
        self.port = udpport
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def __del__(self):
        del self.sock

    def send(self):
        self.sock.sendto(bytes('event', 'utf-8'), (self.udpip, self.port))

    def sendData(self, data):
        self.sock.sendto(bytes(data, 'utf-8'), (self.udpip, self.port))

    def sendOrderData(self, data):
        self.sock.sendto(bytes((RACEORDERMSG+ ' '+ data), 'utf-8'), (self.udpip, self.port))

    def terminate(self):
        print('terminated event')
        self.sock.sendto(bytes('terminated', 'utf-8'), (self.udpip, self.port)) 

class RoundEvent(QTimer):
    def __init__(self, udp):
        super().__init__()
        self.udp = udp
        self.data = json.load(open("test.json", 'r'))

        self.timeout.connect(self.roundEvent)
        self.start(2000)

    def roundEvent(self):
        if len(self.data['remaining_pilots']) > 0:
            self.udp.sendOrderData(json.dumps(self.data))
            del self.data['remaining_pilots'][0]
        else:
            self.stop()
            exit()

if __name__ == '__main__':
    print ("UDP Beep Debug")
    app = QtWidgets.QApplication(sys.argv)
    #udpbeep = udpBeep ("192.168.0.22", 4445)
    udpSend = udpSend("255.255.255.255", 4445)
    end = False
    Round = RoundEvent(udpSend)

    sys.exit(app.exec_())





