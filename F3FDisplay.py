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

if is_running_on_pi():
    from lib.waveshare_epd import epd4in2
else:
    from fake_epd import EPD
import time
from PIL import Image, ImageDraw, ImageFont, ImageQt
from UDPReceive import udpreceive
from tcpClient import tcpClient
from Utils import  getnetwork_info


picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')


class Epaper:
    def __init__(self, ip, gateway):
        super().__init__()
        logging.basicConfig(level=logging.INFO)
        self.ip = ip
        self.gateway = gateway
        try:
            logging.info("F3FDisplay")

            if is_running_on_pi():
                self.epd = epd4in2.EPD()
            else:
                self.epd = EPD()

            logging.info("init and Clear")
            self.epd.init()
            self.epd.Clear()
            self.font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
            self.font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
            self.font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
            self.displayWaitingMsg()
        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")

    def displayWaitingMsg(self):
        try:

            image = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(image)
            self.ip, self.gateway = getnetwork_info()
            stringIp = "IP:" + self.ip
            stringGw = "GW:" + self.gateway
            stringsizeIp = self.font35.getsize(stringIp)
            stringsizeGw = self.font35.getsize(stringGw)
            string0 = 'F3FDISPLAY PILOTS'
            stringsize0 = self.font35.getsize(string0)

            string1 = 'NOT CONNECTED'
            stringsize1 = self.font35.getsize(string1)

            draw.text((int(self.epd.width / 2 - stringsizeIp[0] / 2), 20), stringIp, font=self.font35, fill=0)
            draw.text((int(self.epd.width / 2 - stringsizeGw[0] / 2), 60), stringGw, font=self.font35, fill=0)
            draw.text((int(self.epd.width / 2 - stringsize0[0] / 2), self.epd.height/2-stringsize0[1]), string0, font=self.font35, fill=0)
            draw.text((int(self.epd.width / 2 - stringsize1[0] / 2), self.epd.height/2+stringsize1[1]), string1, font=self.font35, fill=0)
            self.epd.display(self.epd.getbuffer(image))
            image.close()
        except IOError as e:
            logging.info(e)

    def contestNotRunning(self):
        try:
            image = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(image)

            string0 = 'F3FDISPLAY PILOTS'
            stringsize0 = self.font35.getsize(string0)

            string1 = 'CONTEST NOT STARTED'
            stringsize1 = self.font35.getsize(string1)

            draw.text((int(self.epd.width / 2 - stringsize0[0] / 2), self.epd.height/2-stringsize0[1]), string0, font=self.font35, fill=0)
            draw.text((int(self.epd.width / 2 - stringsize1[0] / 2), self.epd.height/2+stringsize1[1]), string1, font=self.font35, fill=0)
            self.epd.display(self.epd.getbuffer(image))
            image.close()
        except IOError as e:
            logging.info(e)

    def displayPilot(self, round, weather, besttimelist, pilotlist):
        try:
            #self.epd.Clear()
            column = 0
            yoffset = 0
            xoffset = 5
            image = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(image)
            string = 'ROUND ' + round
            if len(weather)>0:
                string += ' - ' + '{:.0f}'.format(weather['s']) + 'm/s, ' + '{:.0f}'.format(weather['dir']) + '°'
            stringsize = self.font35.getsize(string)
            draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            for besttime in besttimelist:
                if 'run' in besttime:
                    string = 'Grp : ' + str(besttime['gp']) + ' - ' + besttime['run']
                else:
                    string = 'Grp : ' + str(besttime['gp']) + ' - ' + "No time availables"
                stringsize = self.font24.getsize(string)
                draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24, fill=0)
                yoffset += stringsize[1] + 1

            #yoffset += int(stringsize[1])
            string = 'REMAINING PILOTS :'
            stringsize = self.font35.getsize(string)
            draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1]+1
            yoffset_title = yoffset
            yoffsetMax = 0
            #search yoffset Max
            for pilot in pilotlist:
                string = str(pilot['bib']) + ' : ' + pilot['pil']
                stringsize = self.font24.getsize(string)
                if stringsize[1]>yoffsetMax:
                    yoffsetMax=stringsize[1]
            for pilot in pilotlist:
                string = str(pilot['bib']) + ' : ' + pilot['pil']
                stringsize = self.font24.getsize(string)

                # check if pilot name length is ok in 2 column display
                if stringsize[0] > (self.epd.width / 2 - 4):
                    #string = string[:len(string) - int(stringsize[0]/(self.epd.width / 2 - 4))] + '.'
                    string = string[:int(len(string)*(self.epd.width / 2 - 4)/stringsize[0])-1] + '.'
                    #string = string[:16] + '.'
                    #print(len(string), int(stringsize[0]/(self.epd.width / 2 - 4) + 2), len(string) - int(stringsize[0]/(self.epd.width / 2) + 2))
                    stringsize = self.font24.getsize(string)

                # Check end of display height and width
                if yoffset+yoffsetMax > self.epd.height:
                    if column < 1:
                        xoffset += self.epd.width / 2
                        yoffset = yoffset_title
                        column += 1
                    else:
                        xoffset = self.epd.width + 1
                        yoffset = yoffset_title
                draw.text((xoffset, yoffset), string, font=self.font24, fill=0)
                yoffset += yoffsetMax + 1

            self.epd.display(self.epd.getbuffer(image))
            image.close()
        except IOError as e:
            logging.info(e)


    def sleep(self):
        try:
            logging.info("Goto Sleep...")
            self.epd.sleep()
        except IOError as e:
            logging.info(e)

    def close(self):
        try:
            image = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(image)
            string0 = 'F3F DISPLAY'
            stringsize0 = self.font35.getsize(string0)

            string1 = 'BYE BYE'
            stringsize1 = self.font35.getsize(string1)
            draw.text((int(self.epd.width / 2 - stringsize0[0] / 2), self.epd.height / 2 - stringsize0[1]), string0,
                      font=self.font35, fill=0)
            draw.text((int(self.epd.width / 2 - stringsize1[0] / 2), self.epd.height / 2 + stringsize1[1]), string1,
                      font=self.font35, fill=0)
            self.epd.display(self.epd.getbuffer(image))
            image.close()
        except IOError as e:
            logging.info(e)
        if is_running_on_pi():
            epd4in2.epdconfig.module_exit()


if __name__ == '__main__':

    if not is_running_on_pi():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QCoreApplication(sys.argv)
    ip, gw = getnetwork_info()
    display = Epaper(ip, gw)
    #udp = udpreceive(4445)
    tcp = tcpClient(ip, gw)
    #udp.order_sig.connect(display.displayPilot)
    tcp.order_sig.connect(display.displayPilot)
    tcp.contestNotRunning_sig.connect(display.contestNotRunning)
    tcp.notConnected_sig.connect(display.displayWaitingMsg)

    sys.exit(app.exec_())
    display.close()
    display.sleep()

