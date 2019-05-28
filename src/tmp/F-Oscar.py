#!/usr/bin/env python3

#####################################################
#                                                   #
#     ______        _______..___  ___.   ______     #
#    /  __  \      /       ||   \/   |  /  __  \    #
#   |  |  |  |    |   (----`|  \  /  | |  |  |  |   #
#   |  |  |  |     \   \    |  |\/|  | |  |  |  |   #
#   |  `--'  | .----)   |   |  |  |  | |  `--'  |   #
#    \______/  |_______/    |__|  |__|  \______/    #
#                                                   #
#                                                   #
#####################################################

# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

from consts import Consts
from cell import Cell
import math

class Player():
    def __init__(self, id, arg = None):
    	self.id = id

    def escape(self,allcells):
        for i in range(5):
            cellCopy = allcells.copy()
            for item in cellCopy:
                item.move(i * Consts['FRAME_DELTA'])
            for item in cellCopy:
                if cellCopy[self.id].distance_from(item) < cellCopy[self.id].radius + item.radius and cellCopy[self.id].radius < item.radius:
                    dx = item.pos[0] - cellCopy[self.id].pos[0]
                    dy = item.pos[1] - cellCopy[self.id].pos[1]
                    return math.atan2(dx, dy)

    def attack(self,allcells):
        for i in range(5):
            cellCopy = allcells.copy()
            for item in cellCopy:
                item.move(i * Consts['FRAME_DELTA'])
            for item in cellCopy:
                if cellCopy[self.id].radius + item.radius < cellCopy[self.id].distance_from(item) < cellCopy[self.id].radius + item.radius + Consts["DELTA_VELOC"] * i * i * 9 * Consts["EJECT_MASS_RATIO"] / 2 \
                        and cellCopy[self.id].radius > item.radius > cellCopy[self.id].radius / 9:
                    dx = cellCopy[self.id].pos[0] - item.pos[0]
                    dy = cellCopy[self.id].pos[1] - item.pos[1]
                    return math.atan2(dx, dy)

    def strategy(self, allcells):
        if self.escape(allcells) != None:
            return self.escape(allcells)
        else:
            return self.attack(allcells)

