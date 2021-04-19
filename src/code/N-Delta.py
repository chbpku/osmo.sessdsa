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
import random
import math

class Player():
    def __init__(self, id, arg = None):
        self.id = id


    def atk(self, allcells):    #这是进攻策略
        allcells = [cell for cell in allcells]
        mycell=allcells[0]
        targetA=[]
        for cell in allcells:
            if cell != mycell:
                if mycell.distance_from(cell) <= 3*mycell.radius:    #这是进攻时检索范围，暂设为3倍自身半径
                    if cell.radius < mycell.radius:
                        targetA.append(cell)
        if len(targetA)>=1:
            max_cell = sorted(targetA, key=lambda cell: cell.radius)[-1]    #当范围内有多个可进攻目标时选择最大者
            if max_cell.radius > 0.2*mycell.radius:    #这是进攻时目标的半径下限，暂设为当目标半径小于自身的0.2倍时无视它
                dx = allcells[self.id].pos[0] - max_cell.pos[0]
                dy = allcells[self.id].pos[1] - max_cell.pos[1]
                return math.atan2(dx, dy) if random.random() > 0.4 else None    #进攻时设置了一个随机数以限制喷射的频率，暂设为0.4

    def defence(self, allcells):    #这是防守策略
        allcells = [cell for cell in allcells]
        mycell=allcells[0]
        targetB=[]
        for cell in allcells:
            if cell != mycell:
                if mycell.distance_from(cell) <= (2*mycell.radius+cell.radius):    #这是防守时检索范围，暂设为2倍自身半径外加1倍对方半径
                    if cell.radius > mycell.radius:
                        targetB.append(cell)
        if len(targetB)>=1:
            min_cell = sorted(targetB, key = lambda cell: cell.radius)[0]    #当范围内有多个需防守目标时选择最小者
            dx = min_cell.pos[0] - allcells[self.id].pos[0]
            dy = min_cell.pos[1] - allcells[self.id].pos[1]
            return math.atan2(dx, dy)    #防守时无需限制喷射频率
        else:
            return self.slow(allcells)    #其次执行限速策略

    def slow(self, allcells):    #这是限速策略
        allcells = [cell for cell in allcells]
        mycell=allcells[0]
        if mycell.veloc[0] >= 0.5 or mycell.veloc[1] >= 0.5:
            return math.atan2(mycell.veloc[0], mycell.veloc[1]) if random.random() > 0.7 else None    #限速时也设置了随机数限制喷射频率，暂设为0.7
        else:
            return self.atk(allcells) if random.random() > 0.7 else None    #最后执行进攻策略

    def winner(self):    #应为巩固胜局的策略
        return None

    def strategy(self, allcells):
        allcells = [cell for cell in allcells]
        mycell=allcells[0]
        j = 0
        for cell in allcells:
            if cell != mycell and cell.radius > mycell.radius:
                j += 1
        if j > 0:    #j值的定义和此if循环应为选择执行巩固胜局的策略
            return self.defence(allcells)    #优先执行防守策略
        else:
            return self.winner()
