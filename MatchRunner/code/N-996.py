from consts import Consts
from copy import deepcopy
from cell import Cell
import math

class Player():
    def __init__(self, id, arg = None):
        self.id = id
        # 用于标记战略状态，F=0代表正在搜索要吃的球，F=1代表已找到球，在匀加速状态，F=2代表已找到球，在匀速状态, F=3代表在躲球
        self.state = 0
        # 记录比赛进行的tick数
        self.tick = 0
        # 记录当前theta最优选择
        self.Best_theta = None
        # Best_N1代表需要匀加速的步数
        self.Best_N1 = None
        # Best_N2代表需要匀速的步数
        self.Best_N2 = None
        # 用于记录已经走过的匀加速/匀速运动/躲球的步数
        self.cnt = 0
        # 在360度中搜索多少种角度
        self.N_possibilities = 30
        # 参数设置
        self.V_absolute_max = 1.5  # 我们目前的绝对速度上限，超过这个速度并且很安全的话就会考虑不动一段时间

        # 躲球参数
        self.dangerous_distance = 65  # 危险距离标准
        self.absorb_distance = 20 # 吸收合并距离标准，用于判断在我们吃球路线中是否会有球在这个距离内合并变大吃掉我们
        self.dangerous_ntick = 5 # 判断是否安全时，考虑多少个tick的吸收情况
        self.min_collide_time = 15

        # 吃球参数
        self.min_radius = 0.01  # 吃球的时候不考虑半径小于自身半径？%的球
        self.vmax = 1  # 单方向速度临界值,调的小一点以免过度消耗
        self.ntick1max = 10  # 匀加速的最大tick
        self.ntick2max = 40  # 匀速漂移的最大tick
        self.target_lst_length = 3  # 考虑的可吃对象list的长度
        # 以下吃球参数中a\b\c\d越大代表该参数越重要
        self.a = 1 # 吃球时考虑另一个球距离的权重
        self.b = 100 # 吃球时考虑另一个球相对我半径大小的权重
        self.c = 1 # 吃掉球所需要的ntick1
        self.d = 0.5 # 吃掉球所需要的ntick2
        self.e = 100 # 吃掉球后的半径


    # ========= Part 1 用于使小球匀速/加速/加速后匀速/吸收/发射的功能函数 ==========

    # 输入Cell对象，返回小球基本参数
    def get_cell_info(self, ball):
        # cell_id = ball.id
        x = ball.pos[0]
        y = ball.pos[1]
        vx = ball.veloc[0]
        vy = ball.veloc[1]
        r = ball.radius
        return x, y, vx, vy, r

    # 用小球信息生成一个虚拟小球
    def create_cell(self, x, y, vx, vy, r):
        fake = Cell(100000, [x, y], [vx, vy], r)
        return fake

    # 处理位置x\y的边界问题
    def stay_in_bounds(self, x, y):
        if x < 0:
            x += Consts["WORLD_X"]
        elif x > Consts["WORLD_X"]:
            x -= Consts["WORLD_X"]

        if y < 0:
            y += Consts["WORLD_Y"]
        elif y > Consts["WORLD_Y"]:
            y -= Consts["WORLD_Y"]
        return x, y

    # 匀速
    # 计算ball按照当前速度匀速运行ntick后的参数变化，返回移动后的小球
    def move(self, ball, n_tick):
        x, y, vx, vy, r = self.get_cell_info(ball)
        # cell_id, x, y, vx, vy, r = [self.get_cell_info(ball)[i] for i in range(6)]
        # Adjust the position, according to velocity.
        dt = Consts["FRAME_DELTA"] * n_tick
        move_x = x + vx * dt
        move_y = y + vy * dt
        move_x, move_y = self.stay_in_bounds(move_x, move_y)
        move_ball = self.create_cell(move_x, move_y, vx, vy, r)
        return move_ball

    # 喷射
    # 计算ball朝theta喷射一次后的参数变化
    def eject(self, ball, theta):
        x, y, vx, vy, r = self.get_cell_info(ball)
        if theta is None:
            return self.create_cell(x, y, vx, vy, r)
        # Reduce force in proportion to area
        fx = math.sin(theta)
        fy = math.cos(theta)
        # Push ball
        e_vx = vx - Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
        e_vy = vy - Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
        # Lose some mass
        e_r = r * (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5
        e_ball = self.create_cell(x, y, e_vx, e_vy, e_r)
        return e_ball

    # 匀加速
    # 计算某个小球朝连续朝theta角度喷射后的参数情况
    def accelerate(self, ball, theta, n_tick):
        x, y, vx, vy, r = self.get_cell_info(ball)
        a_ball = self.create_cell(x, y, vx, vy, r)
        for i in range(n_tick):
            a_ball = self.eject(a_ball, theta)
            a_ball = self.move(a_ball, 1)
        return a_ball

    # 计算小球ball1朝连续按theta角度喷射ntick后的速度、半径
    def eject_continious(self, ball, theta, n_tick):
        # 分解加速度
        k = Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"]
        ax = - k * math.sin(theta)
        ay = - k * math.cos(theta)
        x, y = ball.pos[0], ball.pos[1]
        vx = ball.veloc[0]
        vy = ball.veloc[1]
        r = ball.radius
        # 计算i步之后，ball1的速度
        new_vx = vx + ax * n_tick
        new_vy = vy + ay * n_tick
        # 计算i步之后，ball1的半径
        r1new = r * (1 - Consts["EJECT_MASS_RATIO"]) ** (n_tick / 2)
        return x, y, new_vx, new_vy, r1new

    # ========= Part 2 用于计算两个小球相对位置、是否相撞等的功能函数 ==========

    # 计算两个小球的相对速度和位置
    def relative(self, ball1, ball2):
        # 计算ball1相对ball2的速度和位置
        dx = ball1.pos[0] - ball2.pos[0]
        dy = ball1.pos[1] - ball2.pos[1]
        dvx = ball1.veloc[0] - ball2.veloc[0]
        dvy = ball1.veloc[1] - ball2.veloc[1]
        return dx, dy, dvx, dvy

    # 计算两个小球的真实距离（减去二者半径，大于0）
    def true_distance(self, ball1, ball2):
        return max(ball1.distance_from(ball2) - ball1.radius - ball2.radius, 0)

    # 计算两个小球是否相撞
    def if_collide_now(self, ball1, ball2):
        return self.true_distance(ball1, ball2) == 0

    # 球1加速运动，球2加速运动，判断两个小球n_tick内是否相撞（匀速theta传入None即可）
    def if_will_collide(self, ball1, ball2, theta1, theta2, n_tick):
        x1, y1, vx1, vy1, r1 = self.get_cell_info(ball1)
        c_ball1 = self.create_cell(x1, y1, vx1, vy1, r1)
        x2, y2, vx2, vy2, r2 = self.get_cell_info(ball2)
        c_ball2 = self.create_cell(x2, y2, vx2, vy2, r2)
        for i in range(n_tick):
            # c_ball1_i = self.accelerate(c_ball1, theta1, i)
            # c_ball2_i = self.accelerate(c_ball2, theta2, i)
            # if self.if_collide_now(c_ball1_i, c_ball2_i):
            c_ball1 = self.eject(c_ball1, theta1)
            c_ball1 = self.move(c_ball1, 1)
            c_ball2 = self.eject(c_ball2, theta2)
            c_ball2 = self.move(c_ball2, 1)
            if self.if_collide_now(c_ball1, c_ball2):
                # print(i, self.get_cell_info(c_ball1), self.get_cell_info(c_ball2))
                return True
        # print(i, self.get_cell_info(c_ball1), self.get_cell_info(c_ball2))
        return False

    # 计算两个小球相撞后，合成的小球
    def absorb(self, ball1, ball2):
        # Calculate total momentum and mass
        area1, vx1, vy1 = ball1.area(), ball1.veloc[0], ball1.veloc[1]
        area2, vx2, vy2 = ball2.area(), ball2.veloc[0], ball2.veloc[1]
        mass = area1 + area2
        px = vx1 * area1 + vx2 * area2
        py = vy1 * area1 + vy2 * area2
        new_radius = (mass / math.pi) ** 0.5
        new_vx = px / mass
        new_vy = py / mass
        if area1 > area2:
            x = ball1.pos[0]
            y = ball1.pos[1]
        else:
            x = ball2.pos[0]
            y = ball2.pos[1]
        new_ball = self.create_cell(x, y, new_vx, new_vy, new_radius)
        return new_ball

    # ========= Part 3 用于吃球进攻的函数 ==========

    # 选择半径在一定范围以内的球
    def cells_size_range(self, cells, radius1, radius2):
        cells_size = []
        for i in cells:
            if radius1 < i.radius < radius2:
                cells_size.append(i)
        return cells_size

    # 判断是否为对手
    def is_enemy(self, ball):
        if ball.id == abs(1 - self.id):
            return 1
        else:
            return 0

    # 判断ball1在ntick内相对ball_lst是否安全
    def is_safe(self, ball1, ball_lst, theta, ntick1, ntick2):
        for ball2 in ball_lst:
            square_distance, r1new, r2 = self.accelerate_shift(ball1, ball2, theta, ntick1, ntick2)
            if square_distance < (r1new + r2) ** 2:
                return False
        return True

    # 筛选要吃的对象
    def eat_target(self, me, allcells, min_radius):
        eat_target = self.cells_size_range(allcells, min_radius * me.radius, me.radius)
        eat_target = [i for i in eat_target if self.true_distance(i, me) < 300]
        # 如果对手还很是比较大的，因为我们没有十足的把握能吃到，所以先不管
        if len(allcells) >= 2:
            if allcells[abs(1 - self.id)] in eat_target:
                if allcells[abs(1 - self.id)].area() > 0.5 * me.area():
                    eat_target.remove(allcells[abs(1 - self.id)])
        eat_info = []
        result = []
        # 初步筛选要吃的对象，考虑距离、相对半径
        eat_target.sort(key=lambda x: self.a * self.true_distance(me, x) - self.b * x.radius / me.radius)
        if len(eat_target) > self.target_lst_length:
            eat_target = eat_target[0: self.target_lst_length]
        for target in eat_target:
            eat_info_i = self.eat_theta(me, target, self.vmax, self.ntick1max, self.ntick2max, self.N_possibilities)
            if eat_info_i:
                eat_info.append([target, eat_info_i])
        # 考虑吃当前筛选对象的途中会不会有危险
        for i in range(len(eat_info)):
            hide_lst = self.cells_size_range(allcells, me.radius + 0.0000001, 1000)
            theta = eat_info[i][1][0]
            ntick1 = eat_info[i][1][1]
            ntick2 = eat_info[i][1][2]
            if self.is_safe(me, hide_lst, theta, ntick1, ntick2):
                result.append(eat_info[i])
        if result:
            # 二次筛选要吃的对象，考虑吃球需要的匀加速、匀速时间，以及吃球后的半径
            result.sort(key=lambda x: self.c * x[1][1] + self.d * x[1][2] - self.e * x[1][3])
            return result[0:2]
        else:
            return []

    # 计算小球ball1朝连续按theta角度喷射ntick1,再匀速直线运动ntick2后，ball1的新速度，ball1相对ball2距离的平方，ball1和ball2半径
    def accelerate_shift(self, ball1, ball2, theta, ntick1, ntick2):
        # k为加速度
        k = Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"]
        dt = Consts["FRAME_DELTA"]
        # 分解加速度
        ax = - k * math.sin(theta)
        ay = - k * math.cos(theta)
        # 获得相对速度、位置
        dx, dy, dvx, dvy = self.relative(ball1, ball2)
        r1, r2 = ball1.radius, ball2.radius
        # 计算ntick1步之后，相对速度
        new_vx = dvx + ax * ntick1
        new_vy = dvy + ay * ntick1
        # 计算i步之后，ball1的半径
        r1new = r1 * (1 - Consts["EJECT_MASS_RATIO"]) ** (ntick1 / 2)
        # 计算i步之后，相对的位移
        move_x = dvx * ntick1 * dt + ntick1 * (ntick1 + 1) * 0.5 * ax * dt + new_vx * ntick2 * dt
        move_y = dvy * ntick1 * dt + ntick1 * (ntick1 + 1) * 0.5 * ay * dt + new_vy * ntick2 * dt
        delta_x = move_x + dx
        delta_y = move_y + dy
        # 处理边界问题
        min_x = min(abs(delta_x), abs(delta_x + Consts["WORLD_X"]), abs(delta_x - Consts["WORLD_X"]))
        min_y = min(abs(delta_y), abs(delta_y + Consts["WORLD_Y"]), abs(delta_y - Consts["WORLD_Y"]))
        square_distance = min_x**2 + min_y**2
        return square_distance, r1new, r2

    # 选择吃小球的最佳theta
    def eat_theta(self, ball1, ball2, vmax, ntick1max, ntick2max, N_possibilities):
        theta_lst = self.theta_lst(N_possibilities)
        result_lst = []
        # 考虑相对ball2调整距离、初速度后的的ball1
        dx, dy, dvx, dvy = self.relative(ball1, ball2)
        r1, r2 = ball1.radius, ball2.radius
        copy_ball1 = self.create_cell(dx, dy, dvx, dvy, r1)
        for theta in theta_lst:
            # 计算i步匀加速之后，ball1的速度\半径是否符合要求
            for i1 in range(0, ntick1max + 1):
                x, y, new_vx, new_vy, r1new = self.eject_continious(copy_ball1, theta, i1)
                # 如果喷射后的半径大于对方
                if r1new > r2:
                    # 如果速度没有超过临界值，做i步匀加速直线运动
                    if new_vx < vmax or new_vy < vmax:
                        square_distance, r1new, r2 = self.accelerate_shift(ball1, ball2, theta, i1, 0)
                        if square_distance < (r1new + r2) ** 2:
                            r1_after_eat = (r1new * r1new + r2 * r2) ** 0.5
                            if r1_after_eat > r1:
                                result_lst.append([theta, i1, 0, r1_after_eat])
                            break
                            # 如果速度超过临界值，先做i步匀加速直线运动，再做i2步匀速直线运动
                    else:
                        # 计算i步匀加速直线运动、i2步匀速直线运动之后，ball1前进的距离，与ball2的相对位置
                        for i2 in range(0, ntick2max + 1):
                            square_distance, r1new, r2 = self.accelerate_shift(ball1, ball2, theta, i1, i2)
                            if square_distance < (r1new + r2) ** 2:
                                r1_after_eat = (r1new * r1new + r2 * r2) ** 0.5
                                if r1_after_eat > r1:
                                    result_lst.append([theta, i1, i2, r1_after_eat])
                                break
                        break
        if result_lst:
            # 排序标准：按照匀加速时间排序，可以调整
            result_lst.sort(key=lambda x: x[1])
            best_theta = result_lst[0][0]
            best_i = result_lst[0][1]
            best_i2 = result_lst[0][2]
            new_radius = result_lst[0][3]
            return [best_theta, best_i, best_i2, new_radius]
        else:
            return None

    # ========= Part 4 用于躲避防守的函数 ==========

    # 返回一个球和周围的球n_tick内吸收合并后的球
    def collide_others(self, ball1, allcells, absorb_distance, n_tick):
        ball_lst = []
        x, y, vx, vy, r = self.get_cell_info(ball1)
        copy_ball = self.create_cell(x, y, vx, vy, r)
        new = deepcopy(allcells)
        if ball1 in new:
            new.remove(ball1)
        for cell in new:
            if self.true_distance(copy_ball, cell) <= absorb_distance:
                ball_lst.append(cell)
        # print(ball_lst)
        for ball2 in ball_lst:
            if ball2.pos != copy_ball.pos and self.if_will_collide(copy_ball, ball2, None, None, n_tick):
                # print("会撞上", copy_ball.pos)
                # print(ball2.pos)
                copy_ball = self.absorb(copy_ball, ball2)
        return copy_ball

    # 确定危险列表，可以考虑ntick内因吸收合并变大的球
    def dangerous_lst(self, me, allcells, dangerous_distance, absorb_distance, absorb_ntick):
        dangerous_lst = []
        if me in allcells:
            allcells.remove(me)
        for cell in allcells:
            if self.true_distance(me, cell) < dangerous_distance and cell not in dangerous_lst:
                if cell.radius >= me.radius:
                    dangerous_lst.append(cell)
                else:
                    cell2 = self.collide_others(cell, allcells, absorb_distance, absorb_ntick)
                    if cell2.radius >= me.radius:
                        # print("合并危险", cell2.radius)
                        dangerous_lst.append(cell2)
        return dangerous_lst

    # 计算两个小球相撞需要的时间,最大n_tick内相撞
    def collide_time(self, ball1, ball2, theta1, theta2, n_tick):
        for i in range(n_tick):
            if self.if_will_collide(ball1, ball2, theta1, theta2, i):
                return i
        return n_tick

    # 确定危险对象的优先级，找到最危险的
    def most_dangerous(self, me, dangerous_lst, theta1, theta2, n_tick):
        min_collide_time = n_tick
        most_dangerous = None
        for i in dangerous_lst:
            collide_time = self.collide_time(me, i, theta1, theta2, n_tick)
            if collide_time < min_collide_time:
                min_collide_time = collide_time
                most_dangerous = i
        return most_dangerous, min_collide_time

    # 生成theta_lst
    def theta_lst(self, N_possibilities):
        theta_lst = [i * 2 * math.pi / N_possibilities for i in range(0, N_possibilities)]
        return theta_lst

    # 计算ball1向ball2圆心发射的theta
    def face_theta(self, ball1, ball2):
        y_delta = ball2.pos[1] - ball1.pos[1]
        x_delta = ball2.pos[0] - ball1.pos[0]
        if y_delta != 0:
            if y_delta > 0:
                theta = math.atan(x_delta / y_delta) + math.pi
            else:
                theta = math.atan(x_delta / y_delta)
        else:
            if x_delta > 0:
                theta = 3 * math.pi / 2
            else:
                theta = math.pi / 2
        return theta

    # 筛选逃跑的theta
    def filter_escape_theta(self, me, most_dangerous, N_possibilities):
        theta_lst = self.theta_lst(N_possibilities)
        # dx, dy, dvx, dvy = self.relative(me, most_dangerous)
        face_theta = self.face_theta(me, most_dangerous)
        filter_escape_theta = [i for i in theta_lst if not ((face_theta - math.pi/2) < i < (face_theta + math.pi/2))]
        return filter_escape_theta

    # 选择躲避角度，选择一个tick后距离最大的角度
    def escape_theta(self, me, most_dangerous, N_possibilities):
        # theta_lst = self.theta_lst(N_possibilities)
        theta_lst = self.filter_escape_theta(me, most_dangerous, N_possibilities)
        distance_lst = []
        for theta in theta_lst:
            escape_me = self.eject(me, theta)
            escape_me = self.move(escape_me, 1)
            m_most_dangerous = self.move(most_dangerous, 1)
            distance = self.true_distance(escape_me, m_most_dangerous)
            distance_lst.append([theta, distance])
        distance_lst.sort(key=lambda x: x[1], reverse=True)
        best_theta = distance_lst[0][0]
        return best_theta

    # 执行策略函数
    def strategy(self, allcells):
        self.tick += 1
        me = allcells[self.id]
        theta = None

        # 首先判断是否安全
        # 判断自己速度是否太大
        too_fast = (me.veloc[0]**2+me.veloc[1]**2)**0.5 > self.V_absolute_max - 0.5
        # 判断对手会不会吃掉自己
        other_player_threat = allcells[1-self.id].area() > me.area() and self.true_distance(allcells[1-self.id], me) < 100
        if too_fast or other_player_threat:
            self.dangerous_distance = 100
            self.min_collide_time = 25
        # 筛选危险对象
        dangerous_lst = self.dangerous_lst(me, allcells, self.dangerous_distance, self.absorb_distance, self.dangerous_ntick)
        if dangerous_lst:
            # print("危险对象", dangerous_lst)
            most_dangerous, min_collide_time = self.most_dangerous(me, dangerous_lst, theta, None, 10)
            # print("最危险", most_dangerous)
            # print("min collide time", min_collide_time)
            if most_dangerous and min_collide_time < self.min_collide_time:
                self.Best_theta = self.escape_theta(me, most_dangerous, self.N_possibilities)
                return self.Best_theta

        # self.state=0 代表目前在找球
        if self.state == 0:
            # 如果速度很大的话就考虑不动一段时间
            if (me.veloc[0]**2+me.veloc[1]**2)**0.5 > self.V_absolute_max:
                self.Best_theta = None
                self.state = 0
            else:
                # 如果速度在正常范围内，那么找一个能够准确吃球的theta
                self.cnt = 1
                enemy = self.eat_target(me, allcells, self.min_radius)
                # print(enemy)
                if enemy:
                    best_enemy = enemy[0][0]
                    # 根据要吃对象的半径选择ntick1max,半径越大，我们吃球越主动
                    if best_enemy.radius > 20:
                        self.ntick1max = 20
                    elif best_enemy.radius > 10:
                        self.ntick1max = 15
                    else:
                        self.ntick1max = 13
                    # 开始激进
                    if self.tick <= 50:
                        self.ntick1max += 7
                        self.vmax = 1.5
                    elif self.tick > 2500:
                        self.target_lst_length = 1
                        self.vmax = 1
                    else:
                        self.vmax = 1
                    # print("要吃对象", best_enemy)
                    x = self.eat_theta(me, best_enemy, self.vmax, self.ntick1max, self.ntick2max, self.N_possibilities)
                    if x:
                        [self.Best_theta, self.Best_N1, self.Best_N2, new_radius] = x
                    if self.Best_theta:
                        self.state = 1
                    else:
                        self.state = 0
                else:
                    # 如果没有找到合适的theta，那么就不动，继续找球
                    self.Best_theta = None
                    self.state = 0

        # self.state =1 在加速吃球
        elif self.state == 1:
            # 记录已加速tick数
            self.cnt = self.cnt + 1
            if self.cnt >= self.Best_N1:
                self.state = 2
                self.cnt = 0

        # self.state =2 在滑行吃球
        elif self.state == 2:
            # 记录已滑行tick数
            self.Best_theta = None
            if self.cnt >= self.Best_N2:
                self.state = 0
            self.cnt = self.cnt + 1

        return self.Best_theta
