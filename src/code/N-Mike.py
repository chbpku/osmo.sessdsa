from consts import Consts
import math
import copy
from cell import Cell


class Player():
    def __init__(self, id, arg=None):
        self.id = id

    def getAngle(self, mycell, other):  # 相对位置的角度
        dx = other.pos[0] - mycell.pos[0]
        dy = other.pos[1] - mycell.pos[1]  # 算出相对位置
        min_x = min([dx, dx + Consts["WORLD_X"], dx -
                     Consts["WORLD_X"]], key=lambda x: abs(x))
        min_y = min([dy, dy + Consts["WORLD_Y"], dy -
                     Consts["WORLD_Y"]], key=lambda y: abs(y))  # 考虑边界相邻的相对位置
        return math.atan2(min_x, min_y)

    def getVelAngle(self, mycell, other):  # 相对速度的角度
        dVx = -mycell.veloc[0] + other.veloc[0]
        dVy = -mycell.veloc[1] + other.veloc[1]  # 算出相对速度
        return math.atan2(dVx, dVy)

    def ejectAngle(self, mycell, other):
        theta = self.getAngle(mycell, other)  # 得到目标的方向
        alpha = self.getVelAngle(mycell, other)
        dVx = -math.sin(alpha)
        dVy = -math.cos(alpha)
        # 此处就是力学计算....
        if math.sin(alpha - theta) * (dVx**2 + dVy**2)**0.5 >= 5:
            phi = math.asin((math.sin(alpha - theta) * (dVx**2 + dVy**2)**0.5) / 5)
        else:
            phi = math.pi/2
        return (theta + math.pi/2 - phi)%(2*math.pi)


    def eat(self, mycell, smaller):
        cell = sorted(smaller, key=lambda cell: cell.distance_from(mycell))[-1]
        angle = self.ejectAngle(mycell, cell)
        return angle

    def hide(self,mycell,bigger):
        cell = sorted(bigger, key=lambda cell: cell.distance_from(mycell))[-1]
        angle=self.ejectAngle(mycell,cell)
        return angle

    def v_tward(self, mycell, cell):  # cell速度在自己连线上的分量，朝自己为+
        theta = self.getAngle(mycell, cell)
        fx = math.sin(theta)
        fy = math.cos(theta)
        return -((cell.veloc[0] - mycell.veloc[0]) * fx + (cell.veloc[1] - mycell.veloc[1]) * fy)

    def leasttime(self, mycell, bigger):  # 计算最短被吃掉的时间
        t_fun = 0
        for cell in bigger:
            d = mycell.distance_from(cell) - mycell.radius - cell.radius
            v = self.v_tward(mycell, cell)
            postheta = self.getAngle(mycell, cell)
            valtheta = self.getVelAngle(mycell, cell)
            try:
                alpha = abs(
                    math.asin((mycell.radius + cell.radius) / mycell.distance_from(cell)))
            except:
                return 1
            if alpha <= abs(postheta - valtheta) and v > 0:
                t_fun += v / d
        return t_fun

    def escape2(self, mycell, bigger):
        t = self.leasttime(mycell, bigger)
        predictFrame = 5
        n = 180
        beta = (2 * math.pi) / n
        escapeAngel = 0
        for i in range(n):
            fx = math.sin(beta * (i + 0.5))
            fy = math.cos(beta * (i + 0.5))
            new_cell = Cell(pos=[mycell.pos[0] + 5 * fx * predictFrame, mycell.pos[1] + 5 *
                                 fy * predictFrame], veloc=[mycell.veloc[0] + 5 * fx, mycell.veloc[1] + 5 * fy])
            new_cell.stay_in_bounds()
            for cell in bigger:
                cell.move(t)
            t_new = self.leasttime(new_cell, bigger)
            for cell in bigger:
                cell.move(-t)
            if t_new < t:
                escapeAngel = (-beta * (i + 0.5)) % (2 * math.pi)
                t = t_new
        return escapeAngel

    def escape(self, mycell, bigger):  # 逃跑的角度
        danger = []
        for cell in bigger:  # 遍历比自己大的小球信息
            d = mycell.distance_from(cell)  # 取得它们与自己的距离
            n_d = d - mycell.radius - cell.radius  # 得到两球边界的最小相对距离
            alpha = math.asin((mycell.radius + cell.radius) / d)  # 取得危险角度
            if abs(self.getVelAngle(mycell, cell) - self.getAngle(mycell, cell)) < alpha:  # 在危险角度之内的小球放入危险列表内
                danger.append((cell, n_d, alpha))

        blockade = []
        danger = sorted(danger, key=lambda tp: tp[1])
        if danger == []:
            return None
        elif danger[0][1] < 300:
            avoidcell = danger[0][0]
            theta = self.getAngle(mycell, avoidcell)  # 取得它们与自己相对位置的夹角
            phi = self.getVelAngle(mycell, avoidcell)  # 取得它们与自己相对速度的夹角
            if math.tan(phi / 2) >= math.tan(theta / 2):
                avoid = phi - math.pi / 2
            elif math.tan(phi / 2) < math.tan(theta / 2):
                avoid = phi + math.pi / 2
            return avoid
        elif danger[0][1] <= 100:
            for i in range(len(danger)):
                if danger[i][1] <= 100:
                    theta = self.getAngle(mycell, danger[i][0])
                    blockade.append(
                        [theta - danger[i][2], theta + danger[i][2]])

    def foursearch(self, mycell, cellset, t):
        zone_up = []
        zone_down = []
        zone_left = []
        zone_right = []
        alpha = math.atan(0.5)
        for cell in cellset:
            if cell.dead == False:
                cell.move(t)
                beta = self.getAngle(mycell, cell)
                if 0.5 * math.pi - alpha < beta <= math.pi - alpha:
                    zone_up.append(cell)
                if math.pi - 2 * alpha < beta <= math.pi + alpha:
                    zone_left.append(cell)
                if 1.5 * math.pi - alpha < beta <= 2 * math.pi - alpha:
                    zone_down.append(cell)
                else:
                    zone_right.append(cell)
        choice = min(len(zone_up), len(zone_down),
                     len(zone_left), len(zone_right))
        # if choice == len(zone_up):
        # return zone_up, "up"

        if choice == len(zone_down):
            return zone_down, 2  # 数字代表 i*math.pi/2 方向
        elif choice == len(zone_up):
            return zone_up, 0
        elif choice == len(zone_left):
            return zone_left, 1
        else:
            return zone_right, 3

    def globalsearch(self, mycell, bigger):
        cellset, direction1 = self.foursearch(mycell, bigger, 1)
        if direction1 == 0:
            cellset2, direction2 = self.foursearch(
                Cell(pos=[mycell.pos[0], (mycell.pos[1] - 500 / 3) % 500]), cellset, 0)
        elif direction1 == 2:
            cellset2, direction2 = self.foursearch(
                Cell(pos=[mycell.pos[0], (mycell.pos[1] + 500 / 3) % 500]), cellset, 0)
        elif direction1 == 1:
            cellset2, direction2 = self.foursearch(
                Cell(pos=[(mycell.pos[0] - 1000 / 3) % 1000, mycell.pos[1]]), cellset, 0)
        else:
            cellset2, direction2 = self, foursearch(
                Cell(pos=[(mycell.pos[0] + 1000 / 3) % 1000, mycell.pos[1]]), cellset, 0)

        return (direction1, direction2)

    def areatree(self, allcells):
        n = 180
        theta = 2 * math.pi / n  # theta为搜索步长，初定为45°   (调参）
        # n = int(360 / theta)  # n为搜索角度的数目
        areatree = []
        mycell = allcells[self.id]
        for i in range(n):
            areatree.append([])
        t = 3  # 如何实现t
        for cell in allcells:
            if not cell.dead:
                # 500暂定为搜索距离,如果要遍历所有小球可以去掉    （调参）
                if mycell.distance_from(cell) <= 3*mycell.radius:
                    # cell_copy = copy.copy(cell)  # 对cell进行浅拷贝，避免影响平台的运行
                    cell.move(t)  # 利用cell自身的函数，得到它在t秒后到达的位置
                    for j in range(n):
                        # 在搜索区域里则放入区域树里
                        if self.getAngle(mycell, cell) >= j * theta and self.getAngle(mycell, cell) < (j + 1) * theta:
                            areatree[j].append(cell)
                    cell.move(-t)
        return areatree, n

    def search(self, allcells):
        S = allcells[self.id].area()
        F = 0
        areatree, n = self.areatree(allcells)
        theta = 2 * math.pi / n
        for i in range(n):
            F_test = (i + 0.5) * theta
            temp = self.Score(allcells, areatree[i], F_test)
            if temp > 1 * S:
                F = F_test
                S = temp
        if S >= 1.2 * allcells[self.id].area():
            return (F + math.pi) % (2 * math.pi)


    def Score(self, allcells, areatree, F):  # 这个函数将给出若干帧后自己的得分
        predictFrame = 2
        mycell = allcells[self.id]
        S = mycell.area()
        r = mycell.radius
        # 自己朝F的方向飞一下
        mycell.pos[0] += 5 * math.sin(F) * predictFrame
        mycell.pos[1] += 5 * math.cos(F) * predictFrame
        mycell.radius = mycell.radius * \
            (1 - Consts["EJECT_MASS_RATIO"])**(predictFrame / 2)
        for cell in areatree:
            if cell.dead == False and cell != mycell:
                if mycell.distance_from(cell) <= mycell.radius + cell.radius:
                    if mycell.radius <= cell.radius:
                        S = -999
                    else:
                        S += cell.area()
        mycell.pos[0] -= 5 * math.sin(F) * predictFrame
        mycell.pos[1] -= 5 * math.cos(F) * predictFrame
        mycell.radius = mycell.radius / \
            ((1 - Consts["EJECT_MASS_RATIO"])**(predictFrame / 2))

        return S

    def strategy(self, allcells):   # 生成三个列表存储所有的球，比自己大、比自己小、差不多
        count = 0
        mycell = allcells[self.id]
        for cell in allcells:
            if cell.dead == False:
                cell.veloc[0] -= mycell.veloc[0]
                cell.veloc[1] -= mycell.veloc[1]
                count += 1

        bigger = []
        smaller = []
        chabuduo = []
        for cell in allcells:
            if (not cell.dead) and cell != mycell:
                if cell.radius > 0.97 * mycell.radius:
                    bigger.append(cell)
                elif 0.5 * mycell.radius <= cell.radius <= 0.8 * mycell.radius:
                    smaller.append(cell)
                else:
                    chabuduo.append(cell)

        Directiontp = self.globalsearch(allcells[self.id], bigger)

        while True:
            t_fun = self.leasttime(allcells[self.id], bigger)
            angle = self.escape2(allcells[self.id], bigger)
            print(t_fun, angle)
            if t_fun >= 0.01:
                return self.hide(mycell,bigger)
            else:
                F = self.search(allcells)
                if F == 0 or F==None:
                    return None
                else:
                    #return self.eat(mycell,smaller)
                    return F

