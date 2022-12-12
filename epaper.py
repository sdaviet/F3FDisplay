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
# !/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
import json
import io
from Utils import is_running_on_pi

if is_running_on_pi():
    from lib.waveshare_epd import epd4in2, epd7in5_V2
    from GPIOPort import f3fDisplay_gpio
else:
    from fake_epd import fake_EPD

from PIL import Image, ImageDraw, ImageFont, ImageQt

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
import plotly.graph_objects as go
import plotly.io as plotio


class Epaper:
    def __init__(self):
        super().__init__()

        self.font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        self.font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        self.font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
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
            self.draw.text((int(self.epd.width / 2 - stringsize0[0] / 2), self.epd.height / 2 - stringsize0[1]),
                           string0, font=self.font35, fill=0)
            self.draw.text((int(self.epd.width / 2 - stringsize1[0] / 2), self.epd.height / 2 + stringsize1[1]),
                           string1, font=self.font35, fill=0)
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
            self.draw.text((int(self.epd.width / 2 - stringsize0[0] / 2), self.epd.height / 2 - stringsize0[1]),
                           string0, font=self.font35, fill=0)
            self.draw.text((int(self.epd.width / 2 - stringsize1[0] / 2), self.epd.height / 2 + stringsize1[1]),
                           string1, font=self.font35, fill=0)
            self.epd.display(self.epd.getbuffer(self.image))
        except IOError as e:
            logging.info(e)

    def displayPilot(self, round, speed, dir, besttimelist, pilotlist, page=0,
                     weatherx=None, weathermin=None, weathermax=None, weathermoy=None, weatherdir=None):
        try:

            column = 0
            yoffset = 0
            xoffset = 5
            self.clearImage()
            string = 'ROUND ' + round

            string += ' - ' + '{:.0f}'.format(speed) + 'm/s, ' + '{:.0f}'.format(dir) + '°'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            for besttime in besttimelist:
                if 'run' in besttime:
                    string = 'Grp:' + str(besttime['gp']) + ' - ' + besttime['run'].split('\t')[0]
                else:
                    string = 'Grp:' + str(besttime['gp']) + ' - ' + "No time availables"
                stringsize = self.font24.getsize(string)
                self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24, fill=0)
                yoffset += stringsize[1] + 1

            # yoffset += int(stringsize[1])
            string = 'REMAINING PILOTS:'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            yoffset_title = yoffset
            yoffsetMax = 0
            stringsizemax = 0
            # search yoffset Max
            for pilot in pilotlist:
                string = str(pilot['bib']) + ':' + pilot['pil']
                stringsize = self.font24.getsize(string)
                if stringsize[1] > yoffsetMax:
                    yoffsetMax = stringsize[1]
            for pilot in pilotlist:
                string = str(pilot['bib']) + ':' + pilot['pil']
                stringsize = self.font24.getsize(string)

                if stringsize[0] > stringsizemax:
                    stringsizemax = stringsize[0] + 15

                # check if pilot name length is ok in 2 column display
                if stringsize[0] > (self.epd.width / 2 - 4):
                    # string = string[:len(string) - int(stringsize[0]/(self.epd.width / 2 - 4))] + '.'
                    string = string[:int(len(string) * (self.epd.width / 2 - 4) / stringsize[0]) - 1] + '.'
                    # string = string[:16] + '.'
                    # print(len(string), int(stringsize[0]/(self.epd.width / 2 - 4) + 2), len(string) - int(stringsize[0]/(self.epd.width / 2) + 2))
                    stringsize = self.font24.getsize(string)
                    stringsizemax = self.epd.width / 2

                # Check end of display height and width
                if yoffset + yoffsetMax > self.epd.height:
                    if column < 1:
                        xoffset += stringsizemax
                        yoffset = yoffset_title
                        column += 1
                    else:
                        xoffset = self.epd.width + 1
                        yoffset = yoffset_title
                self.draw.text((xoffset, yoffset), string, font=self.font24, fill=0)
                yoffset += yoffsetMax + 1
            self.draw.line([(stringsizemax, yoffset_title), (stringsizemax, yoffset)], fill='black', width=0)
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
            self.draw.text((int(self.epd.width / 2 - stringsize0[0] / 2), self.epd.height / 2 - stringsize0[1]),
                           string0, font=self.font35, fill=0)
            self.draw.text((int(self.epd.width / 2 - stringsize1[0] / 2), self.epd.height / 2 + stringsize1[1]),
                           string1, font=self.font35, fill=0)
            self.epd.display(self.epd.getbuffer(self.image))
        except IOError as e:
            logging.info(e)

    def displayRoundTime(self, round, speed, dir, bestimelist, roundtimeslist):
        try:
            column = 0
            yoffset = 0
            xoffset = 5
            self.clearImage()
            string = 'ROUND ' + round
            string += ' - ' + '{:.0f}'.format(speed) + 'm/s, ' + '{:.0f}'.format(dir) + '°'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            for besttime in bestimelist:
                if 'run' in besttime:
                    string = 'Grp : ' + str(besttime['gp']) + ' - ' + besttime['run'].split('\t')[0]
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
                string = pilot[0] + '-' + pilot[1] + ' :' + pilot[2]
                stringsize = self.font24.getsize(string)
                if stringsize[1] > yoffsetMax:
                    yoffsetMax = stringsize[1]
            for pilot in roundtimeslist:
                string = pilot[0] + '-' + pilot[1] + ' :' + pilot[2]
                stringsize = self.font24.getsize(string)

                # check if pilot name length is ok in 2 column display
                if stringsize[0] > (self.epd.width / 2 - 4):
                    string = pilot[0] + '-' + pilot[1][:int(
                        len(pilot[1]) * (self.epd.width / 2 - 4) / stringsize[0]) - 1] + '. :' + pilot[2]

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

    def displayWeather(self, x, min, moy, max, dir):
        try:
            yoffset = 0
            self.clearImage()
            string = 'WEATHER STATION'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1

            if len(moy) > 0:
                string = '{:.0f}'.format(moy[-1]) + ' m/s'
                if len(dir) > 0:
                    string += ', {:.0f}'.format(dir[-1]) + '°'
                stringsize = self.font24.getsize(string)
                self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24, fill=0)
                yoffset += stringsize[1] + 1
                imgPlot = self.displayWeatherGraph(0, yoffset, x, min, moy, max, dir)
                self.image.paste(imgPlot, (0, yoffset))
            else:
                string = 'Waiting data'
                stringsize = self.font24.getsize(string)
                self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24, fill=0)
                yoffset += stringsize[1] + 1
            self.epd.display(self.epd.getbuffer(self.image))
        except IOError as e:
            logging.info(e)

    def displayWeatherGraph(self, xoffset, yoffset, x, min, moy, max, dir):
        fig = go.Figure()
        fig.update_layout(
            autosize=False,
            width=self.epd.width - xoffset,
            height=self.epd.height - yoffset,
            margin=dict(
                l=2,
                r=10,
                b=2,
                t=10,
                pad=4
            ),
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis=dict(
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(0, 0, 0)',
                linewidth=2,
                ticks='inside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='rgb(0, 0, 0)',
                ),
            ),
            yaxis=dict(
                showgrid=True,
                zeroline=False,
                showline=True,
                showticklabels=True,
                ticklabelposition="inside bottom",
                linecolor='rgb(0, 0, 0)',
                linewidth=2,
                ticks='',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='rgb(0, 0, 0)',
                ),
                autorange=False,
                range=[0, 30.5],
                gridcolor="grey",
            ),
        )
        fig.add_trace(go.Scatter(
            x=x + x[::-1],
            y=max + min[::-1],
            fill='toself',
            fillcolor='rgba(0,0,0,0.3)',
            line_color='rgba(0,0,0,0)',
            showlegend=False,
            name='Fair',
        ))
        fig.add_trace(go.Scatter(
            x=x, y=moy,
            line_color='rgb(0,0,0)',
            showlegend=False,
            name='Fair',
        ))
        buf = io.BytesIO()
        plotio.write_image(fig, buf, 'png', scale=1)
        buf.seek(0)
        return Image.open(buf)

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
            self.draw.text((int(self.epd.width / 2 - stringsize0[0] / 2), self.epd.height / 2 - stringsize0[1]),
                           string0,
                           font=self.font35, fill=0)
            self.draw.text((int(self.epd.width / 2 - stringsize1[0] / 2), self.epd.height / 2 + stringsize1[1]),
                           string1,
                           font=self.font35, fill=0)
            self.epd.display(self.epd.getbuffer(self.image))
            self.image.close()
        except IOError as e:
            logging.info(e)


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
            self.epd = epd7in5_V2.EPD()
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

    def displayPilot(self, round, speed, dir, besttimelist, pilotlist, page=0,
                     weatherx=None, weathermin=None, weathermax=None, weathermoy=None, weatherdir=None):
        try:

            column = 0
            yoffset = 0
            xoffset = 5
            self.clearImage()
            string = 'ROUND ' + round

            string += ' - ' + '{:.0f}'.format(speed) + 'm/s, ' + '{:.0f}'.format(dir) + '°'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            for besttime in besttimelist:
                if 'run' in besttime:
                    string = 'Grp : ' + str(besttime['gp']) + ' - ' + besttime['run'].split('\t')[0]
                else:
                    string = 'Grp : ' + str(besttime['gp']) + ' - ' + "No time availables"
                stringsize = self.font24.getsize(string)
                self.draw.text((int(self.epd.width / 2 - stringsize[0] / 2), yoffset), string, font=self.font24, fill=0)
                yoffset += stringsize[1] + 1

            yoffsetMax = 0
            stringsizemax = 0
            # search yoffset Max
            for pilot in pilotlist:
                string = str(pilot['bib']) + ' : ' + pilot['pil']
                stringsize = self.font24.getsize(string)
                if stringsize[1] > yoffsetMax:
                    yoffsetMax = stringsize[1]
                if stringsize[0] > stringsizemax - 15:
                    stringsizemax = stringsize[0] + 15

            yoffset_title = yoffset
            string = 'REMAINING:'
            stringsize = self.font35.getsize(string)
            self.draw.text((int(stringsizemax / 2 - stringsize[0] / 2), yoffset), string, font=self.font35, fill=0)
            yoffset += stringsize[1] + 1
            yoffset_pilot = yoffset

            print("num pilotlist : " + str(len(pilotlist)))
            for pilot in pilotlist:
                string = str(pilot['bib']) + ' : ' + pilot['pil']
                stringsize = self.font24.getsize(string)

                # check if pilot name length is ok in 2 column display
                if stringsize[0] > (self.epd.width / 2 - 4):
                    string = string[:int(len(string) * (self.epd.width / 2 - 4) / stringsize[0]) - 1] + '.'

                # Check end of display height and width
                if yoffset + yoffsetMax > self.epd.height:
                    break  # display only one column
                self.draw.text((xoffset, yoffset), string, font=self.font24, fill=0)
                yoffset += yoffsetMax + 1
            self.draw.line([(stringsizemax, yoffset_pilot), (stringsizemax, yoffset)], fill='black', width=0)
            self.displayWeatherInRemaining(stringsizemax + 5, yoffset_title, weatherx, weathermin, weathermoy,
                                           weathermax, weatherdir)

            self.epd.display(self.epd.getbuffer(self.image))
        except IOError as e:
            logging.info(e)

    def displayWeatherInRemaining(self, xdisplay, ydisplay, x, min, moy, max, dir):
        try:
            xoffset = xdisplay
            yoffset = ydisplay
            string = 'WEATHER STATION'
            stringsize = self.font35.getsize(string)
            self.draw.text((int((self.epd.width - xoffset) / 2 - stringsize[0] / 2 + xoffset), yoffset), string,
                           font=self.font35, fill=0)
            yoffset += stringsize[1] + 1

            if len(moy) > 0:
                string = '{:.0f}'.format(moy[-1]) + ' m/s'
                if len(dir) > 0:
                    string += ', {:.0f}'.format(dir[-1]) + '°'
                stringsize = self.font24.getsize(string)
                self.draw.text((int((self.epd.width - xoffset) / 2 - stringsize[0] / 2 + xoffset), yoffset), string,
                               font=self.font24, fill=0)
                yoffset += stringsize[1] + 1
                imgPlot = self.displayWeatherGraph(xoffset, yoffset, x, min, moy, max, dir)
                self.image.paste(imgPlot, (xoffset, yoffset))
            else:
                string = 'Waiting data'
                stringsize = self.font24.getsize(string)
                self.draw.text((int((self.epd.width - xoffset) / 2 - stringsize[0] / 2 + xoffset), yoffset), string,
                               font=self.font24, fill=0)
                yoffset += stringsize[1] + 1
        except IOError as e:
            logging.info(e)


class EpaperDefault(Epaper):
    def __init__(self, slot_shutdown, slot_page, slot_page_down):
        super().__init__()

        rpi = is_running_on_pi()
        if rpi:
            logging('not supported')
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
