from consts import Consts
from math import *


class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.target = None
        self.totalarea = 0

    def strategy(self, allcells):

        #关于场地，自身和对手的一些参数
        width = Consts["WORLD_X"]
        height = Consts["WORLD_Y"]
        dv1 = Consts["DELTA_VELOC"]  # 喷射速度
        loss_mass_rate = Consts["EJECT_MASS_RATIO"]
        dv = dv1 * loss_mass_rate  # 喷射一次的速度的变化量

        #自身的参数
        wo = allcells[self.id]
        my_position = wo.pos
        my_velocity = wo.veloc
        my_radius = wo.radius

        #对手的参数
        opponent_id = 1 - self.id
        opponent = allcells[opponent_id]
        opponent_position = opponent.pos
        opponent_velocity = opponent.veloc
        opponent_radius = opponent.radius

        #计算场地上所有球的总面积（质量）
        if not self.totalarea:
            for cell in allcells:
                self.totalarea += cell.radius ** 2

        #以下为数学函数部分，对用列表表示的位置和速度矢量进行一系列运算和判定

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

        def len_of_vector(v): # 求向量的模
            return sqrt(dot(v, v))

        def angle_for_return(angle):  # 将角度转化为[0,2pi)内的角
            if angle > 0:
                if angle > 2 * pi:
                    return angle - 2 * pi
                else:
                    return angle
            else:
                return angle + 2 * pi

        def true_distance(dist):  # 对一个向量dist,计算其考虑穿屏的最小情形
            vx = dist[0]
            vy = dist[1]
            alist = [vx, vx - width, vx + width]
            blist = [vy, vy - height, vy + height]
            alist.sort(key=lambda x: abs(x))
            blist.sort(key=lambda x: abs(x))
            return [alist[0], blist[0]]

        def true_position(cell):  # 返回相对wo考虑到了穿屏后的真实位置
            if cell == wo:
                return cell.pos
            else:
                dist = distance_of_two_cell(wo, cell)
                return plus(my_position, dist)

        def distance_of_two_cell(me, other):  # 真实位矢
            dist = minus(other.pos, me.pos)
            return true_distance(dist)

        def next_tick_distance(me, other):  # 返回下一刻的me与other的相对位置
            dist = distance_of_two_cell(me, other)
            v_relative = minus(me.veloc, other.veloc)
            return minus(dist, multiplication(3, v_relative))

        def directional_angle(a, b):  # 向量a到b的有向角(范围为[0,2pi))
            if sqrt((a[0]**2 + a[1]**2) * (b[0]**2 + b[1]**2)) < 1e-6:
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

        def angle(v1, v2):  # 将[0,2pi)的角变换为[0,pi]
            return pi - abs(pi - directional_angle(v1, v2))

        def distance(me, other):  # 两球me和other中心的距离
            return len_of_vector(true_distance(minus(me.pos, other.pos)))

        def distance_without_radius(me, other):  # 两球me和other除去半径后的距离
            dist = len_of_vector(distance_of_two_cell(me, other))
            return dist - me.radius - other.radius

        def distance_of_cell_to_my_motion_line(me, other):  # other到me当前速度所在直线的距离
            v_relative = minus(me.veloc, other.veloc)
            dist = distance_of_two_cell(me, other)
            return point_to_edge(dist, [0, 0], v_relative)

        def point_to_edge(a, b, c):  # a,b,c分别为场地中点的坐标,返回点a到直线bc的距离
            bc = minus(c, b)
            ba = minus(a, b)
            touying = abs(dot(bc, ba)) / len_of_vector(bc) # ba在bc上的投影长度
            h = dot(ba, ba) - touying ** 2 # 勾股定理
            if h < 1e-6:
                return 0
            else:
                return sqrt(h)

        def after_collision(me, other):  # 碰后合成的细胞的位置，半径和速度

            # 预测当前状态下me能否与other碰撞，若可以则返回预计碰撞时间，否则返回None
            t = time_of_collision2(me, other)

            if t: # 如果可以碰撞
                if me.radius >= other.radius: # 合并的机制是小球并入大球
                    mass = me.radius ** 2 + other.radius ** 2
                    P = plus(multiplication(me.radius ** 2, me.veloc), multiplication(other.radius ** 2, other.veloc)) # 总动量
                    v = multiplication(1 / mass, P)
                    r = sqrt(mass)
                    new_position = plus(me.pos, multiplication(me.veloc, t))
                    return new_position, r, v
                else:
                    return after_collision(other, me)

        # 判定me和other在120个单位内能否碰撞，若可以则返回碰撞前还需运动的距离，否则返回None
        def distance_to_collision(me, other):

            dist = distance_of_two_cell(me, other)
            v1 = minus(me.veloc, other.veloc)

            # 相对速度与距离成钝角无法碰撞返回None
            if dot(v1, dist) < 0:
                return None

            # 100个单位内相对运动小于距离返回None
            if 120 * len_of_vector(v1) < (len_of_vector(dist) - me.radius - other.radius):
                return None

            h = point_to_edge(dist, [0, 0], v1) # 根据当前运动情况me和other中心可能达到的最短距离
            if me.radius + other.radius < h + 1e-3:
                return None
            else:
                l1 = sqrt((me.radius + other.radius) ** 2 - h ** 2)
                l2 = len_of_vector(dist) ** 2 - h ** 2
                if l2 < 1e-4:
                    return None
                l2 = sqrt(l2)
                return l2 - l1

        # 在120个单位内能发生碰撞的两细胞的相撞时间，不能碰撞则返回None，实现过程同上
        def time_of_collision1(r1, r2, dist, v_relative):

            dist = true_distance(dist)

            # 相对速度与距离成钝角无法碰撞返回None
            if dot(v_relative, dist) < 0:
                return None

            # 120个单位内相对运动小于距离返回None
            if 120 * len_of_vector(v_relative) < (len_of_vector(dist) - r1 - r2):
                return None

            h = point_to_edge(dist, [0, 0], v_relative) # 根据当前运动情况me和other中心可能达到的最短距离
            if r1 + r2 < h + 1e-3:
                return None
            else:
                l1 = sqrt((r1 + r2) ** 2 - h ** 2)
                l2 = len_of_vector(dist) ** 2 - h ** 2
                if l2 < 1e-4:
                    return None
                l2 = sqrt(l2)
                return (l2 - l1) / len_of_vector(v_relative)

        # 调用time_of_collision1函数判定me和other在100个单位内能否碰撞，若可以则返回时间，否则返回None
        def time_of_collision2(me, other):

            dist = minus(other.pos, me.pos)
            dist = true_distance(dist)
            v_relative = minus(me.veloc, other.veloc)

            return time_of_collision1(me.radius, other.radius, dist, v_relative)

        def is_intersect(list1, list2):  # 判断两球是否已经相交,list1,list2存储的是[pos,radius]

            position1 = list1[0]
            position2 = list2[0]
            dist = minus(position2, position1)
            dist = true_distance(dist)

            radius1 = list1[1]
            radius2 = list2[1]
            return len_of_vector(dist) < radius1 + radius2

        #####################################################################################################
        #以下为物理函数部分

        def eject_time(me, other):  # 吃球损失估计，近似返回吃到cel需要喷球的次数
            dist = minus(other.pos, me.pos)
            dist = true_distance(dist)
            v = minus(me.veloc, other.veloc)
            theta1 = (me.radius + other.radius) / len_of_vector(dist)
            if theta1 < 1:
                theta1 = asin(theta1)

            alpha = angle(v, dist)
            if alpha < theta1:
                return 0
            else:
                a = 1
                c = 3
                return (1 + a * len_of_vector(v) ** 2) * abs(alpha - theta1) * len_of_vector(v) / dv + c

        def earn(me, other):  # 吃球收益估计，近似预测返回吃到该球后自身质量会变成现在质量的倍数
            N = eject_time(me, other)

            if (1 - loss_mass_rate) ** N < 1.08 * other.radius ** 2 / me.radius ** 2:
                return None
            else:
                return (1 - loss_mass_rate) ** N / 1.08 + other.radius ** 2 / me.radius ** 2

        def chase_time(me, other): # 近似返回吃到球所需的时间
            t1 = distance_without_radius(me, other) / max(len_of_vector(minus(me.veloc, other.veloc)), 0.2)
            t2 = eject_time(me, other)
            return t1 + t2

        def snipe1(me, other): # 追球函数
        #追上的时间，相对速度，位矢取下一帧的位矢
            t = time_of_collision2(me, other)
            v_relative = minus(me.veloc, other.veloc)
            dist = next_tick_distance(me, other)
########################分段吃球########################################
            if not t:                              #原本碰不到的情况
                if len_of_vector(v_relative) > 0.4:#速度比0.4大的情况
                    theta1 = directional_angle(negative(v_relative), dist)
                    if theta1 > pi:
                        theta1 = theta1 - 2 * pi
                    r = abs(theta1 / pi)               #这是一个有用的比值，用于分段逼近
                    if 0.4<r<0.75:############直接垂直射出
                        if pi>directional_angle(dist,v_relative)>0:
                            return directional_angle([0,1],v_relative)+0.5*pi
                        elif pi<directional_angle(dist,v_relative)<2*pi:
                            return directional_angle([0,1],v_relative)-0.5*pi
                    else:           #利用幂函数r**3逼近
                        theta = theta1 * r ** 3
                        return directional_angle([0, 1], negative(v_relative)) + theta + pi
                else:                                #速度小于0.4反向直喷
                    return directional_angle([0, 1], negative(dist))
            #如果本来就能吃到，但是花费时间比较长，就多喷几个加速，加速上限2.1
            elif t > 42 and me.radius ** 2 * (               
                    1 - loss_mass_rate) ** 7 >1.05* other.radius ** 2 + 4 * me.radius ** 2 * loss_mass_rate and 20 * me.radius ** 2 * loss_mass_rate < other.radius ** 2 and len_of_vector(me.veloc)<2.1:
                return directional_angle([0, 1], negative(dist))
            else:
                return None

        def snipe2(me, other):  # 另一个追球函数，激烈程度不及上一个
        #追上的时间，相对速度，位矢取下一帧的位矢
            t = time_of_collision2(me, other)
            v_relative = minus(me.veloc, other.veloc)
            dist = next_tick_distance(me, other)
########################分段吃球########################################
            if not t:                              #原本碰不到的情况
                if len_of_vector(v_relative) > 0.4:#速度比0.4大的情况
                    theta1 = directional_angle(negative(v_relative), dist)
                    if theta1 > pi:
                        theta1 = theta1 - 2 * pi
                    r = abs(theta1 / pi)               #这是一个有用的比值，用于分段逼近
                    if 0.4<r<0.75:############直接垂直射出
                        if pi>directional_angle(dist,v_relative)>0:
                            return directional_angle([0,1],v_relative)+0.5*pi
                        elif pi<directional_angle(dist,v_relative)<2*pi:
                            return directional_angle([0,1],v_relative)-0.5*pi
                    else:           #利用幂函数r**3逼近
                        theta = theta1 * r ** 3
                        return directional_angle([0, 1], negative(v_relative)) + theta + pi
                else:                                #速度小于0.4反向直喷
                    return directional_angle([0, 1], negative(dist))
            #如果本来就能吃到，但是花费时间比较长，就多喷几个加速，加速上限2.1
            elif t > 69 and me.radius ** 2 * (               
                    1 - loss_mass_rate) ** 7 >1.05* other.radius ** 2 + 4 * me.radius ** 2 * loss_mass_rate and 20 * me.radius ** 2 * loss_mass_rate < other.radius ** 2 and len_of_vector(me.veloc)<2.1:
                return directional_angle([0, 1], negative(dist))
            else:
                return None

        def snipe3(me, other):  # 第三个追球函数，主要针对追击对，吃球过程较不激烈
        #追上的时间，相对速度，位矢取下一帧的位矢
            t = time_of_collision2(me, other)
            v_relative = minus(me.veloc, other.veloc)
            dist = next_tick_distance(me, other)
########################分段吃球########################################
            if not t:                              #原本碰不到的情况
                if len_of_vector(v_relative) > 0.4:#速度比0.4大的情况
                    theta1 = directional_angle(negative(v_relative), dist)
                    if theta1 > pi:
                        theta1 = theta1 - 2 * pi
                    r = abs(theta1 / pi)               #这是一个有用的比值，用于分段逼近
                    if 0.4<r<0.75:############直接垂直射出
                        if pi>directional_angle(dist,v_relative)>0:
                            return directional_angle([0,1],v_relative)+0.5*pi
                        elif pi<directional_angle(dist,v_relative)<2*pi:
                            return directional_angle([0,1],v_relative)-0.5*pi
                    else:           #利用幂函数r**3逼近
                        theta = theta1 * r ** 3
                        return directional_angle([0, 1], negative(v_relative)) + theta + pi
                else:                                #速度小于0.4反向直喷
                    return directional_angle([0, 1], negative(dist))
            #如果本来就能吃到，但是花费时间比较长，就多喷几个加速，加速上限2.1
            elif t > 66 and me.radius ** 2 * (               
                    1 - loss_mass_rate) ** 7 >1.05* other.radius ** 2 + 4 * me.radius ** 2 * loss_mass_rate and 20 * me.radius ** 2 * loss_mass_rate < other.radius ** 2 and len_of_vector(me.veloc)<2.1:
                return directional_angle([0, 1], negative(dist))
            else:
                return None

        def escape1(pos1, pos2, v_relative):  # 躲球函数，直接对着目标喷球
            dist = minus(pos2, pos1)
            dist = true_distance(dist)
            direction = minus(dist, v_relative)
            return directional_angle([0, 1], direction)

        def escape2(me, other):
            return escape1(me.pos, other.pos, minus(me.veloc, other.veloc))

        # 以下是预测函数部分，从场上的球中找出目标

        # 从球的列表bigger_list中选出距离最小和时间最短的球
        def get_mintime_and_mindist(me, bigger_list): 

            #存储时间最短的球及其下标
            i1_min = None
            min1 = None

            #存储距离最小的球及其下标
            i2_min = None
            min2 = None
            for i in range(len(bigger_list)):
                t1 = time_of_collision2(me, bigger_list[i])
                d2 = distance_to_collision(me, bigger_list[i])
                if t1 != None:
                    if i1_min == None:
                        i1_min = i
                        min1 = t1
                    else:
                        if t1 < min1:
                            i1_min = i
                            min1 = t1
                if d2 != None:
                    if i2_min == None:
                        i2_min = i
                        min2 = d2
                    else:
                        if d2 < min2:
                            i2_min = i
                            min2 = d2
            return i1_min, min1, i2_min, min2

        # 返回球自身在场上所有可能吃到的球及吃到他们所需的时间，吃到他们后的位置，速度，半径
        def get_time_r_colpos_coldr_colv_list(me):
            alist, blist, clist = [], [], []
            for i in range(2, len(allcells)):
                cell = allcells[i]
                if cell.dead or cell == me or cell.radius >= me.radius:
                    alist.append(None)
                    blist.append(None)
                    clist.append(None)
                    continue

                dist = distance_of_two_cell(me, cell)
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
# 返回自身在场上所有可能吃到的球及吃到他们所需的时间，获得的面积，吃到他们后的位置，速度，半径
        def get_time_area_colpos_coldr_colv_list(me):  
            alist, blist, clist = [], [], []
            for i in range(2, len(allcells)):
                cell = allcells[i]
                if cell.dead or cell == me:
                    alist.append(None)
                    blist.append(None)
                    clist.append(None)
                    continue
                dist = distance_of_two_cell(me,cell)
                v_relative = minus(me.veloc, cell.veloc)
                t = time_of_collision1(me.radius, cell.radius, dist, v_relative)
                alist.append(t)
                if t:
                    blist.append(cell.radius**2)#半径增量
                    clist.append(after_collision(me, cell))#碰后的位置，半径，速度
                else:
                    blist.append(None)
                    clist.append(None)
            return [alist, blist, clist]

        # 将场上的球分类，返回的列表分别存储比自身大，比自身小，比自身大且较近的球
        def get_various_list(me):
            b_list, s_list, c_list = [], [], []
            for x in allcells:
                if x.radius > my_radius and x.dead == False:
                    b_list.append(x)
                if x.radius < my_radius and x.dead == False and x != opponent:
                    s_list.append(x)
                if x.radius > my_radius and x.dead == False and x != me:
                    d1 = distance_without_radius(me, x)
                    if d1 < 160:
                        c_list.append([x, d1])
            return b_list, s_list, c_list

        # 根据自身半径获取进程参数，决定之后的处理方式
        def get_process():
            if my_radius < 40:
                return 2
            else:
                return 1

        # 对距离处在r1_eat与r2_eat之间的球进行做出是否可以吃的判断
        def eatable(me, other, r1_eat, r2_eat):
            if r1_eat < distance_without_radius(me, other) < r2_eat:  # **********
                N = eject_time(me, other)
                dt = chase_time(me, other)
                collision_cell_area_list=[]
                # 首先要确定吃球的路径是安全的
                eat_able=True
                for big_cell in bigger_list:
                    a = distance_of_two_cell(me,big_cell)
                    b = distance_of_two_cell(me,other)
                    v_relative1=minus(big_cell.veloc,me.veloc)
                    if (point_to_edge(true_position(big_cell), my_position,true_position(other)) < me.radius + big_cell.radius + 50 and
                            dot(a, b) > 0 and dot(a, b) < dot(b,b)) and cross_product(v_relative1,my_velocity)<0:
                        eat_able=False
                        break
                if eat_able:
                    alist,blist,clist = get_time_area_colpos_coldr_colv_list(other)# 小球的（碰撞时间，获得面积，增大后的位置半径和速度）
                    # 然后判断该球会不会在dt时间内变为'不可吃'
                    for i in range(len(alist)):  
                        if alist[i] and alist[i] < dt/1.1:
                            r=clist[i][1]
                            if r>me.radius:
                                eat_able=False
                                break
                            else:
                                collision_cell_area_list.append(blist[i])#增大的面积
                    if eat_able:
                        totalarea = other.radius ** 2 + sum([area for area in collision_cell_area_list])
                        if me.radius ** 2 * (1 - loss_mass_rate) ** (N+5) > totalarea:
                            the_earn = earn(me, other)
                            if the_earn and the_earn>1.05:
                                if the_earn>1.15:
                                    return True,True
                                else:
                                    return True,False
                            else:
                                return False,False

        # 分距离段检索是否具有可吃球，若有则存入列表并结束，否则检索下一个距离段
        def get_eatable_list(smaller_list):
            eat_able_list = []
            if process==1:
                for cell in smaller_list:
                    if eatable(wo, cell, 0, 200) and eatable(wo, cell, 0, 200)[0]:
                        eat_able_list.append([cell, earn(wo, cell)])
                if not eat_able_list:
                    for cell in smaller_list:
                        if eatable(wo, cell, 200, 270) and eatable(wo, cell, 200, 270)[0]:
                            eat_able_list.append([cell, earn(wo, cell)])
                if not eat_able_list:
                    for cell in smaller_list:
                        if eatable(wo, cell, 270, 400) and eatable(wo, cell, 270, 400)[0]:
                            eat_able_list.append([cell, earn(wo, cell)])
                if not eat_able_list:
                    for cell in smaller_list:
                        if eatable(wo, cell, 400, 500) and eatable(wo, cell, 400, 500)[0]:
                            eat_able_list.append([cell, earn(wo, cell)])
            else:
                for cell in smaller_list:
                    if eatable(wo, cell, 0, 200) and eatable(wo, cell, 0, 200)[1]:
                        eat_able_list.append([cell, earn(wo, cell)])
                if not eat_able_list:
                    for cell in smaller_list:
                        if eatable(wo, cell, 200, 270) and eatable(wo, cell, 200, 270)[1]:
                            eat_able_list.append([cell, earn(wo, cell)])
                if not eat_able_list:
                    for cell in smaller_list:
                        if eatable(wo, cell, 270, 400) and eatable(wo, cell, 270, 400)[1]:
                            eat_able_list.append([cell, earn(wo, cell)])
                if not eat_able_list:
                    for cell in smaller_list:
                        if eatable(wo, cell, 400, 500) and eatable(wo, cell, 400, 500)[1]:
                            eat_able_list.append([cell, earn(wo, cell)])                
            return eat_able_list

        # 获取传入列表中收益最大和次大的球
        def get_max_max2_cell_and_earn(eat_able_list):
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
                        max_earn_cell = eat_able_cell[0]
                        max_earn = eat_able_cell[1]
            for eat_able_cell in eat_able_list:
                if max2_earn_cell == None:
                    if eat_able_cell[0] != max_earn_cell:
                        max2_earn_cell = eat_able_cell[0]
                        max2_earn = eat_able_cell[1]
                else:
                    if eat_able_cell[0] != max_earn_cell and max2_earn < eat_able_cell[1]:
                        max2_earn_cell = eat_able_cell[0]
                        max2_earn = eat_able_cell[1]
            return max_earn_cell, max_earn, max2_earn_cell, max2_earn

        # 在time时间内不做操作可以获得的收益（指与较小球发生碰撞）
        def time_tick_static_earn(me, time):
            sum = 0
            for smallcell in smaller_list:
                t = time_of_collision2(me, smallcell)
                if t and t < time:
                    sum += smallcell.radius ** 2
            return sum

        ####################################################################################################
        #以下是具体操作部分

        if my_radius ** 2 > 0.5 * self.totalarea:  # 比赛场上一半面积总和要大时，不做操作
            return None

        process = get_process()#根据自己的半径定义当前的进程

        bigger_list, smaller_list, close_list = get_various_list(wo)

        # 躲避球的部分，首先确保自身安全,放在首位
        t_min_i, min_t, d_min_i, min_d = get_mintime_and_mindist(wo, bigger_list)
        if len(bigger_list) > 5:
            if min_d and min_d / sqrt(my_radius) < 5: # 大球离自身比较近时就躲
                return escape2(wo,bigger_list[d_min_i])

        if min_t and min_t < 60:  # 20帧之内就躲
            return escape2(wo,bigger_list[d_min_i])

        for data in close_list:  # 大于自己且距离较近的球

            # 被该球吃到的时间time_list,半径增radius_list,吃后的位置，半径，速度after_eat_list
            time_list, radius_list, after_eat_list = get_time_r_colpos_coldr_colv_list(data[0])
            for i in range(len(time_list)):
                if time_list[i] != None and after_eat_list[i][1] > my_radius:
                    future_position = plus(my_position, multiplication(time_list[i], my_velocity))
                    if is_intersect([future_position, my_radius, my_velocity], after_eat_list[i]): # 会与该球相接触则躲避
                        return escape2(wo, data[0])
                    else:
                        t = len_of_vector(true_distance(minus(my_position, after_eat_list[i][0]))) - my_radius - after_eat_list[i][1] # 距离过近则躲避
                        if t < 24:
                            return escape2(wo, data[0])

        # 小于自身的球被吃到时间,半径增,after_eat_list吃后的半径，位置，速度
        time_list, radius_list, after_eat_list = get_time_r_colpos_coldr_colv_list(wo)
        for data in close_list:  # 大于自身且距离较近的球
            for i in range(len(time_list)):
                if time_list[i]:  # 可与自己相碰
                    if my_radius + radius_list[i] < data[0].radius:
                        future_position = plus(data[0].pos, multiplication(time_list[i], data[0].veloc))
                        if is_intersect(after_eat_list[i], [future_position, data[0].radius]):
                            return escape2(wo, data[0])
                        else:
                            t = len_of_vector(true_distance(minus(future_position, after_eat_list[i][0]))) - after_eat_list[i][1] - data[0].radius
                            if t and t < 15:
                                return escape2(wo, data[0])

        # 吃球部分，目的时尽快增加自己的半径，同时避免让自己的质量损失太多

        # 设置target
        target = None  ###每次重新选target

        # 设置earn变量，判断target的收益一遍决定选择恰当的吃球函数
        eat_able_list = get_eatable_list(smaller_list)

        # 如果不做操作收益足够大，就不做操作
        if time_tick_static_earn(wo, 18) > my_radius ** 2 * 0.1:
            return None
        elif time_tick_static_earn(wo, 9) > 0:
            return None

        # 选出最大和第二大收益球
        max_earn_cell, max_earn, max2_earn_cell, max2_earn = get_max_max2_cell_and_earn(eat_able_list)

        # 当最大收益球的收益足够大时，设置target为最大收益球
        if (max_earn_cell != None and max_earn >= 1.05 + 0.1 * (
                process - 1) and max2_earn_cell != None and max2_earn < 1.05 + 0.1 * (process - 1)) or (
                max_earn_cell != None and max_earn >= 1.05 + 0.1 * (process - 1) and max2_earn == None):
            target = max_earn_cell
            earn = max_earn
            v_relative = minus(my_velocity, target.veloc)
            dist = minus(target.pos, my_position)

            # 根据损失和收益情况选择吃球函数
            if -2 < eject_time(wo, target) < 20 and earn > 1.32:
                return snipe1(wo, target)  
            elif -2 < eject_time(wo, target) < 20 and earn < 1.32:
                return snipe2(wo, target)

        elif max_earn_cell != None and max_earn >= 1.05 + 0.1 * (
                process - 1) and max2_earn_cell != None and max2_earn >= 1.05 + 0.1 * (process - 1):

            # 当次大收益球的收益与损失比时间明显大于最大收益球时，选择次大收益球
            if (max2_earn - 1) / chase_time(wo, max2_earn_cell) > 1.2 * (max_earn - 1) / chase_time(wo, max_earn_cell):
                target = max2_earn_cell
                earn = max2_earn
            else:
                target = max_earn_cell
                earn = max_earn

            v_relative = minus(my_velocity, target.veloc)
            dist = minus(target.pos, my_position)

            # 根据损失和收益情况选择吃球函数
            if -2 < eject_time(wo, target) < 20 and earn > 1.32:
                return snipe1(wo, target)  
            elif -2 < eject_time(wo, target) < 20 and earn < 1.32:
                return snipe2(wo, target)

        # 当局势比较有利时，选择追击对手，目的不是弄死他，而是让其损失
        if not target:

            # opponent表示对手的球，获取相对距离和速度
            dist = distance_of_two_cell(wo, opponent)
            v_relative = minus(my_velocity, opponent_velocity)
            attack_opponent=True
            if opponent_radius > 5 and 0 < len(bigger_list) < 3:
                if (opponent_radius < my_radius * 0.8 and distance_without_radius(wo, opponent) < 120 and angle(dist, v_relative) < pi / 6) or (len_of_vector(v_relative)<0.2 and my_radius>1.3*opponent_radius and len_of_vector(dist)<120):

                    for y in bigger_list:                     
                        a = distance_of_two_cell(wo, y)
                        if (point_to_edge(true_position(y), my_position,true_position(opponent)) < my_radius + y.radius + 60
                         and dot(a, dist) > 0 and dot(a, dist) < dot(dist,dist)):
                            attack_opponent=False
                            break
                    if attack_opponent:
                        return snipe3(wo, opponent)
