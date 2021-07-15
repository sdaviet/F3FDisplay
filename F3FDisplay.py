#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging

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

    def displayPilot(self, roundnumber, pilotlist, besttime):
        try:
            self.epd.Clear()
            column = 0
            yoffset = 0
            xoffset = 5
            image = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(image)
            string = 'ORDRE Manche : ' + str(roundnumber)
            stringsize = self.font35.getsize(string)
            draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            string = 'Meilleur temps : ' + str(besttime)
            stringsize = self.font35.getsize(string)
            draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset_title = yoffset + stringsize[1] + 1
            for pilot in pilotlist:
                yoffset += stringsize[1] + 1
                string = pilot
                stringsize = self.font24.getsize(string)

                # check if pilot name length is ok in 2 column display
                if stringsize[0] > (self.epd.width / 2 - 5):
                    string = pilot[:int(len(pilot) / (stringsize[0] / (self.epd.width / 2 - 5))) - 3] + '.'
                    stringsize = self.font24.getsize(string)

                # Check end of display height and width
                if yoffset + stringsize[1] > self.epd.height:
                    if column < 1:
                        xoffset += self.epd.width / 2
                        yoffset = yoffset_title
                        column += 1
                    else:
                        xoffset = self.epd.width + 1
                draw.text((xoffset, yoffset), string, font=self.font24, fill=0)
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

class RoundEvent(QTimer):
    def __init__(self, display):
        super().__init__()
        self.pilotList = []
        self.roundNum = 1
        self.bestTime = 31.49
        for i in range(1, 50):
            # pilot.append(str(i) + " - Pilot" + str(i) + 'nom trop long .........')
            self.pilotList.append(str(i) + " - Pilot" + str(i))
        self.timeout.connect(self.roundEvent)
        self.display = display
        self.start(2000)

    def roundEvent(self):
        if len(self.pilotList) > 0:
            self.display.displayPilot(self.roundNum, self.pilotList, self.bestTime)
            del self.pilotList[0]

if __name__ == '__main__':

    if not is_running_on_pi():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QCoreApplication(sys.argv)

    display = Epaper()
    Round = RoundEvent(display)
    sys.exit(app.exec_())
    display.sleep()
    display.close()

