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
import cmath
import random
import math


class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.goal = None  # goal_id
        self.heading = None
        self.headingTheta = None
        self.reverse = False
        self.time = 0

    def strategy(self, allcells):
        # print("我的位置", allcells[self.id].pos)
        # print("靶子位置", self.heading)
        self.time += 1
        if self.isInDANGER(allcells):
            print("DANGER!")
            self.goal = None
            self.heading = None
            self.headingTheta = None
            self.reverse = False
            E = [0, 0]
            for i in range(len(allcells)):
                if i != self.id and allcells[i].radius > allcells[self.id].radius:
                    E[0] += self.calculate_E(i, allcells)[0]
                    E[1] += self.calculate_E(i, allcells)[1]
            return self.switchTheta(cmath.phase(complex(E[0], E[1])) % (2 * math.pi))
        elif allcells[self.id].radius / Consts["DEFAULT_RADIUS"] < 0.7:
            return None
        else:
            if self.goal == None or self.searchid(self.goal, allcells) == None:  # 没有目标或目标已死或吸引力过小
                self.goal = None
                self.heading = None
                self.headingTheta = None
                self.reverse = False
                newGoal = self.setGoal(allcells)
                if newGoal != None:
                    g = self.searchid(newGoal, allcells)
                    if self.predictTime(g, allcells) != None:
                        t = self.predictTime(g, allcells) * Consts["FRAME_DELTA"]
                        mygoal = self.predictGoal(allcells, g, t)
                        flag = True
                        for i in range(len(allcells)):  # 判断目标是否处在危险环境中
                            if allcells[i].radius + 2 > allcells[self.id].radius and (
                                    (allcells[i].pos[0] - mygoal.pos[0]) ** 2 + (
                                    allcells[i].pos[1] - mygoal.pos[1]) ** 2) ** 0.5 < 50:
                                flag = False
                                break
                        if flag:
                            self.goal = newGoal
                            self.heading = mygoal.pos
                return None
            else:
                if self.IamBigger(allcells, self.searchid(self.goal, allcells)):
                    print("yes")
                    return None
                distancefromGoal = ((allcells[self.id].pos[0] - allcells[self.searchid(self.goal, allcells)].pos[
                    0]) ** 2 + (
                                            allcells[self.id].pos[1] - allcells[self.searchid(self.goal, allcells)].pos[
                                        1]) ** 2) ** 0.5
                distancefromHeading = ((allcells[self.id].pos[0] - self.heading[0]) ** 2 + (
                        allcells[self.id].pos[1] - self.heading[1]) ** 2) ** 0.5
                if distancefromHeading < 5 and distancefromGoal > 200:
                    self.goal = None
                    self.heading = None
                    return None
                else:
                    return self.GoForIt(allcells)

    # 没考虑越过边界问题(躲避，设定目标）
    def predictGoal(self, allcells, id, t):
        # go to future
        goal_copy = allcells[id].copy()
        goal_copy.pos[0] = goal_copy.pos[0] + goal_copy.veloc[0] * t
        goal_copy.pos[1] = goal_copy.pos[1] + goal_copy.veloc[1] * t
        return goal_copy

    def calculate_E(self, id, allcells):
        theta = cmath.phase(
            complex(self.simplify_pos(id, allcells)[0], self.simplify_pos(id, allcells)[1])) % (
                        2 * math.pi)
        cos = math.cos(theta)
        sin = math.sin(theta)
        veloc_r = (allcells[id].veloc[0] - allcells[self.id].veloc[0]) * cos + (
                allcells[self.id].veloc[1] - allcells[id].veloc[1]) * sin
        d = allcells[self.id].distance_from(allcells[id]) - allcells[self.id].radius - allcells[
            id].radius
        if allcells[id].radius + 0.5 > allcells[self.id].radius:
            E = self.switchVeloc(veloc_r) * self.switchdistance(d)
        else:
            q = math.exp(-veloc_r) / (1.00001 - allcells[id].radius / allcells[self.id].radius)
            E = 1000 * q / d
        return [E * cos, E * sin, E, veloc_r]

    def isInDANGER(self, allcells):
        for i in range(len(allcells)):
            if i != self.id and allcells[i].radius > allcells[self.id].radius:
                if math.fabs(self.calculate_E(i, allcells)[2]) > 100:
                    return True
        return False

    def switchTheta(self, theta):
        if theta < 3 * math.pi / 2:
            theta += math.pi / 2
        else:
            theta -= 3 * math.pi / 2
        return theta

    def switchVeloc(self, v):
        if v >= 0:
            return 0
        elif v > 8:
            return 50 ** 8
        else:
            return 50 ** (-v)

    def switchdistance(self, d):
        safeDistance = 50
        if d <= safeDistance:
            return 10 ** 10
        else:
            return 0

    def searchid(self, id, allcells):
        for i in range(len(allcells)):
            if allcells[i].id == id:
                return i
        return None

    def setGoal(self, allcells):
        goal_list = []
        for i in range(len(allcells)):
            if i > 1 and allcells[i].radius + 0.5 < allcells[self.id].radius and allcells[i].radius > 5:
                E_acell = math.fabs(self.calculate_E(i, allcells)[2])
                if E_acell > 10:
                    goal_list.append([i, E_acell])
        goal_list.sort(key=lambda item: item[1], reverse=True)
        # 这里会有问题！！
        # print(goal_list[0][0],len(allcells))
        return allcells[goal_list[0][0]].id if goal_list else None

    def isBlocked(self, id, allcells):
        for i in range(len(allcells)):
            if self.id != i and allcells[i].radius + 0.5 > allcells[self.id].radius:
                selfTheta = cmath.phase(complex(allcells[id].pos[0] - allcells[self.id].pos[0],
                                                allcells[self.id].pos[1] - allcells[id].pos[1])) % (2 * math.pi)
                deltaTheta = math.fabs(cmath.phase(complex(allcells[i].pos[0] - allcells[self.id].pos[0],
                                                           allcells[self.id].pos[1] - allcells[i].pos[1])) % (
                                               2 * math.pi) - selfTheta)
                if deltaTheta < math.pi / 2 and allcells[self.id].distance_from(allcells[i]) < allcells[
                    self.id].distance_from(allcells[id]):
                    k = (allcells[self.id].pos[1] - allcells[id].pos[1]) / (
                            allcells[id].pos[0] - allcells[self.id].pos[0])

                    d = math.fabs(k * (allcells[i].pos[0] - allcells[self.id].pos[0]) - allcells[self.id].pos[1] -
                                  allcells[i].pos[1]) / (1 + k * k) ** 0.5 - allcells[self.id].radius - allcells[
                            i].radius
                    if d < 0.5:
                        return True
        return False

    def GoForIt(self, allcells):
        g = self.searchid(self.goal, allcells)
        mypos = [0, 0]
        mypos[0] = allcells[self.id].pos[0] - self.heading[0]
        mypos[1] = self.heading[1] - allcells[self.id].pos[1]
        myveloc = [0, 0]
        myveloc[0] = allcells[self.id].veloc[0]
        myveloc[1] = - allcells[self.id].veloc[1]
        veloc = (myveloc[0] ** 2 + myveloc[1] ** 2) ** 0.5
        theta = cmath.phase(complex(mypos[0], mypos[1])) % (2 * math.pi)
        cos = math.cos(theta)
        sin = math.sin(theta)
        veloc_r = myveloc[0] * cos + myveloc[1] * sin
        veloc_t = myveloc[1] * cos - myveloc[0] * sin
        v_max = 1.5 if self.time < 200 else 0.5
        if math.fabs(veloc_t) > 0.15:
            # print("切向", veloc_t)
            if veloc_t > 0:
                return self.switchTheta((theta + math.pi / 2) % (2 * math.pi))
            else:
                return self.switchTheta((theta - math.pi / 2) % (2 * math.pi))
        else:
            if self.headingTheta == None:
                self.headingTheta = theta
                self.reverse = (veloc_r > 0)
            # print("朝向角", self.headingTheta)
            if self.reverse and veloc > v_max:
                # print("径向", self.switchTheta(self.headingTheta % (2 * math.pi)))
                return self.switchTheta(self.headingTheta % (2 * math.pi))
            else:
                self.reverse = False
                # print("径向", self.switchTheta(self.headingTheta % (2 * math.pi)))
                return self.switchTheta(self.headingTheta % (2 * math.pi)) if veloc < v_max else None

    def findtarget(self, allcells, mubiao=None):
        searchradius = allcells[self.id].radius * 5
        while mubiao == None:
            alist = []
            flag1 = allcells[self.id].radius * 0.9 - 0.01 * searchradius
            flag2 = 0.005 * (35 * allcells[self.id].radius - searchradius)
            for i in allcells:
                if i != allcells[1 - self.id] and i != allcells[self.id] and allcells[self.id].distance_from(
                        i) <= searchradius and i.radius <= flag1 and i.radius >= flag2:
                    alist.append(i)
            if len(alist) > 0 and searchradius <= allcells[self.id].radius * 35:
                minv = 0
                count = 0
                for j in range(len(alist)):
                    veloc = (alist[j].veloc[0] ** 2 + alist[j].veloc[1] ** 2) ** 0.5
                    if minv < veloc:
                        minv = veloc
                        count = j
                mubiao = alist[count].id

            elif searchradius < allcells[self.id].radius * 35:
                searchradius = searchradius + allcells[self.id].radius * 5

                continue
            else:
                break
        return mubiao

    def predictTime(self, id, allcells):
        for t in range(10, 100):
            predictPos = [0, 0]
            predictPos[0] = allcells[id].pos[0] + allcells[id].veloc[0] * t * Consts["FRAME_DELTA"]
            predictPos[1] = allcells[id].pos[1] + allcells[id].veloc[1] * t * Consts["FRAME_DELTA"]
            mypos = [0, 0]
            mypos[0] = allcells[self.id].pos[0] - predictPos[0]
            mypos[1] = predictPos[1] - allcells[self.id].pos[1]
            myveloc = [0, 0]
            myveloc[0] = allcells[self.id].veloc[0]
            myveloc[1] = - allcells[self.id].veloc[1]
            theta = cmath.phase(complex(mypos[0], mypos[1])) % (2 * math.pi)
            cos = math.cos(theta)
            sin = math.sin(theta)
            veloc_r = myveloc[0] * cos + myveloc[1] * sin
            veloc_t = myveloc[1] * cos - myveloc[0] * sin
            v_max = 1.5 if self.time < 200 else 0.5
            d = (mypos[0] ** 2 + mypos[1] ** 2) ** 0.5 - allcells[id].radius - allcells[self.id].radius + 10
            a = Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"] / Consts["FRAME_DELTA"]
            if d + veloc_r * math.fabs(veloc_t) / a + (veloc_r - v_max) * math.fabs(v_max - veloc_r) / (2 * a) < 0:
                t1 = math.fabs(veloc_t) / a
                delta = veloc_r ** 2 + 2 * a * (d + veloc_r * t1)
                # print(d, veloc_r * t1)
                if delta >= 0:
                    t2 = (delta ** 0.5 - veloc_r) / a
                    T = (t1 + t2) / Consts["FRAME_DELTA"]
                else:
                    continue
            else:
                t1 = math.fabs(veloc_t) / a
                t2 = math.fabs(v_max - veloc_r) / a
                t3 = (d + veloc_r * t1 + (veloc_r - v_max) * t2 / 2) / v_max
                T = (t1 + t2 + t3) / Consts["FRAME_DELTA"]
            leftarea = allcells[self.id].area() * (1 - Consts["EJECT_MASS_RATIO"]) ** (
                    (t1 + t2) / Consts["FRAME_DELTA"])
            if math.fabs(t - T) < 2 and leftarea > allcells[id].area() and t < self.deadTime(id,
                                                                                             allcells) and leftarea + \
                    allcells[id].area() > allcells[self.id].area():
                return t
        return None

    def copy_allcells(self, allcells):
        return [allcells[i].copy() for i in range(len(allcells))]

    def deadTime(self, id, allcells):
        allcells_copy = self.copy_allcells(allcells)
        # 假装自己和对手都不存在！
        for t in range(100):
            for i in range(len(allcells)):
                if i > 1:
                    allcells_copy[i].move(Consts["FRAME_DELTA"])
            for j in range(len(allcells)):
                if j > 1 and j != id and allcells_copy[id].collide(allcells_copy[j]):
                    return t + 1
        return 100

    def simplify_pos(self, id, allcells):
        x = allcells[id].pos[0] - allcells[self.id].pos[0]
        y = allcells[self.id].pos[1] - allcells[id].pos[1]
        if math.fabs(x) >= 500:
            if x > 0:
                x -= 1000
            else:
                x += 1000
        if math.fabs(y) > 250:
            if y > 0:
                y -= 500
            else:
                y += 500
        return [x, y]

    def IamBigger(self, allcells, id):
        sum = 0
        absorb = 0.8
        for i in range(len(allcells)):
            if i > 1 and allcells[i].radius < allcells[self.id].radius:
                sum += allcells[i].area() * absorb
        return allcells[self.id].area() > allcells[id].area() + sum
