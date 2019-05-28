#!/usr/bin/env python3

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
    def __init__(self, id, arg=None):
        self.id = id
    # 返回相对速度：径向和切向
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
        if me.veloc[0] ==0 and me.veloc[1]==0:
            return math.atan2(cell.pos[0]-me.pos[0],cell.pos[1]-me.pos[1])
        theta = math.atan2(cell.pos[0]-me.pos[0],cell.pos[1]-me.pos[1])
        phi = math.atan2(me.veloc[0]-cell.veloc[0],me.veloc[1]-cell.veloc[1])
        phi0 = math.asin((cell.radius+me.radius)/(cell.distance_from(me)+cell.radius+me.radius))
        if Consts["DELTA_VELOC"]*Consts["EJECT_MASS_RATIO"] >= (me.veloc[0]**2+me.veloc[1]**2)**0.5 or me.veloc[0]**2+me.veloc[1]**2 <= 0.001:
            return theta
        else:
            alpha = math.acos((Consts["DELTA_VELOC"]*Consts["EJECT_MASS_RATIO"])/((me.veloc[0]**2+me.veloc[1]**2)**0.5))
        if phi-theta > 0:
            return phi-alpha
        else:
            return phi+alpha
        #me = allcells[self.id]
        #dx = cells.pos[0] - me.pos[0]
        #dy = cells.pos[1] - me.pos[1]
        #return math.atan2(dx, dy)
        
    # 吸收
    def eat(self, cells, allcells):
        me = allcells[self.id]
        dx = me.pos[0] - cells.pos[0]#-2*me.veloc[0]*Consts["FRAME_DELTA"]
        dy = me.pos[1] - cells.pos[1]#-2*me.veloc[1]*Consts["FRAME_DELTA"]
        return math.atan2(dx, dy)

    def toescape(self,cell,me,t):
        vrx = me.veloc[0]-cell.veloc[0]
        vry = me.veloc[1]-cell.veloc[1]
        movex = vrx*t*Consts["FRAME_DELTA"]
        movey = cell.distance_from(me)+me.radius+cell.radius-vry*t*Consts["FRAME_DELTA"]
        theta = math.atan2(cell.pos[0]-me.pos[0],cell.pos[1]-me.pos[1])
        phi = math.atan2(me.veloc[0]-cell.veloc[0],me.veloc[1]-cell.veloc[1])
        phi0 = math.asin((cell.radius+me.radius)/(cell.distance_from(me)+cell.radius+me.radius))
       # phim = math.asin((Consts["DELTA_VELOC"]*Consts["EJECT_MASS_RATIO"])/((me.veloc[0]**2+me.veloc[1]**2)**0.5))
        if abs(theta-phi)<=abs(phi0):
            return True
        else:
            return False
            
        
    
    def strategy(self, allcells):
        # 筛选活着的球
        me = allcells[self.id]
        livecells = [cell for cell in allcells if cell != me and not cell.dead]
        nextcells = sorted(livecells, key=lambda cell: self.rtveloc(cell, me)[0]*Consts["FRAME_DELTA"] / cell.distance_from(me),reverse=True)
        n = 100
        es = []
        ab = []
        stay = []
        # 按从我最近的开始判断
        for nextcell in nextcells[0:10]:
            vr = self.rtveloc(nextcell,me)
            vrn,vrt = vr[0],vr[1]
            # 比我大的
            if nextcell.radius > me.radius:
                if self.toescape(nextcell,me,30):
                    es.append(nextcell)
                    #return self.escape(me,nextcell)
            # 可能比我大的            
            elif me.radius >= nextcell.radius > me.radius * (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5:
                if vrn*Consts["FRAME_DELTA"] >= nextcell.distance_from(me)*n:#在n帧内连线方向上可以接触
                    if abs(vrt*Consts["FRAME_DELTA"]*n) <= (nextcell.radius + me.radius):#n帧后确实可以接触
                        stay.append(nextcell)
                        #return None
            # 比我小的
            else:
                if vrn*Consts["FRAME_DELTA"]*n >= nextcell.distance_from(me):#在n帧内连线方向上可以接触
                    if abs(vrt*Consts["FRAME_DELTA"]*n) <= (nextcell.radius + me.radius):#n帧后确实可以接触
                        stay.append(nextcell)
                        #return None
                    else:
                        # 非常粗糙的要不要追上去判断
                        m = nextcell.radius**2/(me.radius**2*(Consts["EJECT_MASS_RATIO"]))
                        if m*10 >= (nextcell.distance_from(me)/(Consts["FRAME_DELTA"])-abs(vrn))/(Consts["DELTA_VELOC"]*Consts["EJECT_MASS_RATIO"]):
                            ab.append(nextcell)
                            #return self.eat(nextcell,allcells)
        if es != []:
            print("!")
            return self.escape(es[0],me)
        elif stay != []:
            return None
        elif ab != []:
            return self.eat(ab[0],allcells)
        else:
            return None

        return None


