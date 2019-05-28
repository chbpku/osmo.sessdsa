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
import math


class Player():

    def __init__(self, id, arg=None):
        self.id = id
        self.oppo = int(1 - id)
        self.counter = 0
        self.adjacentRange = 7
        self.target = 0
        self.jet = 0
        self.orientation = 0

    def strategy(self, allcells):
        self.adjacentRange = 20 + allcells[self.id].radius * 10  # 需要根据半径和速度修改
        # print(self.id)
        # print(allcells[self.id].radius)
        relaCells = list(self.relaInfo(allcells))
        adjacent = list(self.adjacentInfo(relaCells))
        dangerRange = self.safeCheck(relaCells, adjacent)
        # print(dangerRange)
        if dangerRange == None:
            # 周边环境比较安全
            if self.counter == 0 and self.jet == 0:
                self.chase(adjacent,allcells)
            if self.jet > 0:
                self.jet -= 1
                if self.jet == 0:
                    self.counter = 15
                return self.orientation
            else:
                if self.counter > 0:
                    self.counter = self.counter - 1
                    return None
                pass

        else:
            # 考虑规避风险
            self.jet = 4
            self.orientation = dangerRange[0]
            self.counter = 0
            return self.orientation

    class Cell():

        def __init__(self, id=None, pos=[0, 0], veloc=[0, 0], radius=5):
            # ID to judge Player or free particle
            self.id = id
            # Variables to hold current position
            self.pos = pos
            # Variables to hold current velocity
            self.veloc = veloc
            # Variables to hold size
            self.radius = radius

    def relaInfo(self, originCells):
        # 修正为自己不动，在最中间
        relaCells = []
        for cell in originCells:
            if not cell.dead:
                rpx = cell.pos[0] - originCells[self.id].pos[0]
                rpy = cell.pos[1] - originCells[self.id].pos[1]
                rvx = cell.veloc[0] - originCells[self.id].veloc[0]
                rvy = cell.veloc[1] - originCells[self.id].veloc[1]
                if rpx > 500:
                    rpx -= 1000
                if rpx < -500:
                    rpx += 1000
                if rpy > 250:
                    rpy -= 500
                if rpy < -250:
                    rpy += 250
                tmp = self.Cell(cell.id, [rpx, rpy], [rvx, rvy], cell.radius)
                relaCells.append(tmp)
        return relaCells

    def adjacentInfo(self, cells):
        # 侦测周边星体
        adjacent = []
        for cell in cells:
            if (cell.pos[0] * cell.pos[0] + cell.pos[1] * cell.pos[1]) ** 0.5 < self.adjacentRange:
                if cell.radius > 5 + cells[self.id].radius * 0.15:
                    adjacent.append(cell)
                    # print(cell.radius)
        return adjacent

    def safeCheck(self, cells, adjacent):
        # 返回一个列表，为不能喷射的指向，没有危险返回None
        dangerRange = []
        for cell in adjacent:
            # print(cells[self.id].radius)
            # print(cell.radius)
            if cell.radius < cells[self.id].radius * 0.95:
                continue
            '''
            if not (cell.pos[0] * cell.veloc[0] < 0 and cell.pos[1] * cell.veloc[
                1] < 0):  # 此步判断的必要性：如果比我大，为什么它远离我我也要往那个方向？
                continue
            '''
            if (cell.pos[0] * cell.pos[0] + cell.pos[1] * cell.pos[1]) ** 0.5 < self.adjacentRange * 0.3:
                ang = math.atan2(cell.pos[0], cell.pos[1])
                if ang < 0:
                    ang += 2 * math.pi
                # print(cell.pos[0], cell.pos[1], ang)
                dangerRange.append(ang)
        if dangerRange == []:
            return None
        else:
            return dangerRange

    def ontrack(self,  other, allcells):
        # 余弦定理算速度与位置连线夹角
        vectormultiple=other.veloc[0]*(-other.pos[0])+other.veloc[1]*(-other.pos[1])
        numbermultiple=(other.pos[0]*other.pos[0]+other.pos[1]*other.pos[1])**0.5*(other.veloc[0]*other.veloc[0]+other.veloc[1]*other.veloc[1])**0.5
        ang=math.acos(vectormultiple/numbermultiple)

        if allcells[self.id].radius + other.radius <= (
                other.pos[0] * other.pos[0] + other.pos[1] * other.pos[1]) ** 0.5 * math.sin(ang):
            return True
        else:
            return False

    def iscloser(self, other):
        return (other.pos[0] * other.pos[0] + other.pos[1] * other.pos[1]) ** 0.5 > (
                    (other.pos[0] + other.veloc[0] * 3) * (other.pos[0] + other.veloc[0] * 3) + (
                        other.pos[1] + other.veloc[1] * 3) * (other.pos[1] + other.veloc[1] * 3)) ** 0.5

    def isclear(self,other,allcells):
        if self.ontrack(other,allcells):
            return False
        else:
            return True

    def chase(self, adjacent,allcells):
        orderedcells=sorted(adjacent, key = lambda cell: cell.radius)
        biggercell=[]
        temp=0

        for cell in orderedcells[::-1]:
            temp+=1
            if cell.raidus>allcells[self.id]*0.95:
                biggercell.append(cell)

            if cell.raidus<adjacent[0].radius*0.95:
                break
        if temp==len(orderedcells):
            pass
        else:
            target=orderedcells[-temp]
            if self.ontrack(target,allcells):
                if len(biggercell)==0:
                    target = orderedcells[-2]
                    changeangle = 2 * math.atan2((target.pos[0] * target.pos[0] + target.pos[1] * target.pos[1]) ** 0.5,
                                                 target.radius)  # 改变角度
                    while not self.ontrack(target, allcells):
                        self.jet = 5
                        ang = math.atan2(target.pos[0], target.pos[1])
                        if ang < 0:
                            ang += 2 * math.pi
                        self.orientation = ang
                else:
                    for cell in biggercell:
                        if self.ontrack(cell,allcells):
                            break
                        changeangle = 2 * math.atan2(
                            (target.pos[0] * target.pos[0] + target.pos[1] * target.pos[1]) ** 0.5,
                            target.radius)  # 改变角度
                        while not self.ontrack(target, allcells):
                            self.jet = 5
                            ang = math.atan2(target.pos[0], target.pos[1])
                            if ang < 0:
                                ang += 2 * math.pi
                            self.orientation = ang








        '''
        maxcell = self.Cell(-1, [0, 0], [0, 0], 0)
        submax = self.Cell(-1, [0, 0], [0, 0], 0)
        for cell in adjacent:
            if cell.radius > maxcell.radius:
                if not cell.radius == adjacent[0].radius:
                    maxcell = cell
        for cell in adjacent:
            if cell.radius > submax.radius and cell.radius < maxcell.radius:
                submax = cell
        if maxcell.pos[0] * maxcell.veloc[0] + maxcell.pos[1] * maxcell.veloc[1] < 5 and submax.radius > adjacent[
            0].radius * 0.6:
            self.jet = 5
            ang = math.atan2(-maxcell.pos[0], -maxcell.pos[1])
            if ang < 0:
                ang += 2 * math.pi
            self.orientation = ang
            pass
        elif submax.pos[0] * submax.veloc[0] < 0 and submax.pos[1] * submax.veloc[1] < 0 and submax.radius > adjacent[
            0].radius * 0.6:
            self.jet = 5
            ang = math.atan2(-submax.pos[0], -submax.pos[1])
            if ang < 0:
                ang += 2 * math.pi
            self.orientation = ang
        '''
