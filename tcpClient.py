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


import socket
import json
from PyQt5.QtCore import QThread, pyqtSignal
from Utils import getnetwork_info
import ConfigReader

tcpPort = 10000

class tcpClient_Status():
    Init = 0
    Listen = 1
    Accepted = 2
    Connected = 3
    InProgress = 4
    Close = 5

class tcpClient(QThread):
    order_sig = pyqtSignal(str, list, list, list)
    contestNotRunning_sig = pyqtSignal()
    notConnected_sig = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__debug = True
        self.ip = None
        self.gateway = None
        self.port = tcpPort
        self.status = tcpClient_Status.Init
        self.client = None
        self.start()

    def run(self):
        while not self.isFinished():
            if self.status == tcpClient_Status.Init:
                try:
                    gateway = ConfigReader.config.conf['server_ip']
                    self.ip, self.gateway = getnetwork_info()
                    if self.gateway == ConfigReader.config.conf['F3FChronoServerIp']:
                        gateway = self.gateway

                    self.Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.Client.connect((gateway, self.port))
                except socket.error as e:
                    print(str(e))
                    del (self.client)
                    self.client = None
                    self.sleep(5)
                else:
                    if self.__debug:
                        print(f'Connection...')
                    self.status = tcpClient_Status.Connected
            elif self.status == tcpClient_Status.Connected:
                data = ''
                try:
                    self.Client.sendall(bytes("F3FDisplay", "utf-8"))
                except socket.error as e:
                    print(str(e))
                try:
                    data = str(self.Client.recv(1024), "utf-8")
                except socket.error as e:
                    print(str(e))
                if self.__debug:
                    print(f'data received : {data}')
                if data == "F3FDisplayServerStarted":
                    self.status = tcpClient_Status.InProgress
                    self.getChronoStatus()
            elif self.status == tcpClient_Status.InProgress:
                try:
                    data = self.Client.recv(2048)
                except socket.error as e:
                    print(str(e))
                else:
                    if data == b'':
                        try:
                            self.Client.sendall(bytes("Test", "utf-8"))
                        except socket.error as e:
                            print(str(e))
                            self.Client.close()
                            self.Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.status = tcpClient_Status.Init
                            del self.Client
                            self.Client = None
                            self.notConnected_sig.emit()
                    else:
                        self.datareceived(data)
            elif self.status == tcpClient_Status.Close:
                self.Client.close()
                self.status = tcpClient_Status.Close

    def getChronoStatus(self):
        if self.status == tcpClient_Status.InProgress:
            self.Client.sendall(bytes("ContestRunning?", "utf-8"))

    def getPilotList(self):
        if self.status == tcpClient_Status.InProgress:
            self.Client.sendall(bytes("getPilotList", "utf-8"))

    def datareceived(self, data):
        print(data)
        m = data.decode('utf-8').split()
        if len(m)>0:
            if m[0] == "ContestRunning?":
                if m[1] == 'True':
                    self.getPilotList()
                else:
                    self.contestNotRunning_sig.emit()
            elif m[0] == "ContestData":
                orderstring = data.decode('utf-8')[len(m[0]) + 1:]
                if self.__debug:
                    print('datasize:' + str(len(orderstring)))
                    print(orderstring)
                orderjson = json.loads(orderstring)
                self.order_sig.emit(orderjson['round'],
                                    orderjson['best'],
                                    orderjson['remain'],
                                    orderjson['roundtime'])
