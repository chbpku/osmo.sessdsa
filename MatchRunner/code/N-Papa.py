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

#from consts import Consts
#from settings import Settings
import random
import math
from consts import Consts

class Player():
    def __init__(self, id, arg = None):
        self.id = id
    
    def relative(self, allcells):
        # 重新选取自身静止的坐标系，计算其他球的相对位置和相对速度
        l = len(allcells)
        rel_allcells = []
        for i in range(l):
            x = (allcells[i].pos[0] - allcells[self.id].pos[0]) % 1000
            y = (allcells[i].pos[1] - allcells[self.id].pos[1]) % 500
            if x > 500:
                x -= 1000
            if y > 250:
                y -= 500
            vx = allcells[i].veloc[0] - allcells[self.id].veloc[0]
            vy = allcells[i].veloc[1] - allcells[self.id].veloc[1]
            r = allcells[i].radius
            d = (x**2 + y **2)**0.5
            v = (vx**2 + vy **2)**0.5
            vr = 0
            if d != 0:
                vr = -(x*vx+y*vy)/d
            vt = (v**2-vr**2)**0.5
            if v**2-vr**2<0:
                vt = 0
            rel_allcells.append([[x, y],[vx,vy],r,d,v,[vr,vt]])
        return rel_allcells

    def time(self, n, allcells,po=(0,0),v=(0,0)):
        # 在假定所有球一直维持当前速度运动并忽略可能发生的撞击的前提下，
        # 判断给定球在一定的帧数内是否会撞上自己，如果是则返回所需帧数
        self_veloc = [allcells[self.id].veloc[0],allcells[self.id].veloc[1]]
        other_veloc = [allcells[n].veloc[0]+v[0],allcells[n].veloc[1]+v[1]]
        self_pos = [allcells[self.id].pos[0],allcells[self.id].pos[1]]
        other_pos = [allcells[n].pos[0]+po[0],allcells[n].pos[1]+po[1]]
        a = 12
        for i in range(a):
            dx = self_pos[0] - other_pos[0]
            dy = self_pos[1] - other_pos[1]
            min_x = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
            min_y = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
            dist = (min_x ** 2 + min_y ** 2) ** 0.5
            # 计算当前的距离
            if allcells[self.id].radius < allcells[n].radius and dist < (allcells[self.id].radius + allcells[n].radius) * 1.2:
                return i  # 给定球大于自身时，为了保持安全距离将相撞的标准放宽至半径和的1.2倍
            elif allcells[self.id].radius >= allcells[n].radius and dist < (allcells[self.id].radius + allcells[n].radius)*0.95:
                return i  # 给定球不大于自身，距离小于半径和时判定相撞
            self_pos[0] = (self_pos[0] + self_veloc[0] * Consts["FRAME_DELTA"]) % Consts["WORLD_X"]
            self_pos[1] = (self_pos[1] + self_veloc[1] * Consts["FRAME_DELTA"]) % Consts["WORLD_Y"]
            other_pos[0] = (other_pos[0] + other_veloc[0] * Consts["FRAME_DELTA"]) % Consts["WORLD_X"]
            other_pos[1] = (other_pos[1] + other_veloc[1] * Consts["FRAME_DELTA"]) % Consts["WORLD_Y"]
            # 计算下一帧两球所处的位置
        else:
            return None
            # 不会相撞时返回None

    def dance_arc(self, n, allcells,rel_allcells):
        #给定一个球，若想俘获它需要朝哪个方向吐
        #(dx,dy)是自己相对于目标的位置向量
        #(dvx,dvy)是目标速度相对于自己速度的速度向量
        dx = -rel_allcells[n][0][0]
        dy = -rel_allcells[n][0][1]
        dvx = rel_allcells[n][1][0]
        dvy = rel_allcells[n][1][1]

        minspeed = max(0.4,rel_allcells[n][5][0])

        if (dvx ** 2 + dvy ** 2) == 0:
            return math.atan2(dx,dy)

        #(dx, dy)和(dvx, dvy)是两个向量，phi表示它们的夹角
        cos_phi = (dx * dvx + dy * dvy) / ((dx ** 2 + dy ** 2) * (dvx ** 2 + dvy ** 2)) ** 0.5
        if cos_phi > 1:
            cos_phi = 1
        elif cos_phi < -1:
            cos_phi = -1
        phi = math.acos(cos_phi)
        
        #theta表示phi最大为多大时，两球仍能相交
        sin_theta = (allcells[self.id].radius*0.9 + allcells[n].radius)/ (allcells[self.id].distance_from(allcells[n]))
        if sin_theta > 1:
            sin_theta = 1
        elif sin_theta < -1:
            sin_theta = -1
        theta = math.asin(sin_theta)        

        #rho表示(dx, dy)与x轴张成的角
        rho = math.atan2(dy, dx)

        if phi < theta:   # 能自然撞上，在相对速度较小的时候加速，否则不动
            if rel_allcells[n][4] < 0.5:
                return math.atan2(dx,dy)
            return None
        else:   # 不能自然撞上，通过喷出球改变角度
            l = minspeed / math.cos(theta)
            x1 = l * math.cos(rho + theta)
            y1 = l * math.sin(rho + theta)
            x2 = l * math.cos(rho - theta)
            y2 = l * math.sin(rho - theta)
            x3 = minspeed * math.cos(rho)
            y3 = minspeed * math.sin(rho)

            d1 = ((x1 - dvx) ** 2 + (y1 - dvy) ** 2) ** 0.5
            d2 = ((x2 - dvx) ** 2 + (y2 - dvy) ** 2) ** 0.5
            d3 = ((x3 - dvx) ** 2 + (y3 - dvy) ** 2) ** 0.5
            if d1 < d2 and d1 < d3:
                return math.atan2(x1 - dvx, y1 - dvy)
            elif d2 < d3:
                return math.atan2(x2 - dvx, y2 - dvy)
            else:
                return math.atan2(x3 - dvx, y3 - dvy)

    def shortest(self, allcells):
        # 找出当前列表中最先撞上自己的球，返回编号和所需帧数
        # 如果没有会撞上自己的球则返回[-1, 10000]
        j = -1  # 编号
        min_time = 10000  # 所需帧数
        for i in range(len(allcells)):
            if i == self.id or allcells[i].radius<0.2*allcells[self.id].radius:
                continue
            coll_time = self.time(i, allcells)
            if coll_time == None:
                continue 
                # 当前被检查的球是自己或者不会与自己相撞，直接跳过
            elif coll_time <= min_time:
                min_time = coll_time
                j = i
        return [j, min_time]

    def co(self,n,allcells,t = 12): #判断吃球的对象是否会在短时间内吃到别的球变得比自己大
        rel_allcells = self.relative(allcells)[:]
        cell_n = rel_allcells[n]
        #吃球时间的预估
        for i in range(int(t)):
            for j in range(len(rel_allcells)):  # 时间i后的状态
                if rel_allcells[j] is not None and j != n:  # 对一些不需要考虑的球进行剔除以减小计算量
                    if 100<(rel_allcells[n][0][0] - rel_allcells[j][0][0])%1000<900 or 100 < (rel_allcells[n][0][1] - rel_allcells[j][0][1])%500<400:
                        rel_allcells[j] = None
                    elif rel_allcells[j][2]<=0.2*allcells[self.id].radius:
                        rel_allcells[j] = None
                    elif j == self.id:
                        rel_allcells[j] = None
                    else:
                        rel_allcells[j][0][0] += rel_allcells[j][1][0] * Consts["FRAME_DELTA"]
                        rel_allcells[j][0][1] += rel_allcells[j][1][1] * Consts["FRAME_DELTA"]

            for l in range(len(rel_allcells)-1):   # 对每一颗球进行判定
                l = (l + n + 1)%len(rel_allcells)
                if rel_allcells[l] is not None and rel_allcells[n] is not None: #如果发生碰撞，将一颗球的状态更新为合并后的球，另一颗记为None
                    if (rel_allcells[n][0][0] - rel_allcells[l][0][0])**2+(rel_allcells[n][0][1] - rel_allcells[l][0][1])**2 <= (rel_allcells[n][2]+rel_allcells[l][2])**2:
                        if rel_allcells[l][2]>allcells[self.id].radius or l == 1-self.id:
                            return 0
                        rel_allcells[n][0][0] = (rel_allcells[n][0][0]*rel_allcells[n][2]**2+rel_allcells[l][0][0]*rel_allcells[l][2]**2)/(rel_allcells[n][2]**2+rel_allcells[l][2]**2)
                        rel_allcells[n][0][1] = (rel_allcells[n][0][1]*rel_allcells[n][2]**2+rel_allcells[l][0][1]*rel_allcells[l][2]**2)/(rel_allcells[n][2]**2+rel_allcells[l][2]**2)
                        rel_allcells[n][1][0] = (rel_allcells[n][1][0]*rel_allcells[n][2]**2+rel_allcells[l][1][0]*rel_allcells[l][2]**2)/(rel_allcells[n][2]**2+rel_allcells[l][2]**2)
                        rel_allcells[n][1][1] = (rel_allcells[n][1][1]*rel_allcells[n][2]**2+rel_allcells[l][1][1]*rel_allcells[l][2]**2)/(rel_allcells[n][2]**2+rel_allcells[l][2]**2)
                        rel_allcells[n][2] = (rel_allcells[n][2]**2+rel_allcells[l][2]**2)**0.5
                        rel_allcells[l] = None
            if  rel_allcells[n][2] > allcells[self.id].radius:   #如果时间t后它比self大则返回时间，否则记为True
                return i
        else:
            return True

    def gain(self,n,allcells,rel_allcells,dist = 30): #对吃球收益的大致判断
        cell_n = rel_allcells[n][:]
        dv1 = max(((cell_n[3]-allcells[self.id].radius - allcells[n].radius)/dist-cell_n[5][0]),0) # 径向速度的大致该变量
        dv2 = cell_n[5][1] # 切向速度的大致该变量
        # if cell_n[3]-allcells[self.id].radius - allcells[n].radius < allcells[n].radius * 3  and dv2  < 2:
        #     dv2 = 0
        cost = (dv1**2+dv2**2)**0.5/0.05 *0.01*math.pi*allcells[self.id].radius**2   # 大致需要喷出的体积
        if math.pi*allcells[self.id].radius**2 - cost/2 <=math.pi*allcells[n].radius**2:   # 收益为负是返回None
            return None
        else:
            return math.pi*allcells[n].radius**2 - cost

        
    def waste(self, n, allcells, rel_allcells):   # 粗略判定目标球和自己之间是否有大球
        cell_n = rel_allcells[n][:]   # 大致划定范围
        if cell_n[0][0] > 0:
            x1, x2 = -10, cell_n[0][0]+10
        if cell_n[0][0] <= 0:
            x1, x2 = cell_n[0][0]-10, 10
        if cell_n[0][1] > 0:
            y1, y2 = -10, cell_n[0][1]+10
        if cell_n[0][1] <= 0:
            y1, y2 = cell_n[0][1]-10, 10
        alpha = self.dance_arc(n, allcells,rel_allcells)
        dx = -rel_allcells[n][0][0]
        dy = -rel_allcells[n][0][1]
        if alpha is None:
            alpha = math.atan2(dx,dy)
        for i in range(len(rel_allcells)):   # 如果存在某大球，撞上大球和吃小球的角度接近则返回认为该小球不可吃
            if allcells[self.id].radius < allcells[i].radius and x1 < allcells[i].pos[0] < x2 and y1 < allcells[i].pos[1] < y2:
                beta = self.dance_arc(i, allcells,rel_allcells)
                if beta is None:
                    beta = math.atan2(dx,dy)
                if abs(alpha - beta) <= 0.05*math.pi:
                    return True
        return False

    def hunt(self, allcells,rel_allcells):
        #从当前所有的球中，筛选半径大于某个阈值的球，选择离自己最近的一个吃掉，返回该球编号
        mini_radius = allcells[self.id].radius * 0.3 #阈值
        #考虑对手，如果对手可吃，则从对手编号开始遍历，否则，直接从2号球开始遍历
        if mini_radius <= allcells[1 - self.id].radius < allcells[self.id].radius:
            mini_num = 1 - self.id
            start = 2
        else:
            mini_num = 2
            start = 3
        lst = [30,100,200,400]   
        for j in range(4):
            if j >= 1 and allcells[self.id].radius <=10*j+10:  # 当半径较大时降低距离所占比重，扩大搜索范围
                break
            gain_max = -0.05*math.pi*allcells[self.id].radius**2 
            
            for i in range(start, len(rel_allcells)):   # 在co和waste符合要求的情况下选择收益最大的球
                gain_i = self.gain(i,allcells,rel_allcells,lst[j])
                if mini_radius <= allcells[i].radius < allcells[self.id].radius and gain_i is not None and gain_i> gain_max:
                    t = min((rel_allcells[i][3]-allcells[self.id].radius-allcells[i].radius)/max(rel_allcells[i][5][0],0.5),int((30*lst[j])**0.5))   # 大致预估吃球时间
                    if self.co(i,allcells,t) is True and self.waste(i, allcells, rel_allcells) is False:
                        allcells_1 = allcells[:i]+allcells[i+1:]
                        first_coll = self.shortest(allcells_1)
                        if not (first_coll[0] != -1 and allcells[first_coll[0]].radius > allcells[self.id].radius and first_coll[1] < 12):
                            mini_num = i
                            gain_max = gain_i
            if gain_max == -0.05*math.pi*allcells[self.id].radius**2:
                continue
            return mini_num


    def strategy(self, allcells):
        rel_allcells = self.relative(allcells)[:]
        first_coll = self.shortest(allcells)
        if first_coll[0] != -1:
            eat = self.co(first_coll[0],allcells,first_coll[1])
            if allcells[first_coll[0]].radius >= allcells[self.id].radius and first_coll[1] < 12:
                # 第一个会撞上自己的球不比自己小
                i = first_coll[0]
                dx = rel_allcells[i][0][0]
                dy = rel_allcells[i][0][1]
                return math.atan2(dx,dy)
            if 0.3*allcells[self.id].radius < allcells[first_coll[0]].radius < allcells[self.id].radius and first_coll[1] < 10:
                if eat is True: # 第一个会撞上自己的球比自己小
                    return None
                if eat is not True:   # 判定当即将撞上自己的球会在撞上自己前先撞上其他球的情况下应该冲上去吃还是跑
                    dx0 = dy0 = 0
                    vx0 = vy0 = 0
                    dx = rel_allcells[first_coll[0]][0][0]
                    dy = rel_allcells[first_coll[0]][0][1]
                    d = rel_allcells[first_coll[0]][3]
                    vx = rel_allcells[first_coll[0]][1][0]
                    vy = rel_allcells[first_coll[0]][1][1]
                    dvx = -0.05 * dx/d
                    dvy = -0.05 * dy/d
                    for i in range(eat):   # 判断改变自己的速度i帧内是否能更早吃到该球
                        dx0 += vx
                        dy0 += vy
                        vx0 += dvx
                        vy0 += dvy
                        vx += dvx
                        vy += dvy
                        t= self.time(first_coll[0],allcells,(dx0,dy0),(vx0,vy0))
                        if t is not None and t < first_coll[0]-3-i:   # 如果可以在它比自己大之前吃到，则冲向它
                            dx = rel_allcells[first_coll[0]][0][0]
                            dy = rel_allcells[first_coll[0]][0][1]
                            return math.atan2(-dx,-dy)
            if eat is not True:
                # 将撞上的球即将变大，则逃跑
                i = first_coll[0]
                dx = rel_allcells[i][0][0]
                dy = rel_allcells[i][0][1]
                return math.atan2(dx,dy)
        else:  # 选择收益最好的球
            target_num = self.hunt(allcells,rel_allcells)
            if target_num != None:
                return self.dance_arc(target_num, allcells,rel_allcells)

