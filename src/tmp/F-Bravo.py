from consts import Consts
from math import *


class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.target = None

    def strategy(self, allcells):
        #####################场景和自己、对手的参数，不用调####################
        width = Consts["WORLD_X"]
        height = Consts["WORLD_Y"]
        dv1 = Consts["DELTA_VELOC"]  # 喷射速度
        loss_mass_rate = Consts["EJECT_MASS_RATIO"]
        dv = dv1 * loss_mass_rate  # 速度变化
        ###############自己的参数###############
        wo = allcells[self.id]
        my_position = wo.pos
        my_velocity = wo.veloc
        my_radius = wo.radius
        ###############对手的参数#############
        opponent_id = 1 - self.id
        opponent = allcells[opponent_id]
        opponent_position = opponent.pos
        opponent_velocity = opponent.veloc
        opponent_radius = opponent.radius

        ######################数学函数，比较严谨，不用调#################
        def dot(a, b):  # 点乘
            if isinstance(a, list):
                return a[0] * b[0] + a[1] * b[1]
            else:
                return a * b

        def cross_product(a, b):  # 叉乘
            return a[0] * b[1] - a[1] * b[0]

        def multiplication(a, v):  # 数乘
            if isinstance(v, list):
                return [a * v[0], a * v[1]]
            else:
                return multiplication(v, a)

        def plus(a, b):  # 加
            return [a[0] + b[0], a[1] + b[1]]

        def minus(a, b):  # 减
            return [a[0] - b[0], a[1] - b[1]]

        def negative(a):  # 取负
            return [-a[0], -a[1]]

        def len_of_vector(v):
            return sqrt(dot(v, v))

        def angle_for_return(angle):  # 最终返回角度[0,2pi)
            if angle > 0:
                if angle > 2 * pi:
                    return angle - 2 * pi
                else:
                    return angle
            else:
                return angle + 2 * pi

        def true_distance(dist):  # true_distance(dist)穿屏最小距离
            vx = dist[0]
            vy = dist[1]
            alist = [vx, vx - width, vx + width]
            blist = [vy, vy - height, vy + height]
            alist.sort(key=lambda x: abs(x))
            blist.sort(key=lambda x: abs(x))
            return [alist[0], blist[0]]

        def true_position(cell):  # true_position(cell)返回相对wo的真实位置(考虑到了穿屏)
            if cell == wo:
                return cell.pos
            else:
                dist = distance_of_two_cell(wo, cell)
                return plus(my_position, dist)

        def distance_of_two_cell(me, other):  # disttance_of_two_cell(me,other)真实位矢
            dist = minus(other.pos, me.pos)
            return true_distance(dist)

        def next_tick_distance(me, other):  # next_tick_distance(dist,v_relative)下一刻位置
            # 由于游戏先变位置，再变速度，我们发射的时候要考虑下一帧的相对位置
            # 本函数会再考虑加速度的时候用到，不考虑的时候不用
            dist = distance_of_two_cell(me, other)
            v_relative = minus(me.veloc, other.veloc)
            return minus(dist, v_relative)

        def angle(v1, v2):  # theta1()夹角[0,pi]
            return pi - abs(pi - directional_angle(v1, v2))

        def distance0(me, other):  # 两球sel和cel的距离
            return len_of_vector(true_distance(minus(me.pos, other.pos)))

        def distance1(me, other):  # distance1(me,other)距离减两个半径
            dist = len_of_vector(distance_of_two_cell(me, other))
            return dist - me.radius - other.radius

        def distance_of_cell_to_my_motion_line(me, other):  # distance_of_cell_to_my_motion_line(me, other)到我运动直线的距离
            v_relative = minus(me.veloc, other.veloc)
            dist = distance_of_two_cell(me, other)
            return point_to_edge(dist, [0, 0], v_relative)

        def point_to_edge(a, b, c):  # 3坐标a,b,c,返回a到直线bc的距离
            bc = minus(c, b)
            ba = minus(a, b)
            touying = abs(dot(bc, ba)) / len_of_vector(bc)
            h = dot(ba, ba) - touying ** 2
            if h < 1e-6:
                return 0
            else:
                return sqrt(h)

        def after_collision(me, other):  # after_collision(me, other)碰后大的细胞的位置半径速度
            t = time_of_collision2(me, other)
            if t:
                if me.radius >= other.radius:
                    mass = me.radius ** 2 + other.radius ** 2
                    P = plus(multiplication(me.radius ** 2, me.veloc), multiplication(other.radius ** 2, other.veloc))
                    v = multiplication(1 / mass, P)
                    r = sqrt(mass)
                    new_position = plus(me.pos, multiplication(me.veloc, t))
                    return new_position, r, v
                else:
                    return after_collision(other, me)

        def time_of_collision1(r1, r2, dist, v_relative):  # 预测两球的相撞时间，同样time1函数是该函数参数为sel,cel的版本
            # 参数(为避免出现math domain error)
            dist = true_distance(dist)
            if 100 * len_of_vector(v_relative) < (len_of_vector(dist) - r1 - r2):
                return None

            if dot(v_relative, dist) < 0:
                return None
            h = point_to_edge(dist, [0, 0], v_relative)
            if r1 + r2 < h + 1e-3:
                return None
            else:
                l1 = sqrt((r1 + r2) ** 2 - h ** 2)
                l2 = len_of_vector(dist) ** 2 - h ** 2
                if l2 < 1e-4:
                    return None
                l2 = sqrt(l2)
                return (l2 - l1) / len_of_vector(v_relative)

        def directional_angle(a, b):  # 向量a到b的有向角([0,2pi))
            if sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2)) < 1e-6:
                return 0
            det = cross_product(a, b)
            cos_alpha = dot(a, b) / (len_of_vector(a) * len_of_vector(b))
            if abs(cos_alpha) > 1 - 1e-3:
                if cos_alpha < 0:
                    return pi
                else:
                    return 0
            alpha = acos(cos_alpha)
            if det > 0:
                return 2 * pi - alpha
            else:
                return alpha

        def distance_to_collision(sel, cel):  # 该函数考虑相对于目标cel相撞还需行进的距离(time_of_collision2(sel,cel)*len_of_vector(v))

            dist = distance_of_two_cell(sel, cel)
            v1 = minus(sel.veloc, cel.veloc)

            if 100 * len_of_vector(v1) < (len_of_vector(dist) - sel.radius - cel.radius):
                return None

            if dot(v1, dist) < 0:
                return None
            h = point_to_edge(dist, [0, 0], v1)
            if sel.radius + cel.radius < h + 1e-3:
                return None
            else:
                l1 = sqrt((sel.radius + cel.radius) ** 2 - h ** 2)
                l2 = len_of_vector(dist) ** 2 - h ** 2
                if l2 < 1e-4:
                    return None
                l2 = sqrt(l2)
                return l2 - l1

        def time_of_collision2(me, other):  #
            r1 = me.radius
            r2 = other.radius
            dist = minus(other.pos, me.pos)
            dist = true_distance(dist)
            v_relative = minus(me.veloc, other.veloc)

            return time_of_collision1(me.radius, other.radius, dist, v_relative)

        def is_intersect(l1, l2):  # 判断两球是否已经相交
            p1 = l1[0]
            p2 = l2[0]
            dist = minus(p2, p1)
            dist = true_distance(dist)
            r1 = l1[1]
            r2 = l2[1]
            return len_of_vector(dist) < r1 + r2

        ################################################################################
        ###########################物理函数##################################
        def eject_time(sel, cel):  # 吃球损失估计，返回吃到cel需要喷球的次数，显然不能精确返回具体数值，看成是一个估计就好
            nonlocal dv
            dist = minus(cel.pos, sel.pos)
            dist = true_distance(dist)
            v = minus(sel.veloc, cel.veloc)
            theta1 = (sel.radius + cel.radius) / len_of_vector(dist)
            if theta1 < 1:
                theta1 = asin(theta1)
            alpha = angle(v, dist)
            if alpha < theta1:
                return 0
            # 参数#速度越大loss越大
            else:
                a = 1  # 1   从0.0~2.0
                c = 3  # 3     从0~4
                return (1 + a * len_of_vector(v) ** 2) * abs(alpha - theta1) * len_of_vector(v) / dv + c

        def earn(me, other):  # 吃球收益估计，返回预测吃到该球后自身质量会变成现在质量的倍数，同上，估计就好
            N = eject_time(me, other)
            # 参数
            if (1 - loss_mass_rate) ** N < 1.1 * other.radius ** 2 / me.radius ** 2:
                return None
            else:
                return (1 - loss_mass_rate) ** N / 1.1 + other.radius ** 2 / me.radius ** 2

        def chase_time(me, other):  # 预测吃到球cel所需花费时间，估计就好
            t1 = distance1(me, other) / max(len_of_vector(minus(me.veloc, other.veloc)), 0.2)
            t2 = eject_time(me, other)
            return t1 + t2

        # 策略函数-----------------------------------
        def stra1(me, other):  # 吃球函数
            v_relative = minus(me.veloc, other.veloc)
            dist = next_tick_distance(me, other)
            theta1 = directional_angle(negative(v_relative), dist)
            if theta1 > pi:
                theta1 = theta1 - 2 * pi
            r = abs(theta1 / pi)
            if r > 0.9:
                r1 = 1 - 5 * (1 - r)
            else:
                r1 = r ** 3
            theta = theta1 * r1
            return directional_angle([0, 1], negative(v_relative)) + theta + pi

        # def stra3(me, other):  # 分段吃球函数
        #     def duan(t):  # duan即位所说的分段函数,duan(r1)为修正系数
        #         if t < 0.7:
        #             return t ** 2
        #         else:
        #             return t
        #     c = next_tick_distance(me,other)
        #     theta1 = directional_angle(negative(v1), c)
        #     # 在己方速度过小时不采用该吃球函数而是直接飞向目标，因为小速度意味着必须要考虑加速度的离散性，控制不好就会乱喷
        #     if len_of_vector(v1) < 0.3:  # *************
        #         return directional_angle([0, 1], c) + pi
        #     if theta1 > pi:
        #         theta1 = theta1 - 2 * pi
        #     r = abs(theta1 / pi)
        #     r1 = r
        #     theta = theta1 * duan(r1)
        #     return directional_angle([0, 1], negative(v1)) + theta + pi

        def stra1_J(me, other):  # 吃、狙球函数,本质上与吃球函数相差不大，随意使用
            v_relative = minus(me.veloc, other.veloc)
            dist = next_tick_distance(me, other)
            theta1 = directional_angle(negative(v_relative), dist)
            if theta1 > pi:
                theta1 = theta1 - 2 * pi
            r = abs(theta1 / pi)
            theta = theta1 * r ** 3
            return directional_angle([0, 1], negative(v_relative)) + theta + pi

        def escape1(pos1, pos2, v_relative):  # 躲球函数，直接对着目标喷球
            dist = minus(pos2, pos1)
            dist = true_distance(dist)
            direction = minus(dist, v_relative)
            return directional_angle([0, 1], direction)

        def escape2(me, other):
            return escape1(me.pos, other.pos, minus(me.veloc, other.veloc))

        # 预测函数-----------------------------------------
        def get_mintime_and_mindist(me, bigger_list):
            i2_min = None
            min2 = None
            i1_min = None
            min1 = None
            for i in range(len(bigger_list)):
                t1 = time_of_collision2(me, bigger_list[i])
                t2 = distance_to_collision(me, bigger_list[i])
                if t2 != None:
                    if i2_min == None:
                        i2_min = i
                        min2 = t2
                    else:
                        if t2 < min2:
                            i2_min = i
                            min2 = t2
                if t1 != None:
                    if i1_min == None:
                        i1_min = i
                        min1 = t1
                    else:
                        if t1 < min1:
                            i1_min = i
                            min1 = t1
            return i1_min, min1, i2_min, min2

        def get_time_r_colpos_coldr_colv_list1(me):  # 返回球cel在场上所有可能吃到的球及吃到他们所需的时间，吃到他们后的位置，速度，半径
            alist, blist, clist = [], [], []
            for i in range(2, len(allcells)):
                other = allcells[i]
                if other.dead or other == me or other.radius >= me.radius:
                    alist.append(None)
                    blist.append(None)
                    clist.append(None)
                    continue
                dist = distance_of_two_cell(me, other)
                v_relative = minus(me.veloc, other.veloc)
                t = time_of_collision1(me.radius, other.radius, dist, v_relative)
                alist.append(t)
                if t != None:
                    blist.append(sqrt(me.radius ** 2 + other.radius ** 2) - me.radius)
                    clist.append(after_collision(me, other))
                else:
                    blist.append(None)
                    clist.append(None)
            return [alist, blist, clist]

        def get_time_r_colpos_coldr_colv_list2(me):  # 和上一函数相同，但同时考虑被吃的情形
            alist, blist, clist = [], [], []
            for i in range(2, len(allcells)):
                cell = allcells[i]
                if cell.dead or cell == me:
                    alist.append(None)
                    blist.append(None)
                    clist.append(None)
                    continue
                dist = minus(cell.pos, me.pos)
                v_relative = minus(me.veloc, cell.veloc)
                t = time_of_collision1(me.radius, cell.radius, dist, v_relative)
                alist.append(t)
                if t != None:
                    blist.append(sqrt(me.radius ** 2 + cell.radius ** 2) - me.radius)
                    clist.append(after_collision(me, cell))
                else:
                    blist.append(None)
                    clist.append(None)
            return [alist, blist, clist]

        def get_various_list(me):
            b_list, s_list, c_list = [], [], []
            for x in allcells:
                if x.radius > selr and x.dead == False:
                    b_list.append(x)
                if x.radius < selr and x.dead == False and x != opponent:
                    s_list.append(x)
                if x.radius > selr and x.dead == False and x != me:
                    d1 = distance1(me, x)
                    if d1 < 160:
                        c_list.append([x, d1])
            return b_list, s_list, c_list

        def get_process():
            # 进程参数设置,前期还是后期不同处理
            count = 0
            for cel in allcells[2:]:
                if len_of_vector(true_position(cel)) < 270 and cel.radius > 0.15 * sel.radius:
                    count += 1
            if count > 10:
                return 3
            else:
                return 1

        sel = allcells[self.id]
        selp = sel.pos
        selv = sel.veloc
        selr = sel.radius

        process = get_process()
        bigger_list, smaller_list, close_list = get_various_list(wo)
        # 苟--------------------------------------------
        # 该游戏中苟的部分并不特别重要，不要让自己死掉的同时尽量少喷球就行，即使删掉该部分的大量代码，也不会对胜率造成太大影响
        # 如果非要追求极致，可以想办法避免出现面前的小球突然吃到球变大而你没反应过来的情形，详见‘进化1‘和’进化2‘
        # 找到所有比自己大的球bigger_list

        # 找到这些球中,碰撞所需时间最小的和碰撞所需距离最小的，他们在bigger_list中的下标记为i1_min和i2_min

        t_min_i, min_t, d_min_i, min_d = get_mintime_and_mindist(wo, bigger_list)

        # 在场上存在较多大球时采用更为保守的躲球方法
        if len(bigger_list) > 5:
            if min_d != None and min_d / sqrt(selr) < 5:
                self.target = None
                cell = bigger_list[d_min_i]
                celp = cell.pos
                celv = cell.veloc
                return escape1(selp, celp, minus(selv, celv))
        if min_t != None and min_t < 60:
            self.target = None
            cell = bigger_list[t_min_i]
            celp = cell.pos
            celv = cell.veloc
            return escape1(selp, celp, minus(selv, celv))

        # 进化算法

        # 进化1
        for x in close_list:  # 都是大于自己的细胞
            t_l, r_l, c_l = get_time_r_colpos_coldr_colv_list1(x[0])  # 小于方圆160比自己大的细胞被吃到时间,半径增,c_l吃后的位置，半径，速度
            for i in range(len(t_l)):
                # 参数
                if t_l[i] != None and c_l[i][1] > selr:
                    p_ = plus(selp, multiplication(t_l[i], selv))
                    if is_intersect([p_, selr, selv], c_l[i]):
                        return escape2(sel, x[0])
                    else:
                        t = len_of_vector(true_distance(minus(sel.pos, c_l[i][0]))) - sel.radius - c_l[i][1]
                        if t != None and t < 20:
                            return escape2(sel, x[0])

        # 进化2
        t_l, r_l, c_l = get_time_r_colpos_coldr_colv_list1(sel)  # 小于自己的细胞被吃到时间,半径增,c_l吃后的半径，位置，速度
        for x in close_list:  # 这里面的细胞都比自己大
            for i in range(len(t_l)):
                if t_l[i] != None:  # 可与自己相碰
                    if selr + r_l[i] < x[0].radius:
                        p_ = plus(x[0].pos, multiplication(t_l[i], x[0].veloc))
                        if is_intersect(c_l[i], [p_, x[0].radius]):
                            return escape2(sel, x[0])
                        else:
                            t = len_of_vector(true_distance(minus(p_, c_l[i][0]))) - c_l[i][1] - x[0].radius
                            if t and t < 12:
                                return escape2(sel, x[0])

        # 吃----------------------------------------------------
        # 该部分是该游戏的核心部分，半径增大的速度就是取胜的关键，同时又不能让自己的质量损失太多
        # 设置target，后面有用
        target = None
        # 本来有设置在大球较多时采用更为保守的方案的策略，现已废弃，故设置为100
        # 选出比自己小的球
        # 作出吃球备选列表eat_able_list
        eat_able_list = []  # [[cel,earn]...]
        for cel in smaller_list:
            # 首先保证距离不大
            if distance1(wo, cel) < 270:  # ****************重要参数
                # 记录各种参数
                N = eject_time(wo, cel)
                dt = chase_time(wo, cel)
                # lst用来记录该球cel在接下来的时间内可能会吃球或被吃的情况，避免出现本想吃掉小球它却突然变大的情况
                # 这种‘二次预测’的部分对胜率造成的影响不大也不小，大概在5%-15%左右，取决于参数设置
                lst = get_time_r_colpos_coldr_colv_list2(cel)
                # zhuang_li_r记录cel可能吃或被吃的球的半径
                zhuang_li_r = []
                # 首先要确定吃球的路径上不存在其他大球
                for big_cell in bigger_list:
                    a = true_distance(minus(big_cell.pos, my_position))
                    b = true_distance(minus(cel.pos, my_position))
                    if (point_to_edge(true_position(big_cell), my_position,
                                      true_position(cel)) < my_radius + big_cell.radius + 80 and
                            dot(a, b) > 0 and dot(a, b) < len_of_vector(b) ** 2):
                        break
                else:

                    # 然后判断该球会不会在dt时间内变为'不可吃'
                    for i in range(len(lst[0])):  # 小球的（碰撞时间，大球增大直径，位置大小速度）
                        if lst[0][i] != None and lst[0][i] < dt:
                            zhuang_li_r.append(lst[2][i][1])
                    for r in zhuang_li_r:
                        if r > cel.radius:
                            break
                    else:
                        area1 = cel.radius ** 2 + sum([x ** 2 for x in zhuang_li_r])  # ？？？
                        if selr ** 2 * (1 - loss_mass_rate) ** N > area1:
                            # 所有情况检查完毕，将它放到eat_able_list列表，并附上对其收益的预测量
                            shouyi1 = earn(wo, cel)
                            if shouyi1 != None:
                                eat_able_list.append([cel, shouyi1])
        # 选出最大收益球
        max_earn_cell = None
        max_earn = None
        max2_earn_cell = None  # 第二大收益球
        max2_earn = None
        for eat_able_cell in eat_able_list:
            if max_earn_cell == None:
                max_earn_cell = eat_able_cell[0]
                max_earn = eat_able_cell[1]
            else:
                if max_earn < eat_able_cell[1]:
                    max_earn = eat_able_cell[1]
                    max_earn_cell = eat_able_cell[0]
        for eat_able_cell in eat_able_list:
            if max2_earn_cell == None:
                if eat_able_cell[0] != max_earn_cell:
                    max2_earn_cell = eat_able_cell[0]
                    max2_earn = eat_able_cell[1]
            else:
                if eat_able_cell[0] != max_earn_cell and max2_earn < eat_able_cell[1]:
                    max2_earn_cell = eat_able_cell[0]
                    max2_earn = eat_able_cell[1]
        if (max_earn_cell != None and max_earn >= 1.05 + 0.18 * (
                process - 1) and max2_earn_cell != None and max2_earn < 1.05 + 0.18 * (process - 1)) or (
                max_earn_cell != None and max_earn >= 1.05 + 0.18 * (process - 1) and max2_earn == None):
            # 所有条件满足，设置target
            target = max_earn_cell
            v = minus(sel.veloc, target.veloc)
            # 此处的2个条件(1)吃到目标球的角度还没对，体现在loss>0,或者吃到目标球的速度还不大，体现在len_of_vector(v)<参数
            # 0.3********************重要参数
            if len_of_vector(v) < 0.3 or eject_time(sel, target) > 0:
                return stra1_J(sel, target)  # 更改吃球函数
        elif max_earn_cell != None and max_earn >= 1.05 + 0.18 * (
                process - 1) and max2_earn_cell != None and max2_earn >= 1.05 + 0.18 * (process - 1):
            # 判断两球的时间收益,如何有效狙击对手同时不把自己玩死是该部分主要考虑的因素果max2的 shouyi/howl 明显大于max1，则吃max2
            if (max2_earn - 1) / chase_time(sel, max2_earn_cell) > 1.0 * (max_earn - 1) / chase_time(sel,
                                                                                                     max_earn_cell):
                target = max2_earn_cell
            else:
                target = max_earn_cell
            v = minus(sel.veloc, target.veloc)
            # 此处的2个条件(1)吃到目标球的角度还没对，体现在loss>0,或者吃到目标球的速度还不大，体现在len_of_vector(v)<参数
            # 0.3********************重要参数
            if len_of_vector(v) < 0.3 or eject_time(sel, target) > 0:
                return stra1_J(sel, target)  # 更改吃球函数

        # 狙--------------------------------------------
        # 狙击对手的部分同样不是本游戏的重点，它的重要性甚至比苟的部分还低，删掉该部分对胜率造成的影响也不大
        # 这是因为，只有在优势情形下才会选择狙击对手，但是本游戏翻盘的希望不大，这是一个半径越大越容易，越小越难的游戏
        # 所以，狙击的意义很多时候仅仅在于快速结束比赛
        # 即便如此，该部分还是对胜率有所提升，同时使得比赛更富有观赏性
        # 如何有效狙击对手同时不把自己玩死是该部分主要考虑的因素
        # 设立target条件避免在正在吃球时去狙击对手，影响自己变大的效率，得不偿失
        if target == None:
            # opponent用来记录对手的球,dist位置向量，v相对速度
            dist = minus(opponent.pos, selp)
            dist = true_distance(dist)
            v = minus(selv, opponent.veloc)
            if opponent.radius > 5:  # 在对手的半径已经毫无希望的时候不再追击，因为对手半径越小，狙击越难
                # 下面的一对条件判别采用了分段判别，因为连续的判别并不好做，故分段调参
                # 条件中所有参数均为重要参数*********************过大会导致胜率降低
                if ((opponent.radius < selr * 0.8 and distance0(sel, opponent) < 200 and angle(dist, v) < pi / 6) or
                        (opponent.radius < selr * 0.65 and distance0(sel, opponent) < 300 and angle(dist,
                                                                                                    v) < pi / 3) or
                        (opponent.radius < selr * 0.75 and len_of_vector(v) < 0.3 and distance0(sel, opponent) < 200) or
                        (opponent.radius < selr * 0.55 and len_of_vector(v) < 0.6 and distance0(sel, opponent) < 300)):

                    # 同样在狙击的路上不存在大球的时候才选择狙击
                    for y in bigger_list:
                        # 参数
                        a = true_distance(minus(y.pos, selp))
                        b = true_distance(minus(opponent.pos, selp))
                        if (point_to_edge(true_position(y), selp, true_position(opponent)) < selr + y.radius + 80 and
                                dot(a, b) > 0 and dot(a, b) < len_of_vector(b) ** 2):
                            break
                    else:  # 在场上大球数量不同时采用不同的狙击方案，大球数量<=1时追击更为狂野
                        # 在己方速度不大(避免追球使自己进入高速状态，速度越大意味着危险越大)时，相对opponent速度不大
                        # 或者角度不对就进行追击
                        # 此处选择stra1为追击函数，实际上选哪个意义不大，因为追击一般都发生在一条直线上
                        # len_of_vector(selv)后的参数为重要参数****************过大会导致胜率降低
                        if len(bigger_list) > 1:
                            if len_of_vector(selv) < 0.5 and (
                                    distance_to_collision(sel, opponent) == None or len_of_vector(v) < 0.7):
                                return stra1(sel, opponent)
                        elif len(bigger_list) == 1:
                            if len_of_vector(selv) < 1 and (
                                    distance_to_collision(sel, opponent) == None or len_of_vector(v) < 1):
                                return stra1(sel, opponent)

                        else:
                            if distance_to_collision(sel, opponent) == None or len_of_vector(v) < 1.8:
                                return stra1(sel, opponent)

# 总结：本代码为基础代码，设置好参数后对该版本的胜率可以超过70%，重要的参数都已用*号标出
# 参数的调试往往是非常漫长且无聊的过程，因为若要研究某个参数对胜率的影响，往往参数的微调只会导致胜率上升或下降很小，有时在5%以内
# 所以为了精确测定胜率变化需要进行大量的比赛，5%的胜率变化至少需要500局的比赛才能够较为准确的测出，即便是同时运行5个kernal程序也
# 需要至少40min！

