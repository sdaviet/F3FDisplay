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

from Utils import is_running_on_pi
if is_running_on_pi():
    from lib.waveshare_epd import epd4in2, epd7in5
    from GPIOPort import f3fDisplay_gpio
else:
    from fake_epd import fake_EPD

from PIL import Image, ImageDraw, ImageFont, ImageQt
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')

class Epaper:
    def __init__(self):
        super().__init__()

        self.font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        self.font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        self.font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)

    def displayWaitingMsg(self, ip, gateway):
        try:
            self.clearImage()
            stringIp = "IP:" + ip
            stringGw = "GW:" + gateway
            stringsizeIp = self.font35.getsize(stringIp)
            stringsizeGw = self.font35.getsize(stringGw)
            string0 = 'F3FDISPLAY'
            stringsize0 = self.font35.getsize(string0)

            string1 = 'NOT CONNECTED'
            stringsize1 = self.font35.getsize(string1)

            self.draw.text((int(self.epd.width / 2 - stringsizeIp[0] / 2), 20), stringIp, font=self.font35, fill=0)
            self.draw.text((int(self.epd.width / 2 - stringsizeGw[0] / 2), 60), stringGw, font=self.font35, fill=0)
            self.draw.text((int(self.epd.width / 2 - stringsize0[0] / 2), self.epd.height/2-stringsize0[1]), string0, font=self.font35, fill=0)
            self.draw.text((int(self.epd.width / 2 - stringsize1[0] / 2), self.epd.height/2+stringsize1[1]), string1, font=self.font35, fill=0)
            self.epd.display(self.epd.getbuffer(self.image))
        except IOError as e:
            logging.info(e)

    def displayContestNotRunning(self):
        try:
            string0 = 'F3FDISPLAY'
            stringsize0 = self.font35.getsize(string0)

            string1 = 'CONTEST NOT STARTED'
            stringsize1 = self.font35.getsize(string1)
            self.clearImage()
            self.draw.text((int(self.epd.width / 2 - stringsize0[0] / 2), self.epd.height/2-stringsize0[1]), string0, font=self.font35, fill=0)
            self.draw.text((int(self.epd.width / 2 - stringsize1[0] / 2), self.epd.height/2+stringsize1[1]), string1, font=self.font35, fill=0)
            self.epd.display(self.epd.getbuffer(self.image))
        except IOError as e:
            logging.info(e)


    def displayPilot(self, round, weather, besttimelist, pilotlist, page=0):
        try:

            column = 0
            yoffset = 0
            xoffset = 5
            self.clearImage()
            string = 'ROUND ' + round
            if weather is not None and len(weather) > 0:
                string += ' - ' + '{:.0f}'.format(weather[0][1]/weather[0][2]) + 'm/s, ' + '{:.0f}'.format(weather[0][4]/weather[0][5]) + '°'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            for besttime in besttimelist:
                if 'run' in besttime:
                    string = 'Grp : ' + str(besttime['gp']) + ' - ' + besttime['run']
                else:
                    string = 'Grp : ' + str(besttime['gp']) + ' - ' + "No time availables"
                stringsize = self.font24.getsize(string)
                self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24, fill=0)
                yoffset += stringsize[1] + 1

            #yoffset += int(stringsize[1])
            string = 'REMAINING PILOTS :'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1]+1
            yoffset_title = yoffset
            yoffsetMax = 0
            #search yoffset Max
            for pilot in pilotlist:
                string = str(pilot['bib']) + ' : ' + pilot['pil']
                stringsize = self.font24.getsize(string)
                if stringsize[1] > yoffsetMax:
                    yoffsetMax = stringsize[1]
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
                self.draw.text((xoffset, yoffset), string, font=self.font24, fill=0)
                yoffset += yoffsetMax + 1
            self.draw.line([(self.epd.width / 2, yoffset_title), (self.epd.width / 2, yoffset)], fill='black', width=0)
            self.epd.display(self.epd.getbuffer(self.image))
        except IOError as e:
            logging.info(e)

    def displayRanking(self):
        try:
            string0 = 'F3FDISPLAY Ranking'
            stringsize0 = self.font35.getsize(string0)

            string1 = 'IN CONSTRUCTION'
            stringsize1 = self.font35.getsize(string1)
            self.clearImage()
            self.draw.text((int(self.epd.width / 2 - stringsize0[0] / 2), self.epd.height/2-stringsize0[1]), string0, font=self.font35, fill=0)
            self.draw.text((int(self.epd.width / 2 - stringsize1[0] / 2), self.epd.height/2+stringsize1[1]), string1, font=self.font35, fill=0)
            self.epd.display(self.epd.getbuffer(self.image))
        except IOError as e:
            logging.info(e)

    def displayRoundTime(self, round, weather, bestimelist, roundtimeslist):
        try:
            column = 0
            yoffset = 0
            xoffset = 5
            self.clearImage()
            string = 'ROUND ' + round
            if weather is not None and len(weather) > 0:
                string += ' - ' + '{:.0f}'.format(weather[0][1]/weather[0][2]) + 'm/s, ' + '{:.0f}'.format(weather[0][4]/weather[0][5]) + '°'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            for besttime in bestimelist:
                if 'run' in besttime:
                    string = 'Grp : ' + str(besttime['gp']) + ' - ' + besttime['run']
                else:
                    string = 'Grp : ' + str(besttime['gp']) + ' - ' + "No time availables"
                stringsize = self.font24.getsize(string)
                self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24, fill=0)
                yoffset += stringsize[1] + 1

            # yoffset += int(stringsize[1])
            string = 'PILOTS Times :'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            yoffset_title = yoffset
            yoffsetMax = 0
            # search yoffset Max
            for pilot in roundtimeslist:
                string = pilot[0] + ' : ' + pilot[2] + ' - ' + pilot[3]
                stringsize = self.font24.getsize(string)
                if stringsize[1] > yoffsetMax:
                    yoffsetMax = stringsize[1]
            for pilot in roundtimeslist:
                string = pilot[0] + ' : ' + pilot[2] + ' - ' + pilot[3]
                stringsize = self.font24.getsize(string)

                # check if pilot name length is ok in 2 column display
                if stringsize[0] > (self.epd.width / 2 - 4):
                    # string = string[:len(string) - int(stringsize[0]/(self.epd.width / 2 - 4))] + '.'
                    string = string[:int(len(string) * (self.epd.width / 2 - 4) / stringsize[0]) - 1] + '.'
                    # string = string[:16] + '.'
                    # print(len(string), int(stringsize[0]/(self.epd.width / 2 - 4) + 2), len(string) - int(stringsize[0]/(self.epd.width / 2) + 2))
                    stringsize = self.font24.getsize(string)

                # Check end of display height and width
                if yoffset + yoffsetMax > self.epd.height:
                    if column < 1:
                        xoffset += self.epd.width / 2
                        yoffset = yoffset_title
                        column += 1
                    else:
                        xoffset = self.epd.width + 1
                        yoffset = yoffset_title
                self.draw.text((xoffset, yoffset), string, font=self.font24, fill=0)
                yoffset += yoffsetMax + 1
            self.draw.line([(self.epd.width / 2, yoffset_title), (self.epd.width / 2, yoffset)], fill='black', width=0)
            self.epd.display(self.epd.getbuffer(self.image))
        except IOError as e:
            logging.info(e)

    def displayWeather(self, data):
        try:
            yoffset = 0
            self.clearImage()
            string = 'WEATHER STATION'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1

            string = '{:.0f}'.format(data[0]) + ' m/s, ' + '{:.0f}'.format(data[1]) + '°'
            stringsize = self.font24.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24, fill=0)
            yoffset += stringsize[1] + 1

            if len(data[2]) > 0:
                string = f'{"Min"} {"Moy"} {"Max"} {"DirMoy"}'
                stringsize = self.font24.getsize(string)
                self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24, fill=0)
                yoffset += stringsize[1] + 1
                for i in data[2][:8]:
                    string = f'{i[0]:2.0f} {"   "} {(i[1]/i[2]):2.0f} {"   "} {i[3]:2.0f} {"     "} {(i[4]/i[5]):2.0f}'
                    stringsize = self.font24.getsize(string)
                    self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24,
                                   fill=0)
                    yoffset += stringsize[1] + 1
                    if yoffset > self.epd.height:
                        break

            self.epd.display(self.epd.getbuffer(self.image))
        except IOError as e:
            logging.info(e)
    def sleep(self):
        try:
            logging.info("Goto Sleep...")
            self.epd.sleep()
        except IOError as e:
            logging.info(e)

    def clearImage(self):
        self.draw.rectangle([(0, 0), (self.epd.width, self.epd.height)], fill=255)

    def close(self):
        try:
            self.clearImage()
            string0 = 'F3F DISPLAY'
            stringsize0 = self.font35.getsize(string0)

            string1 = 'BYE BYE'
            stringsize1 = self.font35.getsize(string1)
            self.draw.text((int(self.epd.width / 2 - stringsize0[0] / 2), self.epd.height / 2 - stringsize0[1]), string0,
                      font=self.font35, fill=0)
            self.draw.text((int(self.epd.width / 2 - stringsize1[0] / 2), self.epd.height / 2 + stringsize1[1]), string1,
                      font=self.font35, fill=0)
            self.epd.display(self.epd.getbuffer(self.image))
            self.image.close()
        except IOError as e:
            logging.info(e)
        if is_running_on_pi():
            self.epd.epdconfig.module_exit()


class Epaper42(Epaper):
    def __init__(self, slot_shutdown, slot_page, slot_page_down):
        super().__init__()
        rpi = is_running_on_pi()
        if rpi:
            self.epd = epd4in2.EPD()
            self.gpio = f3fDisplay_gpio(rpi)
            self.gpio.signal_shutdown.connect(slot_shutdown)
            self.gpio.signal_nextpage.connect(slot_page)
            self.gpio.signal_downpage.connect(slot_page_down)
        else:
            self.epd = fake_EPD(4.2)
            self.epd.signal_shutdown.connect(slot_shutdown)
            self.epd.signal_nextpage.connect(slot_page)
            self.epd.signal_downpage.connect(slot_page_down)
        self.image = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
        self.draw = ImageDraw.Draw(self.image)
        logging.info("init and Clear")
        self.epd.init()
        self.epd.Clear()

class Epaper75(Epaper):
    def __init__(self, slot_shutdown, slot_page, slot_page_down):
        super().__init__()

        rpi = is_running_on_pi()
        if rpi:
            self.epd = epd7in5.EPD()
            self.gpio = f3fDisplay_gpio(rpi)
            self.gpio.signal_shutdown.connect(slot_shutdown)
            self.gpio.signal_nextpage.connect(slot_page)
            self.gpio.signal_downpage.connect(slot_page_down)
        else:
            self.epd = fake_EPD(7.5)
            self.epd.signal_shutdown.connect(slot_shutdown)
            self.epd.signal_nextpage.connect(slot_page)
            self.epd.signal_downpage.connect(slot_page_down)
        self.image = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
        self.draw = ImageDraw.Draw(self.image)
        logging.info("init and Clear")
        self.epd.init()
        self.epd.Clear()

    def displayRoundTime(self, round, weather, bestimelist, roundtimeslist):
        try:
            column = 0
            yoffset = 0
            xoffset = 5
            self.clearImage()
            string = 'ROUND ' + round
            if weather is not None and len(weather) > 0:
                string += ' - ' + '{:.0f}'.format(weather[0][1]/weather[0][2]) + 'm/s, ' + '{:.0f}'.format(weather[0][4]/weather[0][5]) + '°'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            for besttime in bestimelist:
                if 'run' in besttime:
                    string = 'Grp : ' + str(besttime['gp']) + ' - ' + besttime['run']
                else:
                    string = 'Grp : ' + str(besttime['gp']) + ' - ' + "No time availables"
                stringsize = self.font24.getsize(string)
                self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24, fill=0)
                yoffset += stringsize[1] + 1

            # yoffset += int(stringsize[1])
            string = 'PILOTS Times :'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            yoffset_title = yoffset
            yoffsetMax = 0
            # search yoffset Max
            for pilot in roundtimeslist:
                string = pilot[0] + ' : ' + pilot[2] + ' - ' + pilot[3]
                stringsize = self.font24.getsize(string)
                if stringsize[1] > yoffsetMax:
                    yoffsetMax = stringsize[1]
            for pilot in roundtimeslist:
                string = pilot[0] + ' - ' + pilot[1] + ' : ' + pilot[2] + ' - ' + pilot[3]
                stringsize = self.font24.getsize(string)

                # check if pilot name length is ok in 2 column display
                if stringsize[0] > (self.epd.width / 2 - 4):
                    # string = string[:len(string) - int(stringsize[0]/(self.epd.width / 2 - 4))] + '.'
                    string = string[:int(len(string) * (self.epd.width / 2 - 4) / stringsize[0]) - 1] + '.'
                    # string = string[:16] + '.'
                    # print(len(string), int(stringsize[0]/(self.epd.width / 2 - 4) + 2), len(string) - int(stringsize[0]/(self.epd.width / 2) + 2))
                    stringsize = self.font24.getsize(string)

                # Check end of display height and width
                if yoffset + yoffsetMax > self.epd.height:
                    if column < 1:
                        xoffset += self.epd.width / 2
                        yoffset = yoffset_title
                        column += 1
                    else:
                        xoffset = self.epd.width + 1
                        yoffset = yoffset_title
                self.draw.text((xoffset, yoffset), string, font=self.font24, fill=0)
                yoffset += yoffsetMax + 1
            self.draw.line([(self.epd.width / 2, yoffset_title), (self.epd.width / 2, yoffset)], fill='black', width=0)
            self.epd.display(self.epd.getbuffer(self.image))
        except IOError as e:
            logging.info(e)

class EpaperDefault(Epaper):
    def __init__(self, slot_shutdown, slot_page, slot_page_down):
        super().__init__()

        rpi = is_running_on_pi()
        if rpi:
            logging('not supported')
        else:
            self.epd = fake_EPD()
            self.epd.signal_shutdown.connect(slot_shutdown)
            self.epd.signal_nextpage.connect(slot_page)
            self.epd.signal_downpage.connect(slot_page_down)
        self.image = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
        self.draw = ImageDraw.Draw(self.image)
        logging.info("init and Clear")
        self.epd.init()
        self.epd.Clear()
