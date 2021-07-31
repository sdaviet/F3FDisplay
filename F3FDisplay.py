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

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')


class Epaper:
    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.INFO)

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

        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")

    def displayPilot(self, besttimelist, pilotlist):
        try:
            self.epd.Clear()
            column = 0
            yoffset = 0
            xoffset = 5
            image = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(image)

            string = 'BEST TIME :'
            stringsize = self.font35.getsize(string)
            draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            for besttime in besttimelist:
                string = str(besttime['group_number']) + ' - ' + besttime['best_run']
                stringsize = self.font24.getsize(string)
                draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24, fill=0)
                yoffset += stringsize[1] + 1

            #yoffset += int(stringsize[1])
            string = 'REMAINING PILOTS :'
            stringsize = self.font35.getsize(string)
            draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1]+1
            yoffset_title = yoffset
            for pilot in pilotlist:
                string = str(pilot['bib_number']) + ' : ' + pilot['pilot_name']
                stringsize = self.font24.getsize(string)

                # check if pilot name length is ok in 2 column display
                if stringsize[0] > (self.epd.width / 2 - 5):
                    string = string[:len(string) - int(stringsize[0]/(self.epd.width / 2 - 5)) - 2] + '.'
                    stringsize = self.font24.getsize(string)

                # Check end of display height and width
                if yoffset > self.epd.height:
                    if column < 1:
                        xoffset += self.epd.width / 2
                        yoffset = yoffset_title
                        column += 1
                    else:
                        xoffset = self.epd.width + 1
                        yoffset = yoffset_title
                draw.text((xoffset, yoffset), string, font=self.font24, fill=0)
                yoffset += stringsize[1] + 1

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
        if is_running_on_pi():
            epd4in2.epdconfig.module_exit()


if __name__ == '__main__':

    if not is_running_on_pi():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QCoreApplication(sys.argv)

    display = Epaper()
    udp = udpreceive(4445)
    udp.order_sig.connect(display.displayPilot)

    sys.exit(app.exec_())
    display.sleep()
    display.close()

