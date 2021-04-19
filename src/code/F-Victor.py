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
import random

class Player():
    def __init__(self, id, arg = None):
    	self.id = id

    def strategy(self, allcells):
        theta = None
        # me就是allcells列表中的self
        me = allcells[self.id]

        # dangerous代表周围是否有大球威胁，dangerous_angle列表用来储存存在威胁的方向
        dangerous = False
        dangerous_angle=[]

        # sum_mass：其他cell的总质量（用总的r平方表示）
        sum_mass = 0

        # 一个用来标注“是否为第一个要吃的cell”的flag，以及一个用来标记该距离的变量，作用见后面代码
        eat_flag = 0
        eat_dis = 2*me.radius

        # 一个用来标注“是否要吃对手”的flag
        eat_enemy = False

        # 速度方向与y轴的夹角为advance_angle，cos值为cos_ad
        if me.veloc[0]==0 and me.veloc[1]==0:
            advance_angle = None
        else:
            cos_ad = me.veloc[1] / math.sqrt(me.veloc[0] ** 2 + me.veloc[1] ** 2)
            advance_angle = math.acos(cos_ad)
            if me.veloc[0] < 0:
                advance_angle = 2 * math.pi - advance_angle

        # 记录此刻的前进方向（静止时为无）
        advance_angle = None
        if me.veloc[1] == 0:
            if me.veloc[0] > 0:
                advance_angle = math.pi/2
            else:
                advance_angle = math.pi*3/2
        else:
            advance_angle = math.atan(me.veloc[0]/me.veloc[1])
            # advance_angle的取值范围为（-Π/2，Π/2），（-Π/2，0）的要转化为（Π/2，Π）
            if advance_angle < 0:
                advance_angle += math.pi
            # 0或Π的判断
            if advance_angle == 0 and me.veloc[1] < 0:
                advance_angle = math.pi
            # [0,Π]→[0,2Π)
            if me.veloc[0]<0:
                advance_angle = 2*math.pi - advance_angle

        # 遍历
        for cell in allcells:

            # cell为自身时略过本次循环
            if cell.id == self.id:
                continue

            # 本游戏区域+周围8个游戏区域=9个游戏区域，分别取self在9个区域中的不同位置找到最短距离min_dis与对应的角度alpha
            distance_list=[]
            # 用列表pos储存9个位置坐标，mis_dis表示最小距离，num代表区域号码（从左到右从上往下1-9）
            pos=[[me.pos[0]-1000,me.pos[1]-500],[me.pos[0],me.pos[1]-500],[me.pos[0]+1000,me.pos[1]-500], \
                 [me.pos[0]-1000, me.pos[1]],[me.pos[0],me.pos[1]],[me.pos[0]+1000,me.pos[1]], \
                 [me.pos[0]-1000, me.pos[1]+500],[me.pos[0],me.pos[1]+500],[me.pos[0]+1000,me.pos[1]+500]]
            min_dis = math.sqrt(pow(cell.pos[0] - pos[0][0], 2) + pow(cell.pos[1] - pos[0][1], 2))
            num=0
            for i in range(1,9):
                distance = math.sqrt(pow(cell.pos[0] - pos[i][0], 2) + pow(cell.pos[1] - pos[i][1], 2))
                if distance < min_dis:
                    min_dis = distance
                    num = i

            # me指向cell与y轴的夹角为alpha，cos值为cos_a
            delta_x = cell.pos[0]-pos[num][0]
            delta_y = cell.pos[1]-pos[num][1]
            cos_a = delta_y/math.sqrt(delta_x**2 + delta_y**2)
            alpha = math.acos(cos_a)
            if delta_x < 0:
                alpha = 2*math.pi - alpha

            # sum_mass的累加
            sum_mass += pow(cell.radius,2)

            # 如果是对手，当对手在自己的5个半径范围内且质量小于自身的0.7倍且在前方时，直接定好攻击方向（在循环外层，对对手的攻击优于普通cell）
            if cell.id == 1-self.id:
                if min_dis <= me.radius*5 and pow(cell.radius, 2) <= pow(me.radius, 2)*0.95 \
                        and (abs(advance_angle - alpha) <= math.pi / 3.5 or advance_angle == None):
                    eat_enemy = True
                    theta = alpha - math.pi
                    if theta < 0:
                        theta += 2*math.pi

            # 当cell质量比自身大且距离我们很近时，记住这个大球的威胁方向！
            if pow(cell.radius, 2) >= pow(me.radius, 2) and \
                    min_dis <= 1.8*(me.radius + cell.radius):
                dangerous = True
                # 记住哪个方向有存在“大球威胁”
                dangerous_angle.append(alpha)

            # 当cell比我们小且满足一定质量条件时，当我们与cell的距离在一定范围内时（范围依赖于cell.radius），
            # 且当cell在我们前进的大方向时，判断它是否是我们要吃的球：
            elif pow(cell.radius, 2) >= 0.2 * pow(me.radius, 2) and \
                    pow(cell.radius, 2) <= 0.8 * pow(me.radius, 2) and\
                    min_dis < 6*(cell.radius + me.radius) and \
                    (abs(advance_angle - alpha) <= math.pi / 3.5 or advance_angle == None):
                # 第一次遇到符合上述条件的球，将其设为初始选择对象
                if eat_flag == 0:
                    eat_dis = min_dis
                    eat_radius = cell.radius
                    eat_for = alpha
                    eat_flag = 1
                # 如果后来还遇到符合条件的球，选择最大的那个来吃
                elif eat_radius < cell.radius:
                    eat_dis = min_dis
                    eat_radius = cell.radius
                    eat_for = alpha


        ## 遍历完成！##

        # 策略：先考虑躲避威胁，然后考虑球是否足够大和速度限制，接着考虑是否能吃对手，最后考虑要不要吃周围的球，都不符合条件则返回None

        # 如果球球遇到危险，往所有存在“大球威胁”的方向的平均方向喷射，逃跑！
        if dangerous:
            print('dangerous')
            sum_angle = 0
            for i in dangerous_angle:
                sum_angle += i
            theta = sum_angle/len(dangerous_angle)
            print(theta)
            return theta

        # 如果球已经比其他所有球大，就啥都不干了，睡大觉。
        if pow(me.radius,2) >= sum_mass:
            print('big')
            return None

        # 如果离要吃的球已经近在咫尺了，而且速度不算特别快，那就吃他！
        if eat_flag == 1 and eat_dis < 2*me.radius and pow(me.veloc[0],2) + pow(me.veloc[1],2) <= 1.6:
                print('eat')
                theta = eat_for - math.pi
                if theta < 0:
                    theta += 2 * math.pi
                return theta

        # 如果可以吃对手，直接吃他！
        if eat_enemy:
            print('eat_enemy')
            return theta

        # 如果球太快了，就别发射了。
        if pow(me.veloc[0],2) + pow(me.veloc[1],2) >= 0.25+math.e**((-me.radius)/80):
            print('big')
            return None

        # 如果要吃其他cell
        if eat_flag == 1:
            print('eat')
            theta = eat_for - math.pi
            if theta < 0:
                theta += 2*math.pi
            return theta

        return None