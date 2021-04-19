#!/usr/bin/env python3

from consts import Consts
from cell import Cell

import math


class plan():
    def __init__(self, goal, theta, num, time, food, t0=0):
        self.goal = goal      # 吞噬目标
        self.theta = 3.1415926535 + theta    # 喷射方向，不喷为None
        self.time = time      # 抓捕用时
        self.num = int(num)   # 连续喷射次数
        self.food = food      # 收益（吞噬 - 损失）
        self.efficiency = food*food/(time + t0)   # 效率
        if food < 0:
            self.efficiency *= -1

    def update(self, other):
        if other is not None:
            if self.efficiency < other.efficiency:
                self.goal = other.goal  # 吞噬目标
                self.theta = other.theta  # 喷射方向，不喷为None
                self.time = other.time  # 抓捕用时
                self.num = other.num  # 连续喷射次数
                self.food = other.food  # 收益（吞噬 - 损失）
                self.efficiency = other.efficiency

# 描述一个方案

def solution1(a, b, c): #解出一元二次方程的最小正实根
    if a == 0:
        if b == 0:
            if c == 0:
                return 0
            else:
                return None
        else:
            if c / b < 0:
                return - c / b
            else:
                return None

    delta = b * b - 4 * a * c
    if delta < 0:
        return None
    elif delta == 0:
        x = - b / (2 * a)
        if x >= 0:
            return x
        else:
            return None
    else:
        x1 = (- b + math.sqrt(delta)) / (2 * a)
        x2 = (- b - math.sqrt(delta)) / (2 * a)
        if x2 >= 0:
            return x2
        elif x1 >=0:
            return x1
        else:
            return None

def solution2(a, c, d, e, xmax):  # 解方程ax^4+cx^2+dx+e=0的在0~xmax之间的最小正实根，
    c1 = c / a
    d1 = d / a
    e1 = e / a
    x = 0.5
    while x <= xmax:
        if x**4 + c1*x**2 + d1 * x + e1 > 0:
            break
        x += 5
    if x > xmax+0.5:
        x = xmax+0.5
        if x ** 4 + c1 * x ** 2 + d1 * x + e1 < 0:
            return None
    x -= 1
    while x**4 + c1*x**2 + d1 * x + e1 > 0:
        x -= 1
    return x + 1


def solution3(a, v, r, d, cos, xmax):
    t = solution2(0.25 * a * a, a * r - v * v, v * v + 2 * v * d * cos, r * r - 0.25 * v * v - d * d - v*d*cos, xmax=xmax+0.5)
    if t is None:
        return None
    return t - 0.5

def solution4(a, v ,t1, r, d, cos):
    t = solution1(v * v - a * a * t1 * t1, - 2 * a * t1 * r - 2 * v * d * cos, d * d - r * r)
    if t is None:
        return None
    if t >= t1:
        return t
    if abs(t1 * a - v) < 1e-6:
        return None
    t2 = (2 * a * t1 * r + 2 * v * d * cos) / (v * v - a * a * t1 * t1) - t
    if t2 >= t1:
        return t2
    else:
        return None

def calculate_angle(x1, y1, x2, y2):   # 计算夹角，r1在r2的顺时针方向为正
    if (x1*y2 - x2*y1) < 0:
        return math.acos((x1 * x2 + y1 * y2) / (math.sqrt(x1 * x1 + y1 * y1) * math.sqrt(x2 * x2 + y2 * y2)))
    else:
        return -math.acos((x1*x2+y1*y2) / (math.sqrt(x1*x1 + y1*y1)*math.sqrt(x2*x2 + y2*y2)))

def cos_laws(a, b, theta):   # 余弦定理计算对边
    return math.sqrt(a * a + b * b - 2 * a * b * math.cos(theta))

def cos_laws_angle(a, b, c):
    if c > a + b:
        if c < a + b + 5e-3:
            return 3.1415926535
        else:
            return None
    if a > c + b:
        if a < c + b + 5e-3:
            return 0
        else:
            return None
    if b > a + c:
        if b < a + c + 5e-3:
            return 0
        else:
            return None
    return math.acos((a * a + b * b - c * c) / (2 * a * b))

def conduct_plan(difference_angle, theta0, distance, delta_v, v_change, r, time, m0, m1, n1, t0):
    # 规划固定喷射次数的计划， 如果未来得及喷射足够的次数就撞上，也记录计划，若无法抓到，则返回None
    # print(distance, delta_v, difference_angle, v_change, time, r)
    if time == 0:
        return None
    PI = 3.1415926535
    epsilon = 1e-7
    a = v_change / time
    angle_scale = math.asin(r / distance)
    goal_angle = angle_scale
    if angle_scale > abs(difference_angle) + 1e-5:
        s = distance * math.cos(difference_angle) - math.sqrt(r * r - (distance * math.sin(difference_angle))**2)
        if s > time * (delta_v + 0.5 * v_change):
            time1 = solution1(0.5 * a, delta_v, - s)
            num = int(time1)
        else:
            time1 = time + (s - time * (delta_v + 0.5 * v_change)) / (delta_v + v_change)
            num = time
        return plan(n1, theta0 + difference_angle, num, time1, m1 - m0 * (1 - (1 - Consts["EJECT_MASS_RATIO"])**num), t0)
    alpha = abs(difference_angle) - goal_angle
    if alpha > PI / 2:
        min_v = delta_v
    else:
        min_v = delta_v * math.sin(abs(difference_angle) - goal_angle)
    if min_v >= v_change:
        return None


    '''
    beta = math.asin(math.sin(alpha) * delta_v / v_change)
    new_veloc = cos_laws(v_change, delta_v, PI - beta - alpha)
    v_bar = cos_laws(0.5 * v_change, new_veloc, beta)
    half_alpha = math.asin(math.sin(beta) * 0.5 * v_change / v_bar)
    correct_angle = math.atan(math.sin(half_alpha) * v_bar * time / (distance * math.cos(goal_angle)))
    goal_angle = goal_angle - correct_angle
    alpha = abs(difference_angle) - goal_angle
    if alpha > PI / 2:
        min_v = delta_v
    else:
        min_v = delta_v * math.sin(abs(difference_angle) - goal_angle)
    if min_v >= v_change:
        return None
    beta = math.asin(math.sin(alpha) * delta_v / v_change)
    new_veloc = cos_laws(v_change, delta_v, PI - beta - alpha)
    v_bar = cos_laws(0.5 * v_change, new_veloc, beta)
    half_alpha = math.asin(math.sin(beta) * 0.5 * v_change / v_bar)
    if difference_angle > 0:
        time1 = meet(new_veloc * math.cos(theta0 + goal_angle), new_veloc * math.sin(theta0 + goal_angle), \
                     distance * math.cos(theta0) - v_bar * time * math.cos(theta0 + goal_angle + half_alpha), \
                     distance * math.sin(theta0) - v_bar * time * math.sin(theta0 + goal_angle + half_alpha), \
                     math.sqrt(m0 * (1 - Consts["EJECT_MASS_RATIO"])**time) + math.sqrt(m1))

        if time1 is not None:
            return plan(n1, theta0 + goal_angle - beta, time, time + time1, \
                        m1 - m0 * (1 - (1 - Consts["EJECT_MASS_RATIO"])**time))
    else:
        time1 = meet(new_veloc * math.cos(theta0 - goal_angle), new_veloc * math.sin(theta0 - goal_angle), \
                     distance * math.cos(theta0) - v_bar * time * math.cos(theta0 - goal_angle - half_alpha), \
                     distance * math.sin(theta0) - v_bar * time * math.sin(theta0 - goal_angle - half_alpha), \
                     math.sqrt(m0 * (1 - Consts["EJECT_MASS_RATIO"]) ** time) + math.sqrt(m1))
        if time1 is not None:
            return plan(n1, theta0 - goal_angle + beta, time, time + time1, \
                        m1 - m0 * (1 - (1 - Consts["EJECT_MASS_RATIO"]) ** time))
    '''
    new_r = min(0.8 * r, r - 0.8)
    time1 = solution4(a, delta_v, time, new_r - 0.5 * a * time * time + 0.5 * a * time, distance, math.cos(difference_angle))
    if time1 is None:
        return None
    # time1 = solution3(v_change / time, delta_v, new_r - 0.25 * v_change / time, distance, math.cos(difference_angle), time)
    # time1 = solution2(0.25 * (v_change / time)**2, new_r * v_change / time - delta_v*delta_v, \
    #                  2*distance * delta_v * math.cos(difference_angle), new_r * new_r - distance * distance, \
    #                  xmax=time)
    time1 = int(time1) + 1
    new_dis = cos_laws(distance, delta_v * time1, math.cos(difference_angle))
    tmp_theta = cos_laws_angle(distance, new_dis, delta_v * time1)
    food = m1 - m0 * (1 - (1 - Consts["EJECT_MASS_RATIO"])**time)
    if difference_angle < 0:
        tmp_theta = -tmp_theta
    return plan(n1, theta0 - tmp_theta, time, time1, food, t0)

def theta(x, y):
    if y > 0:
        return math.acos(x / math.sqrt(x*x + y*y))
    else:
        return 2 * 3.1415926535 - math.acos(x / math.sqrt(x*x + y*y))

def meet(dvx, dvy, dx, dy, r):
    return solution1(dvx*dvx + dvy*dvy, - 2 * (dy * dvy + dx * dvx), dx * dx + dy * dy - r * r)

class Player():
    def __init__(self, id, args=None):
        self.id = id
        self.frame_count = 0
        self.v_change = Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"] * Consts["FRAME_DELTA"]
        self.eject_radius_ratio = math.sqrt(1 - Consts["EJECT_MASS_RATIO"])
        self.allcells = []
        self.plan = None
        # self.goal_cell = Cell()
        self.epsilon = 1e-7
        self.vx = 0
        self.vy = 0
        self.r = Consts["DEFAULT_RADIUS"]
        self.theta = None
        self.mass_sum = 0
        self.max_v = 15
        self.all_events = None
        self.last_enemy_radius = Consts["DEFAULT_RADIUS"]
        self.last_enemy_change = True
        self.last_update = -100
        self.myself = None
        self.enemy = None
        self.cost0 = 0
        self.cost_time = 0

    def strategy(self, allcells):
        self.frame_count += 1

        # decide to or not to update event list
        if self.frame_count < 320:
            event_update_time = 10
        else:
            event_update_time = 5
        event_update_flag = False
        this_enemy_change = False
        if self.last_enemy_radius != allcells[1-self.id].radius:
            self.last_enemy_radius = allcells[1-self.id].radius
            this_enemy_change = True
        if self.last_enemy_change and not this_enemy_change:
            event_update_flag = True                # When enemy stop to eject
        self.last_enemy_change = this_enemy_change
        if self.frame_count - self.last_update < 10:
            event_update_flag = False
        if self.frame_count - self.last_update >= event_update_time:
            event_update_flag = True
        if event_update_flag:
            self.last_update = self.frame_count
            self.all_events = EventTree(allcells, self.frame_count, 40)

        self.allcells = allcells
        number = len(self.allcells)
        for i in range(number):
            self.allcells[i].veloc[0] *= Consts["FRAME_DELTA"]
            self.allcells[i].veloc[1] *= Consts["FRAME_DELTA"]

        self.myself = allcells[self.id]
        self.enemy = allcells[1-self.id]


        if self.mass_sum == 0:
            for i in range(number):
                self.mass_sum += self.allcells[i].radius ** 2
        if self.allcells[self.id].radius ** 2 > (self.mass_sum / 2):
            return None

        if self.plan is not None:

            need_change = False
            '''if self.plan.goal < number:
                if self.allcells[self.plan.goal].distance_from(self.goal_cell) < 0.5 * self.goal_cell.radius:
                    need_change = False
            if need_change:
                for i in range(number):
                    if (self.allcells[i].distance_from(self.goal_cell) < 0.5 * self.goal_cell.radius):
                        self.plan.goal = i
                        need_change = False
                        break'''
            if self.plan.num > 0:
                if abs(self.allcells[self.id].radius - self.r ** self.eject_radius_ratio) > self.epsilon:
                    need_change = True
            elif abs(self.allcells[self.id].radius - self.r) > self.epsilon:
                need_change = True
            if self.plan.time < 0:
                self.cost0 = 0
                self.cost_time = 0
                # print(1)
            if abs(self.allcells[self.id].radius - self.r) > self.r * 0.1:
                self.cost0 = 0
                self.cost_time = 0
                # print(2)
            goal_dead =True
            for i in range(number):
                if self.allcells[i].id == self.plan.goal:
                    goal_dead = False
            if goal_dead:
                self.cost0 = 0
                self.cost_time = 0
                # print(3)
            if (((self.plan.time < 8) and (self.plan.time > 7)) or (self.plan.time < - 0.9)) or need_change:
                self.plan = None
                self.make_plan()
            else:
                if self.plan.num > 0:
                    self.plan.num -= 1
                self.plan.time -= 1
        else:
            self.make_plan()
        self.vx = self.allcells[self.id].veloc[0]
        self.vy = self.allcells[self.id].veloc[1]
        self.r = self.allcells[self.id].radius
        # if self.plan is not None:
            # self.plan.goal_cell = self.allcells[self.plan.goal]
            # print(self.plan.goal, self.plan.num, self.plan.food, self.plan.time+self.cost_time, self.id)
        if self.plan is None:
            disrupt_state, danger = self.all_events.predict_disrupt(self.myself, [], self.frame_count, self.frame_count+40)
            if danger:
                return self.avoid(disrupt_state)

        # predict enemy move
        mystate = State(self.myself.id, self.myself.pos, self.myself.veloc, self.myself.radius, self.frame_count)
        enemystate = State(self.enemy.id, self.enemy.pos, self.enemy.veloc, self.enemy.radius, self.frame_count)
        mystate.veloc[0] /= Consts["FRAME_DELTA"]
        mystate.veloc[1] /= Consts["FRAME_DELTA"]
        enemystate.veloc[0] /= Consts["FRAME_DELTA"]
        enemystate.veloc[1] /= Consts["FRAME_DELTA"]
        if mystate < enemystate:
            collision_frame = predict_collision(mystate, enemystate, 40)
            if collision_frame:
                self.plan = None
                return self.avoid(enemystate)

        self.cost_time += 1
        if self.plan is None:
            self.theta = None
            return None
        elif self.plan.num == 0:
            self.theta = None
            return None
        else:
            self.theta = self.plan.theta
            self.cost0 += Consts["EJECT_MASS_RATIO"] * self.allcells[self.id].radius ** 2
            return theta(math.sin(self.plan.theta), math.cos(self.plan.theta))

    def make_plan(self):
        # print("MP Frame:", self.frame_count)
        r0 = self.allcells[self.id].radius
        number = len(self.allcells)
        self.plan = None
        for i in range(2, number):
            if i == self.id:
                continue
            if (self.allcells[i].radius < (0.95 ** 0.5) * r0) and (self.allcells[i].radius > 0.15 * r0):
                tmp = self.catchone_safely(self.id, i)
                # print(tmp)
                if tmp is not None:
                    if tmp.time < 100:
                        if self.plan is not None:
                            self.plan.update(tmp)
                        else:
                            self.plan = tmp
        '''
        if self.plan is not None:
            self.goal_cell = self.allcells[self.plan.goal]
        '''

    def catchone_safely(self, n0, n1):
        attempt = self.catchone(n0, self.allcells[n1].id, self.allcells[n1])
        catch_state = None
        if attempt is None:
            # we assume the target will change after a while and try once more
            assume_state = self.all_events.predict_result_state(self.allcells[n1].id, self.frame_count+30)
            if assume_state is None:
                return None
            if assume_state.radius != self.allcells[n1].radius:
                attempt, catch_state = self.try_once_more(n0, n1, assume_state)
                if attempt is None:
                    return None
            else:
                return None

        catch_state = self.all_events.predict_state(attempt.goal, self.frame_count+int(attempt.time)+1)
        if catch_state == None or catch_state.dead:
            # when the target will die, change a target
            return None
        if catch_state.radius != self.allcells[n1].radius:
            attempt, catch_state = self.try_once_more(n0, n1, catch_state)
            if attempt is None:
                return None

        excepts = [attempt.goal]
        '''
        is_colliding = self.all_events.is_colliding(attempt.goal, self.frame_count+int(attempt.time)+1)
        if is_colliding:
            # when we hit the target, it is colliding with other cells
            if self.all_events.predict_state(is_colliding.id[0], self.frame_count+int(attempt.time)+1).radius > self.myself.radius * (1 - Consts["EJECT_MASS_RATIO"]) ** (attempt.num*0.5):
                # if the biggest cell in the collsion is larger than us, change a target
                return None
            else:
                # otherwise, do nothing
                attempt.food = attempt.food + math.pi * (is_colliding.result[0].radius * is_colliding.result[0].radius - catch_state.radius * catch_state.radius)
                attempt.efficiency = attempt.food/attempt.time
                excepts = excepts + is_colliding.id
        '''

        disrupt_state, danger = self.all_events.predict_disrupt(self.myself, excepts, self.frame_count, self.frame_count+int(attempt.time)+1, attempt.num, attempt.theta, True)
        if danger:
            # when being collided, we change a target
            return None

        return attempt

    def try_once_more(self, n0, n1, catch_state):
        if catch_state.radius > self.myself.radius * 0.95 ** 0.5:
            # when the target will become too large, change a target
            return None, None
        else:
            # if we still can try to eat it, make another try based on new state
            new_cell1 = catch_state.update(self.frame_count)
            new_cell1.veloc[0] *= Consts["FRAME_DELTA"]
            new_cell1.veloc[1] *= Consts["FRAME_DELTA"]
            attempt = self.catchone(n0, new_cell1.id, new_cell1)
            if attempt is None:
                return None, None
            new_catch_state = self.all_events.predict_state(attempt.goal, self.frame_count+int(attempt.time)+1)
            if catch_state.radius == new_catch_state.radius and not new_catch_state.dead:
                return attempt, new_catch_state
            else:
                # if the state when it's catched doesn't fit our guess, change a target
                return None, None

    def catchone(self, n0, n1, cell1):
        delta_vx = self.allcells[n0].veloc[0] - cell1.veloc[0]
        delta_vy = self.allcells[n0].veloc[1] - cell1.veloc[1]
        delta_v = math.sqrt(delta_vx * delta_vx + delta_vy * delta_vy)
        final_plan = None
        list = []
        mass_ratio = (cell1.radius / self.allcells[n0].radius) ** 2
        m0 = self.allcells[n0].radius**2
        m1 = cell1.radius ** 2
        if self.cost0 > m1:
            return None
        max_eject0 = int(math.log(max(1 - (m1 - self.cost0) / m0, mass_ratio), 1 - Consts["EJECT_MASS_RATIO"]))
        for i in range(-1, 2):
            for j in range(-1, 2):
                list.append((math.sqrt((cell1.pos[0] - self.allcells[n0].pos[0] + Consts["WORLD_X"] * i)**2+ \
                                  (cell1.pos[1] - self.allcells[n0].pos[1] + Consts["WORLD_Y"] * j)**2), i, j))
        list = sorted(list, key=lambda x: x[0])

        for x in list:
            delta_x = cell1.pos[0] - self.allcells[n0].pos[0] + Consts["WORLD_X"] * x[1]
            delta_y = cell1.pos[1] - self.allcells[n0].pos[1] + Consts["WORLD_Y"] * x[2]
            distance = x[0]
            if distance < self.allcells[n0].radius + cell1.radius:
                return plan(n1, 0, 0, 1e-7, cell1.radius**2)
            if final_plan is not None:
                if final_plan.efficiency > ((m1 - self.cost0)**2/(self.cost_time + distance / min(self.max_v, max_eject0 * self.v_change + delta_v))):
                    continue
            angle_scale = math.asin((self.allcells[n0].radius + cell1.radius) / distance) - self.epsilon
            difference_angle = calculate_angle(delta_x, delta_y, delta_vx, delta_vy)
            max_eject = max_eject0
            if angle_scale > abs(difference_angle):
                time = meet(delta_vx, delta_vy, delta_x, delta_y, self.allcells[n0].radius + cell1.radius)
                if final_plan is None:
                    final_plan = plan(n1, 0, 0, time, m1 - self.cost0, self.cost_time)
                else:
                    final_plan.update(plan(n1, 0, 0, time, m1 - self.cost0, self.cost_time))
                max_eject = min(int((self.max_v - delta_v) / self.v_change), max_eject)
            else:
                max_eject = min(int(cos_laws(self.max_v, delta_v, difference_angle) / self.v_change), max_eject)
            if max_eject <= 1:
                continue
            time1 = solution3(self.v_change, delta_v, \
                              self.allcells[n0].radius * self.eject_radius_ratio ** max_eject + cell1.radius - 0.25 * self.v_change, \
                              distance, math.cos(difference_angle), max_eject)
            if time1 is not None:
                new_dis = cos_laws(distance, delta_v * time1, math.cos(difference_angle))
                tmp_theta = cos_laws_angle(distance, new_dis, delta_v * time1)
                food = cell1.radius ** 2 - self.cost0 - self.allcells[n0].radius**2*(1 - (1 - Consts["EJECT_MASS_RATIO"]) ** int(time1))
                if difference_angle < 0:
                    tmp_theta = -tmp_theta
                if final_plan is None:
                    final_plan = plan(n1, theta(delta_x, delta_y) - tmp_theta, time1, time1, food, self.cost_time)
                else:
                    final_plan.update(plan(n1, theta(delta_x, delta_y) - tmp_theta, time1, time1, food, self.cost_time))
                max_eject = min(max_eject, int(time1))
            max_eject_plan = conduct_plan(difference_angle, theta(delta_x, delta_y), distance, delta_v, \
                                          self.v_change * max_eject, \
                                          self.allcells[n0].radius * self.eject_radius_ratio ** max_eject + cell1.radius, max_eject, \
                                          self.allcells[n0].radius ** 2, m1 - self.cost0, n1, self.cost_time)
            if max_eject_plan is None:
                continue
            max_eject = max_eject_plan.num
            if final_plan is None:
                final_plan = max_eject_plan
            else:
                final_plan.update(max_eject_plan)
            if max_eject <= 1:
                continue
            k = int(math.sqrt(max_eject))
            n = k
            tmp = conduct_plan(difference_angle, theta(delta_x, delta_y), distance, delta_v, \
                               self.v_change * n, \
                               self.allcells[n0].radius * self.eject_radius_ratio ** n + cell1.radius, n, \
                               m0, m1 - self.cost0, n1, self.cost_time)
            while tmp is None:
                n += k
                if n > max_eject:
                    break
                tmp = conduct_plan(difference_angle, theta(delta_x, delta_y), distance, delta_v, \
                                   self.v_change * n, \
                                   self.allcells[n0].radius * self.eject_radius_ratio ** n + cell1.radius, \
                                   n, m0, m1 - self.cost0, n1, self.cost_time)
            if n > max_eject:
                continue
            tmp_eff = tmp.efficiency
            final_plan.update(tmp)
            n += k
            while n <= max_eject:
                tmp = conduct_plan(difference_angle, theta(delta_x, delta_y), distance, delta_v, \
                                   self.v_change * n, \
                                   self.allcells[n0].radius * self.eject_radius_ratio ** n + cell1.radius, \
                                   n, m0, m1 - self.cost0, n1, self.cost_time)
                if tmp is None:
                    break
                final_plan.update(tmp)
                if tmp.efficiency < tmp_eff:
                    break
                tmp_eff = tmp.efficiency
                n += k
            if k < 2:
                continue
            n = n - k
            for i in range(max(n - k + 2, 1), min(max_eject, n + k - 1)):
                tmp = conduct_plan(difference_angle, theta(delta_x, delta_y), distance, delta_v, \
                                   self.v_change * i, \
                                   self.allcells[n0].radius * self.eject_radius_ratio ** i + cell1.radius, i, \
                                   m0, m1 - self.cost0, n1, self.cost_time)
                final_plan.update(tmp)
            '''
            if tmp is None:
                continue
            if tmp.efficiency > tmp_eff:
                final_plan.update(tmp)
                n = n + 1 - int(k / 2)
                tmp = conduct_plan(difference_angle, theta(delta_x, delta_y), distance, \
                                   math.sqrt(delta_vx * delta_vx + delta_vy * delta_vy), \
                                   self.v_change * n, \
                                   self.allcells[n0].radius * self.eject_radius_ratio ** n + cell1.radius, \
                                   n, self.allcells[n0].radius ** 2, cell1.radius ** 2, n1)
                final_plan.update(tmp)

            else:
                n = n + 1 + int(k / 2)
                tmp = conduct_plan(difference_angle, theta(delta_x, delta_y), distance, \
                                   math.sqrt(delta_vx * delta_vx + delta_vy * delta_vy), \
                                   self.v_change * n, \
                                   self.allcells[n0].radius * self.eject_radius_ratio ** n + cell1.radius, \
                                   n, self.allcells[n0].radius ** 2, cell1.radius ** 2, n1)
                final_plan.update(tmp)
            '''
        return final_plan

    def avoid(self, target_state):
        dx = - target_state.pos[0] + self.allcells[self.id].pos[0]
        dy = - target_state.pos[1] + self.allcells[self.id].pos[1]
        dvx = - target_state.veloc[0] + self.allcells[self.id].veloc[0] / Consts["FRAME_DELTA"]
        dvy = - target_state.veloc[1] + self.allcells[self.id].veloc[1] / Consts["FRAME_DELTA"]
        r = target_state.radius + self.allcells[self.id].radius

        through_wall = [False, False]

        collision_time = solve_collision_time(dx, dy, dvx, dvy, r)
        # consider going through four borders up to once
        if dx >= 0:
            mx = dx - Consts["WORLD_X"]
        else:
            mx = dx + Consts["WORLD_X"]
        new_time = solve_collision_time(mx, dy, dvx, dvy, r)
        if collision_time == None or (new_time != None and new_time < collision_time):
            collision_time = new_time
            through_wall = [True, False]
        if dy >= 0:
            my = dy - Consts["WORLD_Y"]
        else:
            my = dy + Consts["WORLD_Y"]
        new_time = solve_collision_time(dx, my, dvx, dvy, r)
        if collision_time == None or (new_time != None and new_time < collision_time):
            collision_time = new_time
            through_wall = [False, True]
        new_time = solve_collision_time(mx, my, dvx, dvy, r)
        if collision_time == None or (new_time != None and new_time < collision_time):
            collision_time = new_time
            through_wall = [True, True]

        if through_wall[0]:
            dx = mx
        if through_wall[1]:
            dy = my
        dx = -dx
        dy = -dy
        ratio_vr = math.sqrt((dvx*dvx + dvy*dvy)/(dx*dx + dy*dy))
        r_theta = theta(dx, dy)
        v_theta = theta(dvx, dvy)
        d_theta = r_theta - v_theta
        if d_theta > math.pi:
            d_theta -= 2 * math.pi
        if d_theta < -math.pi:
            d_theta += 2 * math.pi
        if d_theta > 0:
            v_theta += 0.5*math.pi
        else:
            v_theta -= 0.5*math.pi
        '''
        turn = -1
        if (dvx * dy - dvy * dx) >= 0:
            turn = 1
        fx = - 2 * dx / math.sqrt(dx*dx + dy*dy) + turn * dvy / math.sqrt(dvx*dvx + dvy*dvy)
        fy = - 2 * dy / math.sqrt(dx*dx + dy*dy) - turn * dvx / math.sqrt(dvx*dvx + dvy*dvy)
        '''
        fx = 2 * math.cos(r_theta) + math.cos(v_theta)
        fy = 2 * math.sin(r_theta) + math.sin(v_theta)
        theta0 = theta(fx ,fy)
        return theta(math.sin(theta0), math.cos(theta0))

# 以下为碰撞预测部分

class State():
    # indicate a cell at a particular frame
    def __init__(self, id = None, pos = [0, 0], veloc = [0, 0], radius = 5, frame = 0, dead = False):
        # ID to judge Player or free particle
        self.id = id
        # Variables to hold current position
        self.pos = [0, 0]
        self.pos[0] = pos[0]
        self.pos[1] = pos[1]
        # Variables to hold current velocity
        self.veloc = [0, 0]
        self.veloc[0] = veloc[0]
        self.veloc[1] = veloc[1]
        # Variables to hold size
        self.radius = radius
        # Variables to hold frame of the state
        self.frame = frame
        # Indicate dead or not
        self.dead = dead

    def update(self, target_frame):
        x = self.pos[0] + self.veloc[0] * Consts["FRAME_DELTA"] * (target_frame - self.frame)
        y = self.pos[1] + self.veloc[1] * Consts["FRAME_DELTA"] * (target_frame - self.frame)
        while x < 0:
            x += Consts["WORLD_X"]
        while x > Consts["WORLD_X"]:
            x -= Consts["WORLD_X"]
        while y < 0:
            y += Consts["WORLD_Y"]
        while y > Consts["WORLD_Y"]:
            y -= Consts["WORLD_Y"]
        return State(self.id, [x,y], self.veloc, self.radius, target_frame, self.dead)

    def __lt__(self, state):
        # judge if self will be eaten by state
        if self.radius < state.radius:
            return True
        elif self.radius == state.radius and self.id > state.id:
            return True
        else:
            return False

class Event():
    def __init__(self, id, frame):
        # id indicates which cells collide, the survivor is put in pos 0
        self.id = id
        # frame indicates when they collides
        self.frame = frame
        # next includes the next collisions happens on corresponding cells and the next collision in the world
        self.next = [None for _ in id] + [None]
        # prev includes the prev collisions happens on corresponding cells and the next collision in the world
        self.prev = [None for _ in id] + [None]
        # result tells the state of collided cell after collision
        self.result = [None for _ in id]

    def id_to_pos(self, id):
        if id == -1:
            return id
        else:
            return self.id.index(id)

    def getNext(self, id):
        return self.next[self.id_to_pos(id)]

    def getPrev(self, id):
        return self.prev[self.id_to_pos(id)]

    def setNext(self, newnext, id):
        self.next[self.id_to_pos(id)] = newnext

    def setPrev(self, newprev, id):
        self.prev[self.id_to_pos(id)] = newprev

    def getRes(self, id):
        return self.result[self.id_to_pos(id)]

    def setRes(self, newres, id):
        self.result[self.id_to_pos(id)] = newres

    def __lt__(self, event):
        return self.frame < event.frame
    def __gt__(self, event):
        return self.frame > event.frame
    def __le__(self, event):
        return self.frame <= event.frame
    def __ge__(self, event):
        return self.frame >= event.frame
    def __eq__(self, event):
        if event is None:
            return False
        return self.frame == event.frame and self.id == event.id
    def __ne__(self, event):
        if event is None:
            return True
        return self.frame != event.frame or self.id != event.id

def solve_collision_time(dx, dy, dvx, dvy, r):
    a = dvx*dvx + dvy*dvy
    b = 2*(dy*dvy + dx*dvx)
    c = dx*dx + dy*dy - r*r

    # solve the collision equation
    if a == 0:
        if c <= 0:
            return 0
        else:
            return None

    delta = b * b - 4 * a * c
    if delta < 0:
        return None
    elif delta == 0:
        x = - b / (2 * a)
        if x > 0 and int(x/Consts["FRAME_DELTA"]) == x/Consts["FRAME_DELTA"]:
            return x
        else:
            return None
    else:
        x1 = (- b + math.sqrt(delta)) / (2 * a)
        x2 = (- b - math.sqrt(delta)) / (2 * a)
        if x1 >= Consts["FRAME_DELTA"]:
            if x2 >= 0:
                return x2
            else:
                return 0
        else:
            return None

def predict_collision(cell1, cell2, target_frame):
    # predict if there will be a collision not after target_frame
    dx = cell1.pos[0] - cell2.pos[0]
    dy = cell1.pos[1] - cell2.pos[1]
    dvx = cell1.veloc[0] - cell2.veloc[0]
    dvy = cell1.veloc[1] - cell2.veloc[1]
    r = cell1.radius + cell2.radius
    collision_time = solve_collision_time(dx, dy, dvx, dvy, r)

    # consider going through four borders up to once
    if dx >= 0:
        mx = dx - Consts["WORLD_X"]
    else:
        mx = dx + Consts["WORLD_X"]
    new_time = solve_collision_time(mx, dy, dvx, dvy, r)
    if collision_time == None or (new_time != None and new_time < collision_time):
        collision_time = new_time
    if dy >= 0:
        my = dy - Consts["WORLD_Y"]
    else:
        my = dy + Consts["WORLD_Y"]
    new_time = solve_collision_time(dx, my, dvx, dvy, r)
    if collision_time == None or (new_time != None and new_time < collision_time):
        collision_time = new_time
    new_time = solve_collision_time(mx, my, dvx, dvy, r)
    if collision_time == None or (new_time != None and new_time < collision_time):
        collision_time = new_time

    # ensure the collision happens before target_frame
    if collision_time == None or int(collision_time/Consts["FRAME_DELTA"]) + 1 > target_frame:
        return None
    else:
        return int(collision_time/Consts["FRAME_DELTA"]) + 1

class EventTree():
    def __init__(self, cell_list, frame_now , target_frame_delta):
        self.initial_frame = frame_now
        self.target_frame = frame_now + target_frame_delta

        # the first and the last collision of all main cells
        self.id_heads = [None for _ in range(cell_list[-1].id + 51)]
        self.id_tails = [None for _ in range(cell_list[-1].id + 51)]

        # the first and the last collision in the time considered
        self.id_heads.append(None)
        self.id_tails.append(None)

        # the initial states of all cells
        self.initial_states = [None for _ in range(cell_list[-1].id + 50)]

        # predict all possible collision from their initial states
        self.init_events(cell_list)

        # review all these events and predict new possible ones
        self.review_events()

    def update(self, new_target_frame_delta):
        # predict all possible collision from their initial states
        start_event = self.update_events(new_target_frame_delta)

        # review all these events and predict new possible ones
        if start_event:
            self.review_events(start_event)

    # USE FOR DEBUGGING
    def print_events(self):
        scan_node = self.id_heads[-1]
        print("-------------START----------------")
        while scan_node != None:
            print(scan_node.frame, scan_node.id, scan_node.result[0].pos)
            scan_node = scan_node.getNext(-1)
        print("--------------END-----------------")

    def init_events(self, cell_list):
        # store all possible events temporarily
        temp_list = []

        # evaluate every pair
        for i in range(2, len(cell_list)):
            self.initial_states[cell_list[i].id] = State(cell_list[i].id, cell_list[i].pos, cell_list[i].veloc, cell_list[i].radius, self.initial_frame)

            for j in range(i+1, len(cell_list)):
                collision_frame_delta = predict_collision(cell_list[i], cell_list[j], self.target_frame - self.initial_frame)
                if collision_frame_delta:
                    if cell_list[i].radius >= cell_list[j].radius:
                        temp_list.append(Event([cell_list[i].id, cell_list[j].id], self.initial_frame + collision_frame_delta))
                    else:
                        temp_list.append(Event([cell_list[j].id, cell_list[i].id], self.initial_frame + collision_frame_delta))
                    for id in temp_list[-1].id:
                        self.add_event_id(temp_list[-1], id)

        # sort the collisions by their frame
        temp_list.sort()         # SHOULD WE KEEP ID SORTED ?

        # link them
        storing_node = None
        for event in temp_list:
            if self.id_heads[-1] == None:
                storing_node = event
                self.id_heads[-1] = storing_node
            else:
                storing_node.setNext(event,-1)
                storing_node.getNext(-1).setPrev(storing_node,-1)
                storing_node = storing_node.getNext(-1)
        if storing_node:
            self.id_tails[-1] = storing_node

    def review_events(self, start_event = None):
        # ensure all the collisions are valid
        scan_node = self.id_heads[-1]
        if start_event:
            scan_node = start_event
        # save all events happened meanwhile
        predict_node = scan_node
        while scan_node != None:
            # examine if there is a multi-cell collision
            contemporary_events = [scan_node]
            #DE contemporary_ids = [scan_node.id]
            mc_scan_node = scan_node.getNext(-1)
            while mc_scan_node != None and mc_scan_node <= scan_node:
                contemporary_events.append(mc_scan_node)
                #DE contemporary_ids.append(mc_scan_node.id)
                mc_scan_node = mc_scan_node.getNext(-1)
            if len(contemporary_events) > 1:
                self.merge(contemporary_events)

            # give the result of this collision
            self.calc_result(scan_node)

            # remove all invalid events
            for id in scan_node.id:
                while self.id_tails[id] != scan_node:
                    self.invalid_all(self.id_tails[id])

            # predict possible collision of the survivor after all events at this frame has a result
            if scan_node.getNext(-1) == None or scan_node.getNext(-1) > scan_node:
                while predict_node and predict_node <= scan_node:
                    main_state = predict_node.result[0]
                    for id in range(2, len(self.initial_states)):
                        if id == main_state.id:
                            continue
                        id_state = self.predict_result_state(id, main_state.frame)
                        if id_state == None or id_state.dead:
                            continue
                        collision_frame_delta = predict_collision(main_state, id_state, self.target_frame - main_state.frame)
                        if collision_frame_delta:
                            new_event = None
                            if id_state < main_state:
                                new_event = Event([main_state.id, id_state.id], main_state.frame + collision_frame_delta)
                            else:
                                new_event = Event([id_state.id, main_state.id], main_state.frame + collision_frame_delta)
                            for id in new_event.id:
                                self.add_event_id(new_event, id)
                            self.add_event_id(new_event, -1)
                    predict_node = predict_node.getNext(-1)

            # prepare for the next lap
            scan_node = scan_node.getNext(-1)

    def update_events(self, new_target_frame_delta):
        # predict all possible events in new_target_frame_delta based on precedent prediction
        old_target_frame = self.target_frame
        self.target_frame += new_target_frame_delta

        # store all possible events temporarily
        temp_list = []

        # get new initial states
        cell_list = [None, None]
        for id in range(len(self.initial_states)):
            cell_state = self.predict_result_state(id, old_target_frame)
            if cell_state and not cell_state.dead:
                cell_list.append(cell_state)

        # evaluate every pair
        for i in range(2, len(cell_list)):
            for j in range(i+1, len(cell_list)):
                collision_frame_delta = predict_collision(cell_list[i], cell_list[j], self.target_frame - old_target_frame)
                if collision_frame_delta:
                    if cell_list[i] < cell_list[j]:
                        temp_list.append(Event([cell_list[i].id, cell_list[j].id], old_target_frame + collision_frame_delta))
                    else:
                        temp_list.append(Event([cell_list[j].id, cell_list[i].id], old_target_frame + collision_frame_delta))
                    for id in temp_list[-1].id:
                        self.add_event_id(temp_list[-1], id)

        # sort the collisions by their frame
        temp_list.sort()         # SHOULD WE KEEP ID SORTED ?

        # link them
        storing_node = None
        for event in temp_list:
            if self.id_heads[-1] == None:
                storing_node = event
                self.id_heads[-1] = storing_node
            else:
                if storing_node == None:
                    storing_node = self.id_tails[-1]
                storing_node.setNext(event,-1)
                storing_node.getNext(-1).setPrev(storing_node,-1)
                storing_node = storing_node.getNext(-1)
        if storing_node:
            self.id_tails[-1] = storing_node

        if len(temp_list):
            return temp_list[0]
        else:
            return None

    def add_event_id(self, event, id):
        # add the event to corresponding id_head
        if self.id_heads[id] == None or event < self.id_heads[id]:
            if self.id_heads[id] == None:
                self.id_heads[id] = event
                self.id_tails[id] = self.id_heads[id]
            else:
                event.setNext(self.id_heads[id],id)
                self.id_heads[id].setPrev(event,id)
                self.id_heads[id] = event
        elif event >= self.id_tails[id]:
            self.id_tails[id].setNext(event,id)
            self.id_tails[id].getNext(id).setPrev(self.id_tails[id],id)
            self.id_tails[id] = self.id_tails[id].getNext(id)
        else:
            scan_node = self.id_heads[id]
            while scan_node != None:
                if event < scan_node:
                    new_node = event
                    new_node.setNext(scan_node,id)
                    new_node.setPrev(scan_node.getPrev(id),id)
                    new_node.getPrev(id).setNext(new_node,id)
                    new_node.getNext(id).setPrev(new_node,id)
                    break
                prev_node = scan_node
                scan_node = prev_node.getNext(id)

    def invalid(self, event, id):
        if event.getPrev(id) == None:
            if event.getNext(id) == None:
                self.id_heads[id] = None
                self.id_tails[id] = None
            else:
                self.id_heads[id] = event.getNext(id)
                event.getNext(id).setPrev(None,id)
        elif event.getNext(id) == None:
            self.id_tails[id] = event.getPrev(id)
            event.getPrev(id).setNext(None,id)
        else:
            event.getPrev(id).setNext(event.getNext(id),id)
            event.getNext(id).setPrev(event.getPrev(id),id)

    def invalid_all(self, event):
        for id in event.id:
            self.invalid(event, id)
        self.invalid(event, -1)

    def predict_state(self, id, target_frame):
        if id >= len(self.initial_states):
            return None
        # pridict the state at target_frame before collision at this frame
        if target_frame > self.target_frame:
            self.update((target_frame - self.target_frame)*2)
        state = self.initial_states[id]
        if state == None:
            return None
        id_event = self.id_heads[id]
        while id_event != None:
            if id_event.frame < target_frame:
                state = id_event.getRes(id)
            else:
                break
            id_event = id_event.getNext(id)
        return state.update(target_frame)

    def predict_result_state(self, id, target_frame):
        if id >= len(self.initial_states):
            return None
        # pridict the state at target_frame after collision at this frame
        if target_frame > self.target_frame:
            self.update((target_frame - self.target_frame)*2)
        state = self.initial_states[id]
        if state == None:
            return None
        id_event = self.id_heads[id]
        while id_event != None:
            if id_event.frame <= target_frame:
                state = id_event.getRes(id)
            else:
                break
            id_event = id_event.getNext(id)
        return state.update(target_frame)

    def merge(self, contemporary_events):
        merged = True
        main_event = contemporary_events[0]
        biggest_state = self.predict_state(main_event.id[0], main_event.frame)
        for id in main_event.id:
            self.invalid(main_event, id)
            main_event.setNext(None, id)
            main_event.setPrev(None, id)
        while merged:
            merged = False
            for event in contemporary_events:
                if event == main_event:
                    continue
                for id in event.id:
                    if id in main_event.id:
                        merged = True
                        for sid in event.id:
                            if sid not in main_event.id:
                                sid_state = self.predict_state(sid, main_event.frame)
                                if biggest_state < sid_state:
                                    biggest_state = sid_state
                                    main_event.id.insert(0, sid)
                                    main_event.next.insert(0, None)
                                    main_event.prev.insert(0, None)
                                    main_event.result.insert(0, None)
                                else:
                                    main_event.id.append(sid)
                                    main_event.next.insert(-1, None)
                                    main_event.prev.insert(-1, None)
                                    main_event.result.append(None)
                                break
                        self.invalid_all(event)
                        event.id = []
                        break
        for id in main_event.id:
            self.add_event_id(main_event, id)

    def calc_result(self, event):
        is_survivor = True
        survivor_result = None
        survivor_mass = 0
        survivor_momentum = [0, 0]
        for id in event.id:
            this_result = self.predict_state(id, event.frame)
            if is_survivor:
                survivor_result = this_result
                is_survivor = False
            else:
                this_result.dead = True
                event.setRes(this_result, id)
            survivor_mass += math.pi * this_result.radius * this_result.radius
            survivor_momentum[0] += math.pi * this_result.radius * this_result.radius * this_result.veloc[0]
            survivor_momentum[1] += math.pi * this_result.radius * this_result.radius * this_result.veloc[1]
        survivor_result.radius = (survivor_mass / math.pi) ** 0.5
        survivor_result.veloc[0] = survivor_momentum[0]/survivor_mass
        survivor_result.veloc[1] = survivor_momentum[1]/survivor_mass
        event.result[0] = survivor_result

    def is_colliding(self, id, target_frame):
        # predict if the target cell is colliding at target_frame
        scan_node = self.id_heads[id]
        while scan_node != None:
            if scan_node.frame == target_frame:
                return scan_node
            scan_node = scan_node.getNext(id)
        return None

    def predict_disrupt(self, myself, excepts, frame_now, end_frame, num = 0, theta = 0, predict_after = False):
        # predict if we will be collided, and return the first collided objects
        init_frame = frame_now
        final_frame = end_frame
        end_frame += 1
        mystate = State(myself.id, myself.pos, myself.veloc, myself.radius, frame_now)
        mystate.veloc[0] /= Consts["FRAME_DELTA"]
        mystate.veloc[1] /= Consts["FRAME_DELTA"]
        id_list = []
        disrupt_state = None
        disrupt_frame = Consts["MAX_FRAME"] + 1
        danger = False
        for id in range(2, len(self.initial_states)):
            if id in excepts:
                continue
            id_state_now = self.predict_result_state(id, frame_now)
            if id_state_now == None or id_state_now.dead:
                continue
            id_list.append(id)
        while num > 0:
            # Reduce force in proportion to area
            fx = math.cos(theta)
            fy = math.sin(theta)
            # Push player
            mystate.veloc[0] -= Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
            mystate.veloc[1] -= Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
            # Lose some mass
            mystate.radius *= (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5
            mystate.frame += 1
            frame_now += 1
            # check collide
            for id in id_list:
                id_state = self.predict_result_state(id, frame_now-1)
                if not id_state.dead:
                    collision_frame = predict_collision(mystate, id_state, 1)
                    if collision_frame:
                        new_danger = id_state.radius > mystate.radius
                        if danger:
                            if new_danger and frame_now < disrupt_frame:
                                disrupt_state = id_state.update(init_frame)
                                disrupt_frame = frame_now
                                danger = new_danger
                        else:
                            if new_danger or frame_now < disrupt_frame:
                                disrupt_state = id_state.update(init_frame)
                                disrupt_frame = frame_now
                                danger = new_danger
            # move
            mystate.pos[0] += mystate.veloc[0] * Consts["FRAME_DELTA"]
            mystate.pos[1] += mystate.veloc[1] * Consts["FRAME_DELTA"]
            num -= 1
        for id in id_list:
            id_state = self.predict_result_state(id, frame_now)
            if not id_state.dead:
                collision_frame = predict_collision(mystate, id_state, end_frame-frame_now)
                if collision_frame:
                    new_id_state = self.predict_state(id, frame_now+collision_frame)
                    if new_id_state.radius == id_state.radius:
                        new_danger = id_state.radius > mystate.radius
                        if danger:
                            if new_danger and frame_now+collision_frame < disrupt_frame:
                                disrupt_state = id_state.update(init_frame)
                                disrupt_frame = frame_now + collision_frame
                                danger = new_danger
                        else:
                            if new_danger or frame_now+collision_frame < disrupt_frame:
                                disrupt_state = id_state.update(init_frame)
                                disrupt_frame = frame_now + collision_frame
                                danger = new_danger
        for id in id_list:
            scan_node = self.id_heads[id]
            while scan_node != None and scan_node.frame < end_frame:
                if scan_node.getNext(id) is None or (scan_node.getNext(id) and scan_node.getNext(id).frame > frame_now):
                    id_state = scan_node.getRes(id).update(frame_now)
                    if id_state.dead:
                        break
                    collision_frame = predict_collision(mystate, id_state, end_frame-frame_now)
                    if collision_frame:
                        new_id_state = self.predict_state(id, frame_now+collision_frame)
                        if new_id_state.radius == id_state.radius:
                            new_danger = id_state.radius > mystate.radius
                            if danger:
                                if new_danger and frame_now+collision_frame < disrupt_frame:
                                    disrupt_state = id_state.update(init_frame)
                                    disrupt_frame = frame_now + collision_frame
                                    danger = new_danger
                            else:
                                if new_danger or frame_now+collision_frame < disrupt_frame:
                                    disrupt_state = id_state.update(init_frame)
                                    disrupt_frame = frame_now + collision_frame
                                    danger = new_danger
                scan_node = scan_node.getNext(id)
        if predict_after and disrupt_state is None:
            # predict if will be eaten after attacking
            target_state = self.predict_state(excepts[0], final_frame)
            mystate = mystate.update(final_frame)

            target_mass = math.pi * target_state.radius * target_state.radius
            my_mass = math.pi * mystate.radius * mystate.radius
            mass = target_mass + my_mass
            px = target_mass * target_state.veloc[0] + my_mass * mystate.veloc[0]
            py = target_mass * target_state.veloc[1] + my_mass * mystate.veloc[1]

            mystate.radius = (mass / math.pi) ** 0.5
            mystate.veloc[0] = px/mass
            mystate.veloc[1] = py/mass

            disrupt_state, danger = self.predict_disrupt(mystate, excepts, final_frame, final_frame+40)
        return disrupt_state, danger
