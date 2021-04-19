from consts import Consts
from math import *
import math
import cmath


class Acord():  # 每一个cell与myself对应的距离参数（们）的记录
    def __init__(self):
        self.distance = 0
        self.angle = 0
        self.t = 0

    def __lt__(self, other):
        return (self.t < other.t)

    def __gt__(self, other):
        return (self.t > other.t)


class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.target = None
        self.id = id
        self.tag = 0
        self.theta = []
        self.prey = [None, None]
        self.radius = 0

    ################################################################################################
    # 各种基本参数

    def pos(self, acell, bcell):  # 穿屏操作1
        dx = bcell.pos[0] - acell.pos[0]
        dy = bcell.pos[1] - acell.pos[1]
        if dx > Consts["WORLD_X"] / 2:
            dx -= Consts["WORLD_X"]
        elif dx < -Consts["WORLD_X"] / 2:
            dx += Consts["WORLD_X"]
        if dy > Consts["WORLD_Y"] / 2:
            dy -= Consts["WORLD_Y"]
        elif dy < -Consts["WORLD_Y"] / 2:
            dy += Consts["WORLD_Y"]

        return (dx, dy)

    def through(self, cell1, cell2):  # 穿屏操作2
        rl_x = cell2.pos[0] - cell1.pos[0]
        rl_y = cell2.pos[1] - cell1.pos[1]
        rv_x = cell2.veloc[0] - cell1.veloc[0]
        rv_y = cell2.veloc[1] - cell1.veloc[1]
        if rl_x * rv_x + rl_y * rv_y >= 0:
            if rv_x > 0:
                cell2.pos[0] -= Consts["WORLD_X"]
            if rv_y > 0:
                cell2.pos[1] -= Consts["WORLD_Y"]
            if rv_x < 0:
                cell2.pos[0] += Consts["WORLD_X"]
            if rv_y < 0:
                cell2.pos[1] += Consts["WORLD_Y"]

    def dist(self, acell, bcell):  # 计算两球距离
        return acell.distance_from(bcell)

    def vel(self, acell, bcell):
        """相对速度"""
        return (bcell.veloc[0] - acell.veloc[0], bcell.veloc[1] - acell.veloc[1])

    def norm(self, v):  # 计算向量长度
        return math.sqrt(v[0] ** 2 + v[1] ** 2)

    def myangle(self, a, b):  # 返回向量a,b的夹角,a->b逆时针为正(-pi~pi)
        ac = complex(a[0], a[1])
        bc = complex(b[0], b[1])
        alpha = float((cmath.polar(ac))[1])
        beta = float((cmath.polar(bc))[1])
        return (alpha - beta)

    def perpendicular(self, a, b, c):  # 三个点a,b,c;返回a到直线bc的距离
        u1 = [c[0] - b[0], c[1] - b[1]]
        u2 = [a[0] - b[0], a[1] - b[1]]
        if self.norm(u1) == 0:
            return 0
        u = abs(u1[0] * u2[0] + u1[1] * u2[1]) / self.norm(u1)
        # a = u2[0] ** 2 + u2[1] ** 2 - u ** 2
        if u < 1e-6:
            return 0
        else:
            return u

    def dandt(self, l, v):  # 返回相对距离为l，相对速度为v时走到距离最近点的距离和时间[d,t]
        lrev = [-l[0], -l[1]]
        lv = self.myangle(lrev, v)
        d = self.norm(l) * abs(sin(lv))
        r = self.norm(l) * cos(lv)
        if self.norm(v) == 0:
            t = Consts["MAX_FRAME"]
        else:
            t = r / self.norm(v)
        return [d, t]

    ###############################################################################################
    # 追球函数

    def chase(self, cell, allcells):
        """如果值得追则修改self.theta,self.prey并返回True
        否则返回False并不修改buffer"""

        mycell = allcells[self.id]
        tic = Consts["FRAME_DELTA"]
        emr = Consts["EJECT_MASS_RATIO"]
        num_of_eject = 2
        while num_of_eject < 16:
            loss = mycell.radius ** 2 * (1 - (1 - emr) ** num_of_eject)
            if loss > cell.radius ** 2:
                return False

            dv = Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"] * (1 - Consts["EJECT_MASS_RATIO"])

            a = (num_of_eject ** 2 * dv ** 2 - self.vel(mycell, cell)[0] ** 2 - self.vel(mycell, cell)[
                1] ** 2) * tic ** 2
            b = -num_of_eject ** 2 * 2 * dv ** 2 * tic ** 2 - 2 * self.vel(mycell, cell)[0] * self.pos(mycell, cell)[
                0] * tic - 2 * self.vel(mycell, cell)[1] * self.pos(mycell, cell)[1] * tic
            c = num_of_eject ** 2 * dv ** 2 * tic ** 2 - self.dist(mycell, cell) ** 2

            if a == 0:
                return False

            if b ** 2 - 4 * a * c > 0:
                n1 = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
                n2 = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
                n = min(n1, n2)
                if n < 0:
                    n = max(n1, n2)
                    # n为追上需要的帧数
                if n > 0:
                    theta = math.atan2(self.vel(cell, mycell)[0] * n * tic + self.pos(cell, mycell)[0],
                                       self.vel(cell, mycell)[1] * n * tic + self.pos(cell, mycell)[1])
                    self.theta = [theta] * num_of_eject
                    self.tag = 1
                    self.prey[0] = cell.id
                    self.prey[1] = cell.radius
                    return True
            num_of_eject += 2
        return False

    def has_absorb(self, nowcell):
        # 判断自己是否吸收了新球导致状态改变
        if nowcell.radius > self.radius:
            return True
        else:
            return False

    def stop_chasing(self, allcells):
        # 停止追球
        mycell = allcells[self.id]
        self.prey[0] = None
        self.prey[1] = None
        self.tag = 0
        self.radius = mycell.radius

    def stillchase(self, allcells):
        # 判断是否处于追逐状态
        if self.prey[0]:
            for c in allcells:
                if c.id == self.prey[0]:
                    if math.fabs(c.radius - self.prey[1]) < 1 * 10 ** (-6):
                        return True
            return False

    ################################################################################################
    # 以下三个函数用于判断想要吃的球附近的情况（是否有很多其他可吃小球）
    def yimapingchuan(self, cel, allcells):
        """
        初级版本，只考虑是否直线
        """
        mycell = allcells[self.id]
        celllist = sorted(allcells, key=mycell.distance_from)
        for c in celllist:
            if c.id == cel.id:
                continue
            elif c.id == mycell.id:
                continue
            else:
                if c.radius > self.perpendicular(c.pos, mycell.pos, cel.pos) and c.radius > mycell.radius:
                    return False
        return True

    def neighbour(self, allcells):
        mycell = allcells[self.id]
        neighbourList = []
        for c in allcells:
            if c.id != mycell.id:
                if mycell.distance_from(c) < 200 and self.yimapingchuan(c, allcells):
                    neighbourList.append(c)
        return neighbourList

    def bestangle(self, allcells):
        # 选择合适的球去追
        mycell = allcells[self.id]
        if self.has_absorb(mycell):
            self.stop_chasing(allcells)
        if self.tag == 1:
            if self.stillchase(allcells):
                if len(self.theta) > 0:
                    return self.theta.pop()
                else:
                    return None
            else:
                self.prey[0] = None
                self.prey[1] = None
                self.tag = 0
        else:
            neighbourList = self.neighbour(allcells)
            neighbourList.sort(key=mycell.distance_from)
            neighbourList.sort(key=lambda c: c.radius, reverse=True)
            for c in neighbourList:
                if c.radius < mycell.radius:
                    theta = self.chase(c, allcells)
                    if theta:
                        return self.theta.pop()
            return None

    ################################################################################################
    # 逃跑函数

    def flee(self, celllist):
        danger = 18
        myself = celllist[self.id]
        dangerlist = []

        for i in celllist:
            if i.radius > myself.radius:
                self.through(myself, i)
                v = [i.veloc[0] - myself.veloc[0], i.veloc[1] - myself.veloc[1]]  # 相对myself的速度
                l = [i.pos[0] - myself.pos[0], i.pos[1] - myself.pos[1]]  # 以myself为原点的cell坐标（向量）
                r_sum = i.radius + myself.radius
                situation = self.dandt(l, v)
                d = situation[0]

                if i.id == 1 - self.id:  # 对方玩家可能会穷追猛打
                    if abs(self.myangle([-l[0], -l[1]], v)) < pi / 4 and (
                            self.norm(l) < 2.5 * r_sum or self.norm(l) < 3.5 * i.radius):
                        dangerlist.append([i, self.myangle([0, 1], l), l, r_sum])
                        continue
                    if self.norm(l) < 1.5 * r_sum:
                        dangerlist.append([i, self.myangle([0, 1], l), l, r_sum])
                        continue
                if d < r_sum:  # 一般的cell，计算撞上的时间，小于某值则加入dangerlist
                    if self.norm(v) == 0:
                        t = Consts["MAX_FRAME"]
                    else:
                        t = situation[1] - ((abs(r_sum ** 2 - d ** 2)) ** 0.5) / self.norm(v)
                    if Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"] * t < danger * self.norm(v):
                        dangerlist.append([i, self.myangle([0, 1], l), l, r_sum])

        if len(dangerlist) == 0:
            return None

        sum = 0
        for i in dangerlist:  # 取平均角度
            sum += i[1]
        aver = sum / len(dangerlist)
        if aver > 2 * pi:
            aver -= 2 * pi
        if aver < 0:
            aver += 2 * pi
        return aver

    def strategy(self, allcells):
        celllist = allcells.copy()  # 可能会更改cell的一些属性值，所以拷贝一份
        mycell = allcells[self.id]
        theta = self.flee(celllist)
        if theta:  # theta存在则说明存在危险需要逃跑
            self.theta = []
            self.stop_chasing(allcells)
            return theta
        else:  # 无危险则吃球
            theta = self.bestangle(allcells)
            self.radius = mycell.radius
            return theta
