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

import math as m

class Player():
    def __init__(self, id, arg = None):
        self.id = id
        self.theta = None
        self.has_target = False
        self.change_target = False
        self.target_radius = None
        self.target_vx = None
        self.target_vy = None

    def escape(self,allcells):
        for i in range(6):
            cellCopy = allcells.copy()
            for item in cellCopy:
                if item.id == allcells[1 - self.id].id:
                    item.move(1.05 * i * Consts['FRAME_DELTA'])
                else:
                    item.move(i * Consts['FRAME_DELTA'])
            for item in cellCopy:
                if cellCopy[self.id].distance_from(item) < cellCopy[self.id].radius + 1.1 * item.radius and cellCopy[self.id].radius < item.radius:
                    dx = self.distance_correction(item.pos[0] - cellCopy[self.id].pos[0], 'x')
                    dy = self.distance_correction(item.pos[1] - cellCopy[self.id].pos[1], 'y')
                    return m.atan2(dx, dy)

    def attack(self, allcells):
        my_cell = allcells[self.id].copy()
        my_radius = my_cell.radius

        if (my_cell.veloc[0] ** 2 + my_cell.veloc[1] ** 2) ** 0.5 > 0.9:
            return None
        attackList = []  # 可以攻击的星体列表

        for cell in allcells:
            attack_range = 15 + 20 // len(allcells)  # 攻击范围根据场上剩余星体数量来决定，
            if attack_range > 18:  # 剩余越少，攻击判定的帧数越大，攻击范围越大
                attack_range = 18  # 可调

            radius_ratio = cell.radius / my_radius
            if radius_ratio >= 1:
                continue
            elif radius_ratio < 0.3:  # 滤去较小的星体，可调
                continue
            if cell.id == allcells[1-self.id].id:
                attack_range = 25
            if cell.radius ** 2 * m.pi > 1 - 0.99 ** self.attack_frame_num(cell, my_cell) and self.attack_frame_num(
                    cell, my_cell) < attack_range:
                attackList.append(
                    [self.scoring(radius_ratio, self.attack_frame_num(cell, my_cell)), cell])  # 保存带评分的cell列表

        if attackList:  # 根据评分，分数高的优先攻击。在此用贪心算法，只考虑当前最优解
            attackList_sorted = sorted(attackList)
            target = attackList_sorted[-1][1]

            if self.target_radius == target.radius and self.target_vx == target.veloc[0] and self.target_vy == target.veloc[1]:
                self.change_target = False
            else:
                self.change_target = True

            self.target_radius = target.radius
            self.target_vx = target.veloc[0]
            self.target_vy = target.veloc[1]

            time = attackList_sorted[-1][0] * Consts['FRAME_DELTA']
            dVx = target.veloc[0] - my_cell.veloc[0]
            dVy = target.veloc[1] - my_cell.veloc[1]
            dx = self.distance_correction(target.pos[0] - my_cell.pos[0], 'x')
            dy = self.distance_correction(target.pos[1] - my_cell.pos[1], 'y')

            theta = m.atan2(- dx - dVx * time, - dy - dVy * time)

            return theta

        else:  # 如果没有可攻击的星体，不攻击

            return None

    def attack_frame_num(self, item, my_item):  # 计算需要多少帧可以吃到item
        selfCopy = my_item.copy()
        itemCopy = item.copy()
        distance = selfCopy.distance_from(itemCopy)
        itemCopy.veloc[0] -= selfCopy.veloc[0]
        itemCopy.veloc[1] -= selfCopy.veloc[1]
        selfCopy.veloc[0], selfCopy.veloc[1] = 0, 0
        frame_num = 0
        veloc_get = Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"]
        while distance >= selfCopy.radius + itemCopy.radius:
            itemCopy.move(Consts['FRAME_DELTA'])
            selfCopy.radius *= (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5
            frame_num += 1
            distance = selfCopy.distance_from(itemCopy) - veloc_get * Consts['FRAME_DELTA'] * Consts[
                'FRAME_DELTA'] * frame_num * (frame_num - 1) / 2
        return frame_num


    # 星体半径比越大，距离越近，且距离变化越小（越负），评分越高
    # 评分函数可以调整
    def scoring(self, rr, afn):  # rr=radius_ratio ; afn=attack_frame_num
        # score表达式，可调
        score = rr / (afn + 1) ** 2
        return score

    # 修正涉及到跨边界问题的坐标
    def distance_correction(self, d, xy):  # d：dx或者dy的值；xy：'x'或者'y'
        if xy == 'x':
            dxList = [d, d + Consts["WORLD_X"], d - Consts["WORLD_X"]]
            dxList.sort(key=lambda x: abs(x))
            return dxList[0]
        elif xy == 'y':
            dyList = [d, d + Consts["WORLD_Y"], d - Consts["WORLD_Y"]]
            dyList.sort(key=lambda x: abs(x))
            return dyList[0]

    def moyu(self, allcells):
        my_cell = allcells[self.id].copy()
        my_radius = my_cell.radius

        if (my_cell.veloc[0] ** 2 + my_cell.veloc[1] ** 2) ** 0.5 > 0.9:
            return None
        attackList = []  # 可以攻击的星体列表

        for cell in allcells:
            attack_range = 15 + 20 // len(allcells)  # 攻击范围根据场上剩余星体数量来决定，
            if attack_range > 18:  # 剩余越少，攻击判定的帧数越大，攻击范围越大
                attack_range = 18  # 可调

            radius_ratio = cell.radius / my_radius
            if radius_ratio >= 1:
                continue
            elif radius_ratio < 0.4:  # 滤去较小的星体，可调
                continue
            if cell.id == allcells[1 - self.id].id:
                attack_range = 25
            if cell.radius ** 2 * m.pi > 1 - 0.99 ** self.attack_frame_num(cell, my_cell) and self.attack_frame_num(
                    cell, my_cell) < attack_range:
                attackList.append(
                    [self.scoring(radius_ratio, self.attack_frame_num(cell, my_cell)), cell])  # 保存带评分的cell列表

        if attackList:  # 根据评分，分数高的优先攻击。在此用贪心算法，只考虑当前最优解
            attackList_sorted = sorted(attackList)
            target = attackList_sorted[-1][1]
            if target.id != allcells[1 - self.id].id: # 如果八帧以内会自动碰上，可以摸鱼
                wait_depth = 8
                for i in range(wait_depth):
                    selfCopy = allcells[self.id].copy()
                    targetCopy = target.copy()
                    selfCopy.move(i * Consts['FRAME_DELTA'])
                    targetCopy.move(i * Consts['FRAME_DELTA'])
                    if selfCopy.distance_from(targetCopy) < selfCopy.radius + targetCopy.radius:
                        return None
                return 'No moyuing'
            else:
                return 'No moyuing'
        else:
            return 'No moyuing'

    def strategy(self, allcells):
        if self.escape(allcells) != None:
            return self.escape(allcells)
        elif not self.moyu(allcells):
            return None
        else:
            if not self.has_target: # 如果没有目标，记录theta
                self.theta = self.attack(allcells)
                self.change_target = False
                if self.theta:
                    self.has_target = True
                    return self.theta
                else:
                    self.has_target = False
                    return self.theta
            else: # 如果有目标，看目标是否改变
                theta = self.attack(allcells)
                if self.change_target: # 如果目标改变，记录新theta
                    self.theta = theta
                    return self.theta
                else: # 如果目标没有改变，返回theta
                    return self.theta
