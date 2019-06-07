# !/usr/bin/env python3
#  
# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

import math
from consts import Consts
from cell import Cell


class Player():
    def __init__(self, id, arg = None):
        self.id = id

    def direction1(self,x, y):# 输入x，y方向的数据，然后输出一个角度，弧度值
        #可以输出速度或者两个球连线的方向
        # 这里方向定义与theta一样，表示与y轴正方向夹角，范围为[0,2Π）
        if y > 0 and x ==0:
            return 0
        elif y < 0 and x == 0:
            return math.pi
        elif y == 0 and x > 0:
            return 0.5*math.pi
        elif y == 0 and x < 0:
            return 1.5*math.pi
        elif x==0 and y==0:
            return 0
        else:
            d = (math.atan(abs(x / y)))
            if x > 0 and y > 0:
                return d
            elif x > 0 and y < 0:
                return  math.pi - d
            elif x < 0 and y < 0:
                return d + math.pi
            else:
                return 2*math.pi-d

    # bcell指向acell
    def direction2(self,acell, bcell):
        #输出两个球体连线的方向
        #已考虑穿墙问题
        dy = acell.pos[1] - bcell.pos[1]+(acell.veloc[1]-bcell.veloc[1])#考虑速度方向  相当于考虑的是下一帧
        dx = acell.pos[0] - bcell.pos[0]+(acell.veloc[0]-bcell.veloc[0])
        minx = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
        miny = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
        if minx == abs(dx):
            x=dx
        elif minx == abs(dx + Consts["WORLD_X"]):
            x=dx + Consts["WORLD_X"]
        else:
            x=dx - Consts["WORLD_X"]
        if miny == abs(dy):
            y=dy
        elif miny == abs(dy + Consts["WORLD_Y"]):
            y=dy + Consts["WORLD_Y"]
        else:
            y= dy - Consts["WORLD_Y"]

        return self.direction1(x, y)
    
    # 吃小球
    # 计算追击方向，考虑小球的未来位置
    def direction4(self, my_cell, cell):
        dy = my_cell.pos[1] - cell.pos[1]+(my_cell.veloc[1]-cell.veloc[1]*15)#考虑速度方向  考虑小球未来的位置15帧
        dx = my_cell.pos[0] - cell.pos[0]+(my_cell.veloc[0]-cell.veloc[0]*15)
        minx = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
        miny = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
        if minx == abs(dx):
            x=dx
        elif minx == abs(dx + Consts["WORLD_X"]):
            x=dx + Consts["WORLD_X"]
        else:
            x=dx - Consts["WORLD_X"]
        if miny == abs(dy):
            y=dy
        elif miny == abs(dy + Consts["WORLD_Y"]):
            y=dy + Consts["WORLD_Y"]
        else:
            y= dy - Consts["WORLD_Y"]

        return self.direction1(x, y)

    def distance_from(self,acell, bcell):
        #输出两个球体之间的最近距离
        dx = acell.pos[0] - bcell.pos[0]
        dy = acell.pos[1] - bcell.pos[1]
        min_x = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
        min_y = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
        return (min_x ** 2 + min_y ** 2) ** 0.5

    def v(self,cell):
        #输出合速度
        return (cell.veloc[0] ** 2 + cell.veloc[1] ** 2) ** 0.5

    def direction3(self,acell,bcell):
        #输出两个球体运动方向和连线方向的夹角
        return abs(self.direction1(acell.veloc[1],acell.veloc[0]) - self.direction2(acell,bcell))

    # 获得速度在向量上的投影
    def get_projection(self, rela_veloc, theta):
        alpha = self.direction1(rela_veloc[0], rela_veloc[1])
        projection = math.cos(alpha-theta) * ((rela_veloc[0]**2 + rela_veloc[1]**2) ** 0.5)
        
        return projection


    def strategy(self, allcells):
        bigcells = [] #存大球
        smallcells = []
        md = 0   #大球离我们最小距离
        mindis = 50        # mindis 最近大球的距离     
        minbigcell = -1    # minbigcell 最近大球

        for i in range(0,len(allcells)):
            if allcells[i].radius > allcells[self.id].radius and i!= self.id:
                distance1 = self.distance_from(allcells[self.id], allcells[i])-allcells[i].radius-allcells[self.id].radius
                
                # 找出最近大球，只考虑躲避它
                if distance1 < mindis:
                    minbigcell = i
                    mindis = distance1
            
            r = allcells[self.id].radius
            if allcells[i].radius < allcells[self.id].radius and i!= self.id and allcells[i].radius > 0.2*allcells[self.id].radius:#排除一些特别小的球
                distance2 = self.distance_from(allcells[self.id], allcells[i]) - allcells[i].radius - allcells[self.id].radius
                dir2=self.direction3(allcells[self.id],allcells[i]) #找出在我们前进方向内的小球
                if r <= 24:
                    if distance2 < 80 and dir2 > math.pi*0.9 and dir2 < math.pi*1.1:#吃球角度还需要调整
                        smallcells.append(allcells[i])
                elif r <= 30:
                    if distance2 < 100 and dir2 > math.pi*0.8 and dir2 < math.pi*1.2:
                        smallcells.append(allcells[i])
                else:
                    if distance2 < 120 and dir2 > math.pi*0.7 and dir2 < math.pi*1.3:
                        smallcells.append(allcells[i]) 

        # 躲避大球
        # rela_veloc 相对速度
        # proj_veloc 相对速度在两球连线上的投影速度
        rela_veloc = [allcells[self.id].veloc[i] - allcells[minbigcell].veloc[i] for i in range(2)] 
        theta = self.direction2(allcells[minbigcell], allcells[self.id])
        proj_veloc = self.get_projection(rela_veloc, theta)

        if proj_veloc > 0:
            if mindis < 50 and mindis / proj_veloc < 30:
                if proj_veloc < 0.5:
                    beta = theta + math.pi * 0.2
                else:
                    beta = theta
                if beta >= 2*math.pi:
                    beta -= 2*math.pi
                return beta

       #吃球函数首先只能吃当前运动方向范围内的小球，不能反向吃球，损失太大，其次要吃一定大小范围内的球，
        smallcells = sorted(smallcells, key=lambda cell: cell.radius)
        if len(smallcells) == 0:#周围没球暂时不动，后续可加入主动吃球函数
            return None

        elif len(smallcells) > 0:
            if smallcells[-1].radius > 60*(allcells[self.id].radius * math.sqrt(Consts["EJECT_MASS_RATIO"])):
                return None
            else:
                return self.direction4(allcells[self.id], smallcells[-1])   # 看到周围最大的小球，然后去追