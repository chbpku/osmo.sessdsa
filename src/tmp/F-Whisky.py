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
import random
import math



class Player():
    def __init__(self, id, arg = None):
        self.id = id

    def relative(self, cell1, cell2):
        dx = cell2.pos[0] - cell1.pos[0]
        dy = cell2.pos[1] - cell1.pos[1]
        vx = cell2.veloc[0] - cell1.veloc[0]
        vy = cell2.veloc[1] - cell1.veloc[1]

        dicx = {1: dx, 2: dx + Consts["WORLD_X"], 3: dx - Consts["WORLD_X"]}
        dicy = {1: dy, 2: dy + Consts["WORLD_Y"], 3: dy - Consts["WORLD_Y"]}
        ddx = dicx[sorted(dicx, key = lambda x: abs(dicx[x]))[0]]
        ddy = dicy[sorted(dicy, key = lambda x: abs(dicx[x]))[0]]

        rcell = Cell(None, [ddx, ddy], [vx, vy], cell2.radius)

        return rcell
        
    def ifeat(self, cell1, cell2):
        dx = relative(cell1, cell2).pos[0]
        dy = relative(cell1, cell2).pos[1]
        vx = relative(cell1, cell2).volec[0]
        vy = relative(cell1, cell2).volec[1]

        distance = cell1.dictance_from(cell2)
        r = cell1.radius + cell2.radius

        cos1 = math.sqrt(1 - (r / disrance) ** 2)
        cos2 = - (dx * vx + dy * vy) / (math.sqrt(dx ** 2 + dy ** 2) * math.sqrt(vx ** 2 + vy ** 2))

        if cos1 > cos2:
            return False
        else:
            return True

    def defence(self, max_cell, allcells):
        max_cell1 = self.relative(allcells[self.id], max_cell)
        vx = max_cell1.veloc[0]
        vy = max_cell1.veloc[1]
        v = math.sqrt(vx ** 2 + vy ** 2)
        
        if v < 0.1:
            return None
        else:
            return math.atan2(-vx, -vy)

    def strategy(self, allcells):
        newrad = allcells[self.id].radius * Consts["EJECT_MASS_RATIO"] ** 0.5
        allcells1 = [cell for cell in allcells if cell.radius > allcells[self.id].radius * 0.75]
        close_cell = sorted(allcells1, key = lambda cell: (cell.distance_from(allcells[self.id]) - cell.radius - allcells[self.id].radius))[1]
        max_cell = sorted(allcells1, key = lambda cell: cell.radius)[-1]
        min_cell = sorted(allcells1, key = lambda cell: cell.radius)[0]
        return self.defence(close_cell, allcells)
        if close_cell.radius > allcells[self.id].radius and ifeat(allcells[self.id], close_cell):
            return self.defence(close_cell, allcells)
        else:
            return None


