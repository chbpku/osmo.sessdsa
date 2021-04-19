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
# This program is distributed in the hope th                                                                      at it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.


from consts import Consts
import random
import math


class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.runafternumber = 0
        self.saferange = [0, 2 * math.pi]
        self.number = 0
        self.runaftertheta = 0
        self.judge = None
        self.targetid = None
        self.wait=0
        self.stay=False

    def isOK(self, a, b):  #判断两个数是否同号
        if a > 0 and b > 0:
            return True
        elif a < 0 and b < 0:
            return True

    def cal_theta(self, vx, vy):  # 相对于坐标系y轴的角度
        if vx > 0 and vy > 0:
            theta = math.atan2(vx, vy)
        elif vx > 0 and vy < 0:
            theta = math.pi - math.atan2(vx, -vy)
        elif vx < 0 and vy < 0:
            theta = math.pi + math.atan2(-vx, -vy)
        elif vx < 0 and vy > 0:
            theta = 2 * math.pi - math.atan2(-vx, vy)
        elif vx == 0 and vy > 0:
            theta = 0
        elif vx == 0 and vy < 0:
            theta = math.pi
        elif vy == 0 and vx > 0:
            theta = math.pi * 0.5
        elif vy == 0 and vx < 0:
            theta = math.pi * 1.5
        else:
            theta =0
            print('FFFFFFFFF')
        return theta

    def relative_veloc(self, allcells, other):  # 接受id作为参数，计算相对速度
        vx = allcells[self.id].veloc[0]
        vy = allcells[self.id].veloc[1]
        vx_o = allcells[other].veloc[0]
        vy_o = allcells[other].veloc[1]
        vx_r = float(vx_o - vx)
        vy_r = float(vy_o - vy)
        v_r =math.sqrt( (vx_r ** 2 + vy_r ** 2))
        theta_r = self.cal_theta(vx_r, vy_r)
        return [vx_r, vy_r, theta_r, v_r]

    def relative_dist(self, allcells, other):  # 接受index作为参数，计算相对位移
        dx = allcells[self.id].pos[0]
        dy = allcells[self.id].pos[1]
        dx_o = allcells[other].pos[0]
        dy_o = allcells[other].pos[1]
        dx_r = float(dx_o - dx)
        dy_r = float(dy_o - dy)
        theta_r = self.cal_theta(dx_r, dy_r)
        min_x = min(abs(dx_r), abs(dx_r + Consts["WORLD_X"]), abs(dx_r - Consts["WORLD_X"]))
        min_y = min(abs(dy_r), abs(dy_r + Consts["WORLD_Y"]), abs(dy_r - Consts["WORLD_Y"]))
        d = (min_x ** 2 + min_y ** 2) ** 0.5

        return [dx_r, dy_r, theta_r, d]

    def anglestand(self, theta):
        return (theta % (2 * math.pi))


#与躲避有关的函数
    def run3(self,allcells,other,mindistance1):
        r_o = allcells[other].radius
        r = allcells[self.id].radius
        d = mindistance1
        d_theta = self.relative_dist(allcells, other)[2]  # 位移偏角
        v_theta = (math.pi + self.relative_veloc(allcells, other)[2]) % (2 * math.pi)  # 速度偏角
        if ((r + r_o) / d)*0.999>1:
            return None

        s=(0.999*(1-((r + r_o) / d)**2)**0.5)
        theta=self.towardsme(allcells,other)
        if theta and -1*theta >=0.9*s :
            a = 1 * self.relative_dist(allcells, other)[0]
            b = 1 * self.relative_dist(allcells, other)[1]
            beta = (self.cal_theta(a, b)) % (2 * math.pi)
            return beta
        elif self.relative_dist(allcells,other)[3]<=1.5*allcells[self.id].radius:
            a = 1 * self.relative_dist(allcells, other)[0]
            b = 1 * self.relative_dist(allcells, other)[1]
            beta = (self.cal_theta(a, b)) % (2 * math.pi)
            return beta
        else:
            return None

    def run0(self,allcells,other):
        a = self.relative_dist(allcells, other)[0]+0.00001
        b = self.relative_dist(allcells, other)[1]+0.00001
        theta = (self.cal_theta(a, b)+0.5*math.pi) % (2 * math.pi)
        return theta

    def towardsme(self,allcells,other):
        vrx=self.relative_veloc(allcells,other)[0]
        vry=self.relative_veloc(allcells,other)[1]
        v=self.relative_veloc(allcells,other)[3]
        drx=self.relative_dist(allcells,other)[0]
        dry=self.relative_dist(allcells,other)[1]
        d = self.relative_dist(allcells, other)[3]
        if v!=0 and d!=0:
            c=(vrx*drx+vry*dry)/(v*d)
            if c<0 and c>=-1:
                return c
            elif c<-1:
                print("LLLLLLLLLLLLLL")
                return False
        else:
            return False

    def avoidstar(self, allcells):  # 可能会撞的球和需要躲避的球的字典，将字典存在列表内
        me = allcells[self.id]
        avoidstardic = {}
        bvoidstardic = {}
        theta=0
        for i in allcells:
            if i.id == self.id:
                continue
            else:
                kk = allcells.index(i)
                dr = self.relative_dist(allcells, kk)
                dv = self.relative_veloc(allcells, kk)
                threat = float((dr[0] * dv[0] + dr[1] * dv[1]) / ((dr[3] * dv[3]) + 0.001))
                if dr[3] <= 100 + me.radius + i.radius and i.radius >= me.radius - 1 and threat < 0 and threat>=-1:
                    dr = self.relative_dist(allcells, kk)
                    vr = self.relative_veloc(allcells, kk)
                    d = me.radius + i.radius
                    real_delta = math.acos(threat) - math.pi / 2  # 计算安全角
                    if d / dr[3]<=1:
                        theta = math.acos(d / dr[3])
                    if real_delta <= 1.05 * theta and dr[3] <= 50 + me.radius + i.radius:
                        avoidstardic['%d' % real_delta] = i
                    elif not self.isOK(dr[0], vr[0]) and not self.isOK(dr[1], vr[1]) and \
                            self.relative_dist(allcells, kk)[3] <= 30 + me.radius:
                        bvoidstardic['%d' % real_delta] = i

        dic_dist_big = {}
        dic_dist_small = {}
        for i in allcells:
            if (i.dead is False) and i.id != self.id:
                n = allcells.index(i)  # 索引值！！！非常重要
                dx = allcells[self.id].pos[0] - i.pos[0]
                dy = allcells[self.id].pos[1] - i.pos[1]
                min_x = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
                min_y = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
                d = (min_x ** 2 + min_y ** 2) ** 0.5
                # if i.radius>=allcells[self.id].radius and self.towardsme(allcells,n):
                if i.radius >= allcells[self.id].radius and True:
                    dic_dist_big['%d' % n] = d
                elif (i.radius < 0.9 * allcells[self.id].radius and i.radius >= 0.2 * allcells[self.id].radius) \
                        :
                    dic_dist_small['%d' % n] = d


        return [avoidstardic, bvoidstardic,dic_dist_big]

    def avoidone(self, allcells, adic):
        # 接受def avoidstar返回的字典
        minkey1=100
        mindistance1 = 600
        for key, value in adic.items():  # 距离自己最近的大球
            if value < mindistance1:
                minkey1 = int(key)
                mindistance1 = value
        other_id = abs(self.id - 1)
        if minkey1 == other_id:
            theta = self.run0(allcells, minkey1)
            return theta

        if mindistance1 <= 80:
            print('Oh,BIG')
            # theta=self.run2(allcells,minkey1)
            theta = self.run3(allcells, minkey1, mindistance1)
            return theta

    def run_avoid(self, allcells, other):  # 输入要躲避球的cell, 返回要发射的角度
        indexnumber = allcells.index(other)
        dvr = self.relative_veloc(allcells, indexnumber)
        det_beta = dvr[2] + float(math.pi / 2)
        final = det_beta + self.cal_theta(allcells[self.id].veloc[0], allcells[self.id].veloc[1])
        return self.anglestand(final)

#与吃球有关的函数
    def eatstarlist(self, allcells):  # 返回可以吃的球的cells列表
        me = allcells[self.id]
        eatstarlist = []
        for i in allcells:
            if i.id==self.id:
                continue
            elif me.distance_from(i) <= 50 and i.radius <= me.radius*0.7 and i.radius > max(me.radius * 0.3,0.5) :
                indexnumber=allcells.index(i)
                dv=self.relative_veloc(allcells,indexnumber)
                if dv[3]<=2.0:
                    print('Good')
                    eatstarlist.append(i)
        return eatstarlist

    def rotation(self,theta):
        standangle=self.anglestand(theta+math.pi/2)
        if standangle<=math.pi/2:
            return[math.tan(standangle),1]
        elif standangle<=math.pi:
            return[-math.tan(standangle),-1]
        elif standangle<=math.pi*1.5:
            return [-math.tan(standangle),-1]
        else:
            return [math.tan(standangle),1]

    def run_after(self, allcells, other):  # 输入要吃的球的index,返回要发射的球方向和数量
        dv= self.relative_veloc(allcells, other)
        dr = self.relative_dist(allcells, other)
        v_run = 0.5
        refer=(dr[0] * dv[0] + dr[1] * dv[1]) / (dr[3] * dv[3])
        final=None
        number=0
        if  refer<=1 and refer >=-1 and (dv[3] *math.sqrt(1-refer**2) / (v_run+0.001))<=1 :
            vector= self.rotation(dr[2])
            vectorjudge=vector[0]*dv[0]+vector[1]*dv[1]
            if vectorjudge>0:
                det_beta = dr[2]+math.asin(dv[3] * math.sqrt(1-refer**2) / (v_run+0.001))+0.03
                final = det_beta + self.cal_theta(allcells[self.id].veloc[0], allcells[self.id].veloc[1])
                number = v_run * 20
            else:
                det_beta = dr[2] - math.asin(dv[3] * math.sqrt(1-refer**2) / (v_run+0.001))-0.03
                final = det_beta + self.cal_theta(allcells[self.id].veloc[0], allcells[self.id].veloc[1])
                number = v_run * 20
        if final:
            final=self.anglestand(final)
        return [final, number]

    def safe(self, allcells):
        me = allcells[self.id]
        dic = self.avoidstar(allcells)[0]  # 威胁列表
        if dic == None:  # 如果威胁列表为空，则安全
            return True
        else:
            return False

    def collide(self,allcells,other):#传入目标球的cell，返回是否会相撞
        indexother=allcells.index(other)
        dv = self.relative_veloc(allcells, indexother)
        dr = self.relative_dist(allcells, indexother)
        refer = (dr[0] * dv[0] + dr[1] * dv[1]) / (dr[3] * dv[3])
        if refer<=0 and refer >=-1:
            dis=allcells[self.id].distance_from(other)
            compare=math.pi-math.acos(refer)
            if (allcells[self.id].radius+other.radius)/dis<=1 and math.asin((allcells[self.id].radius+other.radius)/dis)>compare+0.03:
                return True
            else:
                return False
        else:
            return False

    def eatstar(self, allcells, elist):  # 接受eatstarlist的返回值
        maxradius=0
        maxcells=None
        maxindex=None
        for i in elist:
            if maxradius<i.radius:
                maxradius=i.radius
                maxcells=i
        if maxcells is not None and self.collide(allcells,maxcells):
            print('oh')
            maxcells=None
        if maxcells is not None:
            maxindex =allcells.index(maxcells)
        return maxindex # 返回距离最近的且安全时要吃的球的index

    def strategy(self, allcells):
        if self.judge and self.number < self.runafternumber:
            self.number += 1
            return self.runaftertheta
        # 吃球加速的过程
        elif self.judge:
            status=False
            for i in allcells:
                if self.targetid==i.id:
                   status=True
            if status and self.wait<=10:
                self.wait+=1
                print('patient')
                return None
            else:
                    self.number = 0
                    self.runafternumber = 0
                    self.runaftertheta = 0
                    self.judge=False
                    self.targetid=None
                    self.wait=0
                    self.stay=False
                    print('done')
                    return None
            # 判断是否吃球

            ########################################################
        else:
            avoidstartotal = self.avoidstar(allcells)
            avoid_one = self.avoidone(allcells, avoidstartotal[2])
            if avoid_one:
                return avoid_one
            # 有危险，躲球
            else:
                eatstarlist = self.eatstarlist(allcells)
                eatstar_one = self.eatstar(allcells, eatstarlist)
                if eatstar_one and not self.judge:
                    strategy = self.run_after(allcells, eatstar_one)
                    if strategy[0] is not None:
                        print('OK')
                        self.runaftertheta = strategy[0]
                        self.runafternumber = strategy[1]
                        self.number = 1
                        self.judge = True
                        self.targetid =allcells[eatstar_one].id
                        return self.runaftertheta
                    # 初次选定吃球的目标
                else:
                    return None

#与安全区有关的函数
    def safearea(self, allcells, adic):  # avoidstarlist返回的列表，返回安全角度范围
        area = [[0, 2 * math.pi]]
        me = allcells[self.id]
        for key, value in adic.items():
            indexnumber = allcells.index(value)
            dr = self.relative_dist(allcells, indexnumber)
            left = (dr[2] - float(key)) % (2 * math.pi)
            right = (dr[2] + float(key)) % (2 * math.pi)
            if left < right:
                area = self.reform(area, [left, right])
            else:  # 如果角度跨越了2pi
                area = self.reform(area, [left, 2 * math.pi])
                area = self.reform(area, [0, right])
        return area



    def thetaOK(self, theta, safelist):#输入角度和安全区，判断角度是否在安全区内
        safe = False
        for i in safelist:
            if theta >= i[0] and theta <= i[1]:
                safe = True
        return safe

    def reform(self, area, theta):  # 生成新的安全角度区域的列表
        left = theta[0]
        right = theta[1]
        brea = []
        i = 0
        l = len(area)
        while i <= l - 1:
            if area[i][0] <= left and area[i][1] >= left:
                a = [area[i][0], left]
                brea.append(a)
            elif area[i][0] <= right and area[i][1] >= right:
                b = [right, area[i][1]]
                brea.append(b)
            elif not (area[i][0] > left and area[i][1] < right):
                brea.append(area[i])
        return brea#一个新的列表，每个元素也是列表，代表区间
