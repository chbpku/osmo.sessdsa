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
from math import pi, cos, sin, atan2, atan
from copy import deepcopy
from random import random
#################################################################
# 这是Bravo小组的代码，组员有言浩雄、孟繁博、李尚、陈泽欣、刘楚宁
# 参考代码可以查看sample中的brownian_motion.py和cxk.py
# allcells中是由Cell组成的类，Cell类定义和方法见cell.py
##################################################################


def NextFrame(allcells):
    #########
    # 陈泽欣 #
    #########
    # 输入所有星体的list，返回下一帧所有星体的状态
    # 注意这里allcells可以是部分星体列表
    # 可以参考world.py中的一些代码
    # 直接O(N^2)遍历即可
    pass


def ConvertTheta(theta):
    # 转换角度的函数，从和x轴的夹角转换到和y轴的夹角
    return pi / 2 - theta


def StayInBound(pos):
    if pos[0] < -Consts["WORLD_X"] / 2:
        pos[0] += Consts["WORLD_X"]
    if pos[0] >= Consts["WORLD_X"] / 2:
        pos[0] -= Consts["WORLD_X"]
    if pos[1] < -Consts["WORLD_Y"] / 2:
        pos[1] += Consts["WORLD_Y"]
    if pos[1] >= Consts["WORLD_Y"] / 2:
        pos[1] -= Consts["WORLD_Y"]


# 在一个参考系中deltat后的各个星系的状态
# 注意这个函数针对相对玩家静止参考系
# 没有考虑碰撞等因素
def MoveInMyReference(allcells, deltat):
    for i in range(len(allcells)):
        allcells[i].pos[0] += allcells[i].veloc[0] * deltat
        allcells[i].pos[1] += allcells[i].veloc[1] * deltat
        StayInBound(allcells[i].pos)


class Player():
    def __init__(self, id, arg=None):
        self.id = id  # 注意这里的id是0或者1，标记allcells里面哪一个是玩家操控的

    def LargerCells(self, allcells):
        #################
        # 孟繁博, yhxyan#
        #################
        # 输入所有星体的list，返回一个list，包含所有比自己大的星体
        mycell = allcells[self.id]
        largercells = []
        for cell in allcells:
            if cell.radius > mycell.radius and cell.dead == False:
                largercells.append(cell)
        return largercells

    def SmallerCells(self, allcells):
        #################
        # 孟繁博,yhxyan #
        #################
        # 输入所有星体的list，返回一个list，包含所有比自己小的星体
        mycell = allcells[self.id]
        smallercells = []
        for cell in allcells:
            if cell.radius < mycell.radius and cell.radius > mycell.radius*Consts[
                    "EJECT_MASS_RATIO"]**0.5 * 2 and cell.dead == False:
                smallercells.append(cell)
        return smallercells

    def CloserCells(self, L, allcells, inputcell=None):
        ##########
        # yhxyan #
        ##########
        # 输入所有星体的list，返回一个list，包含所有距离小于L的星体（注意边界）
        closercells = []
        if inputcell == None:
            mycell = allcells[self.id]
            for i in range(len(allcells)):
                if mycell.distance_from(allcells[i]) < L and allcells[
                        i].dead == False and i != self.id:
                    closercells.append(allcells[i])
        else:
            mycell = inputcell
            for i in range(len(allcells)):
                if mycell.distance_from(
                        allcells[i]) < L and allcells[i].dead == False:
                    closercells.append(allcells[i])
        return closercells

    def ChangeCoordinate(self, allcells):
        ##########
        # yhxyan #
        ##########
        # 给定allcells列表，返回新的列表，变换到以玩家静止的参考系
        mycell = allcells[self.id]
        new_allcells = deepcopy(allcells)
        for i in range(len(new_allcells)):
            new_allcells[i].pos[0] = new_allcells[i].pos[0] - mycell.pos[0]
            new_allcells[i].pos[1] = new_allcells[i].pos[1] - mycell.pos[1]
            new_allcells[i].veloc[
                0] = new_allcells[i].veloc[0] - mycell.veloc[0]
            new_allcells[i].veloc[
                1] = new_allcells[i].veloc[1] - mycell.veloc[1]
            StayInBound(new_allcells[i].pos)
        return new_allcells

    # 在自己的参考系里N帧后，喷射n次能达到的范围
    def WanderRangeInMyReference(self, allcells, n, N):
        delta_v = Consts["DELTA_VELOC"] * Consts[
            "EJECT_MASS_RATIO"]  # 每次喷射速度的变化量
        L = 0
        for i in range(n):
            L += delta_v * Consts["FRAME_DELTA"] * (N - i)
        return L

    def strategy(self, allcells):
        AllCellsInMyReference = self.ChangeCoordinate(allcells)  # 变换参考系后的list
        mycell = AllCellsInMyReference[self.id]
        othercell = AllCellsInMyReference[int(1 - self.id)]
        #========================================
        #################
        # 刘楚宁, yhxyan #
        #################
        # 首先判定是否需要弹射以避免吞噬
        # 若在N帧以后，会和比自己大的cell发生碰撞，这里需要弹射
        # 这里为简单起见，只处理最先碰到的大球，朝大球运动相对方向弹射
        SearchDepth = 20  # 搜索深度
        largercells = self.LargerCells(AllCellsInMyReference)
        for N in range(SearchDepth):
            MoveInMyReference(largercells, Consts["FRAME_DELTA"])
            for largercell in largercells:
                if mycell.collide(largercell):
                    if N < 10:
                        theta = atan2(largercell.pos[1], largercell.pos[0])
                    else:
                        phi = pi / 2 + atan2(largercell.pos[1],
                                             largercell.pos[0])
                        if (cos(phi) * largercell.veloc[0] +
                                sin(phi) * largercell.veloc[1]) > 0:
                            theta = pi / 2 * (N - 10) / SearchDepth + atan2(
                                largercell.pos[1], largercell.pos[0])
                        else:
                            theta = -pi / 2 * (N - 10) / SearchDepth + atan2(
                                largercell.pos[1], largercell.pos[0])
                    return ConvertTheta(theta)
        #========================================
        ##########
        # yhxyan #
        ##########
        # 这部分完成追杀对面玩家的部分
        # 对未来1到SearchDepth帧搜索判定，如果对面玩家在我们的运动范围之内，则优先追杀对面
        #####
        SearchDepth = 25  # 搜索深度
        if othercell.radius < mycell.radius:
            for N in range(SearchDepth):
                othercell_temppos = [
                    othercell.pos[0] +
                    othercell.veloc[0] * Consts["FRAME_DELTA"] * N,
                    othercell.pos[1] +
                    othercell.veloc[1] * Consts["FRAME_DELTA"] * N
                ]
                StayInBound(othercell_temppos)
                distance = (
                    othercell_temppos[0]**2 + othercell_temppos[1]**2)**0.5
                if distance < othercell.radius + mycell.radius:
                    return None
                elif distance < othercell.radius + mycell.radius + self.WanderRangeInMyReference(
                        allcells, n=min(N, 5), N=N):
                    theta = pi + atan2(othercell_temppos[1],
                                       othercell_temppos[0])
                    return ConvertTheta(theta)

        # 接下来对所有的小的球遍历，选择朝哪一个方向运动
        SearchDepth = 25
        temp_smallercells = self.SmallerCells(AllCellsInMyReference)
        if len(temp_smallercells) > 20:
            thetalist = []
            squarelist = []
            squaredistribution = [0. for i in range(8)]
            for N in range(1, SearchDepth):
                MoveInMyReference(temp_smallercells, Consts["FRAME_DELTA"])
                temp_thetalist = []
                temp_squarelist = []
                for smallercell in temp_smallercells:
                    if mycell.distance_from(
                            smallercell) < self.WanderRangeInMyReference(
                                allcells, n=min(N, 5), N=N):
                        temp_thetalist.append(
                            atan2(smallercell.pos[1], smallercell.pos[0]))
                        temp_squarelist.append(smallercell.radius**2)
                        squaredistribution[int(
                            (atan2(smallercell.pos[1], smallercell.pos[0]) +
                             pi) / pi * 4)] += smallercell.radius**2
                thetalist.append(temp_thetalist)
                squarelist.append(temp_squarelist)
            if max(squaredistribution
                   ) > mycell.radius**2 * Consts["EJECT_MASS_RATIO"] * 10:
                thetaindex = squaredistribution.index(max(squaredistribution))
                theta = pi + thetaindex * 2 * pi / 8 - pi + pi / 8
                return ConvertTheta(theta)
        elif len(temp_smallercells) <= 20 and mycell.radius > 20:
            # 优先吃最大的
            SearchDepth = 100
            step = 1
            temp_smallercells = self.SmallerCells(AllCellsInMyReference)
            for N in range(0, SearchDepth, step):
                MoveInMyReference(temp_smallercells,
                                  Consts["FRAME_DELTA"] * step)
                temp_closercells = self.CloserCells(
                    self.WanderRangeInMyReference(allcells, n=min(N, 5), N=N),
                    temp_smallercells,
                    inputcell=mycell)
                if len(temp_closercells) < 1:
                    continue
                elif len(temp_closercells) >= 1:
                    tempx = temp_closercells[0].pos[0]
                    tempy = temp_closercells[0].pos[1]
                    tempR = temp_closercells[0].radius
                    for i in range(len(temp_closercells)):
                        if temp_closercells[i].radius > tempR:
                            tempx = temp_closercells[i].pos[0]
                            tempy = temp_closercells[i].pos[1]
                            tempR = temp_closercells[i].radius
                    theta = pi + atan2(tempy, tempx)
                    if random() > 0.6:
                        return None
                    else:
                        return ConvertTheta(theta)
        return None