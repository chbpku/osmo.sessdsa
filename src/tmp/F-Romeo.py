# 日志：
# 5.21 代码第三代搭建完成
# 基础功能已齐全，加下来调一波参
# 第四代预计1、优化捕食函数 2、添加一些特殊情况的技能
# 本代码中时间均以帧为单位
import math
from copy import deepcopy
from consts import Consts


class Player:
    def __init__(self, id, arg=None):
        self.id = id
        self.n = 0
        self.chase = False  # 用以追击敌人或某个特定球的模式开关
        self.run = False  # 用以躲避敌人追击
        # 特殊的功能还没有实现
        self.already_win = False    # 必胜局面就坐等胜利，不要送了-_-||

    # ====================数学类函数===================
    def innner_product(self, a, b):
        """内积"""
        return a[0] * b[0] + a[1] * b[1]

    def cross_product(self, a, b):
        """叉积"""
        return a[0] * b[1] - b[0] * a[1]

    def regularization(self, rad):
        """角度正规化"""
        return math.fmod((rad + 3 * math.pi * 2) / math.pi * 180, 360)

    def distance(self, a, b):
        """a,b两点距离"""
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def stay_in_bounds(self, pos):
        """正规化坐标"""
        while pos[0] < 0:
            pos[0] += Consts["WORLD_X"]
        while pos[0] > Consts["WORLD_X"]:
            pos[0] -= Consts["WORLD_X"]

        while pos[1] < 0:
            pos[1] += Consts["WORLD_Y"]
        while pos[1] > Consts["WORLD_Y"]:
            pos[1] -= Consts["WORLD_Y"]
        return pos

    def cross_border_dist(self, my_pos, e_pos):
        """跨越屏幕的最小距离"""
        x_norm = abs(my_pos[0]-e_pos[0])    # 正常x方向距离
        x_cross = abs(Consts["WORLD_X"]-x_norm)     # 跨越屏幕的x方向距离
        x = min(x_norm, x_cross)        # 最短的距离
        y_norm = abs(my_pos[1]-e_pos[1])    # 正常y方向距离
        y_cross = abs(Consts["WORLD_Y"]-y_norm)     # 跨越屏幕的y方向距离
        y = min(y_norm, y_cross)    # 最短的y方向距离
        return (x**2 + y**2)**0.5

    def cross_border_vector(self, my_pos, e_pos):
        """跨越屏幕的方向向量，指向敌人"""
        x_norm = abs(my_pos[0] - e_pos[0])  # 正常x方向距离
        x_cross = abs(Consts["WORLD_X"] - x_norm)  # 跨越屏幕的x方向距离
        if x_norm < x_cross:
            # 若不穿越屏幕
            rel_x = e_pos[0] - my_pos[0]    # 指向敌人的x相对位移
        else:   # 若穿越屏幕
            rel_x = x_cross * (my_pos[0] - e_pos[0]) / x_norm
        y_norm = abs(my_pos[1] - e_pos[1])  # 正常y方向距离
        y_cross = abs(Consts["WORLD_Y"] - y_norm)  # 跨越屏幕的y方向距离
        if y_norm < y_cross:
            # 若不穿越屏幕
            rel_y = e_pos[1] - my_pos[1]
        else:
            rel_y = y_cross * (my_pos[1] - e_pos[1]) / y_norm
        return [rel_x, rel_y]

    def mod(self, a):
        """向量的模"""
        return (a[0] ** 2 + a[1] ** 2) ** 0.5

    def accelerate(self, n):
        """以固定相对速度从静止开始加速的s（t）关系"""
        rate = Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"] * Consts["FRAME_DELTA"]
        return rate * n * (n + 1) / 2

    def solve_root(self, my_cell, e_cell):
        """求根函数,求出"""
        n = 1
        total_rad = my_cell.radius + e_cell.radius
        rel_veloc = [my_cell.veloc[0] - e_cell.veloc[0], my_cell.veloc[1] - e_cell.veloc[1]]
        e_pos = e_cell.pos
        my_pos = my_cell.pos
        function = self.cross_border_dist(e_pos, my_pos) - total_rad - self.accelerate(n)
        while function > 0:
            my_pos[0] += rel_veloc[0] * Consts["FRAME_DELTA"]
            my_pos[1] += rel_veloc[1] * Consts["FRAME_DELTA"]
            my_pos = self.stay_in_bounds(my_pos)
            n += 1
            function = self.cross_border_dist(e_pos, my_pos) - total_rad - self.accelerate(n)
        return n

    def eject_angle(self, n, my_cell, e_cell):
        """输入运行的帧数，己方和地方的当前位置，计算出最小喷射次数下对应的喷射角度"""
        my_veloc = [my_cell.veloc[0] - e_cell.veloc[0], my_cell.veloc[1] - e_cell.veloc[1]]  # 我的相对速度
        my_pos = [my_cell.pos[0] + my_veloc[0] * n * Consts["FRAME_DELTA"],
                  my_cell.pos[1] + my_veloc[1] * n * Consts["FRAME_DELTA"]]
        my_pos = self.stay_in_bounds(my_pos)
        # 我在移动n帧之后的位置
        rel_pos = self.cross_border_vector(e_cell.pos, my_pos)
        # 运行n帧之后敌人指向我的矢量
        return rel_pos

    def run_direction(self, n, my_cell, e_cell):
        """计算喷射次数最少的逃跑方向,n帧以后碰撞"""
        my_veloc = [my_cell.veloc[0] - e_cell.veloc[0], my_cell.veloc[1] - e_cell.veloc[1]]
        # 我的相对速度
        my_pos = [my_cell.pos[0] + my_veloc[0] * n * Consts["FRAME_DELTA"],
                  my_cell.pos[1] + my_veloc[1] * n * Consts["FRAME_DELTA"]]
        # 我在移动n帧以后的位置
        my_pos = self.stay_in_bounds(my_pos)
        rel_pos = self.cross_border_vector(my_pos, e_cell.pos)
        # 运行n帧之后指向敌人的矢量
        return rel_pos

    # ==============================================================

    # =====================核心函数（误）：预测引擎=========================
    def prophet(self):
        """后期要实现的功能，由于效率问题先鸽了"""
        pass

    # ================================================================
    # =====================各类操作函数========================
    def can_eat_k(self, my_cell, e_cell):
        """k帧后可以吃"""
        rel_pos = self.cross_border_vector(my_cell.pos, e_cell.pos)
        # 相对位置
        rel_veloc = [my_cell.veloc[0] - e_cell.veloc[0], my_cell.veloc[1] - e_cell.veloc[1]]
        # 相对速度
        try:  # 不用管异常处理，出现概率极低
            cos = self.innner_product(rel_pos, rel_veloc) / (self.mod(rel_veloc) * self.mod(rel_pos))
        except ZeroDivisionError:
            return False
        try:  # 我对敌人的张角的余弦值
            critical_cos = math.sqrt((self.cross_border_dist(my_cell.pos, e_cell.pos) ** 2 - (
                    e_cell.radius + my_cell.radius) ** 2)) / self.cross_border_dist(my_cell.pos, e_cell.pos)
        except ValueError:
            return False
        if cos > critical_cos:
            # 此时不动就可以吃到，返回吃到所需要的时间
            return math.ceil((self.cross_border_dist(my_cell.pos, e_cell.pos) * cos - (
                    (my_cell.radius + e_cell.radius) ** 2 - self.cross_border_dist(my_cell.pos, e_cell.pos) ** 2 * (
                    1 - cos ** 2)) ** 0.5) / (self.mod(rel_veloc)) * Consts["FRAME_DELTA"])
        else:
            return False

    def need_run_k(self, my_cell, e_cell, delta=12):
        """在K帧后可能被吃掉,delta表示与敌人的临界距离"""
        rel_pos = self.cross_border_vector(my_cell.pos, e_cell.pos)
        # 相对位置
        rel_veloc = [my_cell.veloc[0] - e_cell.veloc[0], my_cell.veloc[1] - e_cell.veloc[1]]
        # 相对速度
        try:  # 不用管异常处理，出现概率极低
            cos = self.innner_product(rel_pos, rel_veloc) / (self.mod(rel_veloc) * self.mod(rel_pos))
        except ZeroDivisionError:
            return False
        try:  # 我对敌人的张角的余弦值(将敌人的存在范围扩大）
            critical_cos = math.sqrt((self.cross_border_dist(my_cell.pos, e_cell.pos) ** 2 - (
                    e_cell.radius + my_cell.radius + delta) ** 2)) / self.cross_border_dist(my_cell.pos, e_cell.pos)
            if cos > critical_cos:
                return math.ceil((self.cross_border_dist(my_cell.pos, e_cell.pos) * cos - (
                        (my_cell.radius + e_cell.radius+delta) ** 2 - self.cross_border_dist(my_cell.pos, e_cell.pos) ** 2 * (
                        1 - cos ** 2)) ** 0.5) / (self.mod(rel_veloc) * Consts["FRAME_DELTA"]))
        except ValueError:
            try:  # 若根式中值小于0，说明进入临界区域内
                critical_cos = math.sqrt((self.cross_border_dist(my_cell.pos, e_cell.pos) ** 2 - (
                        e_cell.radius + my_cell.radius) ** 2)) / self.cross_border_dist(my_cell.pos, e_cell.pos)
                if cos > critical_cos:
                    # 此时不动的话就会被吃掉
                    return math.ceil((self.cross_border_dist(my_cell.pos, e_cell.pos) * cos - (
                            (my_cell.radius + e_cell.radius) ** 2 - self.cross_border_dist(my_cell.pos, e_cell.pos) ** 2 * (
                            1 - cos ** 2)) ** 0.5) / (self.mod(rel_veloc) * Consts["FRAME_DELTA"]))
            except ValueError:
                # 你已经死了,不要挣扎了o(╥﹏╥)o
                return False
        return False

    def future_of_target(self, my_cell, eaten_cell, allcells, my_time, d=50):
        """考虑目标球未来是否会被吃或者吃其它球,返回True说明要回避"""
        danger_list = []
        for cell in allcells:
            if cell == my_cell:
                continue
            if cell == eaten_cell:  # 跳过自己的球和目标球
                continue
            if self.cross_border_dist(eaten_cell.pos, cell.pos) - cell.radius - eaten_cell.radius > d:
                # 不考虑较远的球
                continue
            time = self.can_eat_k(eaten_cell, cell)
            if time:
                # 说明可以吃到
                if time <= my_time:
                    # 这个球会被先吃掉或者吃到其它球
                    if my_cell.radius ** 2 < eaten_cell.radius ** 2 + cell.radius ** 2:
                        # 我的大小比它们合并之后要小
                        return True
                else:
                    # 我会先吃到这个球
                    if my_cell.radius ** 2 + eaten_cell.radius ** 2 < cell.radius ** 2:
                        # 说明我就算吃了还是比它小
                        if my_time - time < 10:
                            # 如果我吃了这个球比它快10帧以下
                            return True
            return False

    def canKill(self, my_cell, e_cell):
        """判断是否可以直接追杀敌人的球"""
        pass

    def canEat(self, my_pos, my_radius, e_pos, e_radius, cells_count, alpha=0.1, beta=0.5, gamma=50):
        """是否能吃"""
        dist = ((my_pos[0] - e_pos[0]) ** 2 + (my_pos[1] - e_pos[1]) ** 2) ** 0.5
        if my_radius - e_radius > alpha * (dist - my_radius - e_radius) + beta and dist - (
                my_radius + e_radius) < gamma:
            return True
        else:
            return False

    def value_function(self, my_pos, e_pos, my_radius, e_radius, num, alpha=20000, beta=50000, gamma=3000):
        """评估函数,目前考虑了敌方大小，敌方半径，追击的喷射数，追击的时间消耗"""
        if e_radius < 3 * (Consts['EJECT_MASS_RATIO']) ** 0.5 * my_radius:
            return 100
        dist = self.cross_border_dist(my_pos, e_pos) - (my_radius + e_radius)
        # 除去半径的距离
        dist_vector = self.cross_border_vector(my_pos, e_pos)
        return alpha * e_radius + beta / dist - num * gamma

    def eject_correction(self, target_pos, my_veloc, delta=0.05):
        """喷射换系矫正，根据动量守恒算的，大概没错吧。。。。。暂时没有用到，后期也许有用？"""
        mod = (target_pos[0] ** 2 + target_pos[1] ** 2) ** 0.5  # 矢量的模
        b = 2 * (target_pos[0] * my_veloc[0] + target_pos[1] * my_veloc[1]) / mod
        c = my_veloc[0] ** 2 + my_veloc[1] ** 2 - (1 - Consts['EJECT_MASS_RATIO']) ** 2 * Consts["DELTA_VELOC"] ** 2
        try:
            k = (-b + math.sqrt(b ** 2 - 4 * c)) / 2
        except ValueError:
            # 根号小于零
            return math.atan2(target_pos[1], -target_pos[0])
        else:
            # if self.cross_product(target_pos, my_veloc) > 0:
            #   return math.atan2(-k * target_pos[0] / mod - my_veloc[0], -k * target_pos[1] / mod - my_veloc[1]) - delta
            # else:
            return math.atan2(-k * target_pos[0] / mod - my_veloc[0], -k * target_pos[1] / mod - my_veloc[1]) + delta

    def strategy(self, allcells):
        """决策的主函数"""
        # =========================初始判断======================
        if self.already_win:
            # 在某些特殊条件下已经获胜
            return None
        # =========================计数===========================
        self.n += 1
        if self.n <= 0:
            return None
        # ========================一些参数的初始化============================
        my_cell = allcells[self.id]  # 我的球
        rival_cell = allcells[1 - self.id]  # 敌人的球
        critical_dist = 80  # 临界距离的判定
        eat_list = []  # 可以吃的列表
        run_list = []  # 需要逃跑的列表
        # ==========================特殊情况的决策==============================
        if 2 * my_cell.radius ** 2 > 0.95 * sum(x.radius**2 for x in allcells):
            self.already_win = True
            return None
        # =========================主循环=============================
        for cell in allcells:
            if cell == allcells[self.id]:
                # 跳过自己
                continue
            # =====================捕食判定=======================
            elif self.cross_border_dist(my_cell.pos, cell.pos) - my_cell.radius - cell.radius < critical_dist:
                # 只判断足够近的球
                if cell.radius < my_cell.radius:
                    # 敌人可能可以吃
                    temp = self.can_eat_k(my_cell, cell)
                    if temp:  # 如果不动就可以吃到
                        eat_list.append((cell, temp, 0))
                    else:
                        num = self.solve_root(deepcopy(my_cell), deepcopy(cell))  # 吃掉敌人至少要喷的球数
                        if my_cell.radius * (1 - Consts['EJECT_MASS_RATIO']) ** (0.5 * num) > cell.radius:
                            # 判断你追上敌人后半径是否会比敌人小
                            eat_list.append((cell, num * Consts["FRAME_DELTA"], num))
                # ===========================逃避判定============================
                else:
                    temp = self.need_run_k(my_cell, cell)
                    if not temp:
                        continue
                    elif temp < 50:
                        run_list.append((cell, temp))

        #print(str(self.n).center(40, "="))
        #print(eat_list)
        #print(run_list)
        # ==========================================处理躲避===============================================
        if run_list != []:
            min_crash_time = 9999   # 最紧迫的敌人
            min_index = 0           # 最紧迫的敌人的序号
            for i in range(len(run_list)):
                # 遍历需要回避的列表
                if run_list[i][1] < min_crash_time:
                    min_crash_time = run_list[i][1]
                    min_index = i
            vector = self.run_direction(run_list[min_index][1], my_cell, run_list[min_index][0])
            return math.atan2(vector[0], vector[1])
        # =========================================躲避处理结束============================================
        # ==========================================处理捕食=========================================
        # ======评估函数建立============
        max_gain = 0
        index = 0
        for i in range(len(eat_list)):
            if eat_list[i][0] == rival_cell:
                value = 1000000
                if value > max_gain and my_cell.radius/rival_cell.radius > 1.2:
                    # 如果去吃敌人价值大并且我的半径比敌人大一定倍数就去捕食敌人
                    max_gain = value
                    index = i
                continue
            value = self.value_function(my_cell.pos, eat_list[i][0].pos, my_cell.radius, eat_list[i][0].radius,
                                        eat_list[i][2])
            if self.future_of_target(my_cell, eat_list[i][0], allcells, eat_list[i][1]):
                # 如果去吃这个球有危险
                value = 0
            if value > max_gain:
                max_gain = value
                index = i
        # ===============处理喷射================
        if eat_list == []:
            return None
        if max_gain > 50000:
            if eat_list[index][2] != 0 and (eat_list[index][2] < 40 or eat_list[index][0] == rival_cell):
                #print(eat_list[index][2])
                # 如果不能直接吃到
                vector = self.eject_angle(eat_list[index][2], my_cell, eat_list[index][0])
                return math.atan2(vector[0], vector[1])
            elif eat_list[index][2] == 0:
                # 此时你不动都可以吃到
                return None
        else:
            return None
        # =============================================捕食处理结束===========================================
