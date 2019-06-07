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
import random
import math
from world import World
import math


def calculator2(a, b, c):
    p = b * b - 4 * a * c
    solvelist = []
    if p >= 0 and a != 0:
        x1 = (-b + p ** (1 / 2)) / (2 * a)
        x2 = (-b - p ** (1 / 2)) / (2 * a)
        solvelist.append(x1)
        solvelist.append(x2)
        return solvelist
    elif a == 0:
        x1 = -c / b
        solvelist.append(x1)
        solvelist.append(x1)
        return solvelist

class Player():
    def __init__(self, id, arg = None):
        self.id = id
        self.deg=None
        self.n=0
        self.target=None
        self.area=0
        self.targetarea=0

    def distance_from(self,allcells, otherid):
        dx = allcells[self.id].pos[0] - allcells[otherid].pos[0]
        dy = allcells[self.id].pos[1] - allcells[otherid].pos[1]
        min_x = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
        min_y = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
        return (min_x ** 2 + min_y ** 2) ** 0.5

    def selfisleft(self,allcells,otherid):
        if allcells[otherid].pos[0]-allcells[self.id].pos[0]>Consts["WORLD_X"]/2 or (allcells[otherid].pos[0]-allcells[self.id].pos[0])<(-Consts["WORLD_X"]/2):
            return False
        else:
            return True

    def slopecalculator(self,allcells,otherid):
        x1 = allcells[otherid].pos[0]
        y1 = allcells[otherid].pos[1]
        x0 = allcells[self.id].pos[0]
        y0 = allcells[self.id].pos[1]
        r = allcells[self.id].radius + allcells[otherid].radius
        a = (-(x0 - x1) ** 2 + r ** 2)
        b = 2 * ((y0 - y1) * (x0 - x1))
        c = r ** 2 - (y0 - y1) ** 2
        p = b * b - 4 * a * c
        if p<0:
            return [0,0]
        return sorted(calculator2(a, b, c))

    def examcrash(self,allcells,i):
        vx = allcells[self.id].veloc[0] - allcells[i].veloc[0]
        vy = allcells[self.id].veloc[1] - allcells[i].veloc[1]
        if self.selfisleft(allcells,i)==True:
            if vx<0:
                return False
            else:
                if vx*self.slopecalculator(allcells,i)[0]<=vy<=vx*self.slopecalculator(allcells,i)[1]:
                    return True
                else:
                    return False
        else:
            if vx>0:
                return False
            else:
                if vx*self.slopecalculator(allcells,i)[1]<=vy<=vx*self.slopecalculator(allcells,i)[0]:
                    return True
                else:
                    return False


    def indanger(self,allcells):
        indanger=False
        for i in range(0,len(allcells)):
            if i==self.id:
                continue
            vx = allcells[self.id].veloc[0] - allcells[i].veloc[0]
            vy = allcells[self.id].veloc[1] - allcells[i].veloc[1]
            v=(vx**2+vy**2)**(1/2)
            if self.distance_from(allcells,i)<1*(v/(Consts["EJECT_MASS_RATIO"]*Consts["DELTA_VELOC"]))*v*Consts["FRAME_DELTA"]+allcells[self.id].radius+allcells[i].radius:
                if allcells[i].radius>=allcells[self.id].radius:
                    if self.examcrash(allcells,i)==True:
                        indanger=True
                        return indanger
        if indanger==False:
            return False

    def closedanger(self,allcells):
        sit=False
        for i in range(0, len(allcells)):
            if i == self.id:
                continue
            if self.distance_from(allcells, i) < (2**0.5)*(allcells[self.id].radius+allcells[i].radius):
                if allcells[self.id].radius<allcells[i].radius:
                    sit=True
                    return [True,i]
        return [sit,None]

    def maxdangerid(self,allcells):
        mindis = 2000
        maxdan = 0
        maxi = 0
        for i in range(0,len(allcells)):
            if i==self.id:
                continue
            vx = allcells[self.id].veloc[0] - allcells[i].veloc[0]
            vy = allcells[self.id].veloc[1] - allcells[i].veloc[1]
            v=(vx**2+vy**2)**(1/2)
            if self.distance_from(allcells,i)<1*(v/(Consts["EJECT_MASS_RATIO"]*Consts["DELTA_VELOC"]))*v*Consts["FRAME_DELTA"]+allcells[self.id].radius+allcells[i].radius:
                if allcells[i].radius>=allcells[self.id].radius:
                    if self.examcrash(allcells,i)==True:
                        if self.distance_from(allcells,i)<mindis:
                            mindis=self.distance_from(allcells,i)
                            maxi=i
        if mindis==2000:
            return None
        else:
            return maxi

    def escapeA(self,allcells):
        i=self.maxdangerid(allcells)
        if i!=None:
            if self.selfisleft(allcells, i) == True:
                thetamax = math.atan(self.slopecalculator(allcells, i)[1])
                thetamin = math.atan(self.slopecalculator(allcells, i)[0])
                vx = allcells[self.id].veloc[0] - allcells[i].veloc[0]
                vy = allcells[self.id].veloc[1] - allcells[i].veloc[1]
                theta0 = math.atan2(vy, vx)
                if thetamax - theta0 > theta0 - thetamin:
                    return -thetamin
                else:
                    return math.pi-thetamax
            else:
                thetamin = math.atan(self.slopecalculator(allcells, i)[0])+math.pi
                thetamax = math.atan(self.slopecalculator(allcells, i)[1])+math.pi
                vx = allcells[self.id].veloc[0] - allcells[i].veloc[0]
                vy = allcells[self.id].veloc[1] - allcells[i].veloc[1]
                theta0 = math.atan2(vy, vx)
                if theta0<0:
                    theta0=theta0+2*math.pi
                if thetamax - theta0 > theta0 - thetamin:
                    return -thetamin
                else:
                    return math.pi-thetamax
        else:
            return None

    def escapeB(self,allcells,i):
        x = allcells[self.id].pos[0] - allcells[i].pos[0]
        y = allcells[self.id].pos[1] - allcells[i].pos[1]
        if x> Consts["WORLD_X"]/2:
            x=x- Consts["WORLD_X"]
        elif x<- Consts["WORLD_X"]/2:
            x=x+ Consts["WORLD_X"]
        else:
            x=x
        if y> Consts["WORLD_Y"]/2:
            y=y- Consts["WORLD_Y"]
        elif x<- Consts["WORLD_Y"]/2:
            y=y+ Consts["WORLD_Y"]
        else:
            y=y
        theta0=math.atan2(y,x)
        return math.pi/2-theta0+math.pi

    def free_farm(self, allcells):
        deltav = Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"]
        scorelist = []
        idlist = []
        anglelist = []
        nlist = []
        maxscore = 0
        imax = 0
        for i in range(0, len(allcells)):
            scoremax = 0
            if i == self.id:
                continue
            if self.selfisleft(allcells, i) == True:
                thetamax = math.atan(self.slopecalculator(allcells, i)[1])
                thetamin = math.atan(self.slopecalculator(allcells, i)[0])
                vx = allcells[self.id].veloc[0] - allcells[i].veloc[0]
                vy = allcells[self.id].veloc[1] - allcells[i].veloc[1]
                theta0 = math.atan2(vy, vx)
            else:
                thetamin = math.atan(self.slopecalculator(allcells, i)[0]) + math.pi
                thetamax = math.atan(self.slopecalculator(allcells, i)[1]) + math.pi
                vx = allcells[self.id].veloc[0] - allcells[i].veloc[0]
                vy = allcells[self.id].veloc[1] - allcells[i].veloc[1]
                theta0 = math.atan2(vy, vx)
                if theta0 < 0:
                    theta0 = theta0 + 2 * math.pi
            if theta0 < 0:
                theta0 = theta0 + 2 * math.pi
            v = (vx ** 2 + vy ** 2) ** (1 / 2)
            if self.distance_from(allcells, i) < 200 + allcells[self.id].radius + allcells[i].radius:
                if allcells[self.id].radius > allcells[i].radius:
                    score = -10000
                    scoremax = -10000
                    if thetamax >= theta0 >=thetamin:
                        for n in range(0, 5):
                            if allcells[self.id].area() * (1 - n * Consts["EJECT_MASS_RATIO"]) > allcells[i].area():
                                deltam = allcells[i].area() - n * Consts["EJECT_MASS_RATIO"] * allcells[self.id].area()
                                if deltam > 0:
                                    score0 = 1000 * deltam * v*(1+ n * deltav) / self.distance_from(allcells,i) - 0.5 * self.distance_from(allcells,i) + 5 * deltam
                                    if score0 <= scoremax:
                                        scoremax = scoremax
                                    else:
                                        scoremax = score0
                            else:
                                break
                        score = scoremax
                        if n == 1:
                            deg = None
                        else:
                            deg = 3 * math.pi / 2 - theta0
                    elif thetamax < theta0 <= thetamax + math.pi / 3:
                        n = math.ceil(v * math.sin(theta0 - thetamax) / deltav)
                        deltam = allcells[i].area() - n * Consts["EJECT_MASS_RATIO"] * allcells[self.id].area()
                        if allcells[self.id].area() * (1 - n * Consts["EJECT_MASS_RATIO"]) > allcells[i].area():
                            score = 1000 * deltam * v * math.cos(theta0 - thetamax) / self.distance_from(allcells,i) - 0.5 * self.distance_from(allcells, i) + 5 * deltam
                            deg = -thetamax
                    elif thetamin > theta0 >= thetamin - math.pi / 3:
                        n = math.ceil(v * math.sin(thetamin - theta0) / deltav)
                        deltam = allcells[i].area() - n * Consts["EJECT_MASS_RATIO"] * allcells[self.id].area()
                        if allcells[self.id].area() * (1 - n * Consts["EJECT_MASS_RATIO"]) > allcells[i].area():
                            score = 1000 * deltam * v * math.cos(thetamin - theta0) / self.distance_from(allcells,i) - 0.5 * self.distance_from(allcells, i) + 5 * deltam
                            deg = math.pi - thetamin
                    elif thetamax + math.pi / 3 < theta0 <= math.pi + (thetamin + thetamax) / 2:
                        n = math.ceil(((3 * deltav) ** 2 + v ** 2 - 2 * 3 * deltav * v * math.cos(theta0 - thetamax)) ** (1 / 2) / deltav)
                        deltam = allcells[i].area() - n * Consts["EJECT_MASS_RATIO"] * allcells[self.id].area()
                        if allcells[self.id].area() * (1 - n * Consts["EJECT_MASS_RATIO"]) > allcells[i].area():
                            score =1000 * deltam * 3 * deltav / self.distance_from(allcells,i) - 0.5* self.distance_from(allcells,i) + 5 * deltam
                            deg = math.pi / 2 - theta0 + math.asin(3 * deltav * math.sin(theta0 - thetamax)) / (((3 * deltav) ** 2 + v ** 2 - 2 * 3 * deltav * v * math.cos(theta0 -thetamax))) ** (1 / 2)
                    else:
                        n = math.ceil(((3 * deltav) ** 2 + v ** 2 - 2 * 3 * deltav * v * math.cos(thetamin - theta0)) ** (1 / 2) / deltav)
                        deltam = allcells[i].area() - n * Consts["EJECT_MASS_RATIO"] * allcells[self.id].area()
                        if allcells[self.id].area() * (1 - n * Consts["EJECT_MASS_RATIO"]) > allcells[i].area():
                            score = 1000 * deltam * 3 * deltav / self.distance_from(allcells,i) - 0.5 * self.distance_from(allcells,i) + 5 * deltam
                            deg = math.pi / 2 - theta0 - math.asin(3 * deltav * math.sin(thetamin - theta0) / ((( 3 * deltav) ** 2 + v ** 2 - 2 * 3 * deltav * v * math.cos(thetamin - theta0)) ** (1 / 2)))
                    if score != -10000:
                        scorelist.append(score)
                        idlist.append(i)
                        anglelist.append(deg)
                        nlist.append(n)
        if len(anglelist) == 0:
            self.n=0
            self.deg=None
            return None
        else:
            for j in range(len(anglelist)):
                if scorelist[j] >= maxscore:
                    imax = j
                    maxscore = scorelist[j]
            self.n = nlist[imax]
            self.deg = anglelist[imax]
            self.target=idlist[imax]
            self.targetarea=allcells[idlist[imax]].area()+allcells[self.id].area() * (1 - n * Consts["EJECT_MASS_RATIO"])
            return anglelist[imax]

    def trueid(self,i):
        k=0-1
        for j in range(0,len(World.cells)):
            if World.cells[j].dead==True:
                continue
            else:
                k=k+1
            if k==i:
                return j


    def excutor_free_farm(self,allcells):
        if self.n!=0:
            self.n=self.n-1
            return self.deg
        else:
            if self.target==None:
                self.free_farm(allcells)
                return self.deg
            elif allcells[self.id].area()<=self.targetarea:
                return None
            else:
                self.free_farm(allcells)
                return self.deg


    def strategy(self, allcells):
        if self.closedanger(allcells)[0]==True:
            return self.escapeB(allcells,self.closedanger(allcells)[1])
        else:
            return None










