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
import random
import math
class Player():
    def __init__(self, id, arg = None):
        self.id = id
#关于本游戏使用的策略
#假如没有对手，理论上只需要一次对全局状态的输入就能得到最优决策序列
#然而，存在对手；但当敌我距离较远时，双方的行为可视为独立的
#利用树可以计算得到若干次决策后的未来，通过选择最优结果来决策是一种思路
#但是既然每次都有状态的输入，为了减小计算量，不妨变得短视一些
#同时只考虑一定范围内的物体和对手,许多参数有待调整
    def cos(self,a,b):
    #求向量余弦
        if (a[0]**2+a[1]**2)*(b[0]**2+b[1]**2)-0<0.0001:
            return 0
        return (a[0]*b[0]+a[1]*b[1])/((a[0]**2+a[1]**2)*(b[0]**2+b[1]**2))**0.5

    def angel(self,theta):
    #把坐标转换为角度
        theta[0]*=10
        theta[1]*=10
        if (theta[0]**2+theta[1]**2)**0.5<0.0000001:
            return None
        temp=abs(theta[1]/(theta[0]**2+theta[1]**2)**0.5)
        if theta[0]>=0 and theta[1]>=0:
            return math.asin(temp)+math.pi
        if theta[0]<0 and theta[1]>=0:
            return 2*math.pi-math.asin(temp)
        if theta[0]<0 and theta[1]<0:
            return math.asin(temp)
        return math.pi-math.asin(temp)

    def dveloc(self,veloc,direct):
    #计算转到目标方向所需加速度
        return direct
        

    def strategy(self, allcells):
        MyCell=allcells[self.id]
        YourCell=allcells[1-self.id]
        theta=[0,0]
        myv=(MyCell.veloc[0]**2+MyCell.veloc[1]**2)**0.5
    #只考虑一定范围内的CELL,同时忽略自身发射的球
        cellList=[]
        mindis=2000#以最近球距离为标准划定感知范围
        numall=0#开局时球较多需要多运动抢占先机，后面需要保留实力
        for i in range(2,len(allcells)):
            if allcells[i].radius> MyCell.radius * Consts["EJECT_MASS_RATIO"] ** 0.5+1 and not allcells[i].dead:
                numall+=1
                if allcells[i].distance_from(MyCell)<mindis:
                    mindis=allcells[i].distance_from(MyCell)
        for i in range(2,len(allcells)):
            if allcells[i].distance_from(MyCell)-allcells[i].radius<max(6*MyCell.radius,3*mindis) \
            and not allcells[i].dead and allcells[i].radius>MyCell.radius * Consts["EJECT_MASS_RATIO"] ** 0.5+1:
    #计算基于相对距离，相对速度，绝对速度，半径等信息
                cellList.append({"pos":[allcells[i].pos[0]-MyCell.pos[0],allcells[i].pos[1]-MyCell.pos[1]],
                        "dis":allcells[i].distance_from(MyCell),"veloc":   
                                 [allcells[i].veloc[0]-MyCell.veloc[0],allcells[i].veloc[1]-MyCell.veloc[1]],
                "v":allcells[i].veloc,"r":allcells[i].radius})
    #接下来对各个cell的方向根据大小和距离赋权,也要考虑速度方向，即向我方前进的球权重大
        for cells in cellList:
    #如果cell大于发射后的大小，赋权为负，球越大，躲避越难，越近越危险
            tempv=(cells["veloc"][0]**2+cells["veloc"][1]**2)**0.5
            if cells["r"]>MyCell.radius:
                weight=-cells["r"]*(2*tempv-self.cos(cells["pos"],cells["v"])*tempv)/(cells["dis"]-cells["r"]-MyCell.radius)
                cells["w"]=weight
    #否则反之，但是此时收益与球的面积成正比，即半径的平方，球越近，越容易吃到
            else:
                weight=cells["r"]**2*(3*tempv-self.cos(cells["v"],cells["pos"])*tempv)/(cells["dis"]-cells["r"]-MyCell.radius)
                cells["w"]=weight
        for cells in cellList:
        #简单对位置赋权
            theta[0]+=cells["pos"][0]*cells["w"]
            theta[1]+=cells["pos"][1]*cells["w"]
        #现在考虑更近距离的单位以做出精细化的应对
        bigger=[]
        smaller=[]
        bigdis=1000
        smalldis=1000
        #需要判断最近的大球和小球来辅助决策，例如最近大球较远就要先考虑吃小球
        for cells in cellList:
        #取1.5倍最近距离和自身未来10秒运动范围较大值为搜索半径
            if cells["dis"]-cells["r"]-MyCell.radius<max(MyCell.radius+10*myv,1.5*mindis):
                if cells["r"]>MyCell.radius:
                    bigger.append(cells)
                    if cells["dis"]-cells["r"]-MyCell.radius<bigdis:
                        bigdis=cells["dis"]-cells["r"]-MyCell.radius
                else:
                    smaller.append(cells)
                    if cells["dis"]-cells["r"]-MyCell.radius<smalldis:
                        smalldis=cells["dis"]-cells["r"]-MyCell.radius
        if len(smaller)!=0 and bigdis>30:
            #此时选取目标方向，ARGMAX权重,并比较最大权重与平均权重之间差异，在贪心与远视之间平衡
            tocell=smaller[0]
            theta=[0,0]
            for cells in smaller:
                if tocell["w"]<cells["w"]:
                    tocell=cells
            #考虑现在的距离与短暂未来的距离，综合判断
                futurepos=[cells["pos"][0]+(cells["dis"]-cells["r"]-MyCell.radius)/(cells["veloc"][0]**2+cells["veloc"][1]**2+0.0001)**0.5*cells["veloc"][0], \
                           cells["pos"][1]+(cells["dis"]-cells["r"]-MyCell.radius)/(cells["veloc"][0]**2+cells["veloc"][1]**2+0.0001)**0.5*cells["veloc"][1]]
                theta[0]+=futurepos[0]*cells["w"]
                theta[1]+=futurepos[1]*cells['w']
            #估计相对碰撞所需时间
            k=(tocell["dis"]-tocell["r"]-MyCell.radius)/(tocell["veloc"][0]**2+tocell["veloc"][1]**2+0.00001)**0.5
            t=tocell["r"]/MyCell.radius
            #最大权重接近平均权重，往最大权重方向，如果非常近，贪心吃掉该球
            if tocell["dis"]-tocell["r"]-MyCell.radius<max(4*myv,20):
                    return self.angel(tocell["pos"])
            if self.cos(theta,tocell["pos"])>0.7:
                #对目标位置进行预测并追击
                return self.angel(self.dveloc(MyCell.veloc,[-tocell["pos"][0]-k*tocell["v"][0],
                                                         -tocell["pos"][1]-k*tocell["v"][1]])) \
                if random.random()<numall/100*(1-t)+0.1 else None
            else:
                self.angel(self.dveloc(MyCell.veloc,theta)) if random.random()<numall/100+0.1 else None
        else:
            theta=[0,0]
            tocell=bigger[0]
            for cells in bigger:
                futurepos=[cells["pos"][0]+(cells["dis"]-cells["r"]-MyCell.radius)/(cells["veloc"][0]**2+cells["veloc"][1]**2+0.0001)**0.5*cells["veloc"][0], \
                           cells["pos"][1]+(cells["dis"]-cells["r"]-MyCell.radius)/(cells["veloc"][0]**2+cells["veloc"][1]**2+0.0001)**0.5*cells["veloc"][1]]
                cells["f"]=futurepos
                #注意威胁度较大的，运动轨迹在我方前进方向上
                if self.cos(futurepos,MyCell.veloc)>0 or self.cos(cells["pos"],MyCell.veloc)>0:
                    theta[0]+=futurepos[0]*cells["w"]
                    theta[1]+=futurepos[1]*cells['w']
                if tocell["dis"]-tocell["r"]>cells["dis"]-cells["r"]:
                    tocell=cells
            #只有距离足够有威胁的近时才考虑逃离
            if tocell["dis"]-tocell["r"]-MyCell.radius<max(10*myv,30):
                k=(tocell["dis"]-tocell["r"]-MyCell.radius)/(tocell["veloc"][0]**2+tocell["veloc"][1]**2+0.0001)**0.5
            #根据大球前进方向躲避策略不同,相当近时紧急逃离，即反向加速
                if tocell["dis"]-tocell["r"]-MyCell.radius<max(4*myv,20):
                    return self.angel([tocell["pos"][0],tocell["pos"][1]])
            #不是很近时向连线垂直方向加速，能最快偏移
                if abs(tocell["pos"][0])<0.0001:
                    if self.cos(tocell["f"],[1,0])>0:
                        return 0
                    else:
                        return math.pi
                dy=-tocell["pos"][0]/tocell["pos"][1]
                if self.cos(tocell["f"],[1,dy])<0:
                    return self.angel([1,dy])
                else:
                    return self.angel([-1,-dy])

		
				
			
			
			
