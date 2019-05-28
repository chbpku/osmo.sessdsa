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

    def survive(self, allcells):
        for item in allcells:
            if allcells[self.id].distance_from(item) < allcells[self.id].radius + item.radius and allcells[self.id].radius < item.radius:
                dx = item.pos[0] - allcells[self.id].pos[0]
                dy = item.pos[1] - allcells[self.id].pos[1]
                return math.atan2(dx,dy)
        return None

    def attack(self, allcells):
        edibleList = []
        for item in allcells:
            if allcells[self.id].distance_from(item) < allcells[self.id].radius + item.radius + Consts["DELTA_VELOC"] * (1 - Consts["EJECT_MASS_RATIO"]) * Consts['FRAME_DELTA']\
                and allcells[self.id].radius < item.radius and item.radius > allcells[self.id].radius / 9:
                dx = allcells[self.id].pos[0] - item.pos[0]
                dy = allcells[self.id].pos[1] - item.pos[1]
                edibleList.append([math.atan2(dx,dy),item.radius])
        # 对edibleList进行优先度排序
        return edibleList[0][0]

    def moyu(self, allcells):
        allcells_sorted = sorted(allcells, key = lambda cell: cell.radius)
        temp = allcells_sorted[0]
        for item in allcells_sorted:
            if item.radius < allcells[self.id].radius:
                temp = item
            else:
                break
        if temp.radius < allcells[self.id].radius / 9:
            return None
        else:
            # 计算怎么更优地吃掉它
            pass

    def strategy(self, allcells):
        for item in allcells:
            item.move(Consts['FRAME_DELTA'])
        if self.survive(allcells):
            return self.survive(allcells)
        elif self.attack(allcells):
            return self.attack(allcells)
        else:
            return self.moyu(allcells)