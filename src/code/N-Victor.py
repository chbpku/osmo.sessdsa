import math
from consts import Consts


class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.cell = None
        self.theta = None
        self.number = 0
        self.aim = None
        self.price = 0
        self.cost = 0
        self.aim_live = 0
        self.time = 1.5
        self.finish = 1
        self.cells = []
        self.time_left = 0
        # 防止突然变大的球把我们吞了
        self.close_cell = None

    def forecast(self, other):
        new_v_x = other.veloc[0] - self.aim.veloc[0]
        new_v_y = other.veloc[1] - self.aim.veloc[1]
        new_v = (new_v_x ** 2 + new_v_y ** 2) ** 0.5

        dx = other.pos[0] - self.aim.pos[0]
        dy = other.pos[1] - self.aim.pos[1]
        x_all = [dx, dx + Consts["WORLD_X"], dx - Consts["WORLD_X"]]
        y_all = [dy, dy + Consts["WORLD_Y"], dy - Consts["WORLD_Y"]]
        x_all.sort(key=lambda ele: abs(ele), reverse=True)
        y_all.sort(key=lambda ele: abs(ele), reverse=True)
        vector_x = x_all.pop()
        vector_y = y_all.pop()
        vector = [vector_x, vector_y]
        # 顺时针转90°
        v_vector = [vector_y, -vector_x]

        # 用以判断夹角
        product = new_v_x * vector_x + new_v_y * vector_y
        v_product = new_v_x * v_vector[0] + new_v_y * v_vector[1]

        distance = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
        sum_r = self.aim.radius + other.radius

        # 速度与vector的夹角，记转过theta_1，介于0到pi，符号代表顺逆时针
        if new_v != 0:
            if abs(product) < distance * new_v:
                theta_1 = math.acos(product / (distance * new_v))
            else:
                if product > 0:
                    theta_1 = 0
                else:
                    theta_1 = math.pi
        else:
            theta_1 = math.pi
        # 修改theta_1符号
        if v_product < 0:
            theta_1 *= -1
        # 球心最短距离，正负代表other在左还是右
        v_distance = distance * math.sin(theta_1)

        # 准备按照是否相遇分两种情况
        if abs(v_distance) < sum_r and new_v != 0:
            # 计算最短接触距离与时间
            h_distance = -distance * math.cos(theta_1) - (sum_r ** 2 - v_distance ** 2) ** 0.5
            time = h_distance / (new_v * Consts["FPS"] * Consts["FRAME_DELTA"])
            if self.aim.area() + other.area() < self.cell.area():
                live = 1
            else:
                if time > self.time_left + 1 or time < 0:
                    live = 1
                else:
                    live = 0
        else:
            live = 1
        return live

    # 对每个球计算策略的子函数
    def substrategy(self, other, k=4):
        aim = other
        new_v_x = other.veloc[0] - self.cell.veloc[0]
        new_v_y = other.veloc[1] - self.cell.veloc[1]
        new_v = (new_v_x ** 2 + new_v_y ** 2) ** 0.5

        dx = other.pos[0] - self.cell.pos[0]
        dy = other.pos[1] - self.cell.pos[1]
        x_all = [dx, dx + Consts["WORLD_X"], dx - Consts["WORLD_X"]]
        y_all = [dy, dy + Consts["WORLD_Y"], dy - Consts["WORLD_Y"]]
        x_all.sort(key=lambda ele: abs(ele), reverse=True)
        y_all.sort(key=lambda ele: abs(ele), reverse=True)
        vector_x = x_all.pop()
        vector_y = y_all.pop()
        vector = [vector_x, vector_y]
        # 顺时针转90°
        v_vector = [vector_y, -vector_x]

        # 用以判断夹角
        product = new_v_x * vector_x + new_v_y * vector_y
        v_product = new_v_x * v_vector[0] + new_v_y * v_vector[1]

        distance = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
        sum_r = self.cell.radius + other.radius

        # 先做旋转，将位置向量变为y轴，记转过theta_0，介于0到pi，符号代表顺逆时针
        if vector_x < 0:
            # 此时左旋theta_0
            theta_0 = -math.acos(vector_y / distance)
        else:
            theta_0 = math.acos(vector_y / distance)

        # 速度与vector的夹角，记转过theta_1，介于0到pi，符号代表顺逆时针
        if new_v != 0:
            if abs(product) < distance * new_v:
                theta_1 = math.acos(product / (distance * new_v))
            else:
                if product > 0:
                    theta_1 = 0
                else:
                    theta_1 = math.pi
        else:
            theta_1 = math.pi
        # 修改theta_1符号
        if v_product < 0:
            theta_1 *= -1
        # 球心最短距离，正负代表other在左还是右
        v_distance = distance * math.sin(theta_1)

        # 准备按照半径与是否相遇分四种情况
        theta = None
        number = 0
        time = -1
        h_distance = distance - sum_r
        # 半径大于我们
        if self.cell.radius <= other.radius:
            if abs(v_distance) < sum_r and new_v != 0:
                # 计算最短接触距离与时间
                h_distance = -distance * math.cos(theta_1) - (sum_r ** 2 - v_distance ** 2) ** 0.5
                time = h_distance / (new_v * Consts["FPS"] * Consts["FRAME_DELTA"])
                if time > 2 or time < 0:
                    type = 0
                # 此时全力避开
                else:
                    type = 1
                    if sum_r < distance:
                        theta_2 = math.acos(sum_r / distance)
                    else:
                        theta_2 = 0
                    theta = math.copysign(1, theta_1) * theta_2 + theta_0
                    v_delta = (sum_r - abs(v_distance)) / (time * Consts["FPS"] * Consts["FRAME_DELTA"])
                    number = math.ceil(1.3 * v_delta / (Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"]))
            else:
                type = 0
        # 半径小于我们
        else:
            type = 2
            if new_v != 0:
                # 两球接触时他们速度的夹角
                theta_2 = theta_1 / k
                theta = math.pi + theta_0 + theta_2
                if theta_2 != 0:
                    v_delta = math.sin(abs(theta_1)) * new_v / math.sin(abs(theta_2))
                    h_distance = h_distance / math.sin(abs(theta_1) - abs(theta_2)) * math.sin(abs(theta_1))
                else:
                    v_delta = k * new_v
                number = math.ceil(
                    v_delta / (Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"]))
                if other.area()>=self.cell.area()*(1-Consts["EJECT_MASS_RATIO"])**number:
                    number=math.ceil(math.log(other.area())/math.log(self.cell.area()*(1-Consts["EJECT_MASS_RATIO"])))-1
                time = h_distance / (
                        Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"] * Consts["FRAME_DELTA"] * Consts[
                    "FPS"] * v_delta)
            # 计算追击策略
            else:
                h_distance = distance - sum_r
                number = 2 * k
                theta = math.pi + theta_0
                time = h_distance / (
                        Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"] * Consts["FRAME_DELTA"] * Consts[
                    "FPS"] * number)
        return type, theta, time, aim, number, h_distance

    # 用以计算最优策略
    def filter(self, substrategy):
        if self.cell.radius<1.2*Consts["DEFAULT_RADIUS"]:
            return substrategy[2] / (substrategy[1]*substrategy[5])
        else:
            return substrategy[2] / substrategy[1]

    def strategy(self, allcells):
        self.cell = allcells[self.id]
        self.aim_live = 0
        strategy = [[], [], []]
        if self.aim != None:
            for cell in allcells:
                if cell.id != self.id and self.aim != None and cell.id == self.aim.id and cell.radius < self.cell.radius:
                    self.aim = cell
                    self.aim_live = 1
            if self.aim_live == 1:
                for cell in allcells:
                    if cell.id != self.aim.id and cell.id != self.id:
                        self.aim_live = self.forecast(cell)
            if self.aim_live == 0:
                self.cost = 0
        for cell in allcells:
            if cell.id != self.id:
                if self.close_cell == None or self.close_cell.distance_from(self.cell) > cell.distance_from(self.cell):
                    self.close_cell = cell
                type, theta, time, aim, number, h_distance = self.substrategy(cell)
                price = cell.area() - (1 - (1 - Consts["EJECT_MASS_RATIO"]) ** (number + self.cost)) * self.cell.area()
                if self.aim != None and cell.id == self.aim.id:
                    price *= self.cell.area()*40
                # 吃人函数
                if cell.id == 1 - self.id and type == 2 and self.cell.distance_from(
                        cell) < 20 + self.cell.radius + cell.radius:
                    type, theta, time, aim, number, h_distance = self.substrategy(cell,10)
                    price = cell.area() - (
                                1 - (1 - Consts["EJECT_MASS_RATIO"]) ** (number + self.cost)) * self.cell.area()
                    price *= self.cell.area() * 9999999
                strategy[type].append([theta, time, price, aim, number, h_distance])

        # 判断是否逃跑
        # 先防止最近的球忽然把我们吞掉
        aim_now = self.aim
        self.aim = self.close_cell
        time_left_now = self.time_left
        self.time_left = 1
        for c in allcells[2:]:
            if self.forecast(c) == 0:
                aim = self.close_cell
                new_v_x = (self.aim.veloc[0] * self.aim.area() + c.veloc[0] * c.area()) / (
                            self.aim.area() + c.area()) - self.cell.veloc[0]
                new_v_y = (self.aim.veloc[1] * self.aim.area() + c.veloc[1] * c.area()) / (
                            self.aim.area() + c.area()) - self.cell.veloc[1]
                new_v = (new_v_x ** 2 + new_v_y ** 2) ** 0.5

                dx = self.aim.pos[0] - self.cell.pos[0]
                dy = self.aim.pos[1] - self.cell.pos[1]
                x_all = [dx, dx + Consts["WORLD_X"], dx - Consts["WORLD_X"]]
                y_all = [dy, dy + Consts["WORLD_Y"], dy - Consts["WORLD_Y"]]
                x_all.sort(key=lambda ele: abs(ele), reverse=True)
                y_all.sort(key=lambda ele: abs(ele), reverse=True)
                vector_x = x_all.pop()
                vector_y = y_all.pop()
                vector = [vector_x, vector_y]
                # 顺时针转90°
                v_vector = [vector_y, -vector_x]

                # 用以判断夹角
                product = new_v_x * vector_x + new_v_y * vector_y
                v_product = new_v_x * v_vector[0] + new_v_y * v_vector[1]

                distance = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
                sum_r = self.cell.radius + ((c.area() + self.aim.area()) / math.pi) ** 0.5

                # 先做旋转，将位置向量变为y轴，记转过theta_0，介于0到pi，符号代表顺逆时针
                if vector_x < 0:
                    # 此时左旋theta_0
                    theta_0 = -math.acos(vector_y / distance)
                else:
                    theta_0 = math.acos(vector_y / distance)

                # 速度与vector的夹角，记转过theta_1，介于0到pi，符号代表顺逆时针
                if new_v != 0:
                    if abs(product) < distance * new_v:
                        theta_1 = math.acos(product / (distance * new_v))
                    else:
                        if product > 0:
                            theta_1 = 0
                        else:
                            theta_1 = math.pi
                else:
                    theta_1 = math.pi
                # 修改theta_1符号
                if v_product < 0:
                    theta_1 *= -1
                # 球心最短距离，正负代表other在左还是右
                v_distance = distance * math.sin(theta_1)

                # 准备按照半径与是否相遇分四种情况
                theta = None
                number = 0
                time = -1
                h_distance = distance - sum_r
                # 半径大于我们
                if abs(v_distance) < sum_r and new_v != 0:
                    # 计算最短接触距离与时间
                    h_distance = -distance * math.cos(theta_1) - (sum_r ** 2 - v_distance ** 2) ** 0.5
                    time = h_distance / (new_v * Consts["FPS"] * Consts["FRAME_DELTA"])
                    if time > 2.5 or time < 0:
                        type = 0
                    # 此时全力避开
                    else:
                        type = 1
                        if sum_r < distance:
                            theta_2 = math.acos(sum_r / distance)
                        else:
                            theta_2 = 0
                        theta = math.copysign(1, theta_1) * theta_2 + theta_0
                        v_delta = (sum_r - abs(v_distance)) / (time * Consts["FPS"] * Consts["FRAME_DELTA"])
                        number = math.ceil(2 * v_delta / (Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"]))
                else:
                    type = 0
                strategy[type].append([theta, time, aim, number, h_distance])
        self.aim = aim_now
        self.time_left = time_left_now


        if strategy[1] != []:
            strategy[1].sort(key=lambda s: s[1])
            self.theta = strategy[1][0][0]
            self.number = strategy[1][0][4]
            self.time = 0
            print(self.theta, self.number)
            # 否则选择单位时间增加最快的策略
        elif self.finish == 1 and self.time > 0.1 and strategy[2] != []:
            strategy[2].sort(key=self.filter)
            if self.filter(strategy[2][-1]) > 0:
                self.theta = strategy[2][-1][0]
                self.number = strategy[2][-1][4]
                if self.aim != strategy[2][-1][3]:
                    self.cost = 0
                    self.time = 0
                self.aim = strategy[2][-1][3]
        else:
            self.number = 0

        if self.number > 1:
            self.number -= 1
            self.cost += 1
        else:
            self.theta = None
            self.finish = 1
        if self.aim != None:
            type, theta, time, aim, number, h_distance = self.substrategy(self.aim)
            self.time_left = time
        self.time += 1 / (Consts["FPS"])

        return self.theta