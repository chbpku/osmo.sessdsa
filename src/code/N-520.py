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
import random


class Player():
    def __init__(self, id, arg=None):
        self.id = id

    def npc(self, allcells):
        alist = []
        blist = []
        clist = []
        flag = 0
        mx = 0
        #mx为攻击阈值
        min=20
        # min为躲避阈值
        ms = allcells[self.id]
        msv = math.sqrt(ms.veloc[0] * ms.veloc[0] + ms.veloc[1] * ms.veloc[1])
        for i in range(len(allcells)):
            if ms.distance_from(allcells[i]) < 100 and i != self.id:
                alist.append(allcells[i])
        #选取范围为100进行防御判定
        for i in range(len(allcells)):
            if ms.distance_from(allcells[i]) < 170 and i != self.id:
                blist.append(allcells[i])
        #选取范围为150进行攻击判定
        if len(blist) != 0 or len(alist) != 0:
            alist = sorted(alist, key=lambda cell: cell.radius)
            #排序
            for i in range(len(alist)):
                  if alist[i].radius > ms.radius:
                    er=(ms.distance_from(alist[i]) - ms.radius - alist[i].radius) ** 2 / math.sqrt(
                        (ms.veloc[0] - alist[i].veloc[0]) ** 2 + (ms.veloc[1] - alist[i].veloc[1]) ** 2) / (
                                                                                     alist[i].radius)
                    #er为防御判定式，值越小，越优先躲避
                    if er<min:
                        #min为躲避阈值
                        min = er
                        dcell = alist[i]
                        flag = 1
            if flag == 1:
                dx = dcell.pos[0] - ms.pos[0]
                dy = dcell.pos[1] - ms.pos[1]
                return math.atan2(dx, dy)
            #向相反方向进行躲避
            elif len(blist) != 0 and flag == 0:
                #若无危险，则进行攻击判定
                blist = sorted(blist, key=lambda cell: cell.radius)
                #排序
                for i in range(len(blist)):
                    if blist[i].radius < ms.radius:
                        if i == len(blist) - 1:
                            mid_cell = blist[i]
                            flag = 1
                        elif blist[i + 1].radius > ms.radius:
                            mid_cell = blist[i]
                            flag = 1
                        #判断所有可攻击对象，即blist[0:i]
                        if flag == 1:
                            for j in range(i, 0, -1):
                                ar=blist[j].radius / (ms.distance_from(blist[j]) - ms.radius-blist[j].radius) ** 2
                                #ar为攻击判定式，值越大，越优先攻击
                                if  ar> mx and ms.radius/0.85>blist[j].radius>ms.radius/2.5 and (ms.distance_from(blist[j])-ms.radius-blist[j].radius<ms.radius*3):
                                    #半径太小或接近的不攻击，距离太远的不攻击
                                    mx = ar
                                    acell = blist[j]
                                    flag = 0
                                if flag == 0 and msv<ms.radius*2/20+ms.radius:
                                    #对速度进行限制
                                    dx = ms.pos[0] - acell.pos[0] +(ms.veloc[0] - acell.veloc[0]) *90
                                    dy = ms.pos[1] - acell.pos[1] + (ms.veloc[1] - acell.veloc[1]) *90
                                    #估算攻击方向
                                    if not (math.atan2(dx, dy)-math.atan2(ms.radius+acell.radius,ms.distance_from(acell))<math.atan2(ms.veloc[0]-acell.veloc[0],ms.veloc[1]-acell.veloc[1])<math.atan2(dx, dy)+math.atan2(ms.radius+acell.radius,ms.distance_from(acell))) :
                                        return math.atan2(dx, dy)

    def strategy(self, allcells):
        return self.npc(allcells)