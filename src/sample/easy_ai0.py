#!/usr/bin/env python3

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
import random
import math

class Player():
    # only move to the smallers
    def __init__(self):
        pass

    def strategy(self, id, allcells):
        min_cell = sorted(allcells, key = lambda cell: cell.radius)[0]
        dx = abs(allcells[id].pos[0] - min_cell.pos[0])
        dy = abs(allcells[id].pos[1] - min_cell.pos[1])
        theta = math.atan(dx / dy)# this can be adjusted, only uses the dx and dy
        return theta
