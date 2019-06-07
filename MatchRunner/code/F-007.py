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
from cell import Cell
import math
import random

class Player():
    def __init__(self, id, arg = None):
        self.id = id
        self.target = None

    def strategy(self, allcells):
        vx0 = allcells[self.id].veloc[0]
        vy0 = allcells[self.id].veloc[1]
        v0 = (vx0 ** 2 + vy0 ** 2) ** 0.5
        nearbyCells=self.selectCell(allcells)
        nearby = sorted(self.selectCell(allcells)[1],key=lambda cell : cell.radius / cell.distance_from(allcells[self.id]))
        #print(len(nearby))
        #print(self.target)
        if len(nearbyCells[0]) > 0:
            for cell in nearbyCells[0]:
                theta = self.avoid(allcells, cell)
                if theta is not None:
                    return theta
                else:
                    return None
        if self.target is not None:
            for cell in nearbyCells[1]:
                if cell.id == self.target and cell.radius<allcells[self.id].radius:
                    return self.eat(allcells, cell)
            else:
                self.target = None
                return None
        elif self.target is None and len(nearby) > 0:
            theta = self.eat(allcells, nearby[-1])
            if theta is not None:
                self.target = nearby[0].id
                return theta
            elif v0 > 3:
                return -math.atan2(vx, vy)
    
    def selectCell(self, allcells):
        cellList = [[], []]
        for i in range(len(allcells)):
            if i != self.id:
                if allcells[i].radius >= allcells[self.id].radius and allcells[self.id].distance_from(allcells[i]) < 50 + allcells[self.id].radius + allcells[i].radius:
                    cellList[0].append(allcells[i])
                if allcells[i].radius<allcells[self.id].radius and allcells[i].radius  > allcells[self.id].radius*0.2 and allcells[self.id].distance_from(allcells[i]) < 30+ allcells[self.id].radius + allcells[i].radius:
                    cellList[1].append(allcells[i])
        return cellList

    def avoid(self, allcells, bigcell):
        rvelocx = allcells[self.id].veloc[0] - bigcell.veloc[0]
        rvelocy = allcells[self.id].veloc[1] - bigcell.veloc[1]
        xdelta = allcells[self.id].pos[0] - bigcell.pos[0]
        ydelta = allcells[self.id].pos[1] - bigcell.pos[1]
        wx = Consts["WORLD_X"]
        wy = Consts["WORLD_Y"]
        if xdelta < -1 * wx / 2:
            dx = xdelta + wx
        elif xdelta > wx / 2:
            dx = xdelta - wx
        else:
            dx = xdelta
        if ydelta < -1 * wy / 2:
            dy = ydelta + wy
        elif ydelta > wy / 2:
            dy = ydelta - wy
        else:
            dy = ydelta

        totalveloc=(rvelocx**2+rvelocy**2)**0.5
        if math.atan2(rvelocy,-rvelocx)<0:
            angle1=math.atan2(rvelocy,-rvelocx)+2*math.pi
        else:
            angle1=math.atan2(rvelocy,-rvelocx)
        if math.atan2(-rvelocy,rvelocx)<0:
            angle2=math.atan2(-rvelocy,rvelocx)+2*math.pi
        else:
            angle2=math.atan2(-rvelocy,rvelocx)
        if not self.ifcollision1(allcells, bigcell):
            return None
        else:
            if not self.ifcollision2(allcells, bigcell):
                if (-rvelocy/rvelocx*dx+dy>0 and rvelocy<0 and rvelocx<0):
                    return angle2
                elif (-rvelocy/rvelocx*dx+dy>0 and rvelocy>0 and rvelocx>0):
                    return angle1
                elif (-rvelocy / rvelocx * dx + dy > 0 and rvelocy < 0 and rvelocx > 0):
                    return angle1
                elif (-rvelocy/rvelocx*dx+dy>0 and rvelocy>0 and rvelocx<0):
                    return angle2
                elif (-rvelocy/rvelocx*dx+dy<0 and rvelocy>0 and rvelocx>0):
                    return angle2
                elif (-rvelocy/rvelocx*dx+dy<0 and rvelocy<0 and rvelocx<0):
                    return angle1
                elif (-rvelocy/rvelocx*dx+dy<0 and rvelocy>0 and rvelocx<0):
                    return angle1
                elif (-rvelocy/rvelocx*dx+dy<0 and rvelocy<0 and rvelocx>0):
                    return angle2
            else:
                #print('c')
                return math.atan2(-dx,-dy)
            
    def ifcollision1(self, allcells, bigcell):#用于预测不发生喷射时小球是否会发生碰撞
        #print('a')
        rvelocx = allcells[self.id].veloc[0] - bigcell.veloc[0]
        rvelocy = allcells[self.id].veloc[1] - bigcell.veloc[1]
        xdelta = -allcells[self.id].pos[0] + bigcell.pos[0]
        ydelta = -allcells[self.id].pos[1] + bigcell.pos[1]
        wx = Consts["WORLD_X"]
        wy = Consts["WORLD_Y"]
        if xdelta < -1 * wx / 2:
            dx = xdelta + wx
        elif xdelta > wx / 2:
            dx = xdelta - wx
        else:
            dx = xdelta
        if ydelta < -1 * wy / 2:
            dy = ydelta + wy
        elif ydelta > wy / 2:
            dy = ydelta - wy
        else:
            dy = ydelta
        mindistance=abs((rvelocy/rvelocx*dx-dy)/(((rvelocy/rvelocx)**2+1)**0.5))
        rplus=allcells[self.id].radius + bigcell.radius
        if mindistance < rplus  and dx*rvelocx+dy*rvelocy>0:
            return True
        else:
            return False
        
    def ifcollision2(self,allcells, bigcell):#用于判定垂直躲避的小球是否会撞到
        #print('b')
        rvelocx = allcells[self.id].veloc[0] - bigcell.veloc[0]
        rvelocy = allcells[self.id].veloc[1] - bigcell.veloc[1]
        xdelta = allcells[self.id].pos[0] - bigcell.pos[0]
        ydelta = allcells[self.id].pos[1] - bigcell.pos[1]
        wx = Consts["WORLD_X"]
        wy = Consts["WORLD_Y"]
        if xdelta < -1 * wx / 2:
            dx = xdelta + wx
        elif xdelta > wx / 2:
            dx = xdelta - wx
        else:
            dx = xdelta
        if ydelta < -1 * wy / 2:
            dy = ydelta + wy
        elif ydelta > wy / 2:
            dy = ydelta - wy
        else:
            dy = ydelta
        rplus = allcells[self.id].radius + bigcell.radius
        ifcollision=False
        for i in range(100):#该参数可以进行调整
            dx=dx+rvelocx
            dy=dy+rvelocy
            distance=(dx**2+dy**2)**0.5
            if distance<rplus:
                ifcollision=True
                break
            else:
                rvelocx += 5 / 99 * (((rvelocy ** 2) / (rvelocx ** 2 + rvelocy ** 2)) ** 0.5)
                rvelocy += 5 / 99 * (((rvelocx ** 2) / (rvelocx ** 2 + rvelocy ** 2)) ** 0.5)
        if ifcollision:
            return True
        else:
            return False

    def KeYiChiDao(self,allcells,smallcell):
        # 我（大球）坐标
        x1 = allcells[self.id].pos[0]
        y1 = allcells[self.id].pos[1]
        # 小球坐标
        x2 = smallcell.pos[0]
        y2 = smallcell.pos[1]
        # 大球速度
        vx1 = allcells[self.id].veloc[0]
        vy1 = allcells[self.id].veloc[1]
        v1 = math.sqrt(vx1 ** 2 + vy1 ** 2)
        # 小球速度
        vx2 = smallcell.veloc[0]
        vy2 = smallcell.veloc[1]
        v2 = math.sqrt(vx2 ** 2 + vy2 ** 2)
        # 两运动轨迹的交点坐标
        x0 = x1 + vx1 * (x1 - x2) / vx2 - vx1
        y0 = y1 + vy1 * (y1 - y2) / vy2 - vy1
        # 小球球心到交点所需时间：
        t_need = (x0 - x2) / vx2
        # 大球若不喷射，在上述时间内能到达的位置：
        x_arrive = x1 + vx1 * t_need
        y_arrive = y1 + vy1 * t_need
        # 这个位置与轨迹交点的距离大小：
        dis = math.sqrt((x_arrive - x0) ** 2 + (y_arrive - y0) ** 2)
        if t_need > 0:
            if dis < allcells[self.id].radius + smallcell.radius:
                return True
    def eat(self, allcells, smallcell):
        # 我（大球）坐标
        x0 = allcells[self.id].pos[0]
        y0 = allcells[self.id].pos[1]
        # 小球坐标
        x1 = smallcell.pos[0]
        y1 = smallcell.pos[1]
        # 相对坐标
        xdelta = x0 - x1
        ydelta = y0 - y1
        wx = Consts["WORLD_X"]
        wy = Consts["WORLD_Y"]
        if xdelta < -1 * wx / 2:
            dx = xdelta + wx
        elif xdelta > wx / 2:
            dx = xdelta - wx
        else:
            dx = xdelta
        if ydelta < -1 * wy / 2:
            dy = ydelta + wy
        elif ydelta > wy / 2:
            dy = ydelta - wy
        else:
            dy = ydelta
        # 确定相对速度
        vx0 = allcells[self.id].veloc[0]
        vy0 = allcells[self.id].veloc[1]
        v0 = (vx0**2+vy0**2)**0.5
        # 小球速度
        vx1 = smallcell.veloc[0]
        vy1 = smallcell.veloc[1]
        dvx = vx0 - vx1
        dvy = vy0 - vy1
        totalv=math.sqrt(dvx**2+dvy**2)
        if math.atan2(dx, dy) < 0:
            dangle = math.atan2(dx, dy) + 2 * math.pi
        else:
            dangle = math.atan2(dx, dy)
        if math.atan2(dvx, dvy) < 0:
            dvangle = math.atan2(dvx, dvy) + 2 * math.pi
        else:
            dvangle = math.atan2(dvx, dvy)
        # 以下代码用于求出角度差值（较小的那个角）
        deltaangle = abs(dangle - dvangle)
        if abs(deltaangle) > math.pi:
            deltaangle = 2 * math.pi - abs(deltaangle)
        # 转向函数
        if self.KeYiChiDao(allcells,smallcell) is True and v0 > 2:
            return None
        if deltaangle < math.pi / 2:
            if dvangle - dangle > 0 and dvangle - dangle < math.pi / 4:
                if self.ifcollision1(allcells, smallcell):
                    return None
                elif dvangle - dangle < math.pi / 48 and (
                        allcells[self.id].veloc[0] ** 2 + allcells[self.id].veloc[1] ** 2) ** 0.5 < 3:
                    return dangle
                else:
                    if dvangle < 3 / 2 * math.pi:
                        return dvangle + math.pi / 2
                    else:
                        return dvangle - 3 / 2 * math.pi
            elif dvangle - dangle > 0 and dvangle - dangle > math.pi * 3 / 2:
                if self.ifcollision1(allcells, smallcell):
                    return None
                elif dvangle - dangle > math.pi * 95 / 48 and (
                        allcells[self.id].veloc[0] ** 2 + allcells[self.id].veloc[1] ** 2) ** 0.5 < 3:
                    return dangle
                else:
                    return dvangle - math.pi / 2
            elif dvangle - dangle < 0 and dvangle - dangle > -math.pi / 2:
                if self.ifcollision1(allcells, smallcell):
                    return None
                elif dvangle - dangle > -math.pi / 48 and (
                        allcells[self.id].veloc[0] ** 2 + allcells[self.id].veloc[1] ** 2) ** 0.5 < 3:
                    return dangle
                else:
                    if dvangle > math.pi / 2:
                        return dvangle - math.pi / 2
                    else:
                        return dvangle + 3 / 2 * math.pi
            elif dvangle - dangle < 0 and dvangle - dangle < -3 / 2 * math.pi:
                if self.ifcollision1(allcells, smallcell):
                    return None
                elif dvangle - dangle < -math.pi * 95 / 48 and (
                        allcells[self.id].veloc[0] ** 2 + allcells[self.id].veloc[1] ** 2) ** 0.5 < 3:
                    return dangle
                else:
                    return dvangle + math.pi / 2
        else:
            if dvangle - math.pi > 0:
                return dvangle - math.pi
            else:
                return dvangle + math.pi



