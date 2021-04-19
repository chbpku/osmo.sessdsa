from consts import Consts
import math
import numpy as np


class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.me = None  # 包含我方信息的cell
        self.enemy = None
        self.threats = None
        self.allcells = None
        self.target = None
        self.changetarget = True  # 判断是否更换目标

    def strategy(self, allcells):
        # 更新Player的自身属性
        self.allcells = allcells
        for each in allcells:
            if each.id == self.id:
                self.me = each
                break
        # 更新enemy
        for each in allcells:
            if each.id == 1 - self.id:
                self.enemy = each
                break
        # 更新威胁
        self.threats = self.findThreats()
        max_radius = self.calc_maxradius()
        if self.me.radius > max_radius:
            return None
        if len(self.threats) == 0:
            if self.target and self.target == self.enemy:
                pass
            else:
                self.target = self.selectTarget()
            if self.target:
                if self.target.radius > self.me.radius:
                    self.changetarget = True
                    #
                    # print('bigger')
                else:
                    return self.grow(self.target)
            else:
                self.changetarget = True

                # print('ate')
        else:
            # ('safe')
            theta = self.safe()
            return theta

    # 在allcells里找出最优的目
    def selectTarget(self):
        target = None
        vx = self.me.veloc[0]
        vy = self.me.veloc[1]
        alist = []
        blist = []
        for each in self.allcells:  # 选出距离较近的
            num = self.calgrownum(each)
            lossr2 = self.me.radius ** 2 * (1 - ((1 - Consts["EJECT_MASS_RATIO"]) ** num))  # 代表损失的质量
            if lossr2 < 0.9 * each.radius ** 2 and each != self.me and self.me.radius ** 2 - lossr2 >= each.radius ** 2:  # 如果吃了它质量不减少，所有目标都要满足这个条件
                mes = self.distance(self.me, each)
                if self.me.radius < 20:
                    if num < 20 and mes[2] < 100:
                        blist.append(each)  # 自己半径较小时的目标
                else:
                    if num < 20:
                        alist.append(each)  # 自己半径较大时的目标

        if self.me.radius < 20 and blist:
            mindis = 100
            for each in blist:
                mes = self.distance(self.me, each)
                if mindis >= mes[2]:  # 找出最近的
                    mindis = mes[2]
                    target = each
            self.changetarget = False
            return target
        if alist:
            rdevidedrlen = alist[0].radius / self.distance(self.me, alist[0])[2]
        for each in alist:  # 找出半径除以距离最大的
            mid = each.radius / self.distance(self.me, each)[2]
            if mid >= rdevidedrlen and self.targetlife(each):
                rdevidedrlen = mid
                target = each
        if target:
            self.changetarget = False
            return target

    def targetlife(self, each):  # 判断目标是否快要死了
        for other in self.allcells:
            if each != other and each != self.me:
                mes = self.distance(each, other)
                vx = each.veloc[0] - other.veloc[0]
                vy = each.veloc[1] - other.veloc[1]
                angle = (mes[0] * vx + mes[1] * vy) / \
                        (math.sqrt((mes[0] ** 2 + mes[1] ** 2) * (vx ** 2 + vy ** 2)))
                newradius = math.sqrt(each.radius ** 2 + other.radius ** 2)
                if angle > 0.9 and mes[2] < 100 and newradius > self.me.radius:
                    return False
                else:
                    return True

    def grow(self, cell):
        # mes = [cell.pos[0]-self.me.pos[0],cell.pos[1]-self.me.pos[1],\
        #   math.sqrt((cell.pos[0]-self.me.pos[0])**2+(cell.pos[1]-self.me.pos[1])**2)]
        mes = self.distance(self.me, cell)
        # 目标的参数
        r = cell.radius
        vx = cell.veloc[0]
        vy = cell.veloc[1]
        # 自己的参数
        selfvx = self.me.veloc[0]
        selfvy = self.me.veloc[1]
        selfr = self.me.radius
        # 径矢的模长
        rlen = mes[2]
        vlen = math.sqrt(self.me.veloc[0] ** 2 + self.me.veloc[1] ** 2)
        ulen = math.sqrt((selfvx - vx) ** 2 + (selfvy - vy) ** 2)
        # 相对速度和径矢之间的夹角
        deltaangle = math.fabs(self.xangle(selfvx - vx, selfvy - vy) - self.xangle(mes[0], mes[1]))
        if deltaangle > math.pi:
            deltaangle = 2 * math.pi - deltaangle
        # 喷一次相对速度的角度改变量
        delta = math.atan2(Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"], ulen)
        # 阈值根据双方的半径设置
        if rlen > r + selfr:
            upperangle = math.asin((r + selfr) / rlen)
        else:
            upperangle = 4
        # print(str(deltaangle)+'   '+'angle '+str(delta)+'  '+str(cell.id)+" my radius: "+str(r))
        # 如果相对速度和径矢之间的夹角不够小，就对速度进行调整
        if deltaangle > upperangle:
            if 2 * upperangle < delta:
                # print('small')
                # u = math.fabs(math.sqrt((selfvx-vx)**2+(selfvy-vy)**2)*math.cos(deltaangle))
                # 相对追击速度大小为abu需要自行设定
                u = 1
                anvx = u * mes[0] / rlen - selfvx + vx
                anvy = u * mes[1] / rlen - selfvy + vy
                return self.xangle(-mes[0], -mes[1])
            elif vlen:
                if (selfvy - vy) * mes[0] + (-selfvx + vx) * mes[1] > 0:
                    return self.xangle(-(selfvy - vy), selfvx - vx)
                else:
                    return self.xangle((selfvy - vy), -selfvx + vx)
            elif not vlen:
                return self.xangle((selfvy - vy), -selfvx + vx)
        elif vlen < 0.7:
            return self.xangle(vx - selfvx, vy - selfvy)

    def findThreats(self):
        threats = []
        for each in self.allcells:
            mes = self.distance(self.me, each)
            # 目标的参数
            r = each.radius
            vx = each.veloc[0]
            vy = each.veloc[1]
            # 自己的参数
            selfvx = self.me.veloc[0]
            selfvy = self.me.veloc[1]
            selfr = self.me.radius
            # 径矢的模长
            rlen = mes[2]
            vlen = math.sqrt(self.me.veloc[0] ** 2 + self.me.veloc[1] ** 2)
            ulen = math.sqrt((selfvx - vx) ** 2 + (selfvy - vy) ** 2)
            # 相对速度和径矢之间的夹角
            deltaangle = math.fabs(self.xangle(selfvx - vx, selfvy - vy) - self.xangle(mes[0], mes[1]))
            if deltaangle > math.pi:
                deltaangle = 2 * math.pi - deltaangle
            # 喷一次相对速度的角度改变量
            delta = math.atan2(Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"], ulen)
            # 阈值根据双方的半径设置
            if rlen > r + selfr:
                upperangle = math.asin((r + selfr) / rlen)
            else:
                upperangle = 4
            if deltaangle <= upperangle:
                if self.distance(self.me, each)[2] - self.me.radius - each.radius < ulen * 30 and each.radius > self.me.radius:
                    threats.append(each)
        return threats

    # 返回两点最短连线与x轴的夹角, start/end为[x, y]列表
    def calc_angle(self, start, end):
        # end的另外四种可能位置
        end1 = [end[0], end[1] - Consts["WORLD_Y"]]
        end2 = [end[0], end[1] + Consts["WORLD_Y"]]
        end3 = [end[0] - Consts["WORLD_X"], end[1]]
        end4 = [end[0] + Consts["WORLD_X"], end[1]]
        end5 = [end[0] + Consts["WORLD_X"], end[1] - Consts["WORLD_Y"]]
        end6 = [end[0] - Consts["WORLD_X"], end[1] - Consts["WORLD_Y"]]
        end7 = [end[0] - Consts["WORLD_X"], end[1] + Consts["WORLD_Y"]]
        end8 = [end[0] + Consts["WORLD_X"], end[1] + Consts["WORLD_Y"]]
        distance = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        angle = math.atan2(end[0] - start[0], end[1] - start[1])
        for each in (end1, end2, end3, end4, end5, end6, end7, end8):
            if math.sqrt((each[0] - start[0]) ** 2 + (each[1] - start[1]) ** 2) < distance:
                distance = math.sqrt((each[0] - start[0]) ** 2 + (each[1] - start[1]) ** 2)
                angle = math.atan2(each[0] - start[0], each[1] - start[1])
        # 把angle转化到区间[0, 2pi)中
        if angle < 0:
            angle = 2 * math.pi + angle
        return angle

    def safe(self):
        thetalist = []
        weightlist = []
        for each in self.threats:
            direction = self.calc_angle(self.me.pos, each.pos)
            thetalist.append(direction)
            weightlist.append((3 * Consts["FPS"]) ** 2 / (self.calc_time(each)) ** 2)
        average_theta = self.average(thetalist, weightlist)
        return average_theta

    def calc_time(self, cell):
        r_vx = self.me.veloc[0] - cell.veloc[0]
        r_vy = self.me.veloc[1] - cell.veloc[1]
        r_v = math.sqrt(r_vx ** 2 + r_vy ** 2)
        distance = self.me.distance_from(cell)
        alpha = abs(self.calc_angle([0, 0], [r_vx, r_vy]) - self.calc_angle(self.me.pos, cell.pos))
        if alpha >= math.pi / 2:
            time = 10000000000
        else:
            md = distance * math.sin(alpha)
            if md - self.me.radius - cell.radius > 0:
                time = distance * math.cos(alpha) / r_v
            else:
                x = distance * math.cos(alpha) - \
                    math.sqrt((self.me.radius + cell.radius) ** 2 - (distance * math.sin(alpha)) ** 2)
                time = x / r_v
        return time

    def average(self, thetaList, weightList):
        previous = thetaList[0]
        weight = weightList[0]
        for i in range(1, len(thetaList)):
            average = (previous * weight + thetaList[i] * weightList[i]) / (weight + weightList[i])
            another_average = average + math.pi
            if another_average >= 2 * math.pi:
                another_average -= 2 * math.pi
            if abs(average - thetaList[i]) <= 0.5 * math.pi:
                previous = average
            else:
                previous = another_average
            weight += weightList[i]
        return previous

    # 输入一个矢量，求出该矢量和y轴正向的夹角，0到2π
    def xangle(self, x, y):
        if x == 0:
            if y > 0:
                return 0.0
            else:
                return math.pi
        elif x > 0:
            if y == 0:
                return 0.5 * math.pi
            elif y > 0:
                return math.atan2(x, y)
            else:
                return math.pi - math.atan2(x, -y)
        else:
            if y == 0:
                return 1.5 * math.pi
            elif y > 0:
                return math.atan2(y, -x) + 1.5 * math.pi
            else:
                return math.pi + math.atan2(-x, -y)

    # 返回最小距离,以及由我指向对方的位置矢量(包括跨屏)[x, y, distance]
    def distance(self, cell1, cell2):  # 输入顺序有要求,cell1应为自己的坐标
        lenth = 1000
        width = 500
        dx = cell2.pos[0] - cell1.pos[0]
        dy = cell2.pos[1] - cell1.pos[1]
        min_x = min(abs(dx), abs(dx + lenth), abs(dx - lenth))
        min_y = min(abs(dy), abs(dy + width), abs(dy - width))
        if min_x == abs(dx):
            x = dx
        elif min_x == abs(dx + lenth):  # 此时我方在屏幕右端,对方在左端
            x = dx + lenth
        else:  # 此时我方在屏幕左端,对方在右端
            x = dx - lenth
        if min_y == abs(dy):
            y = dy
        elif min_y == abs(dy + width):  # 此时我方在x轴附近,对方在上端
            y = dy + width
        else:
            y = dy - width  # 此时对方在x轴附近我方在上端
        distance = math.sqrt(min_x ** 2 + min_y ** 2)
        Distance = [x, y, distance]  # 返回最小距离,以及由我指向对方的位置矢量(包括跨屏)
        return Distance

    def calgrownum(self, cell):  # 计算总追击过程需要喷射的次数
        mes = self.distance(self.me, cell)
        # 目标的参数
        r = cell.radius
        vx = cell.veloc[0]
        vy = cell.veloc[1]
        # 自己的参数
        selfvx = self.me.veloc[0]
        selfvy = self.me.veloc[1]
        selfr = self.me.radius
        # 径矢的模长
        rlen = mes[2]
        ulen = math.sqrt((selfvx - vx) ** 2 + (selfvy - vy) ** 2)
        # 相对速度和径矢之间的夹角
        deltaangle = math.fabs(self.xangle(selfvx - vx, selfvy - vy) - self.xangle(mes[0], mes[1]))
        if deltaangle > math.pi:
            deltaangle = 2 * math.pi - deltaangle
        # 喷一次相对速度的角度改变量
        delta = math.atan2(Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"], ulen)
        # 阈值根据双方的半径设置
        if rlen > r + selfr:
            upperangle = math.asin((r + selfr) / rlen)
        else:
            upperangle = 4
        # 加速阶段喷射的次数
        speednum = 0
        if ulen < 1:
            speednum += (1 - ulen) // (Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"])
        if deltaangle > upperangle:
            return ((deltaangle - upperangle) // delta) + speednum
        else:
            return 0 + speednum

    def calc_maxradius(self):
        sum_mass = 0
        for each in self.allcells:
            sum_mass += each.radius**2
        return math.sqrt(sum_mass/2)


