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

    def direction2(self,acell, bcell):
        #输出两个球体连线的方向
        #已考虑穿墙问题
        dy = acell.pos[1] - bcell.pos[1]
        dx = acell.pos[0] - bcell.pos[0]
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
        #我的设想是，如果一个大球进入到安全范围内，如果这个夹角很大，可以不把这个大球认为是有威胁的
        return abs(self.direction1(bcell.veloc[1],bcell.veloc[0]) - self.direction2(acell,bcell))




    def two_cells(self,cells,selfcell):# 对于周围有两个大球的决策情况 还有待讨论
        if abs(self.direction2(cells[0],cells[1])- self.direction2(cells[0],selfcell))<0.35 and abs(self.direction2(cells[0],cells[1])- self.direction2(cells[1],selfcell))<0.35:
            if (self.distance_from(cells[0],selfcell)-cells[0].radius-selfcell.radius)<(self.distance_from(cells[1],selfcell)-cells[1].radius-selfcell.radius):

                return self.direction2(cells[0], selfcell) 
            else:
                return self.direction2(cells[1], selfcell) 


    def strategy(self, allcells):
        bigcells = [] #存大球
        smallcells = []
        md = 0   #大球离我们最小距离
        temp = Cell() 
        #将对自己球产生威胁的球记录到bigcells
        for i in range(0,len(allcells)):
            if allcells[i].radius > allcells[self.id].radius and i!= self.id:
                distance1 = self.distance_from(allcells[self.id], allcells[i])-allcells[i].radius-allcells[self.id].radius
                #这里，dir表示大球运动方向与打球和我们球之间的夹角
                dir1=self.direction3(allcells[self.id],allcells[i])
                #把安全距离设置成与速度有关函数，如果速度过大，相应的安全距离会变大
                if dir1 > 0 and dir1 < math.pi and distance1 < 50: #z找出运动方向可能和我们相交的大球，角度还需要调，有些大球没存进去
                    if md == 0:#第一次随便存一个球，方便与后面大球比较
                        bigcells.append(allcells[i])
                    else:
                        md += 1
                        if distance1 <(self.distance_from(bigcells[0],allcells[self.id])-bigcells[i].radius-allcells[self.id].radius):#与第一个球比较，如果距离我们更近就插入到0位置
                            temp = bigcells[0]
                            bigcells.insert(0,allcells[i])
                            bigcells.insert(md,temp)#插入位置有待讨论
                        else:#如果当前球没有0近，就插最后
                            bigcells.append(allcells[i])
            if allcells[i].radius < allcells[self.id].radius and i!= self.id and allcells[i].radius > 0.3*allcells[self.id].radius:#排除一些特别小的球
                distance2 = self.distance_from(allcells[self.id], allcells[i]) - allcells[i].radius - allcells[self.id].radius
                dir2=self.direction3(allcells[self.id],allcells[i]) #找出在我们前进方向内的小球
                if distance2 < 80 and dir2 > math.pi*0.9 and dir2 < math.pi*1.1:#吃球角度还需要调整
                    smallcells.append(allcells[i])
       
        
       #吃球函数首先只能吃当前运动方向范围内的小球，不能反向吃球，损失太大，其次要吃一定大小范围内的球，
        smallcells = sorted(smallcells, key=lambda cell: cell.radius)
        if len(bigcells) == 0 and len(smallcells) == 0:#周围没球暂时不动，后续可加入主动吃球函数
            return None
        elif len(smallcells) == 0 and len(bigcells) > 0:#周围有大球没小球            
            if len(bigcells) == 1 and (self.distance_from(allcells[self.id], bigcells[0]) - allcells[i].radius - allcells[self.id].radius) <20:
                return self.direction2(bigcells[0], allcells[self.id]) 
            elif len(bigcells) == 2 and (self.distance_from(allcells[self.id], bigcells[0]) - allcells[i].radius - allcells[self.id].radius) <20:
                return self.two_cells(bigcells, allcells[self.id])
            else:                                     
                if (self.distance_from(allcells[self.id], bigcells[0]) - allcells[i].radius - allcells[self.id].radius) <20:#闪躲离我们最近的球
                    return self.direction2(bigcells[0], allcells[self.id])
                else:
                    return None

        elif len(bigcells) == 0 and len(smallcells) > 0:
            if smallcells[-1].radius > 60*(allcells[self.id].radius * math.sqrt(Consts["EJECT_MASS_RATIO"])):
                return None
            else:
                return self.direction2(allcells[self.id], smallcells[-1]) 

        else:                                              #周围有大球也有小球，现在设置为只躲大球
            return self.direction2(bigcells[0], allcells[self.id]) 
                #smallcells.reverse()
                #for i in range(0, len(smallcells)):
                #    choose = True
                 #   for j in range(0, len(bigcells)):
                 #       if abs(self.direction3(allcells[self.id], smallcells[i]) - self.direction3(allcells[self.id],bigcells[j])) <= math.pi / 6:
                 #           choose == False
                 #           return self.direction2(bigcells[j], allcells[self.id]) 
                 #   if choose:
                 #       return self.direction2(allcells[self.id], smallcells[i]) 
                 #       break

       
