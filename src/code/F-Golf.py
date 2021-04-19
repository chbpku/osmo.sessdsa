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

    # 判断机制：路径分析，是否有碰撞的危险
    # 计算方程：（x1 + Vx1 * t - x2 - Vx2 * t）** 2 +（y1 + Vy1 * t - y2 - Vy2 * t）** 2 = （R1 + R2）** 2
    # 输入：allcells , 检测球在 allcells 里是第几个，之前碰撞危险列表
    # 输出：[ [ ...],...,[ 碰撞时间，碰撞球的ID ，躲避角度] ]
    def pathprediction(self, allcells, preid, lst, xborder, yborder, justpredict, time=0):

        posX_DValue = allcells[preid].pos[0] + 1000 * xborder - allcells[self.id].pos[0]
        posY_DValue = allcells[preid].pos[1] + 500 * yborder - allcells[self.id].pos[1]
        velocX_DValue = allcells[preid].veloc[0] - allcells[self.id].veloc[0]
        velocY_DValue = allcells[preid].veloc[1] - allcells[self.id].veloc[1]
        radius_sum = allcells[self.id].radius + allcells[preid].radius
        discriminant = 4 * (posX_DValue * velocX_DValue + posY_DValue * velocY_DValue) ** 2 - 4 * (
                velocX_DValue ** 2 + velocY_DValue ** 2) * (
                               posX_DValue ** 2 + posY_DValue ** 2 - radius_sum ** 2)
        if discriminant >= 0:  # 会有0/0的错误！！！！
            time1 = ((-2) * (
                    posX_DValue * velocX_DValue + posY_DValue * velocY_DValue) + discriminant ** 0.5) / (
                            2 * velocX_DValue ** 2 + 2 * velocY_DValue ** 2)
            time2 = ((-2) * (
                    posX_DValue * velocX_DValue + posY_DValue * velocY_DValue) - discriminant ** 0.5) / (
                            2 * velocX_DValue ** 2 + 2 * velocY_DValue ** 2)
            if time1 > 0 and time2 > 0:
                time = min(math.ceil(time1), math.ceil(time2))
            elif time1 < 0 and time2 > 0:
                time = math.ceil(time2)
            elif time2 < 0 and time1 > 0:
                time = math.ceil(time1)
            if time != 0:
                if justpredict is True:
                    return time, True
                else:
                    death_cell = [time, preid, math.atan2(posX_DValue, posY_DValue)]
                    lst.append(death_cell)
                    return lst
        if justpredict is True:
            return time, False
        else:
            return lst

    # 返回deathlist
    def eat_strategy(self, allcells, cellNum, lst, time):

        # 计算碰撞后新数据
        newradius = (allcells[cellNum].radius ** 2 + allcells[self.id].radius ** 2) ** 0.5
        newveloc0 = (allcells[cellNum].veloc[0] * (allcells[cellNum].radius ** 2) + allcells[self.id].veloc[0] * (
                    allcells[self.id].radius ** 2)) / (
                                allcells[self.id].radius ** 2 + allcells[cellNum].radius ** 2)
        newveloc1 = (allcells[cellNum].veloc[1] * (allcells[cellNum].radius ** 2) + allcells[self.id].veloc[1] * (
                allcells[self.id].radius ** 2)) / (
                            allcells[self.id].radius ** 2 + allcells[cellNum].radius ** 2)
        newpos0 = allcells[self.id].pos[0] + time * allcells[self.id].veloc[0]
        if newpos0 > 1000:
            newpos0 -= 1000
        elif newpos0 < 0:
            newpos0 += 1000
        newpos1 = allcells[self.id].pos[1] + time * allcells[self.id].veloc[1]
        if newpos1 > 500:
            newpos1 -= 500
        elif newpos1 < 0:
            newpos1 += 500

        for num in range(len(allcells)):
            if num != self.id:
                onewpos0 = allcells[num].pos[0] + time * allcells[num].veloc[0]
                if onewpos0 > 1000:
                    onewpos0 -= 1000
                elif onewpos0 < 0:
                    onewpos0 += 1000
                onewpos1 = allcells[num].pos[1] + time * allcells[num].veloc[1]
                if onewpos1 > 500:
                    onewpos1 -= 500
                elif onewpos1 < 0:
                    onewpos1 += 500

                if (newpos0 - onewpos0) ** 2 + (newpos1 - onewpos1) ** 2 <= (allcells[num].radius + newradius) ** 2 and newradius <= allcells[num].radius:
                    death_cell = [time, num, math.atan2(allcells[num].pos[0] - allcells[self.id].pos[0],
                                                        allcells[num].pos[1] - allcells[self.id].pos[1])]
                    lst.append(death_cell)

        return lst

    # 规避策略（输入：allcells，term）（输出：attackable,evade,angle）
    def evade_strategy(self, allcells):

        death_list = []  # 碰撞帧数，ID, 躲避角度
        detection_radius = 3 * allcells[self.id].radius + 2 * (
                allcells[self.id].veloc[0] ** 2 + allcells[self.id].veloc[
            1] ** 2) ** 0.5 + 50  # 检测半径(与球半径和速度相关)
        attackable, evade = False, False
        angle = 0

        # 检测机制：检测一定范围内有可能碰撞的球
        for cellNum in range(len(allcells)):
            boom, time = False, 0
            if allcells[cellNum].radius > allcells[self.id].radius:
                # 范围检测
                if (allcells[cellNum].pos[0] - allcells[self.id].pos[0]) ** 2 + (
                        allcells[cellNum].pos[1] - allcells[self.id].pos[1]) ** 2 <= detection_radius ** 2:
                    death_list = self.pathprediction(allcells, cellNum, death_list, 0, 0, False)
                # 穿墙检测
                if 1000 - allcells[self.id].pos[0] < detection_radius and allcells[cellNum].pos[0] < 250:
                    death_list = self.pathprediction(allcells, cellNum, death_list, 1, 0, False)
                if allcells[self.id].pos[0] < detection_radius and allcells[cellNum].pos[0] > 750:
                    death_list = self.pathprediction(allcells, cellNum, death_list, -1, 0, False)
                if 500 - allcells[self.id].pos[1] < detection_radius and allcells[cellNum].pos[1] < 175:
                    death_list = self.pathprediction(allcells, cellNum, death_list, 0, 1, False)
                if allcells[self.id].pos[1] < detection_radius and allcells[cellNum].pos[1] > 375:
                    death_list = self.pathprediction(allcells, cellNum, death_list, 0, -1, False)
                # 穿对角线检测
                if 1000 - allcells[self.id].pos[0] < detection_radius and 500 - allcells[self.id].pos[1] < detection_radius and allcells[cellNum].pos[0] < 250 and allcells[cellNum].pos[1] < 250:
                    death_list = self.pathprediction(allcells, cellNum, death_list, 1, 1, False)
                if 1000 - allcells[self.id].pos[0] < detection_radius and allcells[self.id].pos[1] < detection_radius and allcells[cellNum].pos[0] < 250 and allcells[cellNum].pos[1] > 250:
                    death_list = self.pathprediction(allcells, cellNum, death_list, 1, -1, False)
                if  allcells[self.id].pos[0] < detection_radius and allcells[self.id].pos[1] < detection_radius and allcells[cellNum].pos[0] > 750 and allcells[cellNum].pos[1] > 250:
                    death_list = self.pathprediction(allcells, cellNum, death_list, -1, -1, False)
                if  allcells[self.id].pos[0] < detection_radius and 500 - allcells[self.id].pos[1] < detection_radius and allcells[cellNum].pos[0] > 750 and allcells[cellNum].pos[1] < 250:
                    death_list = self.pathprediction(allcells, cellNum, death_list, -1, -1, False)
            # 被动吞噬检测
            if allcells[cellNum].radius < allcells[self.id].radius and allcells[cellNum].radius > allcells[self.id].radius / 99:
                if (allcells[cellNum].pos[0] - allcells[self.id].pos[0]) ** 2 + (
                        allcells[cellNum].pos[1] - allcells[self.id].pos[1]) ** 2 <= detection_radius ** 2:
                    time, boom = self.pathprediction(allcells, cellNum, death_list, 0, 0, True)
                # 穿墙检测
                if 1000 - allcells[self.id].pos[0] < detection_radius and allcells[cellNum].pos[0] < 250:
                    time, boom = self.pathprediction(allcells, cellNum, death_list, 1, 0, True)
                if allcells[self.id].pos[0] < detection_radius and allcells[cellNum].pos[0] > 750:
                    time, boom = self.pathprediction(allcells, cellNum, death_list, -1, 0, True)
                if 500 - allcells[self.id].pos[1] < detection_radius and allcells[cellNum].pos[1] < 175:
                    time, boom = self.pathprediction(allcells, cellNum, death_list, 0, 1, True)
                if allcells[self.id].pos[1] < detection_radius and allcells[cellNum].pos[1] > 375:
                    time, boom = self.pathprediction(allcells, cellNum, death_list, 0, -1, True)
                if boom is True:
                    death_list = self.eat_strategy(allcells, cellNum, death_list, time)

        # 规避决策
        if len(death_list) != 0:
            for i in range(len(death_list) - 1):  # 对碰撞时间排序，重置deathe_list
                for j in range(len(death_list) - 1 - i):
                    if death_list[j][0] > death_list[j + 1][0]:
                        death_list[j], death_list[j + 1] = death_list[j + 1], death_list[j]
            evade, angle = True, death_list[0][2]

        return attackable, evade, angle

    def strategy(self, allcells):
        attackable, evade, angle = self.evade_strategy(allcells)
        if evade is True:
            return angle #检验是否需要规避
        else:
            a = allcells[self.id]
            d = 100
            bigList = [cell for cell in allcells if
                       cell.radius < a.radius and (cell.distance_from(a) > 0 and cell.area() > a.area() / 99)]#场面上的所有价值较大的可吞噬的球
            searchTargets1 = [cell for cell in allcells if cell.radius < a.radius and (
                    (cell.distance_from(a) > 0 and cell.distance_from(a) < d) and cell.area() > a.area() / 99)]#较靠近玩家球的价值较大的可吞噬球
            srearchTarget = []
            for cell in bigList:
                srearchTarget.append(cell)
                if cell.pos[0] > a.pos[0]:
                    cell1 = cell.copy()
                    cell1.pos[0] -= 1000
                    srearchTarget.append(cell1)
                elif cell.pos[0] < a.pos[0]:
                    cell1 = cell.copy()
                    cell1.pos[0] += 1000
                    srearchTarget.append(cell1)
                if cell.pos[1] < a.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] += 500
                    srearchTarget.append(cell1)
                elif cell.pos[1] > a.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] -= 500
                    srearchTarget.append(cell1)
                if cell.pos[0] > a.pos[0] and cell.pos[1] > cell.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] -= 500
                    cell1.pos[0] -= 1000
                    srearchTarget.append(cell1)
                elif cell.pos[0] > a.pos[0] and cell.pos[1] < cell.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] += 500
                    cell1.pos[0] -= 1000
                    srearchTarget.append(cell1)
                elif cell.pos[0] < a.pos[0] and cell.pos[1] < cell.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] += 500
                    cell1.pos[0] += 1000
                    srearchTarget.append(cell1)
                elif cell.pos[0] < a.pos[0] and cell.pos[1] > cell.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] -= 500
                    cell1.pos[0] += 1000
                    srearchTarget.append(cell1)
            #跨界吞噬的暴力算法
            if len(srearchTarget) <= 45:#对与较为后期的一个策略改变
                targetList = []
                for cell in srearchTarget:
                    cell.pos[0] -= a.pos[0]
                    cell.pos[1] -= a.pos[1]
                    cell.veloc[0] -= a.veloc[0]
                    cell.veloc[1] -= a.veloc[1]
                    #修改坐标系
                    for i in range(1, 50):
                        cell.pos[0] += cell.veloc[0] * 3
                        cell.pos[1] += cell.veloc[1] * 3
                        crash = (cell.pos[0] ** 2 + cell.pos[1] ** 2) ** 0.5 <= cell.radius + a.radius
                        if crash:
                            return None
                         #50桢内不喷球能吃掉
                    for frame in range(1, 301):
                        cell.pos[0] += cell.veloc[0] * 3
                        cell.pos[1] += cell.veloc[1] * 3
                        i1 = math.atan2(-cell.pos[0], -cell.pos[1])
                        fx = math.sin(i1)
                        fy = math.cos(i1)
                        cell.veloc[0] += Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
                        cell.veloc[1] += Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
                        if (cell.pos[0] ** 2 + cell.pos[1] ** 2) ** 0.5 <= cell.radius + a.radius and cell.area() < a.area() * (
                                0.99 ** frame):
                            earn = cell.area() + a.area() * (0.99 ** frame) - a.area()
                            if earn > 0:
                                target = {'value': (cell.area() - a.area() * (1 - 0.99 ** frame)) / frame,
                                          'cost': frame,
                                          'theta': math.atan2(-cell.pos[0], -cell.pos[1]),
                                          }
                                targetList.append(target)
                                break
                        best_target = {}
                        if targetList:
                            best_target = sorted(targetList, key=lambda target: target['value'])[-1]
                        if best_target != {}:
                            return best_target['theta']
                        #1000桢内能否吞噬
                        else:
                            return None
            while len(searchTargets1) < 3 and d <= 1500:
                d += 50
                searchTargets1 = [cell for cell in allcells if cell.radius < a.radius and (
                        (cell.distance_from(a) > 0 and cell.distance_from(a) < d) and cell.area() > a.area() / 99)]
            srearchTargets = []
            targetList = []
            best_target = {}
            for cell in searchTargets1:
                srearchTargets.append(cell)
                if cell.pos[0] > a.pos[0]:
                    cell1 = cell.copy()
                    cell1.pos[0] -= 1000
                    srearchTargets.append(cell1)
                elif cell.pos[0] < a.pos[0]:
                    cell1 = cell.copy()
                    cell1.pos[0] += 1000
                    srearchTargets.append(cell1)
                if cell.pos[1] < a.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] += 500
                    srearchTargets.append(cell1)
                elif cell.pos[1] > a.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] -= 500
                    srearchTargets.append(cell1)
                if cell.pos[0] > a.pos[0] and cell.pos[1] > cell.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] -= 500
                    cell1.pos[0] -= 1000
                    srearchTargets.append(cell1)
                elif cell.pos[0] > a.pos[0] and cell.pos[1] < cell.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] += 500
                    cell1.pos[0] -= 1000
                    srearchTargets.append(cell1)
                elif cell.pos[0] < a.pos[0] and cell.pos[1] < cell.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] += 500
                    cell1.pos[0] += 1000
                    srearchTargets.append(cell1)
                elif cell.pos[0] < a.pos[0] and cell.pos[1] > cell.pos[1]:
                    cell1 = cell.copy()
                    cell1.pos[1] -= 500
                    cell1.pos[0] += 1000
                    srearchTargets.append(cell1)
                    #跨界吞噬检测
            for cell in srearchTargets:
                cell.pos[0] -= a.pos[0]
                cell.pos[1] -= a.pos[1]
                cell.veloc[0] -= a.veloc[0]
                cell.veloc[1] -= a.veloc[1]
                 #建立新的坐标系
                for i in range(1, 5):
                    cell.pos[0] += cell.veloc[0] * 3
                    cell.pos[1] += cell.veloc[1] * 3
                    crash = (cell.pos[0] ** 2 + cell.pos[1] ** 2) ** 0.5 <= cell.radius + a.radius
                    if crash:
                        target = {'value': cell.area(),
                                  'cost': i,
                                  'theta': None,
                                 }
                        targetList.append(target)
                for frame in range(1, 301):
                    cell.pos[0] += cell.veloc[0] * 3
                    cell.pos[1] += cell.veloc[1] * 3
                    i1 = math.atan2(-cell.pos[0], -cell.pos[1])
                    fx = math.sin(i1)
                    fy = math.cos(i1)
                    cell.veloc[0] += Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
                    cell.veloc[1] += Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
                    if (cell.pos[0] ** 2 + cell.pos[
                        1] ** 2) ** 0.5 <= cell.radius + a.radius and cell.area() < a.area() * (
                            0.99 ** frame):
                        earn = cell.area() + a.area() * (0.99 ** frame) - a.area()
                        if earn > 0:
                            target = {'value': (cell.area() - a.area() * (1 - 0.99 ** frame)) / frame,
                                      'cost': frame,
                                      'theta': math.atan2(-cell.pos[0], -cell.pos[1]),
                                      }
                            targetList.append(target)
                            break
            if targetList:
                best_target = sorted(targetList, key=lambda target: target['value'])[-1]
            if best_target != {}:
                return best_target['theta']
            else:
                return None