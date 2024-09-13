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
import io
import plotly.graph_objects as go
import plotly.io as plotio
from PyQt5.QtCore import QTimer, pyqtSignal
import ConfigReader
from PIL import Image, ImageDraw, ImageFont, ImageQt
from filewriter import filewriter
from UDPReceive import udpreceive

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
datadir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')

class weather(QTimer):
    weather_signal = pyqtSignal()
    weatherNbData_signal = pyqtSignal(int)

    def __init__(self, log=False):
        super().__init__()
        self.timerinterval = ConfigReader.config.conf['weather_timer_s']
        self.maxweatherdata = ConfigReader.config.conf['max_weather_data']

        self.udp = udpreceive(4445)
        self.udp.winddir_signal.connect(self.slot_winddir)
        self.udp.windspeed_signal.connect(self.slot_windspeed)
        self.file = None
        if log:
            self.file = filewriter()

        self.newdata()
        self.timeout.connect(self.slot_timer)
        self.start(self.timerinterval * 1000)
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
        self.data[5] += 1
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
            x.append(time * self.timerinterval / 60)
            time += 1
            min.append(i[0])
            moy.append(i[1] / i[2])
            max.append(i[3])
            if i[5] > 0:
                dir.append(i[4] / i[5])
        return x, min, moy, max, dir

    def getLastSpeed(self):
        if len(self.list) > 0:
            if self.list[-1][2] > 0:
                return self.list[-1][1] / self.list[-1][2]
        return None

    def getMoySpeed(self):
        moy = 0
        count = 0
        if len(self.list) > 0:
            for i in self.list:
                moy += i[1] / i[2]
                count += 1
            moy = moy / count
        return moy

    def getLastDir(self):
        if len(self.list) > 0:
            if self.list[-1][5] > 0:
                return self.list[-1][4] / self.list[-1][5]
        return None

    def createString(self):
        string=None
        speed = self.getLastSpeed()
        moyspeed = self.getMoySpeed()
        dir = self.getLastDir()
        if speed is not None:
            string = 'A:{:.0f}'.format(speed) + ',M:{:.0f}'.format(moyspeed) + 'm/s'
            if dir is not None:
                string += ',{:.0f}'.format(dir) + '°'
        return string

    def createGraph(self, width=160, height=160, asFile=False):
        x, min, moy, max, dir = self.getData()
        if len(min) <= 0:
            return (None)
        wstring = self.createString()
        if wstring is None:
            wstring = "Waiting Data"
        fig = go.Figure()
        fig.update_layout(
            autosize=False,
            width=width,  #self.epd.width - xoffset,
            height=height - 5,  #self.epd.height - yoffset,
            title=dict(text=wstring, x=0.5, xanchor= 'center', yanchor='middle',
                       font=dict(color="black", size=40)),
            margin=dict(l=2, r=10, b=2, t=40, pad=4),
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis=dict(
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(0, 0, 0)',
                linewidth=2,
                #ticklabelposition="inside",
                ticks='inside',
                tickfont=dict(
                    family='Arial Black',
                    size=16,
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
                    family='Arial Black',
                    size=16,
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
        #processing moy curves for each points
        moycurves = []
        moycurves.append(0)
        for i in moy:
            moycurves[0] = moycurves[0] + i
        moycurves[0] = moycurves[0] / len(moy)
        for i in range(1, len(moy)):
            moycurves.append(moycurves[0])
        fig.add_trace(go.Scatter(
            x=x, y=moycurves,
            mode="lines",
            line_color='rgb(0,0,0)',
            showlegend=False,
            name='Fair',
        ))

        if asFile==False:
            buf = io.BytesIO()
            plotio.write_image(fig, buf, 'png', scale=1)
            buf.seek(0)
            return Image.open(buf)
        else:
            filename = os.path.join(datadir, "weatherGraph.png")
            plotio.write_image(fig, filename, 'png', scale=1)
            return filename

    def weathertofile(self):
        x, min, moy, max, dir = self.getData()
        if len(min) > 0 and self.file is not None:
            self.file.write_weather(min[-1], moy[-1], max[-1], dir[-1])

    def close(self):
        if self.file is not None:
            self.file.close()