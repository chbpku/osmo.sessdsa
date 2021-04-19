import math
from copy import deepcopy
from consts import Consts


class Player:
    def __init__(self, id, arg=None):
        self.id = id
        self.cool = 0       # 喷射计数
        self.chase = False
        self.already_win = False  # 必胜局面就坐等胜利，不要送了-_-||
        self.current_target = None  # 不要随便改变目标[○･｀Д´･ ○]
        self.status = "start"   # 序盘
        self.chase_target = None    # 追击目标


    # ====================数学类函数===================
    def innner_product(self, a, b):
        """内积"""
        return a[0] * b[0] + a[1] * b[1]

    def regularization(self, rad):
        """角度正规化"""
        return math.fmod((rad + 3 * math.pi * 2) / math.pi * 180, 360)

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
        x_norm = abs(my_pos[0] - e_pos[0])  # 正常x方向距离
        x_cross = abs(Consts["WORLD_X"] - x_norm)  # 跨越屏幕的x方向距离
        x = min(x_norm, x_cross)  # 最短的距离
        y_norm = abs(my_pos[1] - e_pos[1])  # 正常y方向距离
        y_cross = abs(Consts["WORLD_Y"] - y_norm)  # 跨越屏幕的y方向距离
        y = min(y_norm, y_cross)  # 最短的y方向距离
        return (x ** 2 + y ** 2) ** 0.5

    def cross_border_vector(self, my_pos, e_pos):
        """跨越屏幕的方向向量，指向敌人"""
        x_norm = abs(my_pos[0] - e_pos[0])  # 正常x方向距离
        x_cross = abs(Consts["WORLD_X"] - x_norm)  # 跨越屏幕的x方向距离
        if x_norm < x_cross:
            # 若不穿越屏幕
            rel_x = e_pos[0] - my_pos[0]  # 指向敌人的x相对位移
        else:  # 若穿越屏幕
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

    def inPath(self, my_pos, my_radius, dir_vec, e_pos, e_radius):
        """某个球是否在路径上的判定"""
        dist_vector = self.cross_border_vector(my_pos, e_pos)   # 跨屏相对位史
        cos = self.innner_product(dir_vec, dist_vector)/(self.mod(dist_vector)*self.mod(dir_vec))
        try:
            critical_cos = math.sqrt(self.mod(dist_vector)**2 - (my_radius+e_radius)**2)/self.mod(dist_vector)
        except ValueError:
            return False
        if cos > critical_cos:
            return True
        else:
            return False

    def change_veloc_to(self, veloc, delta_veloc, dir):
        """使veloc尽量地靠近dir"""
        unit_dir = [dir[0]/self.mod(dir), dir[1]/self.mod(dir)]
        # 单位化的方向
        try:    # 防止出现速度为零的情况
            cos = self.innner_product(veloc, unit_dir) / self.mod(veloc)
        except ZeroDivisionError:
            return [-unit_dir[0], -unit_dir[1]]
        sin = math.sqrt(1-cos**2)       # 张角的sin值
        min_delta = self.mod(veloc) * sin       # 最小的速度改变量
        if min_delta < delta_veloc:
            # 此时可以扭转速度
            total_veloc = math.sqrt(delta_veloc**2 - min_delta**2) + self.mod(veloc) * cos
            return [veloc[0] - unit_dir[0] * total_veloc, veloc[1] - unit_dir[1] * total_veloc]
        else:
            return [veloc[0] - unit_dir[0] * self.mod(veloc) * cos, veloc[1] - unit_dir[1] * self.mod(veloc) * cos]

    def accelerate(self, n):
        """以固定相对速度从静止开始加速的s（t）关系"""
        rate = Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"] * Consts["FRAME_DELTA"]
        return rate * n * (n + 1) / 2

    def part_accelerate(self, n, k):
        """加速n帧，总共运动k帧"""
        rate = Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"] * Consts["FRAME_DELTA"]
        return rate * n * (n + 1) / 2 + (k - n) * rate * n

    def min_eject_num(self, my_cell, e_cell, alpha=3):
        """最小喷射数,近似版，精确版目测会爆时间？？？？
        返回估值参数和最少喷射数"""
        n = 1
        total_rad = my_cell.radius + e_cell.radius
        rel_veloc = [my_cell.veloc[0] - e_cell.veloc[0], my_cell.veloc[1] - e_cell.veloc[1]]
        e_pos = e_cell.pos
        my_pos = my_cell.pos
        function = self.cross_border_dist(e_pos, my_pos) - total_rad - self.part_accelerate(n, alpha * n)
        while function > 0:
            my_pos[0] += rel_veloc[0] * Consts["FRAME_DELTA"] * alpha
            my_pos[1] += rel_veloc[1] * Consts["FRAME_DELTA"] * alpha
            my_pos = self.stay_in_bounds(my_pos)
            n += 1
            function = self.cross_border_dist(e_pos, my_pos) - total_rad - self.part_accelerate(n, alpha * n)
        return n

    def solve_root(self, my_cell, e_cell):
        """求根函数,求出最快喷射数"""
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

    def eject_angle_for_long(self, n, my_cell, e_cell, alpha=3):
        """计算远程追击的喷射角"""
        my_veloc = [my_cell.veloc[0] - e_cell.veloc[0], my_cell.veloc[1] - e_cell.veloc[1]]  # 我的相对速度
        my_pos = [my_cell.pos[0] + my_veloc[0] * n * Consts["FRAME_DELTA"] * alpha,
                  my_cell.pos[1] + my_veloc[1] * n * Consts["FRAME_DELTA"] * alpha]
        my_pos = self.stay_in_bounds(my_pos)
        # 我在移动n帧之后的位置
        rel_pos = self.cross_border_vector(e_cell.pos, my_pos)
        # 运行n帧之后敌人指向我的矢量
        return rel_pos

    def travel(self, my_cell, e_cell):
        """只是向那个方向迁移而已"""
        veloc = [my_cell.veloc[0]-e_cell.veloc[0],my_cell.veloc[1]-e_cell.veloc[1]]
        delta_v = 10 * Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"]
        # 相对速度
        rel_pos = self.cross_border_vector(my_cell.pos, e_cell.pos)     # 相对位置
        return self.change_veloc_to(veloc,delta_v,rel_pos)

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
    def absorb(self, collision, allcells):
        """从world移植用于预测未来"""
        # Calculate total momentum and mass
        mass = sum(allcells[ele].area() for ele in collision)
        px = sum(allcells[ele].area() * allcells[ele].veloc[0] for ele in collision)
        py = sum(allcells[ele].area() * allcells[ele].veloc[1] for ele in collision)
        # Determine the biggest cell
        collision.sort(key=lambda ele: allcells[ele].radius)
        biggest = collision.pop()
        allcells[biggest].radius = (mass / math.pi) ** 0.5
        allcells[biggest].veloc[0] = px / mass
        allcells[biggest].veloc[1] = py / mass
        for ele in collision:
            allcells[ele].dead = True

    def prophet(self, allcells, n):
        """预测n帧以后的情况,target是追击的球"""
        for i in range(n + 1):
            # ===========================计时部分=============================
            frame_delta = Consts["FRAME_DELTA"]
            # ===========================更新===========================
            # 移动
            for cell in allcells:
                if not cell.dead:
                    cell.move(frame_delta)
            collisions = []
            for i in range(len(allcells)):
                if allcells[i].dead:
                    continue
            # 碰撞
                for j in range(i + 1, len(allcells)):
                    if not allcells[j].dead and allcells[i].collide(allcells[j]):
                        if allcells[i].collide_group == None == allcells[j].collide_group:
                            allcells[i].collide_group = allcells[j].collide_group = len(collisions)
                            collisions.append([i, j])
                        elif allcells[i].collide_group != None == allcells[j].collide_group:
                            collisions[allcells[i].collide_group].append(j)
                            allcells[j].collide_group = allcells[i].collide_group
                        elif allcells[i].collide_group == None != allcells[j].collide_group:
                            collisions[allcells[j].collide_group].append(i)
                            allcells[i].collide_group = allcells[j].collide_group
                        elif allcells[i].collide_group != allcells[j].collide_group:
                            collisions[allcells[i].collide_group] += collisions[allcells[j].collide_group]
                            for ele in collisions[allcells[j].collide_group]:
                                allcells[ele].collide_group = allcells[i].collide_group
                            collisions[allcells[j].collide_group] = []
            for collision in collisions:
                if collision != []:
                    self.absorb(collision, allcells)
            if allcells[0].dead:
                # 如果我死了，返回死亡的帧数
                return i
        # 我没有死(*^▽^*)
        return None
    # ================================================================
    # =====================各类操预知数========================
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
                    e_cell.radius + 0.95 * my_cell.radius) ** 2)) / self.cross_border_dist(my_cell.pos, e_cell.pos)
        except ValueError:
            return False
        if cos > critical_cos:
            # 此时不动就可以吃到，返回吃到所需要的时间
            return math.ceil((self.cross_border_dist(my_cell.pos, e_cell.pos) * cos - (
                    (0.95 * my_cell.radius + e_cell.radius) ** 2 - self.cross_border_dist(my_cell.pos, e_cell.pos) ** 2 * (
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
                        (my_cell.radius + e_cell.radius + delta) ** 2 - self.cross_border_dist(my_cell.pos,
                                                                                               e_cell.pos) ** 2 * (
                                1 - cos ** 2)) ** 0.5) / (self.mod(rel_veloc) * Consts["FRAME_DELTA"]))
        except ValueError:
            try:  # 若根式中值小于0，说明进入临界区域内
                critical_cos = math.sqrt((self.cross_border_dist(my_cell.pos, e_cell.pos) ** 2 - (
                        e_cell.radius + my_cell.radius) ** 2)) / self.cross_border_dist(my_cell.pos, e_cell.pos)
                if cos > critical_cos:
                    # 此时不动的话就会被吃掉
                    return math.ceil((self.cross_border_dist(my_cell.pos, e_cell.pos) * cos - (
                            (my_cell.radius + e_cell.radius) ** 2 - self.cross_border_dist(my_cell.pos,
                                                                                           e_cell.pos) ** 2 * (
                                    1 - cos ** 2)) ** 0.5) / (self.mod(rel_veloc) * Consts["FRAME_DELTA"]))
            except ValueError:
                # 你已经死了,不要挣扎了o(╥﹏╥)o
                return False
        return False

    def canKill(self, my_cell, e_cell, allcells, secure_bound=15, critical_radius=25):
        """判断是否可以直接秒杀敌人的球
        secure_bound防止自己白给"""
        num = self.solve_root(deepcopy(my_cell), deepcopy(e_cell))  # 吃掉敌人至少要喷的球数
        if my_cell.radius > critical_radius and 120 > self.cross_border_dist(my_cell.pos, e_cell.pos) > 60:
            # 如果我的半径大于临界半径
            if my_cell.radius * (1 - Consts['EJECT_MASS_RATIO']) ** (0.5 * num) > e_cell.radius + secure_bound:
                # 判断你追上敌人后半径是否会比敌人小
                rel_pos = self.cross_border_vector(my_cell.pos, e_cell.pos) # 相对位置
                for cell in allcells:
                    if my_cell == cell:
                        continue
                    if e_cell == cell:
                        continue
                    if 0.6 * cell.radius > my_cell.radius:
                        # 要回避的，可以考虑更精细的判断
                        if self.inPath(my_cell.pos,my_cell.radius, rel_pos, cell.pos, cell.radius):
                            # 有一个危险的球在路径上
                            return False
                return True
        return False

    def future_of_target(self, my_cell, eaten_cell, allcells, my_time, d=100):
        """考虑目标球未来是否会被吃或者吃其它球或到该球中间有其他球返回True"""
        for cell in allcells:
            # 遍历场上的球
            if cell == my_cell:
                continue
            if cell == eaten_cell:  # 跳过自己的球和目标球
                continue
            if cell.radius + 2 > my_cell.radius:
                # 若那个球比我大
                rel_dir = self.cross_border_vector(my_cell.pos, eaten_cell.pos)
                if self.inPath(my_cell.pos, my_cell.radius, rel_dir, cell.pos,
                               cell.radius) and self.cross_border_dist(my_cell.pos, cell.pos) < self.cross_border_dist(
                        my_cell.pos, eaten_cell.pos):
                    # 有大球在到目标的路径上
                    return True
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

    def future_of_target_for_long(self, my_cell, eaten_cell, allcells, my_time, d=200):
        """用于远程狙击的判定"""
        """考虑目标球未来是否会被吃或者吃其它球或到该球中间有其他球返回True"""
        for cell in allcells:
            if cell == my_cell:
                continue
            if cell == eaten_cell:  # 跳过自己的球和目标球
                continue
            if cell.radius + 2 > my_cell.radius:
                # 若那个球比我大
                rel_dir = self.cross_border_vector(my_cell.pos, eaten_cell.pos)
                if self.inPath(my_cell.pos, my_cell.radius, rel_dir, cell.pos,
                               cell.radius) and self.cross_border_dist(my_cell.pos, cell.pos) < self.cross_border_dist(
                    my_cell.pos, eaten_cell.pos):
                    # 有大球在到目标的路径上
                    return True
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
                        if my_time - time < 30:
                            # 如果我吃了这个球比它快10帧以下
                            return True
            return False

    # ==========================评估函数系列===============================

    def value_function1(self, my_pos, e_pos, my_radius, e_radius, num, alpha=20000, beta=50000, gamma=3000):
        """评估函数,目前考虑了敌方大小，敌方半径，追击的喷射数，追击的时间消耗"""
        if e_radius < 3 * (Consts['EJECT_MASS_RATIO']) ** 0.5 * my_radius:
            return 100
        dist = self.cross_border_dist(my_pos, e_pos) - (my_radius + e_radius)
        # 除去半径的距离
        dist_vector = self.cross_border_vector(my_pos, e_pos)
        return alpha * e_radius + beta / dist - num * gamma


    def value_function2(self, my_cell, e_cell, num, allcells, alpha=20000, beta=50000, gamma=5000, omega=10000):
        """中程评估函数,目前考虑了敌方大小，敌方半径，追击的喷射数，追击的时间消耗"""
        bonus_for_near = 0
        my_radius = my_cell.radius
        e_radius = e_cell.radius
        my_pos = my_cell.pos
        e_pos = e_cell.pos
        e_veloc = e_cell.veloc
        rel_vec = [my_cell.veloc[0] - e_cell.veloc[0], my_cell.veloc[1] - e_cell.veloc[1]]
        chase_pos = [my_pos[0] + num * Consts["FRAME_DELTA"] * rel_vec[0],
                     my_pos[1] + num * Consts["FRAME_DELTA"] * rel_vec[1]]
        chase_pos = self.stay_in_bounds(chase_pos)
        chase_vec = self.cross_border_vector(chase_pos, e_pos)
        # 发射方向
        dist = self.cross_border_dist(my_pos, e_pos) - (my_radius + e_radius)
        if e_radius < 4 * (Consts['EJECT_MASS_RATIO']) ** 0.5 * my_radius:
            return 0
        if dist < 5:
            bonus_for_near = 200000
        try:
            cos = self.innner_product(chase_vec, rel_vec)/(self.mod(rel_vec)*self.mod(chase_vec))
        except ZeroDivisionError:
            # 不想考虑了╮(╯▽╰)╭
            cos = 0
        if cos < -0.1 and self.mod(my_cell.veloc) > 0.3:
            return 0
        # 除去半径的距离
        future_pos = [e_pos[0] + num * e_veloc[0] * Consts["FRAME_DELTA"], e_pos[1] + num * e_veloc[1] * Consts["FRAME_DELTA"]]
        future_pos = self.stay_in_bounds(future_pos)
        #追上时的位置
        bonus = 0
        for cell in allcells:
            if cell.id == my_cell.id:
                # 跳过自己
                continue
            if cell.id == e_cell.id:
                # 跳过目标
                continue
            # ===================危机判断==================
            if cell.radius + 2 > my_cell.radius:
                # 若那个球比我大
                rel_dir = self.cross_border_vector(my_cell.pos, e_cell.pos)
                if self.inPath(my_cell.pos, my_cell.radius, rel_dir, cell.pos,
                               cell.radius) and self.cross_border_dist(my_cell.pos, cell.pos) < self.cross_border_dist(
                    my_cell.pos, e_cell.pos):
                    # 有大球在到目标的路径上
                    return 0
            if self.cross_border_dist(e_cell.pos, cell.pos) - cell.radius - e_cell.radius > 100:
                # 不考虑较远的球
                continue
            time = self.can_eat_k(e_cell, cell)
            if time:
                # 说明可以吃到
                if time <= num:
                    # 这个球会被先吃掉或者吃到其它球
                    if my_cell.radius ** 2 < e_cell.radius ** 2 + cell.radius ** 2:
                        # 我的大小比它们合并之后要小
                        return 0
                else:
                    # 我会先吃到这个球
                    if my_cell.radius ** 2 + e_cell.radius ** 2 < cell.radius ** 2:
                        # 说明我就算吃了还是比它小
                        if num - time < 30:
                            # 如果我吃了这个球比它快10帧以下
                            return 0
            # ===================收益判断===================
            if self.cross_border_dist(future_pos, cell.pos) - e_cell.radius - cell.radius < 35:
                if my_cell.radius**2 + e_cell.radius**2 > 1.4 * cell.radius**2:
                    bonus += cell.radius * alpha / 2
        if False:
            if bonus:
                print()
                print("======bonus======")
                print(bonus)
                print("===========")
        return alpha * e_radius + beta / dist - num * gamma + bonus + omega * cos + bonus_for_near

    def value_function3(self, my_cell,e_cell, alpha=20000, beta=50000, gamma=3000):
        """远距离评估函数"""
        """远程评估"""
        my_radius = my_cell.radius
        e_radius = e_cell.radius
        my_pos = my_cell.pos
        e_pos = e_cell.pos
        my_veloc = my_cell.veloc
        if e_radius < my_radius / 3.5:
            return 0
        dist = self.cross_border_dist(my_pos, e_pos) - (my_radius + e_radius)
        rel_pos = self.cross_border_vector(my_pos, e_pos)
        try:
            cos = self.innner_product(rel_pos, my_veloc)/(self.mod(rel_pos)*self.mod(my_veloc))
        except ZeroDivisionError:
            cos = 0
        # 除去半径的距离
        if cos < -0.9 and self.mod(my_veloc) > 0.15:
            return 0
        return alpha * e_radius + beta / (dist - gamma)
    # ==========================================决策函数=============================================
    # ===============================================================================================

    def strategy_start(self, allcells):
        """序盘决策函数，基本想法是暴力狂吃"""
        # ========================一些参数的初始化============================
        my_cell = allcells[self.id]  # 我的球
        rival_cell = allcells[1 - self.id]  # 敌人的球
        consider_list = [my_cell]
        critical_dist1 = 140  # 捕食临界距离的判定
        critical_dist2 = 60   # 逃避临界距离
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
            elif self.cross_border_dist(my_cell.pos, cell.pos) - my_cell.radius - cell.radius < critical_dist1:
                if self.cross_border_dist(my_cell.pos, cell.pos) - my_cell.radius - cell.radius < 100:
                    consider_list.append(cell)
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
                elif self.cross_border_dist(my_cell.pos, cell.pos) - my_cell.radius - cell.radius < critical_dist2:
                    temp = self.need_run_k(my_cell, cell)
                    # 碰撞发生的时间
                    if not temp:
                        continue
                    elif temp < 40:
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
                if value > max_gain and my_cell.radius/rival_cell.radius > 1.5:
                    # 如果去吃敌人价值大并且我的半径比敌人大一定倍数就去捕食敌人
                    max_gain = value
                    index = i
                continue
            value = self.value_function1(my_cell.pos, eat_list[i][0].pos, my_cell.radius, eat_list[i][0].radius,
                                        eat_list[i][2])
            if self.current_target and self.current_target == eat_list[i][0].id:
                value += 40000
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
            self.current_target = eat_list[index][0].id
            if eat_list[index][2] != 0 and (eat_list[index][2] < 40 or eat_list[index][0] == rival_cell):
                #print(eat_list[index])
                # 如果不能直接吃到
                vector = self.eject_angle(eat_list[index][2], my_cell, eat_list[index][0])
                return math.atan2(vector[0], vector[1])
            elif eat_list[index][2] == 0:
                rel_pos = self.cross_border_vector(eat_list[index][0].pos, my_cell.pos)
                if self.prophet(deepcopy(consider_list), 12):
                    return math.atan2(-rel_pos[0],-rel_pos[1])
                if eat_list[index][1] > 200 and my_cell.radius > eat_list[index][0].radius * 1.05:
                    return math.atan2(rel_pos[0], rel_pos[1])
                # 此时你不动都可以吃到
                return None
        else:
            return None
        # =============================================捕食处理结束===========================================

    def strategy_middle(self, allcells):
        """中局决策函数，基本想法是锁定狙击"""
        self.cool += 1
        #远端冷却
        # ========================一些参数的初始化============================
        my_cell = allcells[self.id]  # 我的球
        rival_cell = allcells[1 - self.id]  # 敌人的球
        consider_list = [my_cell]
        critical_dist1 = 250  # 捕食临界距离的判定
        critical_dist2 = 60   # 逃避临界距离
        eat_list = []  # 可以吃的列表
        run_list = []  # 需要逃跑的列表
        # ==========================特殊情况的决策==============================
        if 2 * my_cell.radius ** 2 > 0.98 * sum(x.radius**2 for x in allcells):
            self.already_win = True
            return None
        if self.canKill(my_cell, rival_cell, allcells):
            self.chase = True
        self.chase = False
        # 斩杀模式的开关
        # ===================================斩杀模式开启===================================
        # 斩杀模式只躲避会死的敌人，不考虑吃其它球
        if self.chase:
            # =====================是否要躲避的判断=========================
            run_list = []
            for cell in allcells:
                if cell == allcells[self.id]:
                    # 跳过自己
                    continue
                if self.cross_border_dist(my_cell.pos, cell.pos) - my_cell.radius - cell.radius > critical_dist2:
                    continue
                if cell.radius < my_cell.radius:
                    continue
                temp = self.need_run_k(my_cell, cell)
                if not temp:
                    continue
                elif temp < 50:
                    run_list.append((cell, temp))
            # 中途躲避开关
            if run_list != []:
                min_crash_time = 9999  # 最紧迫的敌人
                min_index = 0  # 最紧迫的敌人的序号
                for i in range(len(run_list)):
                    # 遍历需要回避的列表
                    if run_list[i][1] < min_crash_time:
                        min_crash_time = run_list[i][1]
                        min_index = i
                vector = self.run_direction(run_list[min_index][1], my_cell, run_list[min_index][0])
                self.chase = False
                return math.atan2(vector[0], vector[1])
            # ===============================================================

            # =======================追击函数============================
            rel_pos = self.cross_border_vector(rival_cell.pos, my_cell.pos)  # 相对位置
            num = self.can_eat_k(my_cell, rival_cell)
            if num:
                # 说明不动就可以追上
                return math.atan2(rel_pos[0], rel_pos[1])
            else:
                # 说明要矫正位置才能追上,就矫正位置
                num = self.solve_root(deepcopy(my_cell), deepcopy(rival_cell))
                vector = self.eject_angle(num, my_cell, rival_cell)
                return math.atan2(vector[0], vector[1])
        # =====================追击判定======================
        chase_cell = None
        if self.chase_target is not None:
            # 可能有追击目标
            #print("================================")
            #print("target is", self.chase_target)

            for cell in allcells:
                if cell.id == self.chase_target:
                    # 如果被追的目标还活着
                    chase_cell = cell
                    if cell.radius > my_cell.radius:
                        # 敌人比我大了，终止追击
                        self.chase_target = None
                    else:
                        break
            else:
                # 敌人死了停止追击
                self.chase_target = None
        self.chase_target = None
        # 追击模式的开关
        # =======================================进入追击模式==========================================
        if self.chase_target:
            for cell in allcells:
                if cell == allcells[self.id]:
                    # 跳过自己
                    continue
                # ===========================逃避判定============================
                elif self.cross_border_dist(my_cell.pos, cell.pos) - my_cell.radius - cell.radius < critical_dist2 and \
                        cell.radius > my_cell.radius:
                    temp = self.need_run_k(my_cell, cell)
                    # 碰撞发生的时间
                    if not temp:
                        continue
                    elif temp < 40:
                        run_list.append((cell, temp))
            # 追击模式中仍考虑逃跑
            if run_list != []:
                min_crash_time = 9999  # 最紧迫的敌人
                min_index = 0  # 最紧迫的敌人的序号
                for i in range(len(run_list)):
                    # 遍历需要回避的列表
                    if run_list[i][1] < min_crash_time:
                        min_crash_time = run_list[i][1]
                        min_index = i
                vector = self.run_direction(run_list[min_index][1], my_cell, run_list[min_index][0])
                return math.atan2(vector[0], vector[1])
            # ==========追击===========
            temp = self.can_eat_k(my_cell, chase_cell)
            if temp:
                # 可以直接吃到
                time = temp
                if self.future_of_target_for_long(my_cell, chase_cell, allcells, time):
                    # 追击比较危险
                    self.chase_target = None
                    return None
                rel_pos = self.cross_border_vector(chase_cell.pos, my_cell.pos)
                if time > 600 and my_cell.radius * 1.1 > chase_cell.radius:
                    return math.atan2(rel_pos[0], rel_pos[1])
                else:
                    pass
            else:       # 不可以吃到
                num = self.solve_root(deepcopy(my_cell), deepcopy(chase_cell))  # 吃掉敌人至少要喷的球数
                if my_cell.radius * (1 - Consts['EJECT_MASS_RATIO']) ** (0.5 * num) > chase_cell.radius * 1.3:
                    time = num
                    if self.future_of_target(my_cell, chase_cell, allcells, time):
                        # 追击比较危险
                        self.chase_target = None
                        return None
                    vector = self.travel(my_cell, chase_cell)
                    # print("change dir")
                    return math.atan2(vector[0], vector[1])
                else:  # 此时吃不了
                    self.chase_target = None
                    return None
            return None
        # ===============================主循环==================================
        for cell in allcells:
            if cell == allcells[self.id]:
                # 跳过自己
                continue
            # =====================捕食判定=======================
            elif self.cross_border_dist(my_cell.pos, cell.pos) - my_cell.radius - cell.radius < critical_dist1:
                if self.cross_border_dist(my_cell.pos, cell.pos) - my_cell.radius - cell.radius < 100:
                    consider_list.append(cell)
                # 只判断足够近的球
                if cell.radius < my_cell.radius:
                    # 敌人可能可以吃
                    temp = self.can_eat_k(my_cell, cell)
                    if temp:  # 如果不动就可以吃到
                        eat_list.append((cell, temp, 0))
                    else:
                        num = self.min_eject_num(deepcopy(my_cell), deepcopy(cell))  # 吃掉敌人至少要喷的球数
                        if my_cell.radius * (1 - Consts['EJECT_MASS_RATIO']) ** (0.5 * (num//3)) > cell.radius:
                            # 判断你追上敌人后半径是否会比敌人小
                            eat_list.append((cell, num * Consts["FRAME_DELTA"], num))
                # ===========================逃避判定============================
                elif self.cross_border_dist(my_cell.pos, cell.pos) - my_cell.radius - cell.radius < critical_dist2:
                    temp = self.need_run_k(my_cell, cell)
                    # 碰撞发生的时间
                    if not temp:
                        continue
                    elif temp < 40:
                        # 如果碰撞时间小于一定阈值
                        run_list.append((cell, temp))
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
        max_gain = 0    # 最大收益
        index = 0       # 目标对应的编号
        for i in range(len(eat_list)):
            if eat_list[i][0] == rival_cell:
                # 对敌人处理
                value = 1000000
                if value > max_gain and my_cell.radius/rival_cell.radius > 1.5 and\
                        self.cross_border_dist(my_cell.pos, rival_cell.pos)-my_cell.radius-rival_cell.radius < 40 and self.mod(my_cell.veloc)<0.2:
                    # 如果去吃敌人价值大并且我的半径比敌人大一定倍数就去捕食敌人
                    max_gain = value
                    index = i
                continue
            value = self.value_function2(my_cell, eat_list[i][0], eat_list[i][2],allcells)
            if self.current_target and self.current_target == eat_list[i][0].id:
                # 对同一个追击目标的执着
                if eat_list[i][0].radius > 1/2 * my_cell.radius:
                    value += 300000
                elif eat_list[i][0].radius > 1/1.5 * my_cell.radius:
                    value += 600000
            if self.future_of_target(my_cell, eat_list[i][0], allcells, eat_list[i][2]):
                # 如果去吃这个球有危险
                value = 0
            if value > max_gain:
                max_gain = value
                index = i
        # ===============处理喷射================
        if eat_list == []:
            return None
        if max_gain > 100000:
            self.stop = False
            self.current_target = eat_list[index][0].id
            if eat_list[index][2] != 0 and (eat_list[index][2]//3 < 15 or max_gain > 600000):
                #print(eat_list[index])
                # 如果不能直接吃到
                vector = self.eject_angle_for_long(eat_list[index][2], my_cell, eat_list[index][0])
                return math.atan2(vector[0], vector[1])
            elif eat_list[index][2] == 0:
                rel_pos = self.cross_border_vector(eat_list[index][0].pos, my_cell.pos)
                if self.prophet(deepcopy(consider_list),12):
                    return math.atan2(-rel_pos[0],-rel_pos[1])
                rel_vec = [my_cell.veloc[0]-eat_list[index][0].veloc[0],my_cell.veloc[1]-eat_list[index][0].veloc[1]]
                if self.mod(rel_vec) < 0.8 and my_cell.radius > eat_list[index][0].radius * 1.1 and self.cool >= 1:
                    self.cool = 0   # 喷射冷却
                    return math.atan2(rel_pos[0], rel_pos[1])
                # 此时你不动都可以吃到
                return None
        else:
            pass
        # ==========================远端判断=======================
        if self.chase_target:
            return None
        max_gain = 0
        target = None
        for cell in allcells:
            if cell.id == self.id:
                continue
            if cell.id == 1 - self.id:
                continue
            if 10/11 * my_cell.radius > cell.radius > 1/2.5 * my_cell.radius or False:
                # False占位,将来用于密度判定
                gain = self.value_function3(my_cell, cell)
                if gain > max_gain:
                    max_gain = gain
                    target = cell.id
        if max_gain > 60000:
            self.chase_target = target
        return None



        # =============================================捕食处理结束===========================================

    def strategy(self, allcells):
        """决策的主函数"""
        # ========================一些参数的初始化============================
        my_cell = allcells[self.id]  # 我的球
        # =========================初始判断======================
        if self.already_win:
            # 在某些特殊条件下已经获胜
            return None
        # =====局势判定======
        count = 0
        for cell in allcells:
            if cell.radius > 2 * Consts["EJECT_MASS_RATIO"] **0.5 * my_cell.radius:
                count += 1
        if count < Consts["CELLS_COUNT"] // 15:
            self.status = "ending"  # 终盘
        elif count < Consts["CELLS_COUNT"] // 5:
            self.status = "middle"  # 中局
        else:
            self.status = "start"   # 序盘
        # ==========================特殊情况的决策==============================
        if 2 * my_cell.radius ** 2 > 0.98 * sum(x.radius ** 2 for x in allcells):
            self.already_win = True
            return None
        # =========================决策==================
        if self.status == "start":
            # 序盘决策
            return self.strategy_start(allcells)
        elif self.status == "middle":
            # 中局决策
            return self.strategy_middle(allcells)
        elif self.status == "ending":
            # 终盘决策
            return self.strategy_middle(allcells)
        else:
            return None
