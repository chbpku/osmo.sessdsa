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

class Player():
    def __init__(self, id, arg = None):
    	self.id = id

    # 返回相对速度([径向，法向])
    # 用处不大
    def rtveloc(self, cells, me):
        dx = cells.pos[0] - me.pos[0]
        dy = cells.pos[1] - me.pos[1]
        ds = (dx * dx + dy * dy) ** 0.5
        dvx = cells.veloc[0] - me.veloc[0]
        dvy = cells.veloc[1] - me.veloc[1]
        rt = [-(dvx * dx + dvy * dy) / ds,(dvx*dy+dvy*dx)/ds]
        return rt

    # 逃跑
    def escape(self,cell,me):
        # cell方向
        WORLD_X = Consts["WORLD_X"]
        WORLD_Y = Consts["WORLD_Y"]
        dist_vect = [cell.pos[0] - me.pos[0], cell.pos[1] - me.pos[1]]
        if dist_vect[0] > WORLD_X / 2:
            dist_vect[0] = dist_vect[0] - WORLD_X
        if dist_vect[1] > WORLD_Y / 2:
            dist_vect[1] = dist_vect[1] - WORLD_Y
        if dist_vect[0] < - WORLD_X / 2:
            dist_vect[0] = dist_vect[0] + WORLD_X
        if dist_vect[1] < - WORLD_Y / 2:
            dist_vect[1] = dist_vect[1] + WORLD_Y
        theta = math.atan2(dist_vect[0],dist_vect[1])
        # 相对速度方向
        phi = math.atan2(me.veloc[0]-cell.veloc[0],me.veloc[1]-cell.veloc[1])
        # 判断直接向对方中央喷的情况
        # 速度变化比自己速度大 or 马上就要撞进去 
        if Consts["DELTA_VELOC"]*Consts["EJECT_MASS_RATIO"]+1e-3 >= (me.veloc[0]**2+me.veloc[1]**2)**0.5 \
                or self.rtveloc(cell, me)[0]*Consts["FRAME_DELTA"]*5+1e-3 >= cell.distance_from(me)-me.radius-cell.radius or abs(phi-theta) <= 0.2 or self.distance(cell,me,5) <= me.radius+cell.radius+1e-3:
            return theta
        else:
            # 使速度方向改变最大时喷出速度与原速度的夹角
            alpha = math.acos((Consts["DELTA_VELOC"]*Consts["EJECT_MASS_RATIO"])/((me.veloc[0]**2+me.veloc[1]**2)**0.5))
        if alpha >= math.pi/2:
            return theta
        if phi-theta > 0:
            print(abs(phi-theta))
            return phi-alpha
        else:
            print(abs(phi-theta))
            return phi+alpha

    def fast_eat(self,target,me):
        WORLD_X = Consts["WORLD_X"]
        WORLD_Y = Consts["WORLD_Y"]
        dist_vect = [target.pos[0] - me.pos[0], target.pos[1] - me.pos[1]]
        if dist_vect[0] > WORLD_X / 2:
            dist_vect[0] = dist_vect[0] - WORLD_X
        if dist_vect[1] > WORLD_Y / 2:
            dist_vect[1] = dist_vect[1] - WORLD_Y
        if dist_vect[0] < - WORLD_X / 2:
            dist_vect[0] = dist_vect[0] + WORLD_X
        if dist_vect[1] < - WORLD_Y / 2:
            dist_vect[1] = dist_vect[1] + WORLD_Y
        relative_veloc = [target.veloc[0] - me.veloc[0], target.veloc[1] - me.veloc[1]]
        dist_0 = dist_vect

        if (relative_veloc[0] ** 2 + relative_veloc[1] ** 2)< 4:
            for i in range(100):
                dist_vect[0] = dist_vect[0] + relative_veloc[0]*Consts["FRAME_DELTA"]
                dist_vect[1] = dist_vect[1] + relative_veloc[1]*Consts["FRAME_DELTA"]
                dist_nearest = [0, 0]
                dist_nearest[0] = dist_vect[0] - Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"] * dist_vect[0] / self.norm(dist_vect) * (i + 1) * (i + 2) / 2
                dist_nearest[1] = dist_vect[1] - Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"] * dist_vect[1] / self.norm(dist_vect) * (i + 1) * (i + 2) / 2
                if self.norm(dist_nearest) < me.radius + target.radius - 1e-3:
                    theta = math.atan2(dist_nearest[0], dist_nearest[1])
                    return theta + math.pi

        dist_vect[0] = dist_0[0]
        dist_vect[1] = dist_0[1]
        if (relative_veloc[0] ** 2 + relative_veloc[1] ** 2) < 25:
            for i in range(70):
                dist_vect[0] = dist_vect[0] + relative_veloc[0] * Consts["FRAME_DELTA"]
                dist_vect[1] = dist_vect[1] + relative_veloc[1] * Consts["FRAME_DELTA"]
                dist_nearest = [0, 0]
                dist_nearest[0] = dist_vect[0] - Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"] * dist_vect[0] / self.norm(dist_vect) * (i + 1) * (i + 2) / 2
                dist_nearest[1] = dist_vect[1] - Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"] * dist_vect[1] / self.norm(dist_vect) * (i + 1) * (i + 2) / 2
                if self.norm(dist_nearest) < me.radius + target.radius - 1e-3:
                    theta = math.atan2(dist_nearest[0], dist_nearest[1])
                    return theta + math.pi

        dist_vect[0] = dist_0[0]
        dist_vect[1] = dist_0[1]
        if (relative_veloc[0] ** 2 + relative_veloc[1] ** 2) > 25:
            for i in range(50):
                dist_vect[0] = dist_vect[0] + relative_veloc[0]*Consts["FRAME_DELTA"]
                dist_vect[1] = dist_vect[1] + relative_veloc[1]*Consts["FRAME_DELTA"]
                dist_nearest = [0, 0]
                dist_nearest[0] = dist_vect[0] - Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"] * dist_vect[0] / self.norm(dist_vect) * (i + 1) * (i + 2) / 2
                dist_nearest[1] = dist_vect[1] - Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"] * dist_vect[1] / self.norm(dist_vect) * (i + 1) * (i + 2) / 2
                if self.norm(dist_nearest) < me.radius + target.radius - 1e-3:
                    theta = math.atan2(dist_nearest[0], dist_nearest[1])
                    return theta + math.pi

        else:
            theta = math.atan2(dist_0[0], dist_0[1])
            return theta + math.pi
        
    def norm(self,v):
        return math.sqrt(v[0] ** 2 + v[1] ** 2)

    def toescape(self,cell,me,t):
        for i in range(0,t,2):
            if self.distance(cell,me,i)-1e-3< me.radius+cell.radius:
                # 返回距离相撞的时间
                return i
        return False

    def toeat(self,cell,me,t):
        m = cell.radius**2/(me.radius**2*(Consts["EJECT_MASS_RATIO"]))
        for i in range(0,t):
            if self.distance(cell,me,i)-me.radius-cell.radius <= (i+1)**2/2*Consts["FRAME_DELTA"]*Consts["DELTA_VELOC"]*Consts["EJECT_MASS_RATIO"] and m>=i+1:
                return True
        return False

    def safeguard(self, target, me, allcells):
        WORLD_X = Consts["WORLD_X"]
        WORLD_Y = Consts["WORLD_Y"]
        for cell in allcells:
            dist_vect = [cell.pos[0] - target.pos[0], cell.pos[1] - target.pos[1]]
            relative_veloc = [cell.veloc[0] - target.veloc[0], cell.veloc[1] - target.veloc[1]]
            if dist_vect[0] > WORLD_X / 2:
                dist_vect[0] = dist_vect[0] - WORLD_X
            if dist_vect[1] > WORLD_Y / 2:
                dist_vect[1] = dist_vect[1] - WORLD_Y
            if dist_vect[0] < - WORLD_X / 2:
                dist_vect[0] = dist_vect[0] + WORLD_X
            if dist_vect[1] < - WORLD_Y / 2:
                dist_vect[1] = dist_vect[1] + WORLD_Y   
            if dist_vect[0] ** 2 + dist_vect[1] ** 2 < 4:
                if target.radius ** 2 + cell.radius ** 2 > me.radius ** 2 - 1e-3:
                    if (self.norm([dist_vect[0] + relative_veloc[0]*Consts["FRAME_DELTA"], dist_vect[1] + relative_veloc[1]]*Consts["FRAME_DELTA"]) < target.radius + cell.radius) \
                       or (self.norm([dist_vect[0] + 2 * relative_veloc[0]*Consts["FRAME_DELTA"], dist_vect[1] + 2 * relative_veloc[1]*Consts["FRAME_DELTA"]]) < target.radius + cell.radius):
                        return 0
            return 1

    def distance(self,cell,me,t):
        dx = cell.pos[0] + cell.veloc[0]*Consts["FRAME_DELTA"]*t - (me.pos[0] + me.veloc[0]*Consts["FRAME_DELTA"]*t)
        dy = cell.pos[1] + cell.veloc[1]*Consts["FRAME_DELTA"]*t - (me.pos[1] + me.veloc[1]*Consts["FRAME_DELTA"]*t)
        min_x = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
        min_y = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
        return (min_x ** 2 + min_y ** 2) ** 0.5
    

    def strategy(self, allcells):
        me = allcells[self.id]
        # 筛选活着的球好像现在不需要了，但是先留着
        livecells = [cell for cell in allcells if cell != me and not cell.dead]
        nextcells = sorted(livecells, key=lambda cell: cell.distance_from(me)-me.radius-cell.radius)[0:10]
        n = 60
        es = []
        ab = []
        stay = []
        # 按从我最近的开始判断
        for nextcell in nextcells:
            # 比我大的
            if nextcell.radius > me.radius:
                if self.toescape(nextcell,me,n) != False:
                    es.append([nextcell,self.toescape(nextcell,me,n)])
            # 可能比我大的            
            elif me.radius >= nextcell.radius > me.radius * (1 - Consts["EJECT_MASS_RATIO"]) ** (0.5*5):
                if self.distance(nextcell,me,15) < me.radius+nextcell.radius:
                    stay.append(nextcell)
            # 比我小的
            else:
                if self.distance(nextcell,me,15) < me.radius+nextcell.radius:
                    stay.append(nextcell)
                else:
                    if self.toeat(nextcell,me,30) and self.safeguard(nextcell,me,allcells) == 1:
                        ab.append(nextcell)
        if es != []:
            # 优先逃离最先相撞的大球
            es.sort(key = lambda cell:cell[1])
            return self.escape(es[0][0],me)
        elif stay != [] and ab != []:
            stm = sorted(stay,key = lambda cell:cell.radius)[-1]
            abm = sorted(ab,key = lambda cell: cell.radius)[-1]
            if stm.radius>abm.radius:
                return None
            else:
                return self.fast_eat(abm,me)
        elif stay != []:
            return None
        elif ab != []:
            # 优先吃最大的
            abm = sorted(ab, key=lambda cell: cell.radius)[-1]
            return self.fast_eat(abm,me)
        else:
            return None
