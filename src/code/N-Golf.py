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

fr = 0
lst_r = []
lst_al = []
lst_direc = []
bigger_cell_lst = []


class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.chase = None
        self.theta = None
        self.score = None
        self.frame = 0
        self.count = 0

    def canshu(self, cell, allcells):  # 统一计算可能用到的参数
        vx_rela = 3 * (cell.veloc[0] - allcells[self.id].veloc[0])  # x方向相对速度，修正
        vy_rela = 3 * (cell.veloc[1] - allcells[self.id].veloc[1])  # y方向相对速度，修正
        x0 = allcells[self.id].pos[0]
        y0 = allcells[self.id].pos[1]
        x1 = cell.pos[0]
        flag1 = True
        if abs(x0 - x1) > abs(x0 - x1 - 1000):  # 考虑边界相通情况，把非自己球坐标取为离自己的球“最近”的坐标
            xx1 = x1 + 1000
            flag1 = False
        elif abs(x0 - x1) > abs(x0 - x1 + 1000):
            xx1 = x1 - 1000
            flag1 = False
        if flag1 == False:
            x1 = xx1
        y1 = cell.pos[1]
        flag2 = True
        if abs(y0 - y1) > abs(y0 - y1 - 500):
            yy1 = y1 + 500
            flag2 = False
        elif abs(y0 - y1) > abs(y0 - y1 + 500):
            yy1 = y1 - 500
            flag2 = False
        if flag2 == False:
            y1 = yy1
        lst_return = [x1, y1, vx_rela, vy_rela]
        return lst_return

    def decide_danger(self, allcells):
        global bigger_cell_lst
        bigger_cell_lst = []
        x0 = allcells[self.id].pos[0]
        y0 = allcells[self.id].pos[1]
        for i in allcells:
            x1 = self.canshu(i, allcells)[0]
            y1 = self.canshu(i, allcells)[1]
            if i.radius > allcells[self.id].radius and (x0 - x1) ** 2 + (y0 - y1) ** 2 < allcells[
                self.id].radius ** 2 + i.radius ** 2 + 6400:
                bigger_cell_lst.append(i)  # 建立“大球列表”

        for cell in bigger_cell_lst:
            x1 = self.canshu(cell, allcells)[0]
            y1 = self.canshu(cell, allcells)[1]
            vx_rela = self.canshu(cell, allcells)[2]
            vy_rela = self.canshu(cell, allcells)[3]
            L = allcells[self.id].distance_from(cell)
            t = (vx_rela * (x0 - x1) + vy_rela * (y0 - y1)) / ((vx_rela ** 2 + vy_rela ** 2) ** 0.5 * (
                        (x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5)  # t等于cos（theta），theta即为相对速度矢量和相对位移矢量的夹角，余弦值用内积求得
            if (1 - t * t) * ((x0 - x1) ** 2 + (y0 - y1) ** 2) > 1.05 * (cell.radius + allcells[self.id].radius) ** 2:
                bigger_cell_lst.remove(cell)  # 暂不考虑这一秒从路径上来看基本可以错开或擦过、没有相撞危险的大球
            if cell.radius >= 30:
                if (cell.radius + allcells[self.id].radius) ** 2 - L ** 2 + L ** 2 * t * t >= 0 and L * t - (
                        (cell.radius + allcells[self.id].radius) ** 2 - L ** 2 + L ** 2 * t * t) ** 0.5 > 40 * (
                        vx_rela ** 2 + vy_rela ** 2) ** 0.5 and cell in bigger_cell_lst:
                    bigger_cell_lst.remove(cell)  # 暂不考虑还没有紧迫的相撞危险的大球（太大的球不能不考虑）
            else:
                if (cell.radius + allcells[self.id].radius) ** 2 - L ** 2 + L ** 2 * t * t >= 0 and L * t - (
                        (cell.radius + allcells[self.id].radius) ** 2 - L ** 2 + L ** 2 * t * t) ** 0.5 > 20 * (
                        vx_rela ** 2 + vy_rela ** 2) ** 0.5 and cell in bigger_cell_lst:
                    bigger_cell_lst.remove(cell)  # 暂不考虑还没有紧迫的相撞危险的大球
        if len(bigger_cell_lst) != 0:
            cell_boss = bigger_cell_lst[0]
            return (cell_boss)  # 需要躲避的那个大球
        else:
            return False  # safe

    def escape(self, boss, allcells):
        boss = self.decide_danger(allcells)
        x0 = allcells[self.id].pos[0]
        y0 = allcells[self.id].pos[1]
        x1 = self.canshu(boss, allcells)[0]
        y1 = self.canshu(boss, allcells)[1]
        vx_rela = self.canshu(boss, allcells)[2]
        vy_rela = self.canshu(boss, allcells)[3]
        if x1 - x0 > 0:
            direction = math.atan((y1 - y0) / (x1 - x0))  # 大概方向是直接向需要躲避的大球中心发射，防止自己被大球吞噬
        else:
            direction = math.atan((y1 - y0) / (x1 - x0)) + math.pi  # 考虑atctan值域 修正
        if boss.id == 1 - self.id:  # 如果被对方追，不要直接送死
            direction += math.pi / 6
        return math.pi / 2 - direction  # 考虑到游戏后台安排将返回值角度定义为由y轴正向向x轴正向转过的角度，在此需要修正返回值

    def choosetarget(self, allcells):
        # 考虑球的质量、距离、相对靠近、相对速度，赋予权重计算分数，并添加进入目标球列表
        targetlst = []
        for cell in allcells:
            score = 0
            if 0.95 * allcells[self.id].radius > cell.radius > 0.15 * allcells[self.id].radius:
                vx_rela = cell.veloc[0] - allcells[self.id].veloc[0]
                vy_rela = cell.veloc[1] - allcells[self.id].veloc[1]
                v_rela = vx_rela ** 2 + vy_rela ** 2

                px_rela = cell.veloc[0] * allcells[self.id].veloc[0]
                py_rela = cell.veloc[1] * allcells[self.id].veloc[1]

                # dx = min
                x1 = self.canshu(cell, allcells)[0]
                if px_rela <= 0 and py_rela <= 0 and (x1 - allcells[self.id].pos[0]) * allcells[self.id].veloc[
                    0] >= 0:
                    score = 15 * cell.radius - allcells[self.id].distance_from(cell) + 15 + 5 * v_rela
                elif px_rela <= 0 and py_rela <= 0 and (x1 - allcells[self.id].pos[0]) * \
                        allcells[self.id].veloc[0] <= 0:
                    score = 15 * cell.radius - allcells[self.id].distance_from(cell) - 15 + -5 * v_rela
                elif px_rela >= 0 and py_rela >= 0:
                    score = 15 * cell.radius - allcells[self.id].distance_from(cell) + 10
                elif px_rela >= 0 and py_rela <= 0 or (px_rela <= 0 and py_rela >= 0):
                    score = 15 * cell.radius - allcells[self.id].distance_from(cell) - 15 + -5 * v_rela

                targetlst.append([cell, score])

        if targetlst == []:  # 如果目标球列表为空
            intchase = None
            chooselst = None
            self.chase = None
            self.score = None
        else:  # 如果目标球列表不为空，初始目标球为离自己最近的球，之后将目标球更新为分数最高的球
            intchase = sorted(targetlst, key=lambda x: allcells[self.id].distance_from(x[0]))[0][0]
            chooselst = list(sorted(targetlst, key=lambda x: x[1], reverse=True))
            self.chase = chooselst[0][0]
            self.score = chooselst[0][1]

        return chooselst, intchase

    def chasetarget(self, allcells):
        # 考虑穿屏情况下的追赶方向
        x1 = self.canshu(self.chase, allcells)[0]
        y1 = self.canshu(self.chase, allcells)[1]
        dx = x1 + 10 * self.chase.veloc[0] - allcells[self.id].pos[0] - allcells[self.id].veloc[0]
        dy = y1 + 10 * self.chase.veloc[1] - allcells[self.id].pos[1] - allcells[self.id].veloc[1]
        if dy != 0:
            theta = math.atan2(dx, dy)
        else:
            theta = 0.5 * math.pi

        self.theta = theta + math.pi

        return theta + math.pi, allcells[self.id].distance_from(self.chase), allcells[self.id].veloc[0] ** 2 + \
               allcells[self.id].veloc[1] ** 2  # 返回追赶方向、离目标球距离和当前自身速度的平方

    def buddha(self, allcells):  # 自身在场上占据绝对优势时采取的策略
        remaining = 0
        for cell in allcells:
            if cell.id != self.id:
                remaining += cell.radius ** 2
        if allcells[self.id].radius ** 2 >= remaining:  # 自身的面积比场上剩余球的面积之和大
            return True

    def strategy(self, allcells):
        global fr
        if self.buddha(allcells):
            fr += 1
            return None
        if self.decide_danger(allcells) != False:
            fr += 1
            lst_r.append(allcells[self.id].radius)
            boss = self.decide_danger(allcells)
            return self.escape(boss, allcells)
        else:
            fr += 1
            self.chase = self.choosetarget(allcells)[1]  # 初始化目标球
            if allcells[self.id].distance_from(allcells[1 - self.id]) <= 100 and allcells[self.id].radius > 1.1 * \
                    allcells[1 - self.id].radius:  # 如果离对手方球很近且面积大于对手，则以对手为目标球
                self.chase = allcells[1 - self.id]
            if self.chase is not None:
                if self.chase.dead or self.score < self.choosetarget(allcells)[0][0][1] - 20:
                    self.chase = self.choosetarget(allcells)[0][0][0]  # 如果目标球被吞噬或者周围有更优的球，更新目标球
                if self.chasetarget(allcells)[1] < 2:  # 如果离目标球很近，停止发射
                    return None
                elif self.chasetarget(allcells)[2] > 0.2 and self.chasetarget(allcells)[1] < 10:  # 如果离目标球较近且速度较大，停止发射
                    return None
                elif self.chasetarget(allcells)[2] > 0.5:  # 如果自身速度较大，停止发射
                    return None
                elif self.score < 50:  # 如果周围没有特别值得追赶的球，停止发射
                    return None
                elif self.frame == 0:  # 每十帧停顿一帧
                    self.frame = 10
                    return None
                else:
                    self.frame -= 1
                    print(self.theta)
                    return self.theta
            else:
                return None
