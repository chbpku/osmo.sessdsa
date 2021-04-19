# 在对实战结果进行比较后，只保留了效果较好的代码，其他尝试过的可选方法将在报告中给出
from consts import Consts
from math import *

class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.target = None
        self.arg = arg
        self.target_shouyi = None

    def strategy(self, allcells):
        # 常数
        WX = Consts["WORLD_X"]
        WY = Consts["WORLD_Y"]
        dv1 = Consts["DELTA_VELOC"]  # 喷射速度
        ratio = Consts["EJECT_MASS_RATIO"]  # 喷射的质量比例
        dv2 = dv1 * Consts["EJECT_MASS_RATIO"]  # 得到喷射后的移动速度
        if len(allcells) < 2:
            return None
        cel1 = allcells[self.id]
        cel1_p = cel1.pos
        cel1_v = cel1.veloc
        cel1_r = cel1.radius
        cel2 = allcells[1 - self.id]
        cel2_v = cel2.veloc
        cel2_p = cel2.pos
        cel2_r = cel2.radius

        def vec_minus(a, b):  # 向量减法
            return [a[0] - b[0], a[1] - b[1]]

        def vec_plus(a, b):  # 向量加法
            return [a[0] + b[0], a[1] + b[1]]

        def vec_length(v):  # 返回v的2范数
            return sqrt(v[0] ** 2 + v[1] ** 2)

        def justify_pos(d):
            # 输入为球a到球b(圆心到圆心)的向量，若穿屏距离较小，则将其矫正为穿屏向量，否则保持原来的距离向量
            # cel1(自己),cel2对方
            nonlocal WX, WY
            # 横轴
            d_list = [d[0], d[0] - WX, d[0] + WX]
            # 找出里面绝对值最小的
            i_min = 0
            d_min = abs(d_list[0])
            for i in range(3):
                if abs(d_list[i]) < d_min:
                    i_min = i
                    d_min = abs(d_list[i])
            # 输出绝对值最小的数本身
            d0 = d_list[i_min]
            # 纵轴同上
            d_list = [d[1], d[1] - WY, d[1] + WY]
            # 找出里面绝对值最小的
            i_min = 0
            d_min = abs(d_list[0])
            for i in range(3):
                if abs(d_list[i]) < d_min:
                    i_min = i
                    d_min = abs(d_list[i])
            # 输出绝对值最小的数本身
            d1 = d_list[i_min]
            d = [d0, d1]
            return d

        def justify_pos1(cel):
            # 返回cel2相对cel1的穿屏坐标
            nonlocal cel1
            dist = vec_minus(cel2.pos, cel1.pos)
            dist = justify_pos(dist)
            p = vec_plus(cel1_p, dist)
            return p

        def thet_pi(a, b):  # 向量a,b的无向角[0,pi)
            theta = thet_2pi(a, b)
            return pi - abs(pi - theta)

        def thet_2pi(a, b):  # 向量a到b的有向角([0,2pi))，余弦定理
            if sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2)) < 1e-6:  # 向量长度过小，忽略夹角
                return 0
            det = a[0] * b[1] - a[1] * b[0]
            jia = (a[0] * b[0] + a[1] * b[1]) / sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2))
            if abs(jia) > 1 - 1e-3:  # 特殊情况
                if jia < 0:
                    return pi
                else:
                    return 0
            jia = acos(jia)
            if det > 0:  # 钝角，逆向为正
                return 2 * pi - jia
            else:
                return jia

        def collide_time(r1, r2, dist, v1):  # 两球当前速度下的相撞（切）时间 # 非估计
            dist = justify_pos(dist)
            h = a_to_bc(dist, [0, 0], v1)
            if vec_length(v1) < 0.01 * (vec_length(dist) - r1 - r2) or v1[0] * dist[0] + v1[1] * dist[1] < 0 or r1 + r2 < h + 1e-3:
                return None
            else:
                l1 = sqrt((r1 + r2) ** 2 - h ** 2)
                l2 = vec_length(dist) ** 2 - h ** 2
                if l2 < 1e-4:
                    return None
                l2 = sqrt(l2)
                return (l2 - l1) / vec_length(v1)

        def collide_time1(sel, cel):  # 两球当前速度下的相撞（切）时间 # 非估计
            r1 = sel.radius
            r2 = cel.radius
            dist = vec_minus(cel.pos, sel.pos)
            dist = justify_pos(dist)
            v1 = vec_minus(sel.veloc, cel.veloc)
            return collide_time(r1, r2, dist, v1)

        def collide_distance(sel, cel):  # 自己cel1,不改变当前速度方向，撞击到目标cel2需要行进的距离
            # 自己cel1,不改变当前速度方向，撞击到目标cel2需要行进的距离
            # 可考虑与time(返回相撞需要的时间)函数合并，所以我这里的这个函数几乎没有什么更改
            r1 = sel.radius
            r2 = cel.radius
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            dist = justify_pos(dist)
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]

            dist = justify_pos(dist)
            # 需要极长时间才能相撞的情况下
            if vec_length(v1) < (vec_length(dist) - r1 - r2) * 0.01:
                return None
            # 钝角
            if v1[0] * dist[0] + v1[1] * dist[1] < 0:
                return None
            h = a_to_bc(dist, [0, 0], v1)
            # 撞不上的情况
            if r1 + r2 < h + 1e-3:
                return None
            else:
                l1 = sqrt((r1 + r2) ** 2 - h ** 2)
                l2 = vec_length(dist) ** 2 - h ** 2
                if l2 < 1e-4:
                    return None
                l2 = sqrt(l2)
                return (l2 - l1)

        def if_collide(l1, l2):  # 判断两球是否已经相交
            d = justify_pos(vec_minus(l2[0], l1[0]))  # d为距离
            r1 = l1[1]
            r2 = l2[1]
            return vec_length(d) < r1 + r2

        def distance(r1, r2, distance):
            return vec_length(distance) - r1 - r2

        def distance1(cel1, cel2):  # 返回两者相交距离
            return distance(cel1.radius, cel2.radius, justify_pos(vec_minus(cel1.pos, cel2.pos)))

        def combine_rp(cel1, cel2):  # 返回 结合后半径， 位置 # 非估计

            r1 = cel1.radius
            r2 = cel2.radius
            v1 = cel1.veloc
            v2 = cel2.veloc
            r = sqrt(r1 ** 2 + r2 ** 2)
            # 动量守恒定律
            v = [(r1 ** 2 * v1[0] + r2 ** 2 * v2[0]) / (r1 ** 2 + r2 ** 2), \
                 (r1 ** 2 * v1[1] + r2 ** 2 * v2[1]) / (r1 ** 2 + r2 ** 2)]
            return r, v

        def combine_prv(cel1, cel2):  # 返回 结合后 位置，半径，速度
            crash_time = collide_time1(cel1, cel2)
            if crash_time != None:
                # 合并后的位置以半径大的球为准
                if cel1.radius > cel2.radius:
                    pos = cel1.pos
                    veloc = cel1.veloc
                else:
                    pos = cel2.pos
                    veloc = cel2.veloc
                p = [pos[0] + veloc[0] * crash_time, pos[1] + veloc[1] * crash_time]
                r, v = combine_rp(cel1, cel2)
            return p, r, v

        def eat_time(cel1, cel2):  # 估计
            # nonlocal min_veloc  # 参数之一，用于估计最低平均速度
            t1 = distance1(cel1, cel2) / max(vec_length(vec_minus(cel1.veloc, cel2.veloc)), 0.2)
            t2 = loss(cel1, cel2)
            t = t1 + t2
            return t

        def a_to_bc(a, b, c):
            l1 = vec_length(vec_minus(a, b))
            l2 = vec_length(vec_minus(a, c))
            l3 = vec_length(vec_minus(b, c))
            thet = thet_pi(vec_minus(a, b), vec_minus(a, c))
            if l3 < 1e-6:
                return l1
            else:
                d = l1 * l2 * sin(thet) / l3
                return d

        def stra1(cel1, cel2):
            nonlocal dv2
            vector_v = vec_minus(cel2.veloc, cel1.veloc)  # 相对速度 -v
            vector_p = vec_minus(cel2.pos, cel1.pos)  # 相对距离 a
            vector_p = justify_pos(vector_p)
            theta = thet_2pi(vector_v, vec_plus(vector_p, vector_v))
            if theta > pi:  # 将角度归为[-pi,pi]
                theta = theta - 2 * pi
            ratio = abs(theta / pi)
            if vec_length(vector_v) < 0.3:  # ************* 相对速度小
                return thet_2pi([0, 1], vector_p) + pi  # 直接飞向目标

            def r1(r):
                if r > 0.9:
                    r1 = 1 - 5 * (1 - r)
                else:
                    r1 = r ** 3
                return r1

            return thet_2pi([0, 1], vector_v) + theta * r1(ratio) + pi

        def away_from(cel1, cel2):  # 躲球函数，直接冲着对方下一秒的地方喷射 # guibi + stra2
            vector_v = vec_minus(cel2.veloc, cel1.veloc)  # 相对速度 -v
            vector_p = vec_minus(cel2.pos, cel1.pos)  # 相对距离 a
            vector_p = justify_pos(vector_p)
            return thet_2pi([0, 1], vec_plus(vector_p, vector_v))  # 与y夹角

        def away_from2(cel1, cel2):  # 躲球函数2，对着对方球下一秒切线外一点喷，加上自己喷射的球的半径*2，*2是为了再偏一点
            nonlocal ratio
            vector_v = vec_minus(cel2.veloc, cel1.veloc)  # 相对速度 -v
            vector_p = vec_minus(cel2.pos, cel1.pos)  # 相对距离 a
            vector_p = justify_pos(vector_p)
            vector_next = vec_plus(vector_p, vector_v)
            # 但是是往左偏还是往右偏是不是需要看具体情况呢
            return thet_2pi([0, 1],
                        vector_next)  + 2 * asin((cel2.radius + sqrt(ratio) * 2 * cel1.radius) / vec_length(vector_next))

        def away_from_rival(p1, p2, v1, dv2):
            # 针对对手的躲球函数，不直接对着目标喷球，偏离一定角度
            nonlocal cel2
            nonlocal ratio
            v = justify_pos(vec_minus(p2, p1))  # 当前距离向量
            v3 = vec_minus(v, v1)  # 一帧后距离向量
            sin_pian = (cel2_r + sqrt(ratio) * 2 * cel1.radius) / vec_length(v3)  # 偏角的tan值
            pian = asin(sin_pian)  # 偏角;12是自己定的
            return thet_2pi([0, 1], v3) + pian  # 在对着目标喷的基础上，偏离偏角值

        def benefit(sel, cel1):  # 吃球收益估计，返回预测吃到该球后自身质量会变成现在质量的倍数，同上，估计就好
            nonlocal ratio
            los = loss(sel, cel1)
            # 参数
            if (1 - ratio) ** los < 1.1 * cel1.radius ** 2 / sel.radius ** 2:
                return None
            else:
                return (1 - ratio) ** los / 1.1 + cel1.radius ** 2 / sel.radius ** 2

        def loss(cel1, cel2):
            # 吃球损失估计，返回吃到cel2需要喷球的次数
            nonlocal dv2
            dist = vec_minus(cel2.pos, cel1.pos)
            dist = justify_pos(dist)
            v = vec_minus(cel1.veloc, cel2.veloc)
            theta = (cel1.radius + cel2.radius) / vec_length(dist)
            if theta < 1:  # 两者不相交时
                theta = asin(theta)  # 以目前的相对位置正好能够碰到的角度
                # 用到了原jia函数
            jiao = thet_pi(v, dist)
            if jiao < theta:
                return 0
            # 参数#速度越大loss越大
            else:
                return abs(jiao - theta) * vec_length(v) / dv2 * (1 + vec_length(v) ** 2) + 3

        def big_cells_in_time(cel, time):  # 实际上，这是一种估计变大的方法，
            # time时间内cel结合了其他的球，速度和位置会有所变化，所以在time时间内可能不一定吃的到。
            area = cel.radius ** 2
            t = time
            for i in range(2, len(allcells)):
                cel2 = allcells[i]
                t_ = collide_time1(cel, cel2)  # 相切时间
                if t_ != None and t_ < time:  # cel2 同 cel的碰撞时间< sel撞到cel的预估时间
                    area += cel2.radius ** 2  # 要吃的求
            return area

        def cel2_not_interupt(sel, cel, cel2):  # cel2（路上可能经过的球） cel（target）
            d2 = 30  # 参数
            a = justify_pos(vec_minus(cel2.pos, sel.pos))  # cel2（路上可能经过的球）相对坐标
            b = justify_pos(vec_minus(cel.pos, sel.pos))  # cel（target）相对坐标
            if (a_to_bc(justify_pos1(cel2), sel.pos, justify_pos1(cel)) < cel1_r + cel2.radius + d2
                    and a[0] * b[0] + a[1] * b[1] > 0  # cosθ>0，锐角
                    and a[0] * b[0] + a[1] * b[1] < vec_length(b) ** 2):  # cosθ<(b/a)，cel2 在 sel和cel连线垂线中间:
                return None  # 有大球
            else:
                return cel2

        def eatable_info(cel):  # 返回球cel在场上所有可能吃到的球及吃到他们所需的时间，吃到他们后的位置，速度，半径
            nonlocal allcells
            lst1 = []  # 时间 # 非估计
            lst2 = []  # 增大的半径
            lst3 = []  # 速度
            r1 = cel.radius
            for i in range(2, len(allcells)):
                cel1 = allcells[i]
                if cel1.dead == True or cel1 == cel or cel1.radius >= cel.radius:
                    lst1.append(None)
                    lst2.append(None)
                    lst3.append(None)
                    continue
                r2 = cel1.radius
                dist = vec_minus(cel1.pos, cel.pos)
                v1 = vec_minus(cel.veloc, cel1.veloc)
                t = collide_time(r1, r2, dist, v1)
                lst1.append(t)
                if t != None:
                    lst2.append(sqrt(r1 ** 2 + r2 ** 2) - r1)
                    lst3.append(combine_prv(cel, cel1))
                else:
                    lst2.append(None)
                    lst3.append(None)
            return [lst1, lst2, lst3]

        # 躲大球部分--------------------------------------------
        big_cells = []
        for x in allcells:
            if x.radius > cel1_r and x.dead == False:
                big_cells.append(x)
        # 找到这些球中,碰撞所需时间最小的和碰撞所需距离最小的，他们在big_cells中的下标记为i_mintime和i_mindist
        i_mindist = None  # 碰撞距离最小
        mindist = None
        i_mintime = None  # 碰撞时间最小
        mintime = None
        for i in range(len(big_cells)):
            t1 = collide_time1(cel1, big_cells[i])
            t2 = collide_distance(cel1, big_cells[i])

            if t2 != None:
                if i_mindist == None:
                    i_mindist = i
                    mindist = t2
                else:
                    if t2 < mindist:
                        i_mindist = i
                        mindist = t2

            if t1 != None:
                if i_mintime == None:
                    i_mintime = i
                    mintime = t1
                else:
                    if t1 < mintime:
                        i_mintime = i
                        mintime = t1

        if len(big_cells) > 5:
            if mindist != None and mindist / sqrt(cel1_r) < 5:
                self.target = None
                cel = big_cells[i_mindist]
                return away_from(cel1, cel)

        if mintime != None and mintime < 60:
            self.target = None
            cel = big_cells[i_mintime]
            return away_from2(cel1, cel)

        threat = []
        for i in range(len(big_cells)):  # 在比我大的球中
            if allcells[i] != cel1:
                dist = distance1(cel1, allcells[i])  # 相撞距离
                if dist < 160:
                    threat.append([big_cells[i], dist])
                    # 所有球中与自己相撞距离小于160的列入threat

        # 两种情况的排除
        # 1.身边的大球突然吃到球变大从而吃掉自己的情况
        for x in threat:
            lst_time, lst_deltar, list_cell = eatable_info(x[0])
            # 对于threat中的每一个球，均返回三个列表。lst1吃到球的时间，lst2为吃到后增大的半径，lst3是结合后的[p,r,v]
            for i in range(len(lst_time)):  # 对于每一个大球可能吃到的球
                # 参数
                if lst_time[i] != None and list_cell[i][1] > cel1_r:  # 如果能被大球吃到，且被吃后比我大了
                    p = vec_plus(cel1_p, [lst_time[i] * cel1_v[0], lst_time[i] * cel1_v[1]])  # 大球吃到球时，我所在的位置
                    if if_collide([p, cel1_r, cel1_v], list_cell[i]) == True:  # 如果会撞上，则提前规避
                        return away_from(cel1, x[0])
                    else:  # 如果撞不上
                        t = distance(cel1_r, list_cell[i][1], justify_pos(vec_minus(list_cell[i][0], p)))  # 我与结合后的球的相撞距离
                        if t != None and t < 20:  # 相撞距离过小也规避
                            return away_from(cel1, x[0])

        # 2.要吃的小球先被大球吃掉从而吃掉自己的情况
        lst_time, lst_deltar, list_cell = eatable_info(cel1)  # 以我当前的速度，吃到球的时间，吃到后增大的半径，结合后的[p,r,v]
        for x in threat:  # 对于每一个离我较近的大球
            for i in range(len(lst_time)):  # 对于每一个我能吃到的球
                if lst_time[i] != None:  # 如果该球我能吃到
                    if cel1_r + lst_deltar[i] < x[0].radius:  # 如果我吃完小球还是比该大球小
                        p = [x[0].pos[0] + lst_time[i] * x[0].veloc[0],
                             x[0].pos[1] + lst_time[i] * x[0].veloc[1]]  # 我吃完小球后该大球的位置
                        if if_collide(list_cell[i], [p, x[0].radius, x[0].veloc]) == True:  # 我吃完小球会撞到该大球
                            if x[0].pos == cel2.pos:  # 如果是对手，特殊处理
                                return away_from_rival(cel1_p, x[0].pos, vec_minus(cel1_v, cel2_v), dv2)  ###v1
                            return away_from2(cel1, x[0])  # 提前规避
                        else:  # 不会撞到
                            t = distance(list_cell[i][1], x[0].radius, justify_pos(vec_minus(p, list_cell[i][0])))
                            if t != None and t < 15 and x[0].pos == cel2_p:
                                return away_from_rival(cel1_p, x[0].pos, vec_minus(cel1_v, cel2_v), dv2)
                            if t != None and t < 12:  # 碰撞距离过小也规避
                                return away_from2(cel1, x[0])

        # 吃对手部分------------------------------------------- # 适用于两者距离非常小的时候（中间不可能有大球），先狙为敬
        if distance1(cel1, cel2) < cel1_r and cel2_r < cel1_r * 0.8:  # 两者距离非常小且 我的大小远大于他的大小
            return stra1(cel1, cel2)

        # 吃球部分-------------------------------------------
        d1 = 270  # 参数
        jindu = self.arg['world'].frame / self.arg['world'].total_frames  # 游戏进行程度
        d1 = d1 * (1 + jindu)
        # 比自己小的球们
        small_cells = []
        for i in allcells[2:]:
            # 取距离自己一定范围内的球 且 比自己小的球
            if i.radius < cel1.radius and distance1(cel1, i) < d1:  # 相撞距离<d1 ****************重要参数
                small_cells.append(i)
        sel = cel1
        list_cell_shouyi = []
        for cel in small_cells:
            for cel2 in big_cells:
                if cel2_not_interupt(sel, cel, cel2) == None:  # 确保所有的大球都不在sel cel路上
                    break
            else:
                dt = eat_time(sel, cel)  # dt时间内，要吃的球会不会变得比我大
                cel_area_new = big_cells_in_time(cel, dt)  # cel 在dt时间后变成的新cel ## 按照原来的写，可以节省一些计算时间
                try:
                    if cel1_r ** 2 * (1 - ratio) ** loss(sel, cel) > cel_area_new:

                        # 所有情况检查完毕，将这个小球cel放到list_cell_shouyi列表，并附上对其收益的预测量，++和自己距离
                        shouyi1 = benefit(sel, cel)
                        if shouyi1 != None:
                            list_cell_shouyi.append([cel, shouyi1, distance1(sel, cel)])
                except:
                    None
        max_shouyi_cell = None
        max_shouyi = 0
        le = len(list_cell_shouyi)
        if le != 0:
            list_cell_shouyi = sorted(list_cell_shouyi, key=lambda x: x[1], reverse=True)
            max_shouyi_cell = list_cell_shouyi[0][0]
            max_shouyi = list_cell_shouyi[0][1]
            ### 在 前两个 备选 cell中进行选择
            if le != 1:  # 如果不是只有一个可选目标的话
                if list_cell_shouyi[0][2] - list_cell_shouyi[1][2] > 5 and \
                        list_cell_shouyi[0][1] - list_cell_shouyi[1][1] < 0.1:
                    # 当收益1更近 且 收益0 和收益1 之间差距较小时，取收益1的cell
                    max_shouyi_cell = list_cell_shouyi[1][0]
                    max_shouyi = list_cell_shouyi[1][1]
        if max_shouyi_cell != None and max_shouyi > 1.15:
            #### 如果 距离很短，且改变方向只要花一点的话，那么改一下。

            # 执行吃球，此处设置max1>1.15因为损失函数和收益函数都不是精确的，保守起见在预测收益较大时才选择吃球
            # 所有条件满足，设置target
            target = max_shouyi_cell
            v = vec_minus(sel.veloc, target.veloc)
            list_cell_shouyi1 = sorted(list_cell_shouyi, key=lambda x: x[2], reverse=False)
            if list_cell_shouyi1[0][2] < 3 \
                    and list_cell_shouyi1[0][0].radius > ratio * sel.radius \
                    and list_cell_shouyi[0][1] > 10:  # 两者距离<5, 且对方的半径>喷出的半径（不然亏了）
                return stra1(sel, list_cell_shouyi1[0][0])  # 吃这个球
            # 此处的2个条件(1)吃到目标球的角度还没对，体现在loss>0,或者吃到目标球的速度还不大，体现在norm(v)<参数
            # 0.3********************重要参数
            if vec_length(sel.veloc) < 0.3 or loss(sel, target) > 0:  # 我觉得算绝对速度比较好
                return stra1(sel, target)  # 更改吃球函数