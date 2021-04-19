from consts import Consts
from math import *
from random import randrange
from cell import Cell

WX = Consts["WORLD_X"]
WY = Consts["WORLD_Y"]
dv1 = Consts["DELTA_VELOC"]  # 喷射速度
rat = Consts["EJECT_MASS_RATIO"]
dv2 = dv1 * Consts["EJECT_MASS_RATIO"]  # 得到速度


class Player():
    def __init__(self, id, arg=None):
        self.id = id

    def strategy(self, allcells):
        self_cell = allcells[self.id]

        def mod(v):
            '''向量取模'''
            return sqrt(v[0] ** 2 + v[1] ** 2)

        def distance_from_point_to_line(A, B, C):
            '''向量法求A到直线BC的距离，我不太会，你们可以试着画一下图解作为实验报告的一部分（x'''
            u1 = [C[0] - B[0], C[1] - B[1]]
            u2 = [A[0] - B[0], A[1] - B[1]]
            u = abs(u1[0] * u2[0] + u1[1] * u2[1]) / mod(u1)
            temp = u2[0] ** 2 + u2[1] ** 2 - u ** 2
            if temp < 1e-6:
                '''不这样有时浮点数会得到负数，下同'''
                return 0
            else:
                return sqrt(temp)

        def theta(A, B):
            '''求两个向量的夹角'''
            if sqrt((A[0] ** 2 + A[1] ** 2) * (B[0] ** 2 + B[1] ** 2)) < 1e-6:
                return 0
            temp = (A[0] * B[0] + A[1] * B[1]) / mod(A) / mod(B)
            if temp > 1:
                '''防报错'''
                return 0
            elif temp < -1:
                return pi
            else:
                return acos(temp)

        def chuan(self_cell, other):
            '''获得两点间的穿屏向量'''
            dx0 = abs(self_cell.pos[0] - other.pos[0])
            dx1 = WX - dx0
            if self_cell.pos[0] - other.pos[0] > 0:
                if dx0 > dx1:
                    dx = dx1
                else:
                    dx = -dx0
            else:
                if dx0 > dx1:
                    dx = -dx1
                else:
                    dx = dx0
            dy0 = abs(self_cell.pos[1] - other.pos[1])
            dy1 = WY - dy0
            if self_cell.pos[1] - other.pos[1] > 0:
                if dy0 > dy1:
                    dy = dy1
                else:
                    dy = -dy0
            else:
                if dy0 > dy1:
                    dy = -dy1
                else:
                    dy = dy0
            return [dx, dy]

        def min_distance(self_cell, other):
            '''保持现有运动状态至两球相撞，other相对self参考系还要走多远，不撞返回None，
            画个图就看出来了我这是什么意思了，可写实验报告'''
            d = chuan(self_cell, other)
            v = [other.veloc[0] - self_cell.veloc[0], other.veloc[1] - self_cell.veloc[1]]
            # 相对速度矢量与位移矢量
            if d[0] * v[0] + d[1] * v[1] >= 0:
                '''这种情况是other远离自己，具体算法是取△t时间算之后的距离**2-之前的距离**2，
                忽略二阶小量后就是这个结果，助教给的和我大于小于号正好反了，不知道谁错了'''
                return None
            min_d = distance_from_point_to_line([0, 0], d, [d[0] + v[0], d[1] + v[1]])
            if min_d - self_cell.radius - other.radius > 1e-3:
                return None
            else:
                l1 = mod(d) ** 2 - min_d ** 2
                l2 = (self_cell.radius + other.radius) ** 2 - min_d ** 2
                if l1 < 1e-6:
                    l1 = 0
                if l2 < 1e-6:
                    l2 = 0
                return sqrt(l1) - sqrt(l2)

        # 重要说明，由于上下两个函数在碰撞不发生时返回None，因此调用它们时要先判断是否为None

        def collision_time(self_cell, other):
            '''保持现有运动状态至两球相撞所用时间'''
            x = min_distance(self_cell, other)
            if x == None:
                return None
            else:
                v = [other.veloc[0] - self_cell.veloc[0], other.veloc[1] - self_cell.veloc[1]]
                return x / mod(v)

        def find_big_cell(self_cell):
            big_cell_list = []
            for cell in allcells:
                if cell.radius > self_cell.radius and cell.dead == False:
                    big_cell_list.append(cell)
            return big_cell_list

        def run(self_cell, other):
            '''直接朝目标喷射'''
            d = chuan(self_cell, other)
            alpha = theta(d, [0, 1])
            if d[0] > 0:
                return alpha
            else:
                return -alpha

        def find_small_cell(self_cell):
            small_cell_list = []
            for cell in allcells:
                if cell.radius < self_cell.radius and cell.dead == False:
                    small_cell_list.append(cell)
            return small_cell_list

        def loss_times(self_cell, other):
            '''自己吃目标需要喷射次数的估计值'''
            collision = collision_time(self_cell, other)
            if collision != None and collision < 1000:  # 1000可调
                '''如果现在这样就能碰撞且时间不太长，就不需要喷射'''
                return 0
            else:
                d = chuan(other, self_cell)
                v0 = [self_cell.veloc[0] - other.veloc[0], self_cell.veloc[1] - other.veloc[1]]
                # 现有相对位移，速度
                vt = [-0.3 * d[0] / mod(d), -0.3 * d[1] / mod(d)]
                # 希望获得的速度
                deltav = [vt[0] - v0[0], vt[1] - v0[1]]
                # 需要的速度改变量
                return floor(mod(deltav) / dv2)  # 向下取整

        def benefit(self_cell, other):
            '''预测吃到球后质量变化倍数，这样不用开平方'''
            los = loss_times(self_cell, other)
            rate = 0.99 ** los + (other.radius / self_cell.radius) ** 2
            return rate

        def grab(self_cell, other):
            '''吃球，具体策略是改变速度使自己相对目标的速度和距离矢量同向'''
            d = chuan(other, self_cell)
            v0 = [self_cell.veloc[0] - other.veloc[0], self_cell.veloc[1] - other.veloc[1]]
            vt = [-0.3 * d[0] / mod(d), -0.3 * d[1] / mod(d)]
            deltav = [vt[0] - v0[0], vt[1] - v0[1]]
            beta = theta([-deltav[0], -deltav[1]], [0, 1])
            if deltav[0] > 0:
                return -beta
            else:
                return beta

        def time(self_cell, other):
            d = self_cell.distance_from(other) - self_cell.radius - other.radius
            t1 = loss_times(self_cell, other)
            t2 = d / (max(mod([self_cell.veloc[0] - other.veloc[0], self_cell.veloc[1] - other.veloc[1]]), 0.3))
            return t1 + t2

        def find_nearby_cell(self_cell):
            nearby_cell_list = []
            for cell in allcells:
                if self_cell.distance_from(
                        cell) - self_cell.radius - cell.radius < 100 and cell.dead == False and cell.id != self.id:
                    nearby_cell_list.append(cell)
            return nearby_cell_list

        big_cell_list = find_big_cell(self_cell)
        big_number = len(big_cell_list)
        if big_number != 0:
            leasttime = 99999
            leastdistance = 99999
            timeleast_cell = big_cell_list[0]
            distanceleast_cell = big_cell_list[0]
            '''找到自己被吃距离最短和用时最短的球及其距离或者时间'''
            for cell in big_cell_list:
                temptime = collision_time(self_cell, cell)
                if temptime != None:
                    if temptime < leasttime:
                        leasttime = temptime
                        timeleast_cell = cell
                tempdistance = min_distance(self_cell, cell)
                if tempdistance != None:
                    if tempdistance < leastdistance:
                        leastdistance = tempdistance
                        distanceleast_cell = cell
            if leastdistance / sqrt(self_cell.radius) < 5 or self_cell.distance_from(
                    distanceleast_cell) - self_cell.radius - distanceleast_cell.radius < 1:
                '''估值条件，有很大修改空间'''
                return run(self_cell, distanceleast_cell)
            if leasttime < 60:
                '''估值条件，可修改'''
                return run(self_cell, timeleast_cell)

        if big_number < 100:  # 100可修改
            '''大球不太多时'''
            small_cell_list = find_small_cell(self_cell)
            alternative_cell_list = []
            for cell in small_cell_list:
                if self_cell.distance_from(cell) < 270:
                    # 目标球不要太远，270可修改
                    los = loss_times(self_cell, cell)
                    if self_cell.radius ** 2 * (1 - rat) ** los > cell.radius ** 2:
                        '''喷射后自己仍大于对方'''
                        shouyi = (benefit(self_cell, cell) - 1) * self_cell.radius ** 2 / time(self_cell, cell)**2
                        alternative_cell_list.append([cell, shouyi])

            # 计算路径上是否可能碰到大球
            for smallcell in alternative_cell_list:
                judge = loss_times(self_cell, smallcell[0])  # 计算要喷射加速的次数
                if judge > 0:  # 速度转换过于复杂，直接按照每喷一次相对速度增加dv2计算方向为目标速度方向，第一次不算
                    # 假设一个球用来模拟，位置与自己相同，速度方向与目标相同，速度大小与自己相同，计算其加速后的状况
                    speed_ratio = mod(self_cell.veloc) / mod(smallcell[0].veloc)
                    # 防止出现0作为分母
                    if self_cell.veloc[0] == 0:
                        tempcos = 0
                    else:
                        tempcos = self_cell.veloc[0] / mod(self_cell.veloc)
                    if self_cell.veloc[1] == 0:
                        tempsin = 0
                    else:
                        tempsin = self_cell.veloc[1] / mod(self_cell.veloc)
                    veloc = []
                    veloc.append(self_cell.veloc[0] * speed_ratio + dv2 * tempcos * (judge - 1))
                    veloc.append(self_cell.veloc[1] * speed_ratio + dv2 * tempsin * (judge - 1))
                    tempcell = Cell(None, self_cell.pos, veloc, self_cell.radius * 0.99 ** (judge - 1))
                    eattime = collision_time(tempcell, smallcell[0])  # 以现在的速度吃到小球的时间
                    for bigcell in big_cell_list:
                        eatentime = collision_time(tempcell, bigcell)  # 被大球吃的时间
                        if eatentime != None and eattime != None:
                            if eattime > eatentime:  # 吃小球所需要的时间大于被大球吃的时间，不吃这个球
                                alternative_cell_list.remove(smallcell)
                                break

            if len(alternative_cell_list) == 0:
                '''没有目标就不动'''
                return None
            else:
                most_beneficial_cell = alternative_cell_list[0][0]
                max_benefit = 0
                for i in alternative_cell_list:
                    temp_benefit = i[1]
                    if temp_benefit > max_benefit:
                        max_benefit = temp_benefit
                        most_beneficial_cell = i[0]
                if max_benefit > 1e-4:
                    #print(max_benefit)
                    # 收益较大时吃对方，1.1可修改
                    target = most_beneficial_cell
                    #print(target.id)
                    v = [self_cell.veloc[0] - target.veloc[0], self_cell.veloc[1] - target.veloc[1]]
                    los = loss_times(self_cell, target)
                    if los > 0 or mod(v) < 0.3:
                        '''如果还需要改变方向或相对速度过小，则使用grab，否则不动，0.3可修改'''
                        return grab(self_cell, target)
