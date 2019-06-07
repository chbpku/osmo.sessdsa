#!/usr/bin/env python3

# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

import math
import random
from consts import Consts


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

        # Properties
        self.collide_group = None
        self.dead = False

    # Methods
    def distance_from(self, other):
        """Calculate the distance from another cell.

        Args:
            other: another cell.
        Returns:
            the minimum distance.

        """
        dx = self.pos[0] - other.pos[0]
        dy = self.pos[1] - other.pos[1]
        min_x = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
        min_y = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
        return (min_x ** 2 + min_y ** 2) ** 0.5

    def collide(self, other):
        """Determine if it collides with another cell.

        Args:
            other: another cell.
        Returns:
            True / False.

        """
        return self.distance_from(other) < self.radius + other.radius

    def area(self):
        """Calculate the area of the cell.

        Args:

        Returns:
            the area of the cell.

        """
        return math.pi * self.radius * self.radius

    def stay_in_bounds(self):
        """Make the out-of-bounds cell stay within the bounds.

        Args:

        Returns:


        """
        if self.pos[0] < 0:
            self.pos[0] += Consts["WORLD_X"]
        elif self.pos[0] > Consts["WORLD_X"]:
            self.pos[0] -= Consts["WORLD_X"]

        if self.pos[1] < 0:
            self.pos[1] += Consts["WORLD_Y"]
        elif self.pos[1] > Consts["WORLD_Y"]:
            self.pos[1] -= Consts["WORLD_Y"]

    def limit_speed(self):
        """Enforce speed limits.

        Args:

        Returns:


        """
        if self.veloc[0] > Consts["MAX_VELOC"]:
            self.veloc[0] = Consts["MAX_VELOC"]
        elif self.veloc[0] < -Consts["MAX_VELOC"]:
            self.veloc[0] = -Consts["MAX_VELOC"]

        if self.veloc[1] > Consts["MAX_VELOC"]:
            self.veloc[1] = Consts["MAX_VELOC"]
        elif self.veloc[1] < -Consts["MAX_VELOC"]:
            self.veloc[1] = -Consts["MAX_VELOC"]

    def move(self, frame_delta):
        """Move the cell according to its velocity.

        Args:
            frame_delta: Time interval between two frames.
        Returns:


        """
        self.collide_group = None
        # Adjust the position, according to velocity.
        self.pos[0] += self.veloc[0] * frame_delta
        self.pos[1] += self.veloc[1] * frame_delta
        self.stay_in_bounds()
        self.limit_speed()


# 地图是1000*500的，但是由于边界的穿越性，本来的反弹变成了直接到对面
# 那就相当于将 地图扩展成了3*3个1000*500
# 计算距离和其他参数的时候，我们只需要考虑最近的那一种情况就行了

# -------------------------------------------
class Player():
    search_radius = 70  # (搜索半径）
    danger_radius = 70  # 危险判定半径
    search_cellnumber = 5

    danger_tick = 0
    tick = -5
    eject_time = 0
    eject_direction = None

    sumMass = 0

    target = None

    def __init__(self, id, arg=None):
        self.id = id

    # -------------------------------辅助计算函数----------------------------------

    # 9个（包括本体）镜像的球
    def mirro_cell(self, cell):
        mirror = []
        x = cell.pos[0]
        y = cell.pos[1]
        for i in range(-1, 2):
            for j in range(-1, 2):
                temp = Cell(cell.id, [0, 0], cell.veloc, cell.radius)
                temp.pos[0] = x + i * Consts["WORLD_X"]
                temp.pos[1] = y + j * Consts["WORLD_Y"]
                mirror.append(temp)
        return mirror

    # 镜像的还原
    def mirro_back(self, cell):
        x = cell.pos[0]
        y = cell.pos[1]
        x = x - Consts["WORLD_X"] * (x // Consts["WORLD_X"])
        y = y - Consts["WORLD_Y"] * (y // Consts["WORLD_Y"])
        cell.pos = (x, y)
        return cell

    # 搜索半径随着数目减小要增大,(随速度增大也要增大?)
    def danger_r(self, a, n):
        v = (a.veloc[1] ** 2 + a.veloc[0] ** 2) ** 0.5
        if v <= 0.5:
            return 70
        else:
            return 70 * (2 * v) ** 2

    def search_r(self, a, allcells):
        rlist = []
        for i in allcells:
            rlist.append(a.distance_from(i))
        rlist.sort(reverse=True)
        if len(rlist) < self.search_cellnumber + 1:
            return rlist[-1]
        if rlist[self.search_cellnumber] < 120:
            return 120
        else:
            return rlist[self.search_cellnumber]

    # b相对a的径向速度（仅考虑未扩展的地图）
    def delta_vr(self, a, b):
        dx = -a.pos[0] + b.pos[0]
        dy = -a.pos[1] + b.pos[1]
        dvx = -a.veloc[0] + b.veloc[0]
        dvy = -a.veloc[1] + b.veloc[1]
        dv = (dvx ** 2 + dvy ** 2) ** 0.5
        if dvx == dvy == 0:
            return 0
        else:
            dvr = dvx * (dx / dv) + dvy * (dy / dv)
            return dvr

    # b相对a的速度大小
    def delta_v(self, a, b):
        dvx = -a.veloc[0] + b.veloc[0]
        dvy = -a.veloc[1] + b.veloc[1]
        dv = (dvx ** 2 + dvy ** 2) ** 0.5
        return dv

    # 直接计算两个点之间的距离
    def delta_r(self, a, b):
        dx = -a.pos[0] + b.pos[0]
        dy = -a.pos[1] + b.pos[1]
        return (dx ** 2 + dy ** 2) ** 0.5

    # 匀速运动的a，b之间的最小距离
    def min_distance(self, a, b):
        dx = -a.pos[0] + b.pos[0]
        dy = -a.pos[1] + b.pos[1]
        dvx = -a.veloc[0] + b.veloc[0]
        dvy = -a.veloc[1] + b.veloc[1]
        dr = (dx ** 2 + dy ** 2) ** 0.5
        theta1 = math.atan2(dvy, dvx)  # 相对速度与x轴夹角
        theta2 = math.atan2(dy, dx)  # 相对位置于x轴 夹角
        return abs(dr * math.sin(theta2 - theta1))

    # 匀速运动到最小距离所花费的时间
    def min_time(self, a, b):
        return self.min_distance(a, b) / (self.delta_v(a, b) * Consts["FRAME_DELTA"])

    def abs_angle(self, t1, t2):
        dt = t1 - t2
        dt = dt - dt // (2 * math.pi) * 2 * math.pi
        return dt

    def sumR(self, a, b):
        return a.radius + b.radius

    # 用mathematica解方程化简得到表达式，a追b的帧数
    def attack_frame(self, a, b, theta, eject_time):
        # 认为是对着一个固定方向连续喷射几个球，然后发生碰撞
        # 这里的theta是运动方向，和喷射方向相反，坐标是与x负方向夹角（为什么要取这个SB坐标！！！！）
        R = self.sumR(a, b)  # 增大保障！
        x0 = a.pos[0] - b.pos[0]
        y0 = a.pos[1] - b.pos[1]
        vx = -a.veloc[0] + b.veloc[0]
        vy = -a.veloc[1] + b.veloc[1]
        fd = Consts["FRAME_DELTA"]
        dv = Consts["DELTA_VELOC"] * Consts['EJECT_MASS_RATIO']
        n = eject_time

        # 计算判别式
        delta = fd ** 2 * ((-(
                dv ** 2 * n ** 2) - vx ** 2 - vy ** 2 - 2 * dv * n * vx * math.cos(
            theta) - 2 * dv * n * vy * math.sin(theta)) * (
                                   dv ** 2 * fd ** 2 * n ** 2 - 2 * dv ** 2 * fd ** 2 * n ** 3 + dv ** 2 * fd ** 2 * n ** 4 - 4 * R ** 2 + 4 * x0 ** 2 + 4 * y0 ** 2 + 4 * dv * fd * (
                                   -1 + n) * n * x0 * math.cos(
                               theta) + 4 * dv * fd * (
                                           -1 + n) * n * y0 * math.sin(
                               theta)) + (-(
                dv ** 2 * fd * n ** 2) + dv ** 2 * fd * n ** 3 + 2 * vx * x0 + 2 * vy * y0 + dv * n * (fd * (
                -1 + n) * vx + 2 * x0) * math.cos(theta) + dv * n * (fd * (-1 + n) * vy + 2 * y0) * math.sin(
            theta)) ** 2)
        if delta < 0:
            return None

        B = -(
                dv ** 2 * fd ** 2 * n ** 2) + dv ** 2 * fd ** 2 * n ** 3 + 2 * fd * vx * x0 + 2 * fd * vy * y0 - dv * fd ** 2 * n * vx * math.cos(
            theta) + dv * fd ** 2 * n ** 2 * vx * math.cos(theta) + 2 * dv * fd * n * x0 * math.cos(
            theta) - dv * fd ** 2 * n * vy * math.sin(theta) + dv * fd ** 2 * n ** 2 * vy * math.sin(
            theta) + 2 * dv * fd * n * y0 * math.sin(theta)
        A = (
                2. * fd ** 2 * (dv ** 2 * n ** 2 + vx ** 2 + vy ** 2 + 2 * dv * n * vx * math.cos(
            theta) + 2 * dv * n * vy * math.sin(theta)))
        frame1 = (B - math.sqrt(delta)) / A
        frame2 = (B + math.sqrt(delta)) / A
        frame = math.ceil(min(frame1, frame2))
        # frame = math.ceil(frame1)
        if frame <= 0 or frame > 80:
            return None
        return math.ceil(frame)

    # a追b划定喷射次数的上限, 返回可以喷射的所有次数的列表
    def effect_eject_time(self, a, b):
        ra = a.radius
        rb = b.radius
        if a.radius <= b.radius:
            return 0
        # 喷完还要大
        n1 = math.floor(2 * math.log1p(rb / ra - 1) / math.log1p(-Consts['EJECT_MASS_RATIO']))
        # 喷完要有收益
        n2 = math.floor(math.log1p(- rb ** 2 / ra ** 2) / math.log1p(-Consts['EJECT_MASS_RATIO']))
        n = min(n1, n2, 20)  # 强制限定到15
        nlist = list(range(0, n + 1))
        return nlist

    # 给出一个合理一些的追击范围，不然0-2pi搜索太困难:速度方向和相切的线的夹角吧
    def effect_attack_theta(self, a, b):
        # vx = -a.veloc[0] + b.veloc[0]
        # vy = -a.veloc[1] + b.veloc[1]
        # theta_v = math.atan2(vx, vy)
        # x0 = a.pos[0] - b.pos[0]
        # y0 = a.pos[1] - b.pos[1]
        # theta_x = math.atan2(x0, y0)
        # R = self.sumR(a, b)
        # dr = self.delta_r(a, b)
        # alpha = math.acos(R / dr)
        # # 计算两条切线的夹角(都是速度角)
        # theta1 = theta_x - alpha - 0.5 * math.pi
        # theta2 = theta_x + alpha + 0.5 * math.pi

        return [2 * math.pi / 30 * n for n in range(29)]

    # a攻击b的喷射方案（不考虑镜像的）
    def attack_method(self, a, b):
        ways = []
        for i in self.effect_eject_time(a, b):
            for th in self.effect_attack_theta(a, b):
                frame = self.attack_frame(a, b, th, i)
                if frame is not None:
                    profit = b.radius ** 2 - a.radius ** 2 * (1 - (1 - Consts['EJECT_MASS_RATIO']) ** i)
                    income = self.income(frame, profit)
                    b = self.mirro_back(b)  # 还原镜像
                    ways.append((frame, i, 0.5 * math.pi - th, income, b))  # 这里的b是可能超出边界的球
        if not ways:
            return None
        best = sorted(ways, key=lambda way: way[3], reverse=True)[0]
        return best

    # 收益函数需要大大的调参！
    def income(self, frame, profit):
        income = profit / frame
        return income

    def sumM(self, cells):
        sum = 0
        for i in cells:
            sum += i.radius ** 2
        return sum

    # ------------------------------策略函数----------------------------------

    # --------------进攻--------------------
    # a到b的最短进攻方案（b向着a过来）
    def best_attack(self, a, b):
        """
        :type a: Cell
        :type b: Cell
        """
        # 先不考虑中间有球
        mirror = self.mirro_cell(b)
        ways = []
        if a.distance_from(b) - self.sumR(a, b) > self.search_radius:
            return None
        #  分析漂浮到达每一个镜像的情况，计算到达二者相距最小距离的时间和这个最小的方向
        for i in mirror:
            if self.delta_r(a, i) - self.sumR(a, i) > self.search_radius:
                continue
            # 使用匀加速策略来吃球！
            method = self.attack_method(a, i)
            if method is None:
                continue

            ways.append(method)
        if not ways:
            return None

        best = sorted(ways, key=lambda way: way[3], reverse=True)[0]  # 最短时间的选择！

        return best

    # 对于ai，不要去吃，除非情况非常的好
    def attack_ai(self, a, enemy, smaller):
        """
                :type a: Cell
                :type enemy: Cell
                """
        if enemy.radius ** 2 / a.radius ** 2 >= 0.9:
            return None
        if self.sumM(smaller) >= a.radius ** 2:
            return None
        # 不考虑中间有球
        mirror = self.mirro_cell(enemy)
        ways = []
        if a.distance_from(enemy) - self.sumR(a, enemy) > self.search_radius:
            return None
        #  分析漂浮到达每一个镜像的情况，计算到达二者相距最小距离的时间和这个最小的方向
        for i in mirror:
            if self.delta_r(a, i) - self.sumR(a, i) > self.search_radius:
                continue
            # 使用匀加速策略来吃球！
            method = self.attack_method(a, i)
            if method is None:
                continue

            ways.append(method)
        if not ways:
            return None

        best = sorted(ways, key=lambda way: way[3], reverse=True)[0]  # 最短时间的选择！

        return best

    # 判断是否在限制时间内发生碰撞，返回限制时间内发生碰撞后的大小（忽略碰撞位移）
    def after_collision(self, cell, allcells, frame_limit):
        mass = cell.radius ** 2
        for other in allcells[2:]:  # 排除自己和敌人
            for i in self.mirro_cell(other):  # 考虑镜像
                min_dis = self.min_distance(cell, i)
                R = self.sumR(cell, i)
                dr = self.delta_r(cell, i)
                dv = self.delta_v(cell, i)
                if min_dis <= R:
                    if dv == 0:
                        continue
                    frame = (math.sqrt(dr ** 2 - min_dis ** 2) - math.sqrt(R ** 2 - min_dis ** 2)) / (
                            dv * Consts['FRAME_DELTA'])
                    if frame <= frame_limit:
                        mass += i.radius ** 2
                        break
        return mass

    # ----------------逃跑--------------------

    # a如何逃离直接背b吃掉的命运
    def best_escape(self, a, b):
        dangers = []
        if a.distance_from(b) - self.sumR(a, b) > self.danger_radius:
            return None
        mirror = self.mirro_cell(b)
        for i in mirror:
            dvr = self.delta_vr(a, i)
            if dvr >= 0:  # 将反向的排除暂时
                continue
            R = self.sumR(a, i)
            dr = self.delta_r(a, i)
            if dr - R > self.danger_radius:  # 将太远的排除掉，只要最有威胁的
                continue
            min_dis = self.min_distance(a, i)
            dv = self.delta_v(a, i)

            # 计算喷射角度，都是垂直速度方向并且远离圆心
            dx = -a.pos[0] + i.pos[0]
            dy = -a.pos[1] + i.pos[1]
            theta_x = math.atan2(dx, dy) + int(math.atan2(dx, dy) < 0) * 2 * math.pi
            dvx = -a.veloc[0] + i.veloc[0]
            dvy = -a.veloc[1] + i.veloc[1]
            theta_v = math.atan2(dvx, dvy) + int(math.atan2(dvx, dvy) < 0) * 2 * math.pi
            if theta_x - theta_v - 0.5 * math.pi + int(
                    theta_x - theta_v - 0.5 * math.pi < 0) * 2 * math.pi <= 0.5 * math.pi:
                theta = theta_v + math.pi * 0.8
            else:
                theta = theta_v - math.pi * 0.8

            # 尝试一下
            theta = theta_x

            if min_dis <= R:  # 这个是可以自己碰撞到的,有危险 (在加大一点？不要极限操作吧...)
                time = (math.sqrt(dr ** 2 - min_dis ** 2) - math.sqrt(R ** 2 - min_dis ** 2)) / (
                        dv * Consts['FRAME_DELTA'])
                dangers.append((time, theta, b))  # 返回碰撞时间和逃离角度
                continue
            if min_dis <= R + 5:  # 避免过于接近
                print('close!')
                time = min_dis / (dv * Consts['FRAME_DELTA'])
                dangers.append((time, theta, b))
                continue

        if not dangers:
            return None
        most_danger = sorted(dangers, key=lambda danger: danger[0])[0]
        return most_danger

    # 远离AI的逃跑策略
    def escape_ai(self, a, enemy):
        dangers = []
        if a.distance_from(enemy) - self.sumR(a, enemy) > self.danger_radius:
            return None
        for i in self.mirro_cell(enemy):
            dvr = self.delta_vr(a, i)
            if dvr >= 0:  # 将反向的排除暂时
                continue
            R = self.sumR(a, i)
            dr = self.delta_r(a, i)
            if dr - R > self.danger_radius:
                continue
            min_dis = self.min_distance(a, i)
            dv = self.delta_v(a, i)

            dvx = -a.veloc[0] + i.veloc[0]
            dvy = -a.veloc[1] + i.veloc[1]
            dx = a.pos[0] - i.pos[0]
            dy = a.pos[1] - i.pos[1]
            theta_v = math.atan2(dvx, dvy)  # 敌人相对a的速度矢量
            theta_x = math.atan2(dx, dy)  # 敌人指向a的位移矢量
            dtheta = abs(theta_x - theta_v)

            # 计算逃跑ai的角度，偏离位移矢量方向吧
            # if dtheta >= math.pi:  # 变得<pi
            #     dtheta = 2 * math.pi - dtheta
            #     if dtheta >= math.radians(20):
            #         theta = theta_x + math.pi
            #     else:
            #         theta = theta_x + math.pi + 2 * int(theta_x < theta_v) * math.radians(20) - math.radians(20)
            # else:
            #     if dtheta >= math.radians(20):
            #         theta = theta_x + math.pi
            #     else:
            #         theta = theta_x + math.pi + 2 * int(theta_x > theta_v) * math.radians(20) - math.radians(20)

            theta = theta_x + math.pi
            if min_dis <= R:  # 这个是可以自己碰撞到的,有危险 (在加大一点？不要极限操作吧...)
                time = (math.sqrt(dr ** 2 - min_dis ** 2) - math.sqrt(R ** 2 - min_dis ** 2)) / (
                        dv * Consts['FRAME_DELTA'])
                dangers.append((time, theta, enemy))  # 返回碰撞时间和逃离角度
                continue
            if min_dis <= R + 5:  # 避免过于接近
                print('ai close!')
                time = min_dis / (dv * Consts['FRAME_DELTA'])
                dangers.append((time, theta, enemy))

        if not dangers:
            return None
        most_danger = sorted(dangers, key=lambda danger: danger[0])[0]
        return most_danger

    # 在给出的会造成危险的情况下，多个危险怎么跑？，限定到只有两个？
    def escape(self, dangers):
        if len(dangers) == 1:
            print('danger!')
            self.danger_tick = dangers[0][0]
            return dangers[0][1]
        # # 多个危险的时候要怎么办啊(不管了！)
        # if len(dangers) >= 2:
        #     dangers = sorted(dangers, key=lambda danger: danger[0])[:2]
        #     a = dangers[0]
        #     b = dangers[1]
        #     theta = (a[1] * b[0] + b[1] * a[0]) / (a[0] + b[0]) + math.pi  # 角度加权紧急程度
        #     print('danger!')
        #     return theta
        if len(dangers) == 0:
            return None

    def strategy(self, allcells):

        player = allcells[self.id]
        enemy = None
        bigger = []
        smaller = []

        # 最高逻辑
        if self.sumMass == 0:
            self.sumMass = self.sumM(allcells)
        if 2 * player.radius ** 2 > self.sumMass:
            return None

        self.search_radius = self.search_r(player, allcells)
        self.danger_radius = self.danger_r(player, len(allcells))

        # 标记出敌人，区分大的和小的
        for i in allcells:
            if i == player:
                continue
            if i.id + self.id == 1:  # 只能是0+1了
                enemy = i
            if i.radius >= player.radius:
                bigger.append(i)
            else:
                smaller.append(i)

        # 逃跑：
        if not bigger:
            pass
        else:
            dangers = []
            for cell in bigger:
                if cell == enemy:
                    danger = self.escape_ai(player, cell)
                else:
                    danger = self.best_escape(player, cell)
                if danger is not None:
                    dangers.append(danger)
            if not dangers:
                pass
            else:
                # self.tick = 0
                self.eject_time = 0
                self.target = None
                return self.escape(dangers)

        # 危险躲避进程，不要轻举妄动
        if self.danger_tick > 0:
            self.danger_tick = self.danger_tick - 1
            return None

        # 吃球

        # 还在之前的吃球进程中
        if self.tick > 0:
            self.tick = self.tick - 1
            if self.eject_time <= 0:
                return None
            else:
                self.eject_time = self.eject_time - 1
                return self.eject_direction
        if self.tick > -5:
            if self.target in [i.id for i in allcells]:
                self.tick = self.tick - 1
                return None
            else:
                self.tick = -5

        # 寻找有没有能吃的
        if len(smaller) == 0:
            return None
        methods = []
        for cell in smaller:
            if cell == enemy:  # 暂时先不管敌人
                continue
            else:
                method = self.best_attack(player, cell)
            if method is not None:
                methods.append(method)
        if not methods:
            return None
        methods = sorted(methods, key=lambda m: m[3], reverse=True)  # method: 吃球所花帧数，喷射次数，喷射角度，收益，目标cell

        # 判断能不能吃（简单考虑碰撞
        for m in methods:
            player_mass = player.radius ** 2 * (1 - Consts['EJECT_MASS_RATIO']) ** m[1]
            target_mass = self.after_collision(m[4], allcells, m[0])
            if player_mass > target_mass:
                # 一旦找到方案，这一帧就要开始喷射？（还是下一帧？）
                self.target = m[4].id
                self.eject_direction = m[2]  # 喷射方向
                self.tick = m[0] - 1
                self.eject_time = m[1] - 1
                print(self.eject_time)
                if self.eject_time >= 0:
                    return self.eject_direction
                else:
                    return None
        return None
