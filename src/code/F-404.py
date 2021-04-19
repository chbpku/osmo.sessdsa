from math import *
from consts import Consts


class globally:
    isLater = False
    playertime = 0
    working = False
    worktime = 0
    targettime = 0
    number = 0
    aim = 0
    isAlreadyWin = False


class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.target = None
        self.veloc_end = 0
        self.eating = False
        self.last_square = (Consts["DEFAULT_RADIUS"] ** 2) * pi
        self.isLater = False
        self.zhongqi_qiang = False

    def strategy(self, allcells):
        # pragma region BASICS

        # disable printing

        # 返回v的2范数
        def norm(v):
            return sqrt(v[0] ** 2 + v[1] ** 2)

        def square(v):
            return v[0] ** 2 + v[1] ** 2

        # 3坐标a,b,c,返回a到直线bc的距离
        def zhijiao(a, b, c):
            u1 = [c[0] - b[0], c[1] - b[1]]
            u2 = [b[0] - a[0], b[1] - a[1]]
            if norm(u1) == 0:
                return norm(u2), 0
            u = -(u1[0] * u2[0] + u1[1] * u2[1]) / norm(u1)
            # if u<0:
            # print('wrong')
            h2 = u2[0] ** 2 + u2[1] ** 2 - u ** 2  # 随便覆盖变量名不是一个好习惯
            if h2 < 1e-6:
                h2 = 0
            # print(norm(u2) ** 2 - h2)
            return sqrt(h2), sqrt(square(u2) - h2)

        # 向量a到b的有向角([0,2pi))
        def thet(a, b):
            if sqrt(square(a) * square(b)) < 1e-6:
                return 0
            det = a[0] * b[1] - a[1] * b[0]
            jia = (a[0] * b[0] + a[1] * b[1]) / sqrt(square(a) * square(b))
            if abs(jia) > 1 - 1e-3:
                if jia < 0:
                    return pi
                else:
                    return 0
            jia = acos(jia)

            if det > 0:
                return 2 * pi - jia
            else:
                return jia

        def chuan(v):  # 穿屏最小向量(例如坐标[1,1]到坐标[999,499]之间不穿屏向量是[998,498]穿屏向量则是[-2,-2])
            # 只有坐标会用到穿屏函数，速度无论穿不穿都是一样的，不需要穿屏
            nonlocal WX, WY
            lst = [v[0] - WX, v[0], v[0] + WX]
            min1 = abs(lst[0])
            i_min = 0
            for i in range(3):
                if abs(lst[i]) < min1:
                    i_min = i
                    min1 = abs(lst[i])
            v0 = lst[i_min]

            lst = [v[1] - WY, v[1], v[1] + WY]
            min1 = abs(lst[0])
            i_min = 0
            for i in range(3):
                if abs(lst[i]) < min1:
                    i_min = i
                    min1 = abs(lst[i])
            v1 = lst[i_min]

            return [v0, v1]

        # more simple version of chuan
        def chuan_s(v):
            nonlocal WX, WY
            if v[0] > WX / 2:
                v[0] -= WX
            elif v[0] < -WX / 2:
                v[0] += WX
            if v[1] > WY / 2:
                v[1] -= WY
            elif v[1] < -WY / 2:
                v[1] += WY
            return v

        # 向量a,b的无向角[0,pi)
        def jia(a, b):
            theta = thet(a, b)
            return pi - abs(pi - theta)

        def dianz(a, b, c):  # 3坐标a,b,c,返回a到直线bc的距离
            u1 = [c[0] - b[0], c[1] - b[1]]
            u2 = [a[0] - b[0], a[1] - b[1]]
            u = abs(u1[0] * u2[0] + u1[1] * u2[1]) / norm(u1)
            a = u2[0] ** 2 + u2[1] ** 2 - u ** 2
            if a < 1e-6:
                return 0
            else:
                return sqrt(a)

        # 两球sel和cel的距离
        def distance(sel, cel):
            selp = sel.pos
            celp = cel.pos
            return norm(chuan([selp[0] - celp[0], selp[1] - celp[1]]))

        def mydistance(sel, cel):
            selp = sel.pos
            celp = cel.pos
            return chuan([selp[0] - celp[0], selp[1] - celp[1]])

        def dang(r1, r2, dist, v1):
            return norm(dist) - r1 - r2

        def time(r1, r2, dist, v1):
            dist = chuan(dist)
            if norm(v1) < (norm(dist) - r1 - r2) * 0.01:
                return None

            if v1[0] * dist[0] + v1[1] * dist[1] < 0:
                return None
            h = dianz(dist, [0, 0], v1)
            if r1 + r2 < h + 1e-3:
                return None
            else:
                l1 = sqrt((r1 + r2) ** 2 - h ** 2)
                l2 = square(dist) - h ** 2
                if l2 < 1e-4:
                    return None
                l2 = sqrt(l2)
                return (l2 - l1) / norm(v1)

        def qie(sel, cel):
            r1 = sel.radius
            r2 = cel.radius
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            dist = chuan(dist)
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            dist = chuan(dist)
            if norm(v1) < (norm(dist) - r1 - r2) * 0.01:
                return None

            if v1[0] * dist[0] + v1[1] * dist[1] < 0:
                return None
            h = dianz(dist, [0, 0], v1)
            if r1 + r2 < h + 1e-3:
                return None
            else:
                l1 = sqrt((r1 + r2) ** 2 - h ** 2)
                l2 = square(dist) - h ** 2
                if l2 < 1e-4:
                    return None
                l2 = sqrt(l2)
                return (l2 - l1)

        def jiehe(cel1, cel2):
            r1 = cel1.radius
            r2 = cel2.radius
            v1 = cel1.veloc
            v2 = cel1.veloc
            r = sqrt(r1 ** 2 + r2 ** 2)
            v = [(r1 ** 2 * v1[0] + r2 ** 2 * v2[0]) / (r1 ** 2 + r2 ** 2),
                 (r1 ** 2 * v1[1] + r2 ** 2 * v2[1]) / (r1 ** 2 + r2 ** 2)]
            return r, v

        def time1(sel, cel):
            r1 = sel.radius
            r2 = cel.radius
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            dist = chuan(dist)
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]

            return time(r1, r2, dist, v1)

        def jiehe_yu(cel1, cel2):
            t = time1(cel1, cel2)
            if t != None:
                if cel1.radius > cel2.radius:
                    p1 = cel1.pos
                    v1 = cel1.veloc
                    p = [p1[0] + v1[0] * t, p1[1] + v1[1] * t]
                    r, v = jiehe(cel1, cel2)

                else:
                    p2 = cel2.pos
                    v2 = cel2.veloc
                    p = [p2[0] + v2[0] * t, p2[1] + v2[1] * t]
                    r, v = jiehe(cel1, cel2)
            return p, r, v

        def jiao(l1, l2):
            p1 = l1[0]
            p2 = l2[0]
            dist = [p2[0] - p1[0], p2[1] - p1[1]]
            dist = chuan(dist)
            r1 = l1[1]
            r2 = l2[1]
            return norm(dist) < r1 + r2

        WX = Consts["WORLD_X"]
        WY = Consts["WORLD_Y"]
        dv1 = Consts["DELTA_VELOC"]  # 喷射速度
        rat = Consts["EJECT_MASS_RATIO"]
        dv2 = dv1 * Consts["EJECT_MASS_RATIO"]  # 得到速度
        if len(allcells) < 2:
            return None
        sel = allcells[self.id]
        selp = sel.pos
        selv = sel.veloc
        selr = sel.radius
        MassOfAll = 0

        # pragma endregion
        # pragma region IMPORTS
        def chuan1(cel):
            nonlocal sel
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            dist = chuan(dist)
            p = [sel.pos[0] + dist[0], sel.pos[1] + dist[1]]
            return p

        def dang1(sel, cel):  #
            r1 = sel.radius
            r2 = cel.radius
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            return dang(r1, r2, dist, 0)

        def stra3(sel, cel):  # 分段吃球函数,来自AIexample
            def duan(t):  # duan即位所说的分段函数,duan(r1)为修正系数
                if t < 0.7:
                    return t ** 2
                else:
                    return t

            nonlocal dv2
            p1 = sel.pos
            p2 = cel.pos
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            a = [p2[0] - p1[0], p2[1] - p1[1]]
            a = chuan(a)
            p2 = [p1[0] + a[0], p1[1] + a[1]]
            p3 = [p1[0] + v1[0], p1[1] + v1[1]]

            b = [p3[0] - p1[0], p3[1] - p1[1]]
            c = [p2[0] - p3[0], p2[1] - p3[1]]
            theta1 = thet([-v1[0], -v1[1]], c)
            # 在己方速度过小时不采用该吃球函数而是直接飞向目标，因为小速度意味着必须要考虑加速度的离散性，控制不好就会乱喷
            if norm(v1) < 0.3:  # *************
                return thet([0, 1], a) + pi

            if theta1 > pi:
                theta1 = theta1 - 2 * pi

            # 比
            r = abs(theta1 / pi)
            # r1为重要参数(函数参数)******************，不同的r1意味着不同的吃球速度和开销
            r1 = r
            theta = theta1 * duan(r1)
            return thet([0, 1], [-v1[0], -v1[1]]) + theta + pi

        # 引用损失估计函数
        def loss(sel, cel):  # 吃球损失估计，返回吃到cel需要喷球的次数，显然不能精确返回具体数值，看成是一个估计就好
            nonlocal dv2
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            dist = chuan(dist)
            v = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            theta1 = (sel.radius + cel.radius) / norm(dist)
            if theta1 < 1:
                theta1 = asin(theta1)
            jiao = jia(v, dist)
            if jiao < theta1:
                return 0
            # 参数#速度越大loss越大
            else:
                return abs(jiao - theta1) * norm(v) / dv2 * (1 + norm(v) ** 2) + 3

        # 引用估算吃到球的时间的函数
        def howl(sel, cel):  # 预测吃到球cel所需花费时间，估计就好
            t1 = dang1(sel, cel) / max(norm(
                [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]), 0.2)
            t2 = loss(sel, cel)
            return t1 + t2

        # 引用收益函数
        def shouyi(sel, cel):  # 吃球收益估计，返回预测吃到该球后自身质量会变成现在质量的倍数，同上，估计就好
            nonlocal rat
            los = loss(sel, cel)
            # 参数
            if (1 - rat) ** los < 1.1 * cel.radius ** 2 / sel.radius ** 2:
                return None
            else:
                return (1 - rat) ** los / 1.1 + cel.radius ** 2 / sel.radius ** 2

        def stra1_J(sel, cel):  # 吃、狙球函数,本质上与吃球函数相差不大，随意使用
            nonlocal dv2
            p1 = sel.pos
            p2 = cel.pos
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            a = [p2[0] - p1[0], p2[1] - p1[1]]
            a = chuan(a)
            p2 = [p1[0] + a[0], p1[1] + a[1]]
            p3 = [p1[0] + v1[0], p1[1] + v1[1]]

            b = [p3[0] - p1[0], p3[1] - p1[1]]
            c = [p2[0] - p3[0], p2[1] - p3[1]]
            theta1 = thet([-v1[0], -v1[1]], c)
            if theta1 > pi:
                theta1 = theta1 - 2 * pi

            # r1为重要参数******************
            r = abs(theta1 / pi)

            r1 = r
            theta = theta1 * r1 ** 3
            return thet([0, 1], [-v1[0], -v1[1]]) + theta + pi

        def time_li_all_c(cel):  # 和上一函数相同，但同时考虑被吃的情形
            nonlocal allcells
            lst1 = []
            lst2 = []
            lst3 = []
            r1 = cel.radius
            for i in range(2, len(allcells)):
                cel1 = allcells[i]
                if cel1.dead == True or cel1 == cel:  # 改动：吃掉自己不是None
                    lst1.append(None)
                    lst2.append(None)
                    lst3.append(None)
                    continue
                r2 = cel1.radius
                dist = [cel1.pos[0] - cel.pos[0], cel1.pos[1] - cel.pos[1]]
                v1 = [cel.veloc[0] - cel1.veloc[0], cel.veloc[1] - cel1.veloc[1]]
                t = time(r1, r2, dist, v1)
                lst1.append(t)
                if t != None:
                    lst2.append(sqrt(r1 ** 2 + r2 ** 2) - r1)
                    lst3.append(jiehe_yu(cel, cel1))
                else:
                    lst2.append(None)
                    lst3.append(None)

            return [lst1, lst2, lst3]

        # pragma endregion
        # pragma region ESCAPE
        # my escape function is used
        ##################################################
        def time_li_x_c(cel):
            nonlocal allcells
            lst1 = []  # 时间
            lst2 = []  # 半径增加量
            lst3 = []  # 位置，半径，速度
            r1 = cel.radius
            for i in range(2, len(allcells)):
                cel1 = allcells[i]
                if cel1.dead == True or cel1 == cel or cel1.radius >= cel.radius:
                    lst1.append(None)
                    lst2.append(None)
                    lst3.append(None)
                    continue
                r2 = cel1.radius
                dist = [cel1.pos[0] - cel.pos[0], cel1.pos[1] - cel.pos[1]]
                v1 = [cel.veloc[0] - cel1.veloc[0], cel.veloc[1] - cel1.veloc[1]]
                t = time(r1, r2, dist, v1)
                lst1.append(t)
                if t != None:
                    lst2.append(sqrt(r1 ** 2 + r2 ** 2) - r1)
                    lst3.append(jiehe_yu(cel, cel1))
                else:
                    lst2.append(None)
                    lst3.append(None)

            return [lst1, lst2, lst3]

        def stra2(p1, p2, v1, dv2):
            v = [p2[0] - p1[0], p2[1] - p1[1]]
            v = chuan(v)
            v3 = [v[0] - v1[0], v[1] - v1[1]]
            return thet([0, 1], v3)

        def guibi(sel, cell):
            selp = sel.pos
            selv = sel.veloc
            celp = cell.pos
            celv = cell.veloc
            return stra2(selp, celp, [selv[0] - celv[0], selv[1] - celv[1]], dv2)
        #**********************************躲球
        da_li = []
        for x in allcells:
            if x.radius > selr and x.dead == False:
                da_li.append(x)
        i2_min = None
        min2 = None
        i1_min = None
        min1 = None
        for i in range(len(da_li)):
            celp = da_li[i].pos
            celv = da_li[i].veloc
            t1 = time1(sel, da_li[i])
            t2 = qie(sel, da_li[i])
            if t2 != None:  # 搜索最小的
                if i2_min == None:
                    i2_min = i
                    min2 = t2
                else:
                    if t2 < min2:
                        i2_min = i
                        min2 = t2
            if t1 != None:  # 搜索最小的
                if i1_min == None:
                    i1_min = i
                    min1 = t2
                else:
                    if t1 < min2:
                        i1_min = i
                        min1 = t2
        if len(da_li) > 5:
            if min2 != None and min2 / sqrt(selr) < 5:  # 参数
                self.target = None
                self.eating = False
                cell = da_li[i2_min]
                celp = cell.pos
                celv = cell.veloc
                return stra2(selp, celp, [selv[0] - celv[0], selv[1] - celv[1]], dv2)
        if min1 != None and min1 < 60:  # 参数
            self.target = None
            self.eating = False
            cell = da_li[i1_min]
            celp = cell.pos
            celv = cell.veloc
            return stra2(selp, celp, [selv[0] - celv[0], selv[1] - celv[1]], dv2)
        d_lst = []
        for i in range(len(da_li)):
            if allcells[i] != sel:
                celp = da_li[i].pos
                celv = da_li[i].veloc
                t1 = dang(selr, da_li[i].radius, chuan([celp[0] - selp[0], celp[1] - selp[1]]),
                          [selv[0] - celv[0], selv[1] - celv[1]])
                if t1 < 160:
                    d_lst.append([da_li[i], t1])
        for x in d_lst:
            t_l, r_l, c_l = time_li_x_c(x[0])
            for i in range(len(t_l)):
                if t_l[i] != None and c_l[i][1] > selr:
                    p_ = [selp[0] + t_l[i] * selv[0], selp[1] + t_l[i] * selv[1]]
                    if jiao([p_, selr, selv], c_l[i]) == True:
                        self.target = None
                        self.eating = False
                        return guibi(sel, x[0])
                    else:
                        t = dang(selr, c_l[i][1], chuan([c_l[i][0][0] - p_[0], c_l[i][0][1] - p_[1]]),
                                 [selv[0] - c_l[i][2][0], selv[1] - c_l[i][2][1]])
                        if t != None and t < 20:
                            self.target = None
                            self.eating = False
                            return guibi(sel, x[0])
        t_l, r_l, c_l = time_li_x_c(sel)
        for x in d_lst:
            for i in range(len(t_l)):
                if t_l[i] != None:
                    if selr + r_l[i] < x[0].radius:
                        p_ = [x[0].pos[0] + t_l[i] * x[0].veloc[0], x[0].pos[1] + t_l[i] * x[0].veloc[1]]
                        if jiao(c_l[i], [p_, x[0].radius]) == True:
                            self.target = None
                            self.eating = False
                            return guibi(sel, x[0])
                        else:
                            t = dang(c_l[i][1], x[0].radius, chuan([p_[0] - c_l[i][0][0], p_[1] - c_l[i][0][1]]),
                                     [c_l[i][2][0] - x[0].veloc[0], c_l[i][2][1] - x[0].veloc[1]])
                            if t != None and t < 12:
                                self.target = None
                                self.eating = False
                                return guibi(sel, x[0])
        #***************************************************************************************************************
        # pragma endregion
        if globally.isLater == False:
        #    print("mid")

            # 吃----------------------------------------------------
            def qian_qi(allcells):
                def time_chi(sel, cel):
                    nonlocal dv2
                    v0 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
                    v0 = norm(v0)
                    a = dv2 / 2
                    dis = distance(sel, cel)
                    return (sqrt(v0 ** 2 + 4 * a * dis) - v0) / 4 / a + 10

                def chi_qiu(allcells):
                    # ********先判断有没有近在眼前的
                    # 缺陷：没有判断相对速度和吃到的难易程度，仅根据距离和大小来判断
                    near = []
                    near_target = None
                    near_r = 0
                    for i in allcells:  # 这里有参数
                        if distance(sel, i) - sel.radius - i.radius < 30 and norm(
                                i.veloc) < 1 and i.radius ** 2 > sel.radius ** 2 * 0.4 and i.radius < sel.radius*0.95 and loss(
                            sel, i) > 0 and norm(sel.veloc)<0.5:
                            near.append(i)
                    for i in near:
                        if i.radius > near_r:
                            near_target = i
                            near_r = i.radius
                    if near_target != None:
                        # print("near")
                        return stra1_J(sel, near_target)
                    # ***************基础吃球部分
                    # 缺陷：附近有比自己大的球，会严重影响正常吃球
                    if self.target != None:
                        a = loss(sel, self.target)
                        if time_chi(sel, self.target) > 50:
                            #print(a, "xx", time_chi(sel, self.target))
                            self.target = None
                            self.eating = False
                            # print("1")
                    if self.target != None:
                        # print(norm(sel.veloc),"p", self.veloc_end)
                        if norm(sel.veloc) > self.veloc_end / 15 and loss(sel, self.target) <= 0:
                            self.target = None
                            self.eating = True
                            # print("true")
                            return None
                        return stra1_J(sel, self.target)
                    if self.eating == True:
                        now_square = pi * (sel.radius ** 2)
                        if now_square > self.last_square:
                            self.eating = False
                            # print("3")
                        self.last_square = now_square
                        return None
                    lst = []
                    for i in allcells[2:]:
                        square_t = pi * (i.radius ** 2)
                        square_sel = pi * (sel.radius ** 2)
                        if square_sel * 0.9 > square_t and square_t > square_sel * 0.15:
                            for y in da_li:
                                a = chuan([y.pos[0] - selp[0], y.pos[1] - selp[1]])
                                b = chuan([i.pos[0] - selp[0], i.pos[1] - selp[1]])
                                if (dianz(chuan1(y), selp, chuan1(i)) < selr + y.radius + 80 and
                                        a[0] * b[0] + a[1] * b[1] > 0 and a[0] * b[0] + a[1] * b[1] < norm(b) ** 2):
                                    # print("break")
                                    break
                            else:
                                dis = distance(sel, i)
                                n1 = dis * square_sel / square_t / 18
                                n2 = (square_sel - square_t) / (rat * square_sel) * 0.55
                                # print(n1,n2)

                                n = min(n1, n2)
                                veloc_end = sqrt(sel.veloc[0] ** 2 + sel.veloc[1] ** 2) + 0.05 * n
                                shouyi = square_t / dis ** 2 * 100
                                lst.append([i, veloc_end, n, shouyi])
                    k = len(lst)
                    while k > 0:
                        j = 0
                        while j < k - 1:
                            if lst[j + 1][3] > lst[j][3]:
                                lst[j], lst[j + 1] = lst[j + 1], lst[j]
                            j += 1
                        k -= 1
                    if lst != []:
                        self.target = lst[0][0]
                        self.veloc_end = lst[0][1]
                        return stra1_J(sel, self.target)
                    else:
                        return None

                def qiang_qiu(allcells):
                    # 先搞一个列表，存储对对方性价比高的球
                    enemy_eat_0 = []
                    enemy_eat = []
                    me = allcells[self.id]
                    enemy = allcells[1 - self.id]
                    for i in allcells[2:]:

                        # print(500>distance(i,enemy)>300 and time1(enemy,i)!=None,distance(i,enemy)<300 and time1(enemy,i)==None,time1(enemy,i)!=None)

                        if 300 > distance(i, enemy) > 50 and time1(enemy, i) != None:  # 重要参数，仅考虑离对方距离50-300以内的球
                            r, v = jiehe(i, enemy)  # 计算对方把球吃掉后的半径
                            if r > me.radius and enemy.radius < me.radius - 3 and time_chi(me, i) - 0 < time1(enemy, i):
                                # 对方吃完比自己大 and 对方现在比自己小一点（3，重要参数） and 我吃到的时间比对方吃到的时间短，0是待修改参数
                                enemy_eat_0.append(i)  # 加入备选列表进行进一步判断
                                # print("1")
                        elif 300 > distance(i, enemy) > 50 and time1(enemy, i) == None:
                            r, v = jiehe(i, enemy)
                            if r > me.radius and enemy.radius < me.radius - 3:
                                enemy_eat_0.append(i)
                                # print("2")
                        elif time1(enemy, i) != None:
                            r, v = jiehe(i, enemy)
                            if r > me.radius and enemy.radius < me.radius - 3:
                                enemy_eat_0.append(i)
                                # print("3")
                    # enemy_eat_0是初始筛选列表
                    # print(enemy_eat_0)
                    da_li = []
                    for x in allcells:
                        if x.radius > me.radius and x.dead == False:
                            da_li.append(x)
                    for cel in enemy_eat_0:
                        caneat = True  # 以下代码判断是否有大球阻挡
                        for y in da_li:
                            a = chuan([y.pos[0] - selp[0], y.pos[1] - selp[1]])
                            b = chuan([cel.pos[0] - selp[0], cel.pos[1] - selp[1]])
                            if (dianz(chuan1(y), selp, chuan1(cel)) < selr + y.radius + 80 and
                                    a[0] * b[0] + a[1] * b[1] > 0 and a[0] * b[0] + a[1] * b[1] < norm(b) ** 2):
                                caneat = False
                                break
                        if caneat == False:
                            continue  # 以上代码判断是否有大球阻挡
                        shouyi1 = shouyi(sel, cel)  # 以下代码判断收益最大的，直接上去吃
                        if shouyi1 != None:
                            enemy_eat.append([cel, shouyi1])
                        max_shouyi = 0
                        for i in enemy_eat:  # 找到最大的记为target
                            if i[1] > max_shouyi:
                                max_shouyi = i[1]
                                self.target = i[0]
                        # print("target:", target)
                        if self.target != None:
                            return stra1_J(me, self.target)  # 直接冲上去
                        else:
                            return None

                def judge_later(allcells):
                    j = 0
                    for i in allcells:
                        if norm(i.veloc) < 1:
                            j += 1
                    if j < 5:
                        globally.isLater = True
                    print(j)
                        # print("end!")
                if self.target!=None:
                    if self.target.dead==True or self.target.radius>sel.radius:
                        self.target=None
                judge_later(allcells)
                if globally.isLater == True:
                    return None
                x = qiang_qiu(allcells)
                if self.target == None:
                    if x == None:
                        self.zhongqi_qiang = False
                        return chi_qiu(allcells)
                    else:
                        return x
                elif self.zhongqi_qiang == True:
                    return qiang_qiu(allcells)
                else:
                    return chi_qiu(allcells)

            return qian_qi(allcells)
        # pragma endregion
        #***************************************************************************************************************
        else:
            # pragma region ENDGAME
            def AlreadyWin(sel, allcells):  # 判断是否获胜（质量超过50%），一旦获胜立即进入永远地return none

                nonlocal MassOfAll
                if MassOfAll == 0:
                    for i in allcells:
                        if not i.dead:
                            MassOfAll += i.radius ** 2
                if 2 * (sel.radius ** 2) > MassOfAll:
                    return True
                else:
                    return False

            def Watching(sel, cel, work):  # 监控对手的函数：Big brother is watching you.
                # sel是自己，cel是监控的对象（通常为对手），work为监视的操作，
                # 可监视的操作包括：
                # 对手和自己的半径比（谁占优势）；
                # 对手追逐的球是否和自己一样；（包括判断方向、速度、加速度；）
                if work == 'RadioOfRadius':
                    return (sel.radius / cel.radius)  # >1的话我们比较大
                    # 考虑根据这个监控功能分策略执行
                if work == 'Snatch':  # 我们是否可能在抢同一个球
                    goal = Hunting(sel, allcells)
                    if jia([goal[0] - cel[0], goal[1] - cel[1]], sel.veloc) < 0.13 \
                            and howl(cel, goal) < howl(sel, goal) and cel.veloc > 3:
                        # 如果角度对得比较准；时间比我们短，速度也不慢（参数可粗调）；
                        return True

            def LimitVeloc1(sel, theta):  # 功能同上一个函数，只是输入形式变成了角度
                # theta范围0到2pi
                MaxVeloc = 62  # 可调
                if sel.veloc[0] * cos(theta) + sel.veloc[1] * sin(theta) > MaxVeloc:
                    return False  # 意味着可以停止喷射
                else:
                    return True  # 意味着可以继续喷射

            def Hunting(sel, allcells):  # 这个函数试图确定中后局怎么吃球
                Eatable = []  # 可吃列表
                ChosenList = []  # 进一步筛选的列表
                Howsmall = 0.9  # 比例是自己多少以下的球可吃()
                Toosmall = 0.3  # 太小的球也不算在内
                for i in allcells:
                    if (not i.dead) and (Howsmall * sel.radius > i.radius > Toosmall * sel.radius):
                        Eatable.append(i)
                for i in Eatable:
                    NumOfGet = shouyi(sel, i)  # 估算收益是多少
                    BenefitRatio = 1.1  # 获利多少，才前去吃
                    if NumOfGet != None:
                        if NumOfGet > BenefitRatio:
                            ChosenList.append(i)
                if len(ChosenList) == 0:
                    return None

                def judgeFuc(sel, cel):  # 判断一个球值不值得吃
                    return (shouyi(sel, cel) * shouyi(sel, cel) / howl(sel, cel))  # 粗略估计，可调

                bestchoice = None  # 用于记录最佳选择
                bestscore = 0.8  # 用于记录最佳选择的分数,保底是0.8（可调），否则便会return none
                for i in ChosenList:
                    if judgeFuc(sel, i) > bestscore:
                        bestchoice = i
                        bestscore = judgeFuc(sel, i)
                return bestchoice

            # *************以下开始执行***************
            if globally.isAlreadyWin:  # 判断是否已经获胜
                return None
            if AlreadyWin(allcells[self.id], allcells):
                globally.isAlreadyWin = True
                return None
            goal = Hunting(allcells[self.id], allcells)
            if goal is not None:
                goal_theta = stra3(allcells[self.id], goal)
                if LimitVeloc1(allcells[self.id], goal_theta):
                    return goal_theta
                else:
                    return None
            else:
                return None
        # pragma endregion