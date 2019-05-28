from consts import Consts
from cell import Cell

import math
import random

class Player():

    def __init__(self, id, arg = None):
        self.id = id

    def radar(self, allcells):
        myradius = allcells[self.id].radius
        distance = 0
        if myradius < 10:
            distance = 150 - 5 * myradius
        elif myradius < 50:
            distance = 4 * myradius
        else:
            distance = 200
        # 如果在此范围内没有合格的cell，扩大范围。
        enlarge = None
        for cell in allcells:
            if cell.radius > 0.224 * myradius:
                enlarge = True
        if enlarge:
            distance += 2 * myradius
        return distance
    # 定义检测函数，同时得到威胁cell和可吃cell
    def watch_cells(self, allcells):
        # a_distance是雷达探测距
        alist = []  # 存放有威胁的cell
        blist = []   # 存放朝向自己的可吃cell
        blist2 = []  # 存放除了朝向自己的外，在自己附近的可吃cell
        a_distance = self.radar(allcells)
        # 先得到自己的cell的一些参数，半径，速度，位置
        myradius = allcells[self.id].radius
        myveloc = allcells[self.id].veloc
        mypos = allcells[self.id].pos
        # 遍历allcells，在检测范围内找到alist，blist，blist2, 均可能包含另一个玩家，但不包含自己
        for i in allcells:
            if allcells[self.id].distance_from(i) < a_distance:  # 排除检测范围外的cell
                dx = mypos[0] - i.pos[0]
                dy = mypos[1] - i.pos[1]
                dp_theta = math.atan2(dx, dy)  # 由i指向自己的向量的角度
                v_theta = math.atan2(i.veloc[0] - myveloc[0], i.veloc[1] - myveloc[1])  # 相对速度的指向
                d_theta = abs(dp_theta - v_theta)  # 上述两者的夹角
                a_dis =  allcells[self.id].distance_from(i) # 两cell圆心距离
                b_dis = a_dis-myradius-i.radius  # 两cell最近距离
                # 有把自己吞噬的可能的cell
                if i.radius > myradius:
                    if d_theta < math.pi/2 and math.sin(d_theta)*a_dis <= i.radius + myradius:
                        alist.append([i, b_dis, dp_theta,d_theta])
                # 在自己半径的0.4到0.9倍的cell中找blist，blist2
                elif myradius*0.4 < i.radius < myradius*0.9:
                    if d_theta < math.pi/3:  # 向自己运动
                        # 求出与自己相撞所用时间
                        t = b_dis / (math.cos(d_theta) * (
                                    (i.veloc[0] - myveloc[0]) ** 2 + (i.veloc[1] - myveloc[1]) ** 2)) ** 0.5
                        # 检查是否需要小做调整
                        if math.sin(d_theta) * a_dis <= (i.radius + myradius):
                            move_or_not = None
                        else:
                            move_or_not = True
                        # 把cell，用时，否需要小做调整，相对位置的指向，相对速度的指向存到blist
                        blist.append([i, t, move_or_not, dp_theta, v_theta,b_dis])
                    # 把在自己附近且相对速度较小的cell存到blist2，参数都可调
                    if b_dis<30 and ((i.veloc[0] - myveloc[0])**2 + (i.veloc[1] - myveloc[1])**2)**0.5 < 4:
                        blist2.append([i, b_dis, a_dis, dp_theta, v_theta, a_dis-b_dis])
        return alist, blist, blist2

    # 定义逃脱函数
    def escape_threat(self, cells_list,allcells):
        the_cell_d = sorted(cells_list, key=lambda x: x[1])[0]  # 得到有威胁cell中最近的那一个
        if the_cell_d[1] < 30:# 当距离足够小时启动喷射，进行逃离
            return the_cell_d[2]+math.pi
        else:
            return None
    # 对于朝自己运动的可吃cell
    def eat_food(self, cells_list,allcells):
        the_cell_t = sorted(cells_list, key=lambda x: x[5])[0]  # 得到最快到达自己的那一个作为吞噬目标
        if the_cell_t[2]:  # 需要做小调整
            return 2*the_cell_t[3] - the_cell_t[4]   # 这个角度只是大致的，并非精确计算得到
        else:
            if math.sqrt(allcells[self.id].veloc[0]**2+allcells[self.id].veloc[1]**2) <= \
                                      0.2*abs(math.sqrt(the_cell_t[0].veloc[0]**2+the_cell_t[0].veloc[1]**2)):
                #速度达到可吃cell的0.2，便不再喷射
                return the_cell_t[3]
            else:
                return None

    # 对于不朝自己运动的可吃cell
    def eat_food2(self,cells_list,allcells):
        the_cell_d = sorted(cells_list, key=lambda x: x[1])[0]  # 得到最近的那一个
        if math.sin(abs(the_cell_d[3] - the_cell_d[4])) * the_cell_d[2] > the_cell_d[5]:  # 一旦达到碰撞条件则不再喷射
            return 2 * the_cell_d[2] - the_cell_d[3]
        if allcells[self.id].distance_from(the_cell_d[0]) <= 20:
            return 2 * the_cell_d[2] - the_cell_d[3]#靠的足够近的时候又开始喷射

    # 主要策略
    def strategy(self, allcells):
        threat_list, food_list, food_list2 = self.watch_cells(allcells)
        if allcells[self.id].veloc[0]==0 and allcells[self.id].veloc[1]==0:
            return 2 * math.pi * random.random()#如果一开始速度为零，随机喷出一个cell，获得一个初速度（可以做出改进，多喷几次，角度朝cell多的方向）
        if len(threat_list) != 0:   # 有威胁时
            a = self.escape_threat(threat_list,allcells)
            if a != None:  # 需要逃离时
                return a
        # 若上面未通过返回参数而结束，则继续下面代码
        if len(food_list2) != 0:  # 有不朝自己运动的可吃cell时
            return self.eat_food2(food_list2,allcells)
        if len(food_list) != 0:  # 有朝自己运动的可吃cell时
            return self.eat_food(food_list,allcells)