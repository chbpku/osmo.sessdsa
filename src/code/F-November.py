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
from copy import deepcopy

class Player():
    def __init__(self, id, arg = None):
    	self.id = id
    	self.stop = 0
    	       
    def relative(self, cell1, cell2):
        dx = cell2.pos[0] - cell1.pos[0]
        dy = cell2.pos[1] - cell1.pos[1]
        vx = cell2.veloc[0] - cell1.veloc[0]
        vy = cell2.veloc[1] - cell1.veloc[1]

        dicx = {1: dx, 2: dx + Consts["WORLD_X"], 3: dx - Consts["WORLD_X"]}
        dicy = {1: dy, 2: dy + Consts["WORLD_Y"], 3: dy - Consts["WORLD_Y"]}
        ddx = dicx[sorted(dicx, key = lambda x: abs(dicx[x]))[0]]
        ddy = dicy[sorted(dicy, key = lambda x: abs(dicx[x]))[0]]

        rcell = Cell(cell2.id, [ddx, ddy], [vx, vy], cell2.radius)

        return rcell

    def ifeat(self, cell1, cell2):
        dx = self.relative(cell1, cell2).pos[0]
        dy = self.relative(cell1, cell2).pos[1]
        vx = self.relative(cell1, cell2).veloc[0]
        vy = self.relative(cell1, cell2).veloc[1]

        distance = cell1.distance_from(cell2)
        r = (cell1.radius + cell2.radius) * 1.1
        if math.sqrt(vx ** 2 + vy ** 2) == 0:
            return False
        if r > distance:
            return True
        cos1 = math.sqrt(1 - (r / distance) ** 2)
        cos2 = - (dx * vx + dy * vy) / (math.sqrt(dx ** 2 + dy ** 2) * math.sqrt(vx ** 2 + vy ** 2))

        if cos1 >= cos2:
            return False
        else:
            return True

    
    def littleworld(self, depth, allcells):
        reallcells = []
        sheld = []
        for cell in allcells:
            sheld.append(self.relative(allcells[self.id], cell))
        reallcells = [cell for cell in sheld if (math.sqrt(cell.pos[0] ** 2 + cell.pos[1] ** 2) < 18 * allcells[self.id].radius and cell.radius > allcells[self.id].radius * 0.1 and not(cell.id == self.id))]
        self.cells = reallcells
        self.t = 45
        #记录每个角的碰撞情况
        Tcells = []
        TcellsX = []
        for i in range(self.t):
            Tcells.append([])
            TcellsX.append([])
        for i in range(depth):
            r = 0.075 * i * (i - 1)
            radius = allcells[self.id].radius * (0.99 ** (i / 2))
            
            frame_delta = Consts["FRAME_DELTA"]
            for cell in self.cells:
                cell.pos = [cell.pos[0] + cell.veloc[0] * frame_delta, cell.pos[1] + cell.veloc[1] * frame_delta]
                d = math.sqrt(cell.pos[0] ** 2 + cell.pos[1] ** 2)
                if d < r + radius + cell.radius and d > r - radius - cell.radius:
                    for j in range(self.t):
                        a = j * 2 * math.pi / self.t
                        if len([cell2 for cell2 in Tcells[j] if cell.id == cell2[1].id]) > 0 or len([cell2 for cell2 in TcellsX[j] if cell.id == cell2[1].id]) > 0:
                            continue
                        dr = [cell.pos[0] - r * math.cos(a), cell.pos[1] - r * math.sin(a)]
                        Dr = math.sqrt(dr[0] ** 2 + dr[1] ** 2)
                        if Dr < radius + cell.radius - 8:
                            if radius > cell.radius * 1.06:
                                Tcells[j].append([i, deepcopy(cell)])
                        elif radius <= cell.radius:
                            if Dr < radius + cell.radius:
                                TcellsX[j].append([i, deepcopy(cell)])
        #计算每个角的收益
        benifit = []
        danger = []
        for i in range(self.t):
            beni = 0
            if len(Tcells[i]) == 0:
                benifit.append([i, beni])
                continue
            if len(TcellsX[i]) > 0 and TcellsX[i][0][0] < Tcells[i][0][0]:
                benifit.append([i, beni])
                continue
            for j in range(len(Tcells[i])):
                n = Tcells[i][j][0]
                cell = Tcells[i][j][1]
                radius = allcells[self.id].radius * (0.99 ** ( n / 2))
                beni = (cell.radius ** 2 + radius ** 2 -  allcells[self.id].radius ** 2) * (0.1 ** j) + beni
            benifit.append([i, beni])        
        maxb = sorted(benifit, key = lambda ben: ben[1])[-1]
        return maxb
    
    def strategy(self, allcells):
        #判断是不是安全的
        newrad = allcells[self.id].radius * Consts["EJECT_MASS_RATIO"] ** 0.5
        rangecells = [cell for cell in allcells if cell.distance_from(allcells[self.id]) < 7 * allcells[self.id].radius and cell.radius > newrad * 2 and not(cell.id == self.id) and cell.distance_from(allcells[self.id]) > allcells[self.id].radius + cell.radius]
        if len(rangecells) > 0:
            closecell = sorted(rangecells, key = lambda cell: cell.distance_from(allcells[self.id]))[0]
            if closecell.radius >= allcells[self.id].radius and self.ifeat(allcells[self.id], closecell):
                self.stop = 10
                return math.atan2(self.relative(allcells[self.id], closecell).pos[0], self.relative(allcells[self.id], closecell).pos[1])
        if self.stop != 0:
            self.stop -= 1
            return None
        
        n = int(math.sqrt(9 * allcells[self.id].radius / 0.075)) + 1
        pre = self.littleworld(n, allcells)
        v = math.sqrt(allcells[self.id].veloc[0] ** 2 + allcells[self.id].veloc[1] ** 2)
        if (pre[1] <= 25 or v > 2) and pre[1] < (allcells[self.id].radius ** 2) * 0.5 or pre[1] < (allcells[self.id].radius ** 2) * 0.05:
            return None
        else:
            a = pre[0] * 2 * math.pi / self.t
            return math.atan2(- math.cos(a), - math.sin(a))
 
