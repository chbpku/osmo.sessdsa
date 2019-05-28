#!/usr/bin/env python3

#####################################################
#                                                   #
#     ______        _______..___  ___.   ______     #
#    /  __  \      /       ||   \/   |  /  __  \    #
#   |  |  |  |    |   (----`|  \  /  | |  |  |  |   #
#   |  |  |  |     \   \    |  |\/|  | |  |  |  |   #
#   |  `--'  | .----)   |   |  |  |  | |  `--'  |   #
#    \______/  |_______/    |__|  |__|  \______/    #
#                                                   #
#                                                   #
#####################################################

# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

from consts import Consts
import math
import copy


class Player():
    def __init__(self, id, arg=None):
        self.id = id

    def norm(self, v):  # 求范数
        return math.sqrt(v[0] ** 2 + v[1] ** 2)

    def chi(self, zj, tag):  # zj是自己星体，tag是目标的星体 主要的功能是拦截吃，目前的问题是还没有完全写好，要处理直接吃的问题
        v_zj = zj.veloc
        v_tag = tag.veloc
        vec_dis = [(zj.pos[0] - tag.pos[0]), (zj.pos[1] - tag.pos[1])]  # 相对向量
        vec_vel = [(v_zj[0] - v_tag[0]), (v_zj[1] - v_tag[1])]
        time = float(self.norm(vec_dis) / self.norm(vec_vel))
        ful_pos = [0, 0]
        ful_pos = tag.pos + [tag.veloc[0] * time, tag.veloc[1] * time]
        vec_u = [ful_pos[0] - zj.pos[0], ful_pos[1] - zj.pos[1]]
        return (math.atan(vec_u[1] / vec_u[0]) + math.pi) % (2 * math.pi)

    def disxy_from(self, me, other):  # 取得目标球体和自己的横纵坐标方向差
        dx = other.pos[0] - me.pos[0]
        dy = other.pos[1] - me.pos[1]
        min_x, min_y = 0, 0
        if abs(dx) == min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"])):
            min_x = dx
        elif abs(dx + Consts["WORLD_X"]) == min(abs(dx), abs(dy + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"])):
            min_x = dx + Consts["WORLD_X"]
        elif abs(dx - Consts["WORLD_X"]) == min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"])):
            min_x = dx - Consts["WORLD_X"]

        if abs(dy) == min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"])):
            min_y = dy
        elif abs(dy + Consts["WORLD_Y"]) == min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"])):
            min_y = dy + Consts["WORLD_Y"]
        elif abs(dy - Consts["WORLD_Y"]) == min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"])):
            min_y = dy - Consts["WORLD_Y"]
        return [min_x, min_y]

    def distance_from(self, me, other):  # 取得目标球体和自己的距离
        dx = other.pos[0] - me.pos[0]
        dy = other.pos[1] - me.pos[1]
        min_x = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
        min_y = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
        return (min_x ** 2 + min_y ** 2) ** 0.5

    def veloc_from(self, me, other):  # 取得目标球体和自己的相对速度
        vx = other.veloc[0] - me.veloc[0]
        vy = other.veloc[1] - me.veloc[1]
        return [vx, vy]
##待解决问题1：躲避玩家；问题2：两球突然变大
    def indanger(self, me, allcells):  # 判断自己周围是否有和比自己大的球体对撞的风险,，并且排除两个球突然变大吃掉自己的风险，cells按距离大小排好           
        def forward(me, other): #需要向前模拟的步数与速度有关
            vm_ = me.veloc
            vm = math.sqrt(vm_[0] ** 2 + vm_[1] ** 2)
            v1_ = other.veloc
            v1 = math.sqrt(v1_[0] ** 2 + v1_[1] ** 2)
            return max(20, 40*vm+30*v1) if other.radius > me.radius else max(20, 50*vm)

        cells = sorted(allcells, key=lambda cell: self.distance_from(me, cell) - cell.radius - me.radius)

        alist = copy.deepcopy(cells)
        me_copy = copy.deepcopy(me)
        count = 0 #简单模拟若干次后的情形
        while count < forward(me_copy, alist[1]):
            me_copy.pos[0] += me_copy.veloc[0]
            me_copy.pos[1] += me_copy.veloc[1]
            me.pos[0] = me.pos[0] % Consts["WORLD_X"]
            me.pos[1] = me.pos[1] % Consts["WORLD_Y"]
            for x in range(len(alist)):
                i = alist[x]
                i.pos[0] += i.veloc[0]
                i.pos[1] += i.veloc[1]                
                i.pos[0] = i.pos[0] % Consts["WORLD_X"]
                i.pos[1] = i.pos[1] % Consts["WORLD_Y"]
                if self.distance_from(me_copy, i) < i.radius + 1.3 * me_copy.radius \
                and i.radius > me_copy.radius and i.id != self.id \
                and self.closer(me_copy, i):
                    #if alist[1].radius > me_copy.radius and x != 1:
                    #    return [1, x]                        
                    #else:
                        #print("aaaaaaaa")
                    return x
            count += 1

        alist = copy.deepcopy(cells)
        me_copy = copy.deepcopy(me)
        if len(alist)>= 3: #排除两个球突然变大吃掉自己的风险
            for cxk in range(1, min(len(alist)-1, 18)): 
                other1 = alist[cxk]
                y = cxk+1
                d_ = self.distance_from(other1, alist[cxk+1])-alist[cxk+1].radius
                for x in range(cxk+1, min(len(alist), 19)):
                    if self.distance_from(other1, alist[x]) - alist[x].radius < d_:
                        d_ = self.distance_from(other1, alist[x]) - alist[x].radius
                        y = x
                other2 = alist[y]
                ozi = other2 if other2.radius > other1.radius else other1
                ozi2 = other1 if other2.radius > other1.radius else other2
                if (other1.radius**2 + other2.radius**2)**0.5 > me_copy.radius and self.closer(other1, other2) and ozi2 != cells[-1]:# and d_ < 2*self.distance_from(other1, me_copy) - me_copy.radius:
                    ob = copy.deepcopy(ozi)
                    os = copy.deepcopy(ozi2)
                    ome = copy.deepcopy(me_copy)
                    i = 1
                    num = 0
                    while i < forward(os, ob):
                        ob.pos[0] += ob.veloc[0]
                        ob.pos[1] += ob.veloc[1]
                        ob.pos[0] = ob.pos[0] % Consts["WORLD_X"]
                        ob.pos[1] = ob.pos[1] % Consts["WORLD_Y"]
                        os.pos[0] += os.veloc[0]
                        os.pos[1] += os.veloc[1]
                        os.pos[0] = os.pos[0] % Consts["WORLD_X"]
                        os.pos[1] = os.pos[1] % Consts["WORLD_Y"]
                        ome.pos[0] += ome.veloc[0]
                        ome.pos[1] += ome.veloc[1]
                        ome.pos[0] = ome.pos[0] % Consts["WORLD_X"]
                        ome.pos[1] = ome.pos[1] % Consts["WORLD_Y"]
                        if (1.15 * os.radius < ome.radius <= 0.9*ob.radius) and (ome.radius + os.radius >= self.distance_from(ome, os)) and (ome.radius + ob.radius < self.distance_from(ome, ob)) and (ob.radius + os.radius < self.distance_from(ob, os)):
                            #print("zzzzzzzzzzz")
                            break
                        elif (1.15 * ob.radius < ome.radius) and ((ome.radius + os.radius >= self.distance_from(ome, os) or ome.radius + ob.radius >= self.distance_from(ome, ob)))and (ob.radius + os.radius < self.distance_from(ob, os)):                        
                            #print("ggggggggggg")
                            break
                        elif ob.radius +  os.radius >= self.distance_from(ob, os):
                            num = 1
                            break
                        i += 1
                    if num != 0:
                        ro = (ob.radius**2 + os.radius**2)**0.5
                        vx = (ob.radius**2*ob.veloc[0] + os.radius**2*os.veloc[0]) / (ob.radius**2 + os.radius**2)
                        vy = (ob.radius**2*ob.veloc[1] + os.radius**2*os.veloc[1]) / (ob.radius**2 + os.radius**2)
                        ob.radius, ob.veloc[0], ob.veloc[1] = ro, vx, vy
                        j = 1
                        while j < forward(ome, ob) * 0.6:
                            ob.pos[0] += vx
                            ob.pos[1] += vy
                            ob.pos[0] = ob.pos[0] % Consts["WORLD_X"]
                            ob.pos[1] = ob.pos[1] % Consts["WORLD_Y"]
                            ome.pos[0] += ome.veloc[0]
                            ome.pos[1] += ome.veloc[0]
                            ome.pos[0] = ome.pos[0] % Consts["WORLD_X"]
                            ome.pos[1] = ome.pos[1] % Consts["WORLD_Y"]
                            if ro + 1.1 * ome.radius >= self.distance_from(ome, ob):
                                #print("cccccccccccc")
                                return cxk
                            j += 1
        return False

    def escape(self, me, lst, ind):#ind为数字时，躲避某个球；ind为2元列表时，同时躲避两个球
        if type(ind) is int:#对着该球喷
            x = self.disxy_from(me, lst[ind])[0]
            y = self.disxy_from(me, lst[ind])[1]
            #print(ind, "bbbbbbbbbbbb")
            return math.atan2(x, y) 
        else:#对着二球中间喷
            x1 = self.disxy_from(me, lst[ind[0]])[0]
            y1 = self.disxy_from(me, lst[ind[0]])[1]            
            x2 = self.disxy_from(me, lst[ind[1]])[0]            
            y2 = self.disxy_from(me, lst[ind[1]])[1]            
            #print((math.atan2(x1, y1) + math.atan2(x2, y2))/2, math.atan2(x1, y1), math.atan2(x2, y2))
            return (math.atan2(x1, y1) + math.atan2(x2, y2))/2

    def closer(self, me, other):  # 判断目标球体是不是在离自己越来越近
        dis = self.distance_from(me, other)
        me.pos[0] += me.veloc[0]
        other.pos[0] += other.veloc[0]
        me.pos[1] += me.veloc[1]
        other.pos[1] += other.veloc[1]
        dist = self.distance_from(me, other)
        return dis > dist

    def not_closer(self, me, other):  # 判断目标球体是不是在离自己越来越远
        if self.closer(me, other):
            return False
        else:
            return True

    def theta(self, v1, v2):  # 计算向量之间的夹角，范围从0到2pi
        angle1 = math.atan2(v1[0], v2[0])
        angle2 = math.atan2(v1[1], v2[1])
        return angle2 - angle1

    def vector_add(self, v1, v2):  # 矢量加法
        final = v1
        final[0] = v1[0] + v2[0]
        final[1] = v1[1] + v2[1]
        return final

    def vector_angle(self, v1, v2):  # 求矢量夹角
        x1, y1 = v1[0], v1[1]
        x2, y2 = v2[0], v2[1]
        angle1 = math.atan2(x1, y1)
        angle2 = math.atan2(x2, y2)
        theta = angle2 - angle1
        return theta + math.pi

    def capture1(self, me, other):  # 粗暴的抓捕方式，直接追逐
        veloc = self.veloc_from(me, other)
        pos = self.disxy_from(me, other)
        final = []
        final.append(20 * veloc[0] + pos[0])
        final.append(20 * veloc[1] + pos[1])
        return math.atan2(final[0], final[1]) + math.pi

    def time(self, me, other):  # me为自己星体，other为目标球体，若目标不会相撞，
        t = 0
        sel = copy.deepcopy(me)
        cel = copy.deepcopy(other)
        while self.distance_from(sel, cel) > sel.radius + cel.radius:
            if self.closer(sel, cel) is not True:
                return False
            t += 1
            sel.pos[0] += sel.veloc[0]
            sel.pos[1] += sel.veloc[1]
            cel.pos[0] += cel.veloc[0]
            cel.pos[1] += cel.veloc[1]
        return t

    def expect(self, me, other):
        sel = copy.deepcopy(me)
        cel = copy.deepcopy(other)
        sel.pos[0] += sel.veloc[0]
        sel.pos[1] += sel.veloc[1]
        cel.pos[0] += cel.veloc[0]
        cel.pos[1] += cel.veloc[1]
        return

    def isclosest(self, me, other):  # 判断何时两个球之间距离最短
        sel = copy.deepcopy(me)
        cel = copy.deepcopy(other)
        initial = self.distance_from(sel, cel)
        if self.closer(sel,cel)is not True:
            return cel
        else:
            while self.distance_from(sel, cel) >= initial:
                sel.pos[0] += sel.veloc[0]
                sel.pos[1] += sel.veloc[1]
                cel.pos[0] += cel.veloc[0]
                cel.pos[1] += cel.veloc[1]
            return cel

    def chase(self, me, other):#吃球函数，直接让球行进至目标球离自己最近的位置
        x = self.disxy_from(me, other)[0]
        y = self.disxy_from(me, other)[1]
        #if self.time(me,other)<=5 and other.id>=2:#如果目标为另外玩家，全力加速吃掉
        #    return None
        return math.atan2(x, y) + math.pi

    def loss(self, sel, cel):
        def norm(v):  # 返回v的2范数
            return math.sqrt(v[0] ** 2 + v[1] ** 2)

        def thet(a, b):  # 向量a到b的有向角([0,2pi))
            if math.sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2)) < 1e-6:
                return 0
            det = a[0] * b[1] - a[1] * b[0]  # ，二维向量叉乘结果大于0，就是由一个向量a正旋转到另一个向量b的角度小于180，小于零就是大于180.等于零就是共线嘛
            jia = (a[0] * b[0] + a[1] * b[1]) / math.sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2))
            if abs(jia) > 1 - 1e-3:
                if jia < 0:
                    return math.pi
                else:
                    return 0
            jia = math.acos(jia)
            if det > 0:
                return 2 * math.pi - jia
            else:
                return jia

        def jia(a, b):  # 向量a,b的无向角[0,pi)
            theta = thet(a, b)
            return math.pi - abs(math.pi - theta)

        # nonlocal Consts
        con_veloc = Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"]  # 喷出速度
        p1 = sel.pos
        p2 = cel.pos
        dis = [p2[0] - p1[0], p2[1] - p1[1]]
        rel_vel = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
        if norm(dis) != 0: 
            jiao1 = (sel.radius + cel.radius) / norm(dis)  # 刚刚好吃到的时候
        else:
            return 0
        if jiao1 < 1:  # 等于1的时候已经吃了
            jiao1 = math.asin(jiao1)
        jiao2 = jia(rel_vel, dis)  # 相对位置和相对速度的夹角
        if jiao2 < jiao1:
            return 0  # 此时已经在轨道里面，滑过去就可以了
        else:  # 速度越大，喷出次数越多。这时候不在滑行的轨道，证明角度不对，还要喷球
            return abs(jiao1 - jiao2) * norm(rel_vel) / con_veloc * (1 + norm(rel_vel) ** 2) + 4  # 返回大概喷多少次，大概的数字

    def price(self, sel, cel):  # 返回吃球之后的增大的倍数，还是估计值，返回值要大于1.4倍，因为是估计的值
        # nonlocal Consts
        rate = Consts["EJECT_MASS_RATIO"]
        sun = self.loss(sel, cel)
        if (1 - rate) ** sun < 1.1 * (cel.radius / sel.radius) ** 2:
            return 0
        else:
            return (1 - rate) ** sun / 1.1 + (cel.radius / sel.radius) ** 2  # 要大于1.18

    def chitime(self, sel, cel):  # 模拟吃球的估计时间：喷球的时间+（相对距离-两个球半径之和）/相对速度 这是一个先喷后滑行吃的过程的时间，不可能一直喷球加速吃，太浪费
        def norm(v):  # 返回v的2范数
            return math.sqrt(v[0] ** 2 + v[1] ** 2)

        p1 = sel.pos
        p2 = cel.pos
        r1 = sel.radius
        r2 = cel.radius
        dis = [p2[0] - p1[0], p2[1] - p1[1]]
        rel_vel = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
        peng = norm(dis) - r1 - r2
        t1 = peng / (max(rel_vel, 0.3))  # 滑行时间
        t2 = self.loss(sel, cel)  # 喷球时间
        return t1 + t2

    def caneat(self, me, other, n):
        me2 = copy.deepcopy(me)
        other2 = copy.deepcopy(other)
        for i in range(n):
            me2.pos[0] += me2.veloc[0]
            me2.pos[1] += me2.veloc[1]
            other2.pos[0] += other2.veloc[0]
            other2.pos[1] += other2.veloc[1]
            if me2.radius + other2.radius >= self.distance_from(me2, other2):
                return True
        return False
    
    def strategy(self, allcells):
        me = allcells[self.id]  # me代表自己的星体
        k = 0 if self.id == 1 else 1
        cells = sorted(allcells, key=lambda cell: self.distance_from(me, cell) - cell.radius - me.radius)  # 按距离大小排列
        if me.radius == max(allcells, key=lambda cell: cell.radius):  # 如果自己是最大的，不动
            return None
        indanger_ =  self.indanger(me, allcells)
        if indanger_ is not False:  # 判断是否在危险区域，如果在危险区域则逃离
            return self.escape(me, cells, indanger_)

        prepare=[]
        for each in cells:
            if each.dead is True or each.id == self.id or each.radius > me.radius:  # 判断死亡或比自己大
                continue
            if each.radius <= me.radius * 0.1:  # 如果半径比小于0.1，说明目标球体比喷射出的还小，不需要判断
                continue
            if self.distance_from(me, each) > 5 * (me.radius + each.radius):  # 星体离自己太远、不判断
                continue
            sun = self.loss(me, each)
            rate = Consts["EJECT_MASS_RATIO"]
            v_r_ = [me.veloc[0] - each.veloc[0], me.veloc[1] - each.veloc[1]]
            if self.caneat(me, each, 8) is False and each != allcells[k] and self.distance_from(me, each) - me.radius - each.radius < 0.25 * me.radius and (rate**0.5+0.03)*me.radius < each.radius < me.radius*(1-rate)**0.5**sun and self.price(me, each) > 1.13 and (self.loss(me, each) > 0 or self.norm(v_r_) < 3.5): # 太近的又不太小的星体赶紧吞下,参数要调整             
                cel = self.isclosest(me, each)
                #print("ddddddddd")
                return self.chase(me, cel)   
            elif each.radius<me.radius and each != allcells[k]:#*(1-rate)**0.5**sun:
                if self.price(me, each) > 1.2:
                    prepare.append(each)
        final=sorted(prepare,key=lambda cell:self.price(me,cell))
        if len(final)==0:
            return None
        else:
            target = final[-1]
            v_r = [me.veloc[0] - target.veloc[0], me.veloc[1] - target.veloc[1]]
            if self.loss(me, target) > 0 or self.norm(v_r) < 0.31:
                cel = self.isclosest(me, target)
                return self.chase(me, cel)




