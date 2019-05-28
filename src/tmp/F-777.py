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

# from consts import Consts
# from settings import Settings
# from cell import Cell
# import random
import math



class Player():
    def __init__(self, id, arg = None):
        self.id = id
    def getdistance(self,cell1,other):
        dx = cell1.pos[0] - other.pos[0]
        dy = cell1.pos[1] - other.pos[1]
        min_x = min(abs(dx), abs(dx +1000), abs(dx - 1000))
        min_y = min(abs(dy), abs(dy + 500), abs(dy - 500))
        return (min_x ** 2 + min_y ** 2) ** 0.5
    def strategy(self, allcells):
        delta_time = 3
        distancelist = []
        nearcellList = []
        warningList = []
        mycell = allcells[self.id]
        targetcell = None
        for cell in allcells:
            if self.getdistance(mycell,cell) - mycell.radius <50 :
                nearcellList.append(cell)
        sortlist = sorted(nearcellList, key=lambda cell: cell.distance_from(mycell))
        for target in sortlist:
            if target.id == mycell.id:
                continue
            elif target.radius >=mycell.radius * (1-0.01) :
                warningList.append(target)
                break
            elif target.radius < mycell.radius:
                targetcell = target
                break

        if len(warningList) >0:
            warningcell = warningList[0]
            newx = warningcell.pos[0] + 3 * warningcell.veloc[0]
            newy = warningcell.pos[1] + 3 * warningcell.veloc[1]
            mynewx = mycell.pos[0] + 3* mycell.veloc[0]
            mynewy = mycell.pos[1] + 3 *mycell.veloc[1]
            distance = ((mynewx-newx)**2 + (mynewy-newy)**2) **0.5
            if distance < mycell.radius + warningcell.radius +10:
                dx = -mycell.pos[0] + warningcell.pos[0]
                dy = -mycell.pos[1] + warningcell.pos[1]
                relative_theta = math.atan2(dy,dx)
                return  relative_theta
        else:
            if targetcell is None:
                return None
            else:
                v = (mycell.veloc[0] ** 2 + mycell.veloc[1] ** 2) ** 0.5

                newx2 = targetcell.pos[0] + 3 * targetcell.veloc[0]
                newy2 = targetcell.pos[1] + 3 * targetcell.veloc[1]
                mynewx = mycell.pos[0] + 3 * mycell.veloc[0]
                mynewy = mycell.pos[1] + 3 * mycell.veloc[1]
                distance1 = self.getdistance(mycell,targetcell)
                distance2 =  ((mynewx-newx2)**2 + (mynewy-newy2)**2) **0.5
                if distance1 >distance2 :
                    return None
                else:
                    dx = -mycell.pos[0] + targetcell.pos[0]
                    dy = -mycell.pos[1] + targetcell.pos[1]
                    relative_theta = math.atan2(dy, dx)
                    mycell_veloc_theta = math.atan2(mycell.pos[1],mycell.pos[0])

                    if abs(mycell_veloc_theta-relative_theta) > 0.5 * math.pi or v > 0.2:
                        return None
                    else:
                        return relative_theta + math.pi
