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

from math import *

from consts import Consts


class Player():
    def __init__(self, id, arg=None):
        self.id = id

    def strategy(self, allcells):
        """物理和几何引擎"""

        def norm(v):  # 返回v的2范数
            return sqrt(v[0] ** 2 + v[1] ** 2)

        def point_to_line(a, b, c):  # 3坐标a,b,c,返回a到直线bc的距离
            u1 = [c[0] - b[0], c[1] - b[1]]
            u2 = [a[0] - b[0], a[1] - b[1]]
            u = abs(u1[0] * u2[0] + u1[1] * u2[1]) / norm(u1)
            a = u2[0] ** 2 + u2[1] ** 2 - u ** 2
            if a < 1e-6:
                return 0
            else:
                return sqrt(a)

        def thet(a, b):  # 向量a到b的有向角([0,2pi))
            if sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2)) < 1e-6:
                return 0
            det = a[0] * b[1] - a[1] * b[0]
            jia = (a[0] * b[0] + a[1] * b[1]) / sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2))
            if abs(jia) > 1 - 1e-3:
                if jia < 0:
                    return pi
                else:
                    return 0
            jia = acos(jia)
            if det > 0:
                return 2 * pi - jia
            else:
                return jia

        def chuan(v):  # 穿屏最小向量(例如坐标[1,1]到坐标[999,499]之间不穿屏向量是[998,498]穿屏向量则是[-2,-2])
            # 只有坐标会用到穿屏函数，速度无论穿不穿都是一样的，不需要穿屏
            nonlocal WX, WY
            lst = [v[0] - WX, v[0], v[0] + WX]
            min1 = abs(lst[0])
            i_min = 0
            for i in range(3):
                if abs(lst[i]) < min1:
                    i_min = i
                    min1 = abs(lst[i])
            v0 = lst[i_min]

            lst = [v[1] - WY, v[1], v[1] + WY]
            min1 = abs(lst[0])
            i_min = 0
            for i in range(3):
                if abs(lst[i]) < min1:
                    i_min = i
                    min1 = abs(lst[i])
            v1 = lst[i_min]

            return [v0, v1]

        def jia(a, b):  # 向量a,b的无向角[0,pi)
            theta = thet(a, b)
            return pi - abs(pi - theta)

        def distance(sel, cel):  # 两球sel和cel的距离
            selp = sel.pos
            celp = cel.pos
            return norm(chuan([selp[0] - celp[0], selp[1] - celp[1]]))

        def dang(r1, r2, dist, v1):  # 相撞距离,参数为两球半径，dist是相距’向量‘，v1是相对速度,dang1函数是该函数参数为sel,cel
            # 的版本
            return norm(dist) - r1 - r2

        def dang1(sel, cel):
            r1 = sel.radius
            r2 = cel.radius
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            return dang(r1, r2, dist, 0)

        def time(r1, r2, dist, v1):  # 预测两球的相撞时间，同样time1函数是该函数参数为sel,cel的版本
            # 参数(为避免出现math domain error)
            dist = chuan(dist)
            if norm(v1) < (norm(dist) - r1 - r2) * 0.01:
                return None

            h = point_to_line(dist, [0, 0], v1)
            if v1[0] * dist[0] + v1[1] * dist[1] < 0:
                return None
            if r1 + r2 < h + 1e-3:
                return None
            else:
                l1 = sqrt((r1 + r2) ** 2 - h ** 2)
                l2 = norm(dist) ** 2 - h ** 2
                if l2 < 1e-4:
                    return None
                l2 = sqrt(l2)
                return (l2 - l1) / norm(v1)

        def time_meeting(sel, cel):  #
            r1 = sel.radius
            r2 = cel.radius
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            dist = chuan(dist)
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]

            return time(r1, r2, dist, v1)

        def new_velocity(player, theta):
            fx = sin(theta)
            fy = cos(theta)
            v = player.veloc
            v[0] -= Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
            v[1] -= Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
            return v

        def best_choice(dist, v1):
            dv = Consts["DELTA_VELOC"]*Consts["EJECT_MASS_RATIO"]
            de_angle = asin(dv/norm(v1)) if dv < norm(v1) else pi  # 喷射后速度的最大偏转
            theta = thet(v1, dist)
            if theta > pi:
                theta = theta-2*pi
            # 喷射后达不到与相对距离重合的方向
            if jia(dist, v1) >= de_angle:
                return thet([0, 1], v1)+theta/(jia(dist, v1)+1e-8)*(pi/2-de_angle)
            # 喷射后可以达到与相对距离重合的方向
            h = point_to_line(v1, [0, 0], dist)
            alpha = asin(h/dv) if abs(h/dv)<=1 else pi/2
            beta = pi-alpha-de_angle
            return thet([0, 1], v1) + theta/(jia(dist, v1)+1e-8)*beta



        """辅助函数"""

        def get_absorbable(sel):  # cell_absorb 参数为allcells列表，返回一个可吃的cell的list
            cells_can_absorb = []
            for cell in allcells:
                if cell.radius < sel.radius:
                    if ((sel.pos[0] - cell.pos[0]) ** 2 + (sel.pos[1] - cell.pos[1]) ** 2) ** 0.5 <= 200 + sel.radius:
                        # this radius can be adjusted
                        cells_can_absorb.append(cell)
            return cells_can_absorb

        def npc_enlarge(npc):
            nonlocal allcells, INF
            absorbable = get_absorbable(npc)
            time_min = INF
            target_cell = None
            for cell in absorbable:
                t = time_meeting(npc, cell)
                if t is not None and t < time_min:
                    time_min = t
                    target_cell = cell
            if target_cell is None:
                return npc.radius, None
            r = sqrt(npc.radius ** 2 + target_cell.radius ** 2)
            return r, time_min

        def barrier(sel, v_org, time0):  # 路径障碍
            # 如果我们要追target的话，说明target是比我们小的，所以在bigger中不用考虑target
            # 如果有障碍，返回True，没有则返回False
            if time0 is None:
                return False
            r1 = sel.radius
            bigger = [i for i in range(len(allcells)) if allcells[i].radius > sel.radius]
            for i in bigger:
                r2 = allcells[i].radius
                # 现在的位置矢量
                dist = chuan([-(sel.pos[0] - allcells[i].pos[0]), -(sel.pos[1] - allcells[i].pos[1])])
                v = v_org[0] - allcells[i].veloc[0], v_org[1] - allcells[i].veloc[1]
                t = time(r1, r2, dist, v)
                if t is not None and t <= time0:
                    return True
            return False

        """评估函数"""

        def safe_index(my_cell):
            nonlocal allcells, INF
            bigger = [i for i in range(len(allcells)) if allcells[i].radius > my_cell.radius]
            index = INF
            r_sub = None
            for i in bigger:
                t = time_meeting(my_cell, allcells[i])
                r, t2 = npc_enlarge(allcells[i])
                coll = distance(my_cell, allcells[i]) - my_cell.radius - allcells[i].radius
                t = coll*50 if t is None or coll*50 < t else t
                if r + my_cell.radius > distance(my_cell, allcells[i]) and t2 is not None:
                    t = t2 if t is None or t2 < t else t
                r, t2 = npc_enlarge(my_cell)
                if r + allcells[i].radius > distance(my_cell, allcells[i]) and t2 is not None:
                    t = t2 if t is None or t2 < t else t
                if t is not None and t < index:
                    index = t
                    r_sub = i
                elif t == index:
                    r_sub = i if allcells[i].radius > my_cell.radius else r_sub
            return r_sub, index

        def evaluate(sel, target):
            r1 = sel.radius
            r2 = target.radius
            r, time_enlarge = npc_enlarge(target)
            theta = eat(sel, target)
            v_new = new_velocity(sel, theta)  # 喷射后的速度
            dict = target.pos[0] - sel.pos[0], target.pos[1] - sel.pos[1]
            v1 = sel.veloc[0] - target.veloc[0], sel.veloc[1] - target.veloc[1]
            v2 = v_new[0] - target.veloc[0], v_new[1] - target.veloc[1]
            time_non = time(r1, r2, dict, v1)  # 不喷
            time_ej = time(r1, r2, dict, v2) # 喷
            # 以下重要
            # loss_ratio = 0.1
            # value_non = r2**2/time_non if time_non is not None else -INF
            # value_ej = r2**2/time_ej - r1**2*Consts["EJECT_MASS_RATIO"]*loss_ratio**2 if time_ej is not None else -INF
            loss_ratio = 2
            arg = 1.045  # 一个玄学的balance参数，不可超过1.06
            value_non = r2 ** 2 / time_non / (r1 ** 2) if time_non is not None else -INF
            value_ej = arg * (r2 ** 2 - r1 ** 2 * Consts["EJECT_MASS_RATIO"] * loss_ratio) / time_ej / (
                    r1 ** 2)-(norm(sel.veloc)/5)**2 if time_ej is not None else -INF
            # value_ej = INF

            if r2**3/r1**2/dang1(sel, target) > 0.4:
                value_ej = INF
            if time_non is not None and time_non < 25:
                value_non = INF
            # 判断路径上有无大球
            if barrier(sel, sel.veloc, time_non):
                value_non = -INF
            if barrier(sel, v_new, time_ej):
                value_ej = -INF
            # 判断会不会在追击时变得过小
            if time_ej is not None:
                r_final = sqrt(r1 ** 2 * 0.99 ** ceil(time_ej))
            else:
                r_final = sel.radius
            if time_ej is not None:
                if r_final < r2:
                    value_ej = -INF
            # 判断目标会不会突然变大
            if r > r_final and time_enlarge is not None:
                if time_non is not None and time_non > time_enlarge:
                    value_non -= INF
                if time_ej is not None and time_ej > time_enlarge:
                    value_ej -= INF

            if value_non >= value_ej:
                return None, value_non
            else:
                return theta, value_ej

        """行动函数"""

        def escape(me, op):
            dist = op.pos[0] - me.pos[0], op.pos[1] - me.pos[1]
            dist = chuan(dist)
            v = me.veloc[0] - op.veloc[0], me.veloc[1] - op.veloc[1]
            best = [dist[0] - v[0], dist[1] - v[1]]
            return thet([0, 1], best)

        def eat(sel, cel):  # 吃球函数
            # sel不会朝着目标的方向加速，而是与该方向呈一定夹角的角度，该夹角的计算依赖于相对速度与该方向的夹角
            # 具体详见下面代码
            # p1,p2分别为自己和目标的坐标，v1位相对速度，a为自己朝向目标的向量，其他参数则不需要使用
            p1 = sel.pos
            p2 = cel.pos
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            a = [p2[0] - p1[0], p2[1] - p1[1]]
            a = chuan(a)
            p2 = [p1[0] + a[0], p1[1] + a[1]]
            p3 = [p1[0] + v1[0], p1[1] + v1[1]]

            b = [p3[0] - p1[0], p3[1] - p1[1]]
            c = [p2[0] - p3[0], p2[1] - p3[1]]
            theta1 = thet([-v1[0], -v1[1]], c)
            theta0 = thet([0, 1], [-v1[0], -v1[1]]) + pi
            time_min = INF
            if theta1 > pi:
                theta1 = theta1 - 2 * pi
            theta = theta1
            # for i in range(-10, 11):
            #     t = theta1*(1+i/200)
            #     v = new_velocity(sel, t + theta0)
            #     tim = time(sel.radius, cel.radius, a, v)
            #     if tim and tim < time_min:
            #         theta = t
            # r1即为所说的修正系数，下面的stra3函数修改了此处的r1
            # r1为重要参数(函数参数)*****************，不同的r1意味着不同的吃球速度和开销
            r = abs(theta1 / pi)
            if r > 0.9:
                r1 = 1 - 5 * (1 - r)
            else:
                r1 = r ** 3
            theta = theta*r1  # r1相当于歪了一个角度
            return theta0 + theta

        def eat_new(sel, cel):
            p1 = sel.pos
            p2 = cel.pos
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            dist = chuan([p2[0]-p1[0], p2[1]-p1[1]])
            theta = best_choice(dist, v1)
            return theta


        """常数"""
        INF = float('inf')
        WX = Consts["WORLD_X"]
        WY = Consts["WORLD_Y"]

        """战略主程序"""

        warn = safe_index(allcells[self.id])
        if warn[1] <= 200 and warn[0] is not None:
            theta = escape(allcells[self.id], allcells[warn[0]])
            return theta

        cell_absorb = get_absorbable(allcells[self.id])
        # cell_absorb 参数为cell列表和id，返回一个cell的list，
        max_eval, theta = -INF, None
        for cell in cell_absorb:
            t, now_eval = evaluate(allcells[self.id], cell)
            # evaluate用来评估合理性
            if now_eval > max_eval:
                max_eval = now_eval
                theta = t
        return theta
