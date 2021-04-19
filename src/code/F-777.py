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
import random
import math

#游戏主体思路：
#每一帧遍历所有小球，对大球使用avoid函数，如果有躲避的必要，优先躲避
#对小球，根据小球的距离，大小计算小球的价值，选择价值最大的小球接近
#接近方式采用减小切向相对速度的方式，在切向速度较小以后，再径向加速

class Player():
    def __init__(self, id, arg = None):
        self.id = id
        self.t=0                #用于激进追击时计数
        self.total_area=0       #记录全图小球总体积
        self.num=0              #记录回合数

    def cal_cos(self,veloc0,veloc1):    #返回两个速度对应的余弦值
        return (veloc0[0]*veloc1[0]+veloc0[1]*veloc1[1])/((veloc0[0]**2+veloc0[1]**2)**0.5*(veloc1[0]**2+veloc1[1]**2)**0.5)

    def avoid(self, my_cell, other_cell):   #躲避函数
        vx=other_cell.veloc[0]-my_cell.veloc[0] #相对速度vx
        vy=other_cell.veloc[1]-my_cell.veloc[1] #相对速度vy
        #相对位移，考虑跨屏情况，共三种
        xlist=[my_cell.pos[0]-other_cell.pos[0], my_cell.pos[0]-Consts["WORLD_X"]-other_cell.pos[0], my_cell.pos[0]+Consts["WORLD_X"]-other_cell.pos[0]]
        #对三种情况选择最小的x相对值
        '''此代码已弃用
        min_x=min(abs(xlist[0]), abs(xlist[1]), abs(xlist[2]))
        if min_x == abs(xlist[0]):
            x=xlist[0]
        elif min_x == abs(xlist[1]):
            x=xlist[1]
        else:
            x=xlist[2]
        '''
        x=sorted(xlist,key=lambda x_:abs(x_))[0]
        #同上，现在选择最小的y相对值
        ylist=[my_cell.pos[1]-other_cell.pos[1], my_cell.pos[1]-Consts["WORLD_Y"]-other_cell.pos[1], my_cell.pos[1]+Consts["WORLD_Y"]-other_cell.pos[1]]
        '''此代码已弃用
        y=min(abs(ylist[0]), abs(ylist[1]), abs(ylist[2]))
        min_y=min(abs(ylist[0]), abs(ylist[1]), abs(ylist[2]))
        if min_y == abs(ylist[0]):
            y=ylist[0]
        elif min_y == abs(ylist[1]):
            y=ylist[1]
        else:
            y=ylist[2]
        '''
        y=sorted(ylist,key=lambda y_:abs(y_))[0]
        #计算相对速度和距离矢量的夹角的余弦值
        if (vx**2+vy**2)**0.5*(x**2+y**2)**0.5!=0:#如果距离不为零（当然不可能）且相对速度不为零，就返回计算值
            cos_theta=(vx*x+vy*y)/((vx**2+vy**2)**0.5*(x**2+y**2)**0.5)
        else:#反之，就取夹角余弦值为1
            cos_theta=1
        #最短距离
        distance=(x**2+y**2)**0.5
        #对距离不同的球进行判断
        if distance-other_cell.radius-my_cell.radius<60:#只考虑距离较小的
            sin_theta=(1-cos_theta**2)**0.5
            if cos_theta>0 and distance*sin_theta-20<=other_cell.radius+my_cell.radius:
                #print(other_cell.pos,vy*x+vx*y,vy,vx) 用于调试
                if vy*x-vx*y<0:
                    return (vy,-vx)
                else:
                    return (-vy, vx)
            else:
                return None
        else:
            return None

    def strategy(self, allcells):
        my_cell=allcells[self.id]       #自己
        enemy=allcells[abs(1-self.id)]  #对手
        if self.num==0:                 #在第一回合，计算环境总质量
            for cell in allcells:
                self.total_area+=cell.area()
        elif my_cell.area()>0.5*self.total_area:    #在其余回合，只要自己的质量过半，就什么都不做（已经赢了）
            return None
        self.num+=1     #计数
        hunt_value=-1   #用于记录最大价值
        # 记录目标方向
        plan_x=0
        plan_y=0
        player_perspeed=Consts["DELTA_VELOC"]*Consts["EJECT_MASS_RATIO"]#吐球所得冲量
        check_list=[]  #可能成为目标的球
        escape_plan=[] #需要避开的球

        for i in range(len(allcells)):  #遍历所有小球
            other_cell=allcells[i]
            # 目标是除自己和对手外的比自己小，但质量合适的球
            if other_cell.id != my_cell.id and other_cell.id != enemy.id and other_cell.area() < my_cell.area() and other_cell.area() > 0.016*my_cell.area():
                #小球不应为自己，并且要比自己小且不会太小，另外应追球方法并非十分直接，此处避免追对手，防止把自己浪输
                #大致过程类似avoid
                vx=other_cell.veloc[0]-my_cell.veloc[0]
                vy=other_cell.veloc[1]-my_cell.veloc[1]
                xlist=[my_cell.pos[0]-other_cell.pos[0], my_cell.pos[0]-Consts["WORLD_X"]-other_cell.pos[0], my_cell.pos[0]+Consts["WORLD_X"]-other_cell.pos[0]]
                '''
                x=min(abs(xlist[0]), abs(xlist[1]), abs(xlist[2]))
                min_x=min(abs(xlist[0]), abs(xlist[1]), abs(xlist[2]))
                if min_x == abs(xlist[0]):
                    x=xlist[0]
                elif min_x == abs(xlist[1]):
                    x=xlist[1]
                else:
                    x=xlist[2]
                '''
                x = sorted(xlist, key=lambda x_: abs(x_))[0]
                ylist=[my_cell.pos[1]-other_cell.pos[1], my_cell.pos[1]-Consts["WORLD_Y"]-other_cell.pos[1], my_cell.pos[1]+Consts["WORLD_Y"]-other_cell.pos[1]]
                '''
                y=min(abs(ylist[0]), abs(ylist[1]), abs(ylist[2]))
                min_y=min(abs(ylist[0]), abs(ylist[1]), abs(ylist[2]))
                if min_y == abs(ylist[0]):
                    y=ylist[0]
                elif min_x == abs(xlist[1]):
                    y=ylist[1]
                else:
                    y=ylist[2]
                '''
                y = sorted(ylist, key=lambda y_: abs(y_))[0]
                if (vx**2+vy**2)**0.5*(x**2+y**2)**0.5!=0:
                    cos_theta=(vx*x+vy*y)/((vx**2+vy**2)**0.5*(x**2+y**2)**0.5)
                else:
                    cos_theta=1
                vr_x=(vx**2+vy**2)**0.5*cos_theta/(x**2+y**2)**0.5*x
                vr_y=(vx**2+vy**2)**0.5*cos_theta/(x**2+y**2)**0.5*y
                vtheta_x=vr_x-vx
                vtheta_y=vr_y-vy
                distance=(x**2+y**2)**0.5
                #选择喷球方向
                if cos_theta>0:
                    eject_x=vtheta_x
                    eject_y=vtheta_y
                    time=distance/(vr_x**2+vr_y**2)**0.5
                else:
                    eject_x=vtheta_x+player_perspeed*x/(x**2+y**2)**0.05-vr_x
                    eject_y=vtheta_y+player_perspeed*y/(x**2+y**2)**0.05-vr_y
                    time=distance/((player_perspeed*x/(x**2+y**2)**0.05)**2+(player_perspeed*y/(x**2+y**2)**0.05)**2)**0.5
                new_mass=my_cell.area()*0.99**(int((eject_x**2+eject_y**2)**0.5/player_perspeed))+other_cell.area()     #吃球后的新质量
                if my_cell.area()*0.99**(int((eject_x**2+eject_y**2)**0.5/player_perspeed))>other_cell.area():  #如果说吐球之后目标还能被吃
                    value=(new_mass-my_cell.area())/time   #用于是否能作为目标的价值判断
                    # 把所有合适的都加入目标序列
                    if value>0:
                        check_list.append([value,(eject_x,eject_y),distance,cos_theta,(vtheta_x,vtheta_y),tuple(other_cell.pos),my_cell.area()-other_cell.area()])
                    #选取价值最大者作为目标
                    if value>hunt_value and value>0:
                        hunt_value=value
                        plan_x=eject_x
                        plan_y=eject_y
                        new_vx=vr_x
                        new_vy=vr_y
            #对大球使用avoid函数判断
            elif other_cell.id != my_cell.id and allcells[i].area() >= my_cell.area():#球比我大，我可能要躲
                avoid_plan=self.avoid(my_cell,other_cell)
                if avoid_plan:
                    escape_plan.append(avoid_plan)
        if escape_plan:#如果有需要逃跑的球
            escape_x=0
            escape_y=0
            for plan in escape_plan:#由于每个球都要兼顾，所以把逃跑速度方向向量加和做为最终逃跑方向
                escape_y+=plan[0]
                escape_x+=plan[1]
            theta=math.atan2(escape_y,escape_x)
            self.t=0
            return theta
        #如果最大价值小球的价值仍然过低，不动
        if hunt_value<=0.4:    #参数
            return None
        #其余根据相对位移与相对速度差的余弦值判断
        else:
            #余弦值较小，可在一定程度上朝小球加速，至于加速与否，与自己和对手的大小有关
            if (plan_x**2+plan_y**2)**0.5<0.08:             #参数
                if self.t!=0 and (new_vx**2+new_vy**2)**0.5<1:
                    theta=math.atan2(new_vx,new_vy)
                    self.t-=1
                else:
                    self.t=0
                    theta=None
                return theta
            else:
                theta=math.atan2(plan_x,plan_y)
                #如果自己比对手大很多，则可不用太过激进
                #否则可在调整结束后加速
                if (plan_x**2+plan_y**2)**0.5<0.04 and my_cell.area()<enemy.area()*2:
                    self.t=5
                return theta