# -*- coding: utf-8 -*-
# This file is part of AYAB.
#
#    AYAB is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    AYAB is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with AYAB.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright 2014 Sebastian Oliva, Christian Obersteiner, Andreas Müller, Christian Gerbrandt
#    https://github.com/AllYarnsAreBeautiful/ayab-desktop

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from bitarray import bitarray
import numpy as np


class Progress:
    """Knitting progress window.

    @author Tom Price
    @date   June 2020
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.current_row = -1
        self.total_rows = -1
        self.repeats = -1
        self.colorSymbol = ""
        self.hall_l = 0
        self.hall_r = 0
        self.carriage_type = ""
        self.carriage_position = 0
        self.lineNumber = -1
        self.color = -1
        self.alt_color = None
        self.bits = bitarray()

    def get_carriage_info(self, msg):
        hall_l = int((msg[2] << 8) + msg[3])
        hall_r = int((msg[4] << 8) + msg[5])

        if msg[6] == 1:
            carriage_type = "K Carriage"
        elif msg[6] == 2:
            carriage_type = "L Carriage"
        elif msg[6] == 3:
            carriage_type = "G Carriage"
        else:
            carriage_type = ""

        carriage_position = int(msg[7])

        self.hall_l = hall_l
        self.hall_r = hall_r
        self.carriage_type = carriage_type
        self.carriage_position = carriage_position


class KnitProgress:

    def __init__(self, parent):
        self.area = parent.area
        self.area.setContentsMargins(1, 1, 1, 1)

    def reset(self):
        self.container = QtWidgets.QWidget()
        self.container.setMinimumSize(100,100)
        self.grid = QtWidgets.QGridLayout(self.container)
        self.grid.setContentsMargins(1, 1, 1, 1)
        self.grid.setSpacing(0)
        self.grid.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.area.setWidget(self.container)
        self.row = -1

    def update(self, progress, row_multiplier):
        if progress.current_row < 0:
            return
        row, swipe = divmod(progress.lineNumber, row_multiplier)
        direction = progress.lineNumber % 2
        # row
        w0 = self.__label("Row")
        self.grid.addWidget(w0, progress.lineNumber, 0)
        w1 = self.__label(str(progress.current_row))
        self.grid.addWidget(w1, progress.lineNumber, 1, 1, 1, Qt.AlignRight)
        # pass
        w2 = self.__label("Pass " + str(swipe + 1))
        self.grid.addWidget(w2, progress.lineNumber, 2)
        # color
        if progress.colorSymbol == "":
            coltext = ""
        else:
            coltext = "Color " + progress.colorSymbol
        w3 = self.__label(coltext)
        self.grid.addWidget(w3, progress.lineNumber, 3)
        # carriage and direction
        try:
            carriage = progress.carriage[0] + progress.carriage[2] + " "
        except:
            carriage = ""
        w4 = self.__label(carriage + ["\u2192 ","\u2190 "][direction])
        self.grid.addWidget(w4, progress.lineNumber, 4)
        # TODO: hints, notes, memos
        w0.show()
        w1.show()
        w2.show()
        w3.show()
        w4.show()
        self.area.ensureWidgetVisible(w0)
        # graph line of stitches
        for c in range(len(progress.bits)):
            wc = self.__stitch(progress.color, progress.bits[c], progress.alt_color)
            self.grid.addWidget(wc, progress.lineNumber, 6 + c)
        return
        
    def __label(self, text):
        table = "<table><tbody><tr height='12'><td style='font-weight: normal;'>" + text + "</td></tr></tbody></table>"
        label = QtWidgets.QLabel()
        label.setText(table)
        label.setTextFormat(Qt.RichText)
        return label
    
    def __stitch(self, color, bit, alt_color=None, symbol=0x20):
        table = "<table style='font-weight: normal;'><tbody><tr height='12'><td width='12' align='center' "
        if bit:
            table = table + "style='border: 1 solid black; color: #{:06x}; background-color: #{:06x};'>".format(self.__contrast_color(color), color) + chr(symbol)
        elif alt_color is not None:
            table = table + "style='border: 1 solid black; color: #{:06x}; background-color: #{:06x};'>".format(self.__contrast_color(alt_color), alt_color) + chr(symbol)
        else:
            table = table + "style='border: 1 dotted black;'>"
        table = table + "</td></tr></tbody></table>"
        label = QtWidgets.QLabel()
        label.setText(table)
        label.setTextFormat(Qt.RichText)
        return label
    
    # functions used to calculate contrasting text color
    def __rgb2array(self, color):
        return np.array([color // 0x1000, (color // 0x100) & 0xFF, color & 0xFF])
    
    def __greyscale(self, rgb):
        return np.dot([.299, .587, .114], rgb)
    
    def __contrast_color(self, color):
        return [0x000000,0xFFFFFF][self.__greyscale(self.__rgb2array(color)) < 0x80]
