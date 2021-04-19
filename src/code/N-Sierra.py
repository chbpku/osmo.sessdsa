from consts import Consts
from math import *
from random import randrange
from cell import Cell
import math

class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.target = None
        self.n = 0
        self.m = 0
        self.d = 1

    def strategy(self, allcells):
        # 基本几何函数---------------------------------
        # 用于后续操作的星体坐标系
        def norm(v):  # 返回v的2范数
            return sqrt(v[0] ** 2 + v[1] ** 2)

        # cell.py第47行distance_from 两球的距离
        def distance(self, other):
            return Cell.distance_from(self, other)

        # 用于后续操作的星体坐标系
        def chuan(v):
            list1 = [v[0], v[0] + Consts["WORLD_X"], v[0] - Consts["WORLD_X"]]
            list2 = [v[1], v[1] + Consts["WORLD_Y"], v[1] - Consts["WORLD_Y"]]
            list1.sort(key=abs, reverse=True)
            list2.sort(key=abs, reverse=True)
            return [list1.pop(), list2.pop()]

        def direction(self, other):  # 方向向量,cel1为参照
            v = [self.pos[0] - other.pos[0], self.pos[1] - other.pos[1]]
            return direction_v(v)

        def relative_speed(self, other):  # 相对速度
            vx = -self.veloc[0] + other.veloc[0]
            vy = -self.veloc[1] + other.veloc[1]
            return [vx, vy]

        def coordinate(cells):  # 坐标系转换,为实现allcells转换这里是cells，可以带入cellsthen等等cellgroup
            coordinatecells = []
            for cell in cells:
                x = Cell.__init__(cell, id=cell.id, pos=direction(cell), veloc=relative_speed(cell), radius=cell.radius)
                coordinatecells.append(x)
            return coordinatecells

        # 向量夹角
        def costheta(a, b):
            c = [b[0] - a[0], b[1] - a[1]]
            an = norm(a)
            bn = norm(b)
            cn = norm(c)
            cos = (an ** 2 + bn ** 2 - cn ** 2) / (2 * an * bn)
            if cos < 1e-6:
                return 0
            else:
                return cos

        def jia(a, b):
            y = costheta(a, b)
            if abs(y) < 1:
                x = math.acos(y)
                return pi - abs(pi - x)
            else:
                return 0

        # 相撞距离见cell.py line62
        # collide(self,other)
        def collide(self, other):
            return Cell.collide(self, other)

        def vsum(v1, v2):
            return [v1[0] + v2[0], v1[1] + v2[1]]

        def vmulti(v, m):
            return [v[0] * m, v[1] * m]

        def after_collide(cel1, cel2):
            if collide(cel1, cel2):
                celllist = [cel1, cel2]
                celllist.sort(key=lambda ele: self.cells[ele].radius)  # 排序找出最大球
                biggest = cellist.pop()
                m1 = cel1.radius ^ 2
                m2 = cel2.radius ^ 2
                M = m1 + m2
                biggest.radius = math.sqrt(M)
                v = vmulti(vmulti(cel1.veloc, m1) + vmulti(cel2.veloc, m2), 1 / M)
                biggest.veloc = limit.speed(v)
            return biggest

        def after_eject(self, theta):
            eject = Cell()
            fx = math.sin(theta)
            fy = math.cos(theta)
            eject.veloc = vsum(self.veloc, vmulti([fx, fy], Consts["DELTA_VELOC"] * (1 - Consts["EJECT_MASS_RATIO"])))
            self.veloc[0] -= Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
            self.veloc[1] -= Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
            eject.radius = player.radius * Consts["EJECT_MASS_RATIO"] ** 0.5
            self.radius *= (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5

        # 预测相撞情况
        def collide_possible(direction, speed, rsum):
            a = norm(direction)
            if a < rsum + 1e-6:
                return True, 0
            cosc = costheta(direction, speed)
            acos = 2 * a * cosc
            ac2 = a ** 2 - c ** 2
            test = acos ** 2 - 4 * ac2
            if test < 0 or cosc < 0:
                return False, None
            else:
                return True, (acos - math.sqrt(test)) / 2 / norm(speed)

        def collide_time(self, other):
            # 利用相对位置、相对速度
            v1 = direction(self, other)
            a = norm(v1)
            c = self.radius + other.radius
            if norm(v1) < c + 1e-6:  #
                return 0
            # c2=a2+b2-2abcosc
            v2 = relative_speed(self, other)
            cosc = costheta(v1, v2)
            acos = 2 * a * cosc
            ac2 = a ** 2 - c ** 2
            test = acos ** 2 - 4 * ac2
            if test < 0 or cosc < 0:
                return None
            else:
                return (acos - math.sqrt(test)) / 2 / norm(v2)

        def loss(sel, cel):  # 返回最小喷球次数
            nonlocal dv2
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            dist = chuan(dist)
            v = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            if norm(dist) == 0:
                return 0
            else:
                theta1 = (sel.radius + cel.radius) / norm(dist)
                # 两球心对自己球的张角
                if theta1 < 1:
                    theta1 = asin(theta1)
                jiao = jia(v, dist)
                if jiao < theta1:
                    return 0
                # 如果速度在张角内，没有损失
                else:
                    return abs(jiao - theta1) * norm(v) / dv2 * (1 + norm(v) ** 2) + 3

        # 预测接下来t时间内的变化
        def encounter(self):
            # 返回球cel在场上所有可能吃到的球及吃到他们所需的时间，吃到他们后的位置，速度，半径
            bigcells = []
            smallcells = []
            times1 = []
            times2 = []
            for cell in allcells:
                if cell.dead or cell == self:
                    continue
                elif cell.radius >= self.radius:
                    times1.append(collide_time(self, cell))
                    bigcells.append(after_collide(self, cell))
                else:
                    times2.append(collide_time(self, cell))
                    smallcells.append(after_collide(self, cell))
            return (bigcells, times1, smallcells, times2)

        def delta1(allcells):
            cellsthen = []
            for cell in allcells:
                x = cell
                x.pos[0] += x.veloc[0] * 1
                x.pos[1] += x.veloc[1] * 1
                x.stay_in_bounds()
                x.limit_speed()
                cellsthen.append(x)
            return cellsthen

        def deltat(allcells, t):
            if t == 1:
                cellsthen = delta1(allcells)
                return cellsthen
            else:
                return deltat(deltat(allcells, t - 1), t - 1)

        def dianzhi(a, b, c):  # 3坐标a,b,c,返回a到直线bc的距离
            d = abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / sqrt(
                (b[0] - c[0]) ** 2 + (b[1] - c[1]) ** 2)
            if d < 1e-6:
                return 0
            else:
                return d

        def thet(a, b):  # 向量a到b的有向角([0,2pi))
            if (a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2) < 1e-6:
                return 0
            # 如果两向量有一个为0，则认为是0夹角
            cha = a[0] * b[1] - a[1] * b[0]
            # a叉乘b的结果，用于判断方向
            jia = (a[0] * b[0] + a[1] * b[1]) / sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2))
            # 点乘求夹角cos
            if abs(jia) > 1 - 1e-3:
                if jia < 0:
                    return pi
                else:
                    return 0
            jia = acos(jia)
            if cha > 0:
                return 2 * pi - jia
            else:
                return jia

        def chuan(v):  # 穿屏向量
            nonlocal WX, WY
            lis = [v[0] - WX, v[0], v[0] + WX]
            min1 = abs(lis[0])
            i_min = 0
            for i in range(3):
                if abs(lis[i]) < min1:
                    i_min = i
                    min1 = abs(lis[i])
            v0 = lis[i_min]
            # 找到绝对值最小的向量

            lis = [v[1] - WY, v[1], v[1] + WY]
            min1 = abs(lis[0])
            i_min = 0
            for i in range(3):
                if abs(lis[i]) < min1:
                    i_min = i
                    min1 = abs(lis[i])
            v1 = lis[i_min]
            return [v0, v1]

        def chuan1(cel):  # 返回cel相对sel的穿屏坐标(即sel.pos+chuan(cel.pos-sel.pos))
            nonlocal sel
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            dist = chuan(dist)
            p = [sel.pos[0] + dist[0], sel.pos[1] + dist[1]]
            return p

        def dang(r1, r2, dist, v1):  # 相撞距离,参数为两球半径，dist是相距’向量‘，v1是相对速度
            return norm(dist) - r1 - r2

        def dang1(sel, cel):  # 当给出的参数为两个细胞时的相撞距离
            r1 = sel.radius
            r2 = cel.radius
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            return dang(r1, r2, dist, 0)

        def time(r1, r2, dist, v1):  # 预测两球的相撞时间，v1为1相对2的速度，dis为相对坐标
            dist = chuan(dist)
            if norm(v1) < dang(r1, r2, dist, v1) * 0.01:
                return None
            # 当v1*100还小于距离时，认为不会相碰（0.01为自设参数）
            if v1[0] * dist[0] + v1[1] * dist[1] < 0:
                return None
            # 如果速度与距离夹角绝对值大于九十度认为不相碰
            h = dianzhi(dist, [0, 0], v1)
            if r1 + r2 < h + 1e-3:
                return None
            # 如果半径之和大于相对位置到速度向量的距离则不能相碰
            else:
                l1 = sqrt((r1 + r2) ** 2 - h ** 2)
                l2 = norm(dist) ** 2 - h ** 2
                if l2 < 1e-4:
                    return None
                l2 = sqrt(l2)
                return (l2 - l1) / norm(v1)

        def time1(sel, cel):  # 当给出的参数为两个球时的相撞时间计算
            r1 = sel.radius
            r2 = cel.radius
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            dist = chuan(dist)
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            return time(r1, r2, dist, v1)

        def qie(sel, cel):  # 相对于目标cel相撞还需行进的距离(time1(sel,cel)*norm(v))
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            time = time1(sel, cel)
            # 用相撞时间乘以v1即可
            if time is None:
                return None
            else:
                return time * norm(v1)

        def stra1(sel, cel):  # 吃球函数
            # sel不会朝着目标的方向加速，而是与该方向呈一定夹角的角度，该夹角的计算依赖于相对速度与该方向的夹角
            # 具体详见下面代码
            # p1,p2分别为自己和目标的坐标，v1位相对速度，a为自己朝向目标的向量，其他参数则不需要使用
            nonlocal dv2
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
            if theta1 > pi:
                theta1 = theta1 - 2 * pi

            # r1即为所说的修正系数，下面的stra3函数修改了此处的r1
            # r1为重要参数(函数参数)*****************，不同的r1意味着不同的吃球速度和开销
            r = abs(theta1 / pi)
            if r > 0.9:
                r1 = 1 - 5 * (1 - r)
            else:
                r1 = r ** 3
            theta = theta1 * r1
            return thet([0, 1], [-v1[0], -v1[1]]) + theta + pi

        def stra3(sel, cel):  # 分段吃球函数
            def duan(t):  # duan即位所说的分段函数,duan(r1)为修正系数
                if t < 0.7:
                    return t ** 2
                else:
                    return t

            nonlocal dv2
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
            # 在己方速度过小时不采用该吃球函数而是直接飞向目标，因为小速度意味着必须要考虑加速度的离散性，控制不好就会乱喷
            if norm(v1) < 0.3:  # *************
                return thet([0, 1], a) + pi

            if theta1 > pi:
                theta1 = theta1 - 2 * pi

            # 比
            r = abs(theta1 / pi)
            # r1为重要参数(函数参数)******************，不同的r1意味着不同的吃球速度和开销
            r1 = r
            theta = theta1 * duan(r1)
            return thet([0, 1], [-v1[0], -v1[1]]) + theta + pi

        def stra1_J(sel, cel):
            nonlocal dv1
            nonlocal rat
            alpha = rat
            u = dv1
            S = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            Sx = float(S[0])
            Sy = -float(S[1])
            v = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            vx = 1 * float(v[0])
            vy = -1 * float(v[1])
            a = -25*u * math.log(1 - alpha)
            t = solveEquation(-a ** 2 / 4, 0, norm(v) ** 2, -2 * (vx * Sx + vy * Sy), norm(S) ** 2)
            ax = 2 * (vx * t - Sx) / t ** 2
            ay = -2 * (vy * t - Sy) / t ** 2
            phi = thet([0, 1], [ax, ay])
            if phi > pi:
                phi -= 2 * pi
            return phi

        def solveEquation(a, b, c, d, e):
            P = (c ** 2 + 12 * a * e - 3 * b * d) / 9
            Q = (27 * a * (d ** 2) + 2 * (c ** 3) + 27 * (b ** 2) * e - 72 * a * c * e - 9 * b * c * d) / 54
            D = (Q ** 2 - P ** 3) ** (1 / 2)

            if abs(Q + D) >= abs(Q - D):
                u = (Q + D) ** (1 / 3)
            else:
                u = (Q - D) ** (1 / 3)

            if u != 0:
                v = P / u
            else:
                v = 0

            w = complex(-1 / 2, 3 ** (1 / 2) / 2)

            m = 0
            for k in range(1, 4):
                m_k = (b ** 2 - 8 * a * c / 3 + 4 * a * ((w ** (k - 1)) * u + (w ** (4 - k)) * v)) ** (1 / 2)
                if abs(m_k) >= abs(m):
                    m = m_k
                    k_mark = k

            k = k_mark
            if m != 0:
                S = 2 * b ** 2 - 16 * a * c / 3 - 4 * a * (w ** (k - 1) * u + w ** (4 - k) * v)
                T = (8 * a * b * c - 16 * (a ** 2) * d - 2 * b ** 3) / m
            elif m == 0:
                S = b ** 2 - 8 * a * c / 3
                T = 0

            x_n = []  # save all roots in x_n
            for n in range(1, 5):
                if math.ceil(n / 2) == 1:
                    x = (- b - m + (-1) ** (n + 1) * (S - T) ** (1 / 2)) / (4 * a)
                elif math.ceil(n / 2) == 2:
                    x = (- b + m + (-1) ** (n + 1) * (S + T) ** (1 / 2)) / (4 * a)
                x_n.append(x)

            x_optimized = []  # get a non-negative, non-complex, minimum root
            for x in x_n:
                if (x.real > 0) and (abs(x.imag) < 1.0e-10):
                    x_optimized.append(x.real)
            '''
            if x_optimized == None:
                for x in x_n:
                    if (x.real > 0):
                        x_optimized.append(abs(x))
            '''
            x_optimized.sort()
            x = x_optimized[0]
            return x

        def stra2(p1, p2, v1, dv2):  # 躲球函数，直接对着目标喷球
            v = [p2[0] - p1[0], p2[1] - p1[1]]
            v = chuan(v)
            v3 = [v[0] - v1[0], v[1] - v1[1]]
            return thet([0, 1], v3)

        def guibi(sel, cell):  # 躲球函数(参数为sel,cel)
            nonlocal dv2
            selp = sel.pos
            selv = sel.veloc
            celp = cell.pos
            celv = cell.veloc
            return stra2(selp, celp, [selv[0] - celv[0], selv[1] - celv[1]], dv2)

        def time_li_x(cel):  # 返回time,deltar函数列表,只看比自己小的求
            nonlocal allcells
            lst1 = []
            lst2 = []
            r1 = cel.radius
            for i in range(len(allcells)):
                cel1 = allcells[i]
                if cel1.dead == True or cel1 == cel or cel1.radius >= cel.radius:
                    lst1.append(None)
                    lst2.append(None)
                    continue
                r2 = cel1.radius
                dist = [cel1.pos[0] - cel.pos[0], cel1.pos[1] - cel.pos[1]]
                v1 = [cel.veloc[0] - cel1.veloc[0], cel.veloc[1] - cel1.veloc[1]]
                t = time(r1, r2, dist, v1)
                lst1.append(t)
                if t != None:
                    lst2.append(sqrt(r1 ** 2 + r2 ** 2) - r1)
                else:
                    lst2.append(None)

            return [lst1, lst2]

        # 预测函数-----------------------------------------
        def time_li_x_c(cel):  # 返回球cel在场上所有可能吃到的球及吃到他们所需的时间，吃到他们后的位置，速度，半径
            nonlocal allcells
            lst1 = []
            lst2 = []
            lst3 = []
            r1 = cel.radius
            for i in range(2, len(allcells)):
                cel1 = allcells[i]
                if cel1.dead == True or cel1 == cel or cel1.radius >= cel.radius:
                    lst1.append(None)
                    lst2.append(None)
                    lst3.append(None)
                    continue
                r2 = cel1.radius
                dist = [cel1.pos[0] - cel.pos[0], cel1.pos[1] - cel.pos[1]]
                v1 = [cel.veloc[0] - cel1.veloc[0], cel.veloc[1] - cel1.veloc[1]]
                t = time(r1, r2, dist, v1)
                lst1.append(t)
                if t != None:
                    lst2.append(sqrt(r1 ** 2 + r2 ** 2) - r1)
                    lst3.append(jiehe_yu(cel, cel1))
                else:
                    lst2.append(None)
                    lst3.append(None)

            return [lst1, lst2, lst3]

        def time_li_all_c(cel):  # 和上一函数相同，但同时考虑被吃的情形
            nonlocal allcells
            lst1 = []
            lst2 = []
            lst3 = []
            r1 = cel.radius
            for i in range(2, len(allcells)):
                cel1 = allcells[i]
                if cel1.dead == True or cel1 == cel:
                    lst1.append(None)
                    lst2.append(None)
                    lst3.append(None)
                    continue
                r2 = cel1.radius
                dist = [cel1.pos[0] - cel.pos[0], cel1.pos[1] - cel.pos[1]]
                v1 = [cel.veloc[0] - cel1.veloc[0], cel.veloc[1] - cel1.veloc[1]]
                t = time(r1, r2, dist, v1)
                lst1.append(t)
                if t != None:
                    lst2.append(sqrt(r1 ** 2 + r2 ** 2) - r1)
                    lst3.append(jiehe_yu(cel, cel1))
                else:
                    lst2.append(None)
                    lst3.append(None)

            return [lst1, lst2, lst3]

        def jiehe(cel1, cel2):  # 返回两球结合后的半径和速度
            r1 = cel1.radius
            r2 = cel2.radius
            v1 = cel1.veloc
            v2 = cel1.veloc
            r = sqrt(r1 ** 2 + r2 ** 2)
            v = [(r1 ** 2 * v1[0] + r2 ** 2 * v2[0]) / (r1 ** 2 + r2 ** 2),
                 (r1 ** 2 * v1[1] + r2 ** 2 * v2[1]) / (r1 ** 2 + r2 ** 2)]
            return r, v

        def jiehe_yu(cel1, cel2):  # 返回两球结合后的位置，半径，速度
            t = time1(cel1, cel2)
            if t != None:
                if cel1.radius > cel2.radius:
                    p1 = cel1.pos
                    v1 = cel1.veloc
                    p = [p1[0] + v1[0] * t, p1[1] + v1[1] * t]
                    r, v = jiehe(cel1, cel2)

                else:
                    p2 = cel2.pos
                    v2 = cel2.veloc
                    p = [p2[0] + v2[0] * t, p2[1] + v2[1] * t]
                    r, v = jiehe(cel1, cel2)
            return p, r, v

        def jiao(l1, l2):  # 判断两球是否已经相交
            p1 = l1[0]
            p2 = l2[0]
            dist = [p2[0] - p1[0], p2[1] - p1[1]]
            dist = chuan(dist)
            r1 = l1[1]
            r2 = l2[1]
            return norm(dist) < r1 + r2


        def get(sel, cel):  # 吃球收益估计，返回预测吃到该球后自身质量会变成现在质量的倍数
            nonlocal rat
            los = loss(sel, cel)
            # 参数
            r1 = sel.radius
            r2 = cel.radius
            s1 = r1**2
            s11 = s1 * (1 - rat) ** los
            s = s11 + r2 ** 2
            k = s / (r1 ** 2)
            if k < 1.2:
                return None
            else:
                return k

        def howl(sel, cel):  # 预测吃到球cel所需花费时间
            t1 = dang1(sel, cel) / max(norm(
                [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]), 0.2)
            t2 = loss(sel, cel)
            return t1 + t2

        def kechi(sel, xiao_li, da_li):
            kechi_li = []
            for cel in xiao_li:
                if dang1(sel, cel) < control1:
                    los = loss(sel, cel)
                    dt = howl(sel, cel)
                    lst = time_li_all_c(cel)
                    # lst用来记录目标球在接下来的时间内可能会吃球或被吃的情况，避免出现本想吃掉小球它却突然变大的情况
                    peng_li = []
                    # peng_li记录cel可能吃或被吃的球的半径
                    for j in da_li:
                        # 先判断路上没有大球
                        a = chuan([j.pos[0] - selp[0], j.pos[1] - selp[1]])
                        # a为自己到j的矢量
                        b = chuan([cel.pos[0] - selp[0], cel.pos[1] - selp[1]])
                        # b为自己到目标的矢量
                        if (dianzhi(chuan1(j), selp, chuan1(cel)) < selr + j.radius + 30 and
                                a[0] * b[0] + a[1] * b[1] > 0 and a[0] * b[0] + a[1] * b[1] < norm(b) ** 2):
                            # 判断方法：a\b夹角小于90°且a在b上的投影小于b，j到行进直线的距离小于半径和（保险起见加了30）
                            break
                    else:
                        # 如果没有找到大球然后判断目标球会不会在dt时间内变大
                        for i in range(len(lst[0])):
                            if lst[0][i] != None and lst[0][i] < dt:
                                peng_li.append(lst[2][i][1])
                        # 在dt内能与目标球碰撞后的半径
                        for r in peng_li:
                            if r > cel.radius:
                                break
                        # 如果目标球被吃了直接终止行动
                        else:
                            mo = cel.radius ** 2 + sum([x ** 2 for x in peng_li])
                            if selr ** 2 * (1 - rat) ** los > 1.1*mo:
                                # 保险起见再次分析能否将其吃下
                                # 至此已排除危险而后进行利益最大化
                                shouyi1 = get(sel, cel)
                                dis = distance(sel, cel)
                                p1 = sel.pos
                                p2 = cel.pos
                                v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
                                a = [p2[0] - p1[0], p2[1] - p1[1]]
                                a = chuan(a)
                                p2 = [p1[0] + a[0], p1[1] + a[1]]
                                p3 = [p1[0] + v1[0], p1[1] + v1[1]]
                                c = [p2[0] - p3[0], p2[1] - p3[1]]
                                theta1 = thet([-v1[0], -v1[1]], c)
                                if theta1 > pi:
                                    theta1 = theta1 - 2 * pi
                                angle = abs(theta1 / pi)
                                if shouyi1 != None:
                                    kechi_li.append([cel, shouyi1, dis, angle])
            return kechi_li

        # 常数
        WX = Consts["WORLD_X"]
        WY = Consts["WORLD_Y"]
        dv1 = Consts["DELTA_VELOC"]  # 喷射速度
        rat = Consts["EJECT_MASS_RATIO"]
        dv2 = dv1 * Consts["EJECT_MASS_RATIO"]  # 得到速度
        if len(allcells) < 2:
            return None
        sel = allcells[self.id]
        selp = sel.pos
        selv = sel.veloc
        selr = sel.radius

        # 吃
        da_li = []
        xiao_li = []
        for i in allcells[1:]:
            if i.radius < selr:
                xiao_li.append(i)
            else:
                da_li.append(i)
        # 建立比自己小的或者大的球的列表
        control1 = 300
        control2 = 30
        q_dis = 0.06
        q_ang = 1/pi
        chi_li = kechi(sel, xiao_li, da_li)
        target1 = None
        #print(self.m)
        #print('=',self.n)
        if self.d == 0:
            self.d = 1
            if self.n > 0:
                self.n -= 1
                target = self.target
                if self.n == 1:
                    self.m = howl(sel, target)
                if target != None:
                    if target.radius > sel.radius:
                        target = None
                        self.target = None
                        self.n = 0
                        self.m = 0
                    else:
                        return stra1_J(sel, target)
            else:
                if self.m > 0:
                    self.m -= 1
                else:
                    if len(chi_li) < control2:
                        for u in chi_li:
                            if target1 == None:
                                target1 = u[0]
                                shou = u[1]
                                cou = shou - q_dis * u[2] - q_ang * u[3]
                            else:
                                if cou < u[1] - q_dis * u[2] - q_ang * u[3]:
                                    shou = u[1]
                                    cou = shou - q_dis * u[2] - q_ang * u[3]
                                    target1 = u[0]
                            # 执行吃球，此处设置max1>1.1因为损失函数和收益函数都不是精确的，保守起见在预测收益较大时才选择吃球
                            if target1 != None and shou > 1.3:
                                # 所有条件满足，设置target
                                target = target1
                                v = [sel.veloc[0] - target.veloc[0], sel.veloc[1] - target.veloc[1]]
                                # 此处的2个条件(1)吃到目标球的角度还没对，体现在loss>0,或者吃到目标球的速度还不大，体现在norm(v)<参数
                                # 0.3********************重要参数
                                if norm(v) < 0.3 or loss(sel, target) > 0:
                                    self.n = loss(sel, target)
                                    self.target = target
                                    print(target.pos)

                                    return stra1_J(sel, target)  # 更改吃球函数

                                else:
                                    return None
                    else:
                        for i in chi_li:
                            shouyi1 = i[1]
                            kechi2 = kechi(i[0], xiao_li)
                            for j in kechi2:
                                if j[0].id != i[0].id:
                                    shouyi2 = j[1]
                                    shouyi = shouyi1 * shouyi2
                                    if shouyi > shou:
                                        shou = shouyi
                                        if target1 != None:
                                            target = target1
                                            v = [sel.veloc[0] - target.veloc[0], sel.veloc[1] - target.veloc[1]]
                                            # 此处的2个条件(1)吃到目标球的角度还没对，体现在loss>0,或者吃到目标球的速度还不大，体现在norm(v)<参数
                                            # 0.3********************重要参数
                                            if norm(v) < 0.3 or loss(sel, target) > 0:
                                                self.n = loss(sel, target)
                                                self.target = target
                                                return stra1_J(sel, target)
        else:
            self.d -= 1
        # 跑--------------------------------------------
        dada=[]
        for i in allcells:
            if i.radius>selr and i.dead != True:
                dada.append(i)
        t_min = None
        d_min = None
        i_t_min =None
        i_d_min = None
        for i in range(len(dada)):
            celp = dada[i].pos
            celv = dada[i].veloc
            t = time1(sel, dada[i])
            d = qie(sel,dada[i])
            if d!=None:
                if i_d_min == None:
                    i_d_min=i
                    d_min=d
                else:
                    if d<d_min:
                        d_min=d
                        i_d_min=i
            if t !=None:
                if i_t_min== None:
                    i_t_min=i
                    t_min=t
                else:
                    if t<t_min:
                        t_min=t
                        i_t_min=i
        if len(dada) > 20:
            if d_min != None and d_min / sqrt(selr) < 5:
                self.target = None
                cell = dada[i_d_min]
                celp = cell.pos
                celv = cell.veloc
                return stra2(selp, celp, [selv[0] - celv[0], selv[1] - celv[1]], dv2)
        else:
            if t_min != None and t_min < 60:
                self.target = None
                cell = dada[i_t_min]
                celp = cell.pos
                celv = cell.veloc
                return stra2(selp, celp, [selv[0] - celv[0], selv[1] - celv[1]], dv2)



