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

    def strategy(self, allcells):
        self.allcells = allcells
        self.mycell = allcells[self.id]
        self.hiscell = allcells[1 - self.id]
        self.min_cell = sorted(allcells, key=lambda cell: cell.radius)[0]
        if self.Escape() is None and self.Attack() is None and self.attackhim() is None:
            return None
        elif self.Escape() and self.NeedToEscape():
            if random.randint(0, 2) == 0:
                return None
            aim = self.Escape()
            [x, y] = self.RelativePos(aim)
            if x > 0:
                if y > 0:
                    return math.atan(x / y)
                else:
                    return math.pi / 2 - math.atan(y / x)
            else:
                if y > 0:
                    return -math.atan(x / y)
                else:
                    return -math.pi / 2 - math.atan(y / x)
        elif self.Emergency():
            return self.Emergency()
        elif self.Attack():
            return self.Attack()
        elif self.attackhim():
            aim = self.attackhim()
            return self.LaunchXY(self.RelativePos(aim))
        return None

    def RelativePos(self, cell):  # 相对位置矢量
        if self.jump(cell) == 0:
            x = cell.pos[0] - self.mycell.pos[0]  # x方向分量
            y = cell.pos[1] - self.mycell.pos[1]  # y方向分量
            return [x, y]
        elif self.jump(cell) == 1:
            x = cell.pos[0] - self.mycell.pos[0] + 1000  # x方向分量
            y = cell.pos[1] - self.mycell.pos[1]  # y方向分量
            return [x, y]
        elif self.jump(cell) == 2:
            x = cell.pos[0] - self.mycell.pos[0] - 1000  # x方向分量
            y = cell.pos[1] - self.mycell.pos[1]  # y方向分量
            return [x, y]
        elif self.jump(cell) == 3:
            x = cell.pos[0] - self.mycell.pos[0]  # x方向分量
            y = cell.pos[1] - self.mycell.pos[1] + 500  # y方向分量
            return [x, y]
        elif self.jump(cell) == 4:
            x = cell.pos[0] - self.mycell.pos[0]  # x方向分量
            y = cell.pos[1] - self.mycell.pos[1] - 500  # y方向分量
            return [x, y]

    def RelativeVel(self, cell):  # 相对速度矢量
        vx = cell.veloc[0] - self.mycell.veloc[0]  # x方向速度分量
        vy = cell.veloc[1] - self.mycell.veloc[1]  # y方向速度分量
        return [vx, vy]

    def RelativeDis(self, cell):  # 相对位置标量
        return (self.RelativePos(cell)[0] ** 2 + self.RelativePos(cell)[1] ** 2) ** 0.5

    def RelativeabsVel(self, cell):  # 相对速度标量
        return (self.RelativeVel(cell)[0] ** 2 + self.RelativeVel(cell)[1] ** 2) ** 0.5

    def norm(self, item):  # 计算一个矢量的大小
        return math.sqrt(item[0] ** 2 + item[1] ** 2)

    def MinDis(self, aim):  # 计算一个星体与自己的最短距离
        Cos = self.RelativePos(aim)[0] / self.RelativeDis(aim)
        Sin = self.RelativePos(aim)[1] / self.RelativeDis(aim)
        velocR = self.RelativeVel(aim)[0] * Cos + self.RelativeVel(aim)[1] * Sin
        velocT = self.RelativeVel(aim)[1] * Cos - self.RelativeVel(aim)[0] * Sin
        theta = math.atan(abs(velocT) / abs(velocR))
        if velocR > 0:
            return None
        return self.RelativeDis(aim) * math.sin(theta) - self.mycell.radius + aim.radius

    def AfterStrike(self, item):  # 计算碰撞后的半径和速度
        r = math.sqrt(self.mycell.radius ** 2 + item.radius ** 2)
        # 质量守恒
        v1 = ((self.mycell.radius ** 2) * self.mycell.veloc[0] + (item.radius ** 2) * item.veloc[0]) / (
                self.mycell.radius ** 2 + item.radius ** 2)
        v2 = ((self.mycell.radius ** 2) * self.mycell.veloc[0] + (item.radius ** 2) * item.veloc[0]) / (
                self.mycell.radius ** 2 + item.radius ** 2)
        # 动量守恒
        return [r, v1, v2]

    def CanTouch(self, aim):
        Cos = self.RelativePos(aim)[0] / self.RelativeDis(aim)
        Sin = self.RelativePos(aim)[1] / self.RelativeDis(aim)
        velocR = self.RelativeVel(aim)[0] * Cos + self.RelativeVel(aim)[1] * Sin
        velocT = self.RelativeVel(aim)[1] * Cos - self.RelativeVel(aim)[0] * Sin
        theta = math.atan(abs(velocT) / abs(velocR))
        if self.RelativeDis(aim) * math.sin(theta) >= self.mycell.radius + aim.radius:
            return False
        else:
            return True

    def velocR(self, aim):
        Cos = self.RelativePos(aim)[0] / self.RelativeDis(aim)
        Sin = self.RelativePos(aim)[1] / self.RelativeDis(aim)
        velocR = self.RelativeVel(aim)[0] * Cos + self.RelativeVel(aim)[1] * Sin
        return velocR

    def velocT(self, aim):
        Cos = self.RelativePos(aim)[0] / self.RelativeDis(aim)
        Sin = self.RelativePos(aim)[1] / self.RelativeDis(aim)
        velocT = self.RelativeVel(aim)[1] * Cos - self.RelativeVel(aim)[0] * Sin
        return velocT

    def MinTime(self, aim):
        if self.velocR(aim) < 0:
            return -self.RelativeDis(aim) / self.velocR(aim)
        else:
            return self.RelativeDis(aim) / self.velocR(aim)

    def Direction(self, vector):  # 计算一个矢量的方向，以单位矢量表示
        x = vector[0] / self.norm(vector)
        y = vector[1] / self.norm(vector)
        return [x, y]

    def Add(self, a, b):  # 矢量加法
        return [a[0] + b[0], a[1] + b[1]]

    def Minus(self, a, b):  # 矢量减法
        return [a[0] - b[0], a[1] - b[1]]

    def Escape(self):  # 返回的是最危险的星体
        CanBeDangerous = []
        for i in self.allcells:
            if self.RelativeDis(i) - self.mycell.radius - i.radius > 50 or i.dead:
                continue
            if i.radius > self.mycell.radius:
                CanBeDangerous.append(i)
        if CanBeDangerous == []:
            return None
        TheMostDangerous = sorted(CanBeDangerous, key=lambda cell: self.RelativeDis(cell) - cell.radius)[0]
        # print(self.RelativePos(TheMostDangerous))
        return TheMostDangerous

    def NeedToEscape(self):
        aim = self.Escape()
        Cos = self.RelativePos(aim)[0] / self.RelativeDis(aim)
        Sin = self.RelativePos(aim)[1] / self.RelativeDis(aim)
        velocR = self.RelativeVel(aim)[0] * Cos + self.RelativeVel(aim)[1] * Sin
        velocT = self.RelativeVel(aim)[1] * Cos - self.RelativeVel(aim)[0] * Sin
        if velocR >= 0:
            return False
        else:
            if self.RelativeDis(aim) - self.mycell.radius - aim.radius < 5:
                return True
            theta = math.atan(abs(velocT) / abs(velocR))
            if self.RelativeDis(aim) * math.sin(theta) > self.mycell.radius + aim.radius:
                return False
            else:
                return True

    def attackhim(self):
        if self.RelativeDis(self.hiscell) < 150 and self.mycell.radius > 1.15 * self.hiscell.radius:
            return self.hiscell

    def Attack(self):
        lst = []
        lstMoreThanEight = []
        lstSixToEight = []
        lstFourToSix = []
        lstLessThanFour = []
        for index in self.allcells:
            if index.radius < 0.95 * self.mycell.radius:
                lst.append(index)
        for index in lst:
            if index.radius > 0.8 * self.mycell.radius and self.CanMTE(index):
                lstMoreThanEight.append(index)
            elif index.radius > 0.6 * self.mycell.radius and self.CanSTE(index):
                lstSixToEight.append(index)
            elif index.radius > 0.4 * self.mycell.radius and self.CanFTS(
                    index) and index.radius > 0.1 * self.mycell.radius:
                lstFourToSix.append(index)
            elif self.CanLTF(index):
                lstLessThanFour.append(index)
        aimMTE = None
        aimSTE = None
        aimFTS = None
        aimLTF = None
        if lstMoreThanEight:
            aimMTE = self.attackChoose(lstMoreThanEight)
        elif lstSixToEight:
            aimSTE = self.attackChoose(lstSixToEight)
        elif lstFourToSix:
            aimFTS = self.attackChoose(lstFourToSix)
        elif lstLessThanFour:
            aimLTF = self.attackChoose(lstLessThanFour)
        aim = self.Compare([aimMTE, aimSTE, aimFTS, aimLTF])
        if aim is not None:
            return self.AttackAim(aim)
        return None

    def CanMTE(self, index):
        func1 = self.RelativeDis(index) < self.mycell.radius ** 2
        func2 = self.norm(index.veloc) < 0.25
        func3 = self.RelativeabsVel(index) < 0.35
        return func1 and (func2 and func3)

    def CanSTE(self, index):
        func1 = self.RelativeDis(index) < self.mycell.radius ** 2
        func2 = self.norm(index.veloc) < 0.22
        func3 = self.RelativeabsVel(index) < 0.32
        return func1 and (func2 and func3)

    def CanFTS(self, index):
        func1 = self.RelativeDis(index) < self.mycell.radius ** 2
        func2 = self.norm(index.veloc) < 0.20
        func3 = self.RelativeabsVel(index) < 0.30
        return func1 and (func2 and func3)

    def CanLTF(self, index):
        func1 = self.RelativeDis(index) < self.mycell.radius ** 2
        func2 = self.norm(index.veloc) < 0.2
        func3 = self.RelativeabsVel(index) < 0.3
        return func1 and (func2 and func3)

    def attackChoose(self, lst):
        CanTouchList = []
        CanNotTouchList = []
        for index in lst:
            if self.CanTouch(index):
                CanTouchList.append(index)
            else:
                CanNotTouchList.append(index)
        if CanTouchList:
            return min(CanTouchList, key=lambda cell: self.RelativeDis(cell))
        elif CanNotTouchList:
            ComeList = []
            NotComeList = []
            for aim in CanNotTouchList:
                Cos = self.RelativePos(aim)[0] / self.RelativeDis(aim)
                Sin = self.RelativePos(aim)[1] / self.RelativeDis(aim)
                velocR = self.RelativeVel(aim)[0] * Cos + self.RelativeVel(aim)[1] * Sin
                velocT = self.RelativeVel(aim)[1] * Cos - self.RelativeVel(aim)[0] * Sin
                if velocR < 0:
                    ComeList.append(aim)
                else:
                    NotComeList.append(aim)
            if ComeList:
                return min(ComeList, key=lambda cell: self.MinDis(cell) * abs(self.velocT(cell)))
            else:
                return min(NotComeList, key=lambda cell: self.velocR(cell) * abs(self.velocT(cell)))
        else:
            return None

    def Compare(self, aimList):  # 比较方法有待进一步的调整
        if self.check(aimList[0]):
            return aimList[0]
        elif self.check(aimList[1]):
            return aimList[1]
        elif self.check(aimList[2]):
            return aimList[2]
        elif self.check(aimList[3]):
            return aimList[3]
        else:
            return None

    def check(self, aim):
        if aim is None:
            return None
        if self.CanTouch(aim):
            return True
        else:
            if self.velocR(aim) < 0:
                if abs(self.velocR(aim)) / (abs(self.velocT(aim))):
                    return True
                else:
                    return True
            else:
                if self.velocR(aim) / (abs(self.velocT(aim))):
                    if self.velocR(aim) < 0.1:
                        return True
                    else:
                        return False
                else:
                    return False

    def AttackAim(self, aim):

        VelocLaunch = Consts["DELTA_VELOC"]  # 喷射速度
        VelocGain = VelocLaunch * Consts["EJECT_MASS_RATIO"]  # 得到速度
        if aim == None:
            return None
        else:
            if self.CanTouch(aim):
                if self.RelativeabsVel(aim) < 0.1:
                    return self.LaunchXY(self.RelativePos(aim))
                return None
            if self.MinDis(aim):
                vector1 = self.Direction(self.RelativeVel(aim))
                vector1 = [vector1[0] * self.MinDis(aim), vector1[1] * self.MinDis(aim)]
                vector2 = self.RelativePos(aim)
                vector = self.Add(vector1, vector2)
                return self.LaunchXY(vector)
            else:
                return self.LaunchXY(self.RelativePos(aim))


    def LaunchXY(self, Aim):
        [x, y] = [-Aim[0], -Aim[1]]
        if x > 0:
            if y > 0:
                return math.atan(x / y)
            else:
                return math.pi / 2 - math.atan(y / x)
        else:
            if y > 0:
                return -math.atan(x / y)
            else:
                return -math.pi / 2 - math.atan(y / x)

    def Emergency(self):
        for index in self.allcells:
            if index == self.mycell:
                continue
            else:
                if index.radius > 0.1 * self.mycell.radius and index.radius < self.mycell.radius and self.RelativeDis(
                        index) - self.mycell.radius - index.radius < index.radius / 4:
                    return self.LaunchXY(self.RelativePos(index))
        return None

    def jump(self, aim):
        dis0 = self.norm([aim.pos[0] - self.mycell.pos[0], aim.pos[1] - self.mycell.pos[1]])
        dis1 = self.norm([aim.pos[0] - self.mycell.pos[0] + 1000, aim.pos[1] - self.mycell.pos[1]])
        dis2 = self.norm([aim.pos[0] - self.mycell.pos[0] - 1000, aim.pos[1] - self.mycell.pos[1]])
        dis3 = self.norm([aim.pos[0] - self.mycell.pos[0], aim.pos[1] - self.mycell.pos[1] + 500])
        dis4 = self.norm([aim.pos[0] - self.mycell.pos[0], aim.pos[1] - self.mycell.pos[1] - 500])
        dismin = min(dis0, dis1, dis2, dis3, dis4)
        if dismin == dis0:
            return 0
        elif dismin == dis1:
            return 1
        elif dismin == dis2:
            return 2
        elif dismin == dis3:
            return 3
        elif dismin == dis4:
            return 4
