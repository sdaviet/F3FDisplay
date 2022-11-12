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
import os
from PIL import Image, ImageDraw, ImageFont, ImageQt
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')



class graf:
    def __init__(self, size):
        super().__init__()
        self.font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        self.size = size
        self.image = Image.new('1', self.size, 255)  # 255: clear the frame
        self.draw = ImageDraw.Draw(self.image)
        self.plot = None
        self.axis = None


    def addplot(self, data):
        if self.axis == None:
            self.axis = axis(self.draw, data)

        self.clear

    def clearImage(self):
        self.draw.rectangle([(0, 0), self.size], fill=255)

    def show(self):
        self.image.show("test plot class")

class plot():
    def __init__(self, draw):
        super().__init__()
        self.draw = draw

    def add(self, data):
        print("plot")


class axis():
    def __init__(self, draw):
        super().__init__()
        self.draw = draw

    def setAxis(self, data):
        print("setAxis")

