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
import datetime


class filewriter():
    def __init__(self):
        super().__init__()
        cur_path = os.path.dirname(__file__)

        filename = os.path.join(cur_path, 'data', str(datetime.date.today()) + " weather.txt")
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != exc.errno.EEXIST:
                    raise
        fileexits = os.path.isfile(filename)
        self.file = open(filename, "a", encoding='utf-8')
        if not fileexits:
            self.file.write("time;min; moy; max; dir;\n")

    def write_weather(self, min, moy, max, dir):
        try:
            self.file.write(str(datetime.datetime.now().time())+';{:.2f};{:.2f};{:.2f};{:.2f};\n'.format(
                min, moy, max, dir))
            self.file.flush()
            os.fsync(self.file.fileno())
        except (IOError, OSError):
            print("error file writing")

    def close(self):
        self.file.close()



if __name__ == '__main__':
    file = filewriter()
    file.write_weather(10,12,15,0)
    file.close()