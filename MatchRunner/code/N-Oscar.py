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
#from settings import Settings
import random
import math

#初始化节点类和图类以便后续定义相应结构
class Vertex:
    def __init__(self,key):
        self.id = key
        self.connectedTo = {}
        
    def addNeighbor(self,nbr,weight=0):
        self.connectedTo[nbr] = weight
    
    def __str__(self):
        return str(self.id)+' connectedTo: '+str([x.id for x in self.connectedTo])
    
    def getConnections(self):
        return self.connectedTo.keys()
    
    def getId(self):
        return self.id
    
    def getWeight(self,nbr):
        return self.connectedTo[nbr]
    
class Graph:
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0
        
    def addVertex(self,key):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key)
        self.vertList[key] = newVertex
        return newVertex
    
    def getVertex(self,n):
        if n in self.vertList:
            return self.vertList[n]
        else:
            return None
        
    def __contains__(self,n):
        return n in self.vertList
    
    def addEdge(self,f,t,cost=0): #在节点之间加边，即权重
        if f not in self.vertList:
            nv = self.addVertex(f)
        if t not in self.vertList:
            nv = self.addVertex(t)
        self.vertList[f].addNeighbor(self.vertList[t],cost)
    
    def getVertices(self):
        return self.vertList.keys()
    
    def __iter__(self):
        return iter(self.vertList.values())
    
class Player():
    def __init__(self, id, arg = None):
        self.id = id
        self.first = 1
        self.target = None #选择target作为吃球目标并继承
        print("MUSIC!!!")
        
    
    
    def strategy(self, allcells):     

        def norm(v):#返回v的模长
            return math.sqrt(v[0]**2+v[1]**2)
        
        def screen_cross(v): #返回穿屏的最小向量
            nonlocal world_x, world_y #引入world的基本变量
            #返回穿屏的位移中绝对值最小的位移
            v_x = sorted([v[0],v[0]-world_x,v[0]+world_x],key = lambda x:abs(x))[0] 
            v_y = sorted([v[1],v[1]-world_y,v[1]+world_y],key = lambda x:abs(x))[0]
            return [v_x, v_y]
            
        def target_theta(v): #返回对应向量与y轴正方向的夹角
            #考虑到三角函数的性质，只需要计算所求角的余弦值，根据x的正负判断夹角边的方向。
            c_theta = math.acos(v[1]/norm(v))
            #vx大于0表示角度在0到π之间
            if v[0] >= 0:
                return c_theta
            #vx小于0表示角度在π到2π之间
            else:
                return 2*math.pi-c_theta
        
        def vector_product(v1,v2): #计算向量的内积
            return v1[0]*v2[0]+v1[1]*v2[1]
        
        def vector_toward(pos1,pos2): #计算从pos1到pos2的位移
            return [pos2[0]-pos1[0],pos2[1]-pos1[1]] 
        
        def vertical_dis(a,b,c): #计算点a到点b与点c所确定直线的距离
            #确认bc点所确定的直线的一般表达式Ax+By+C=0的参数
            A = c[1]-b[1]
            B = b[0]-c[0]
            C = b[1]*c[0]-c[1]*b[0]
            #根据公式确定距离
            up = abs(a[0]*A+a[1]*B+C)
            down = math.sqrt(A*A+B*B)
            if down != 0:
                return up/down
            else: #极个别情况下传入bc坐标相等，由于该公式用于计算速度与位移的距离，则直接返回向量a的模
                return norm(a)
        
        #操作
        def static_one(self_cell, target):
            #0:不建议吃；1：可以喷射吃‘2：无需喷射即可吃到
            dist = screen_cross(vector_toward(self_cell.pos, target.pos)) #计算两个cell的穿屏最小位移
            rel_v = [self_cell.veloc[0]-target.veloc[0], self_cell.veloc[1]-target.veloc[1]] #计算两个cell的相对速度
            h = vertical_dis(dist,[0,0],rel_v) #计算速度方向与位移方向的夹角
            #速度与位移夹角为负或速度相对距离过小时初步判断不能吃到球，不建议吃
            if vector_product(rel_v, dist) < 0 or norm(rel_v)< norm(dist)*0.01: 
                s = 0
            #保持当前状态运动可以吃到时不继续喷球
            elif self_cell.radius+target.radius > h and norm(rel_v) > norm(dist)*0.02:
                s = 2
            #需要喷射球才可以吃到
            else:
                s = 1
            return s 
        
        #判断是否安全，返回list，内容为[是否安全，造成威胁的球]   
        def safe(self_cell,near_three_bcells):
            if len(near_three_bcells) == 0: #周围没有大球时安全=0，威胁球为None
                return [0,None]
            else:
                for i in near_three_bcells: #检测威胁球
                    cel = i
                    dist = screen_cross(vector_toward(self_cell.pos,cel.pos)) #计算两个cell的穿屏最小位移
                    v1 = [self_cell.veloc[0]-cel.veloc[0], self_cell.veloc[1]-cel.veloc[1]] #计算两个cell的相对速度
                    h = vertical_dis(dist,[0,0],v1) #计算速度方向与位移方向的夹角
                    if self_cell.radius+i.radius>=h+1e-3 and v1[0]*dist[0]+v1[1]*dist[1]>0: #维持当前状态会相撞
                        return [1,i] #返回安全=1（即不安全）与产生威胁的球
                return [0, None]
        
        def thet(a,b):#向量a到b的有向角([0,2pi))
            if norm(a) * norm(b) <1e-6: #计算向量的模长，过小时认为不存在
                return 0
            det = a[0]*b[1]-a[1]*b[0] #计算向量的外积
            angle = vector_product(a,b)/norm(a)/norm(b) #计算两向量的夹角的余弦
            if abs(angle)>1-1e-3: #当夹角余弦值接近1的时候
                if angle<0:
                    return math.pi
                else:
                    return 0
            angle = math.acos(angle) #反推计算向量夹角的角度
            if det>0: #根据内积判断角度范围
                return 2*math.pi-angle
            else:
                return angle
        
        def chaise(self_cell, target): #定义吃球函数
            p1 = self_cell.pos #定义两个cell各自的位置
            p2 = target.pos
            v1 = [self_cell.veloc[0]-target.veloc[0],self_cell.veloc[1]-target.veloc[1]]
            a = vector_toward(p2,p1)
            a = screen_cross(a)
            c = [a[0]-v1[0],a[1]-v1[1]] #定义位移向量与相对速度向量的差，即确定喷射角度
            theta1 = thet([-v1[0],-v1[1]],c) #计算速度与喷射角度的角度差
            if theta1 > math.pi:
                theta1 = theta1-2*math.pi
            r = abs(theta1/math.pi) #确定调整角度的相对值
            if norm(v1)<0.3: #v较小时，直接返回调整角度
                return thet([0,1],a)+math.pi                     
            if r>0.8:
                r1=1-5*(1-r)
            else:
                r1=r**2
            theta0 = theta1*r1
            return thet([0,1],[-v1[0],-v1[1]]) + theta0 + math.pi
                        
        def escape(self_cell, target): ##逃跑函数
            self_veloc = self_cell.veloc #定义速度
            rel_v = [self_veloc[0]-target.veloc[0], self_veloc[1]-target.veloc[1]] #获取相对速度
            dist = screen_cross(vector_toward(self_cell.pos,target.pos)) #获取相对位移
            eject_veloc = [dist[0] - rel_v[0], dist[1] - rel_v[1]] #根据相对距离最大原则返回喷球的角度，即位移向量与速度向量之差
            return target_theta(eject_veloc) #利用target_theta函数确定喷射角度
        
        def zipcell(cell): #定义cell压缩变形函数，使用tuple定义速度与位置，防止因为地址相同而在预测中改变原始传入的cell参数
            ziptuple = (cell.id,tuple(cell.pos),tuple(cell.veloc),str(cell.radius),cell.collide_group,cell.dead)
            return ziptuple
        
        def zipcells(cells): #对包含cell的list做统一变换，返回一个list       
            zipcell_out = [zipcell(cell) for cell in cells]
            return zipcell_out
        
        def unpackcell(ziptuple): #“解压”变换后的tuple，重新生成所需的cell
            from cell import Cell
            unpackcell = Cell(ziptuple[0],list(ziptuple[1]),list(ziptuple[2]),float(ziptuple[3]))
            unpackcell.collidegroup = ziptuple[4]
            unpackcell.dead = ziptuple[5]
            return unpackcell
        
        def unpackcells(zipcell_list): #对一整组list进行解压，获取类似于allcells的list                        
            unpack_list = [unpackcell(ziptuple) for ziptuple in zipcell_list]
            return unpack_list  
        
        def cell_redefine(inputcell): #对单个的cell进行变换，防止地址调用
            return unpackcell(zipcell(inputcell))
        
        #基本参数
        save = zipcells(allcells) #储存allcell的基本信息
        world_x = Consts["WORLD_X"] #地图长
        world_y = Consts["WORLD_Y"] #地图宽
        eject_v = Consts["DELTA_VELOC"] #喷射速度
        outmass = Consts["EJECT_MASS_RATIO"] #喷射出的质量
        dv1 = Consts["DELTA_VELOC"] #喷射速度
        get_v = dv1*Consts["EJECT_MASS_RATIO"] #得到速度      
        self_cell = allcells[self.id] #自己对应的cell
        self_veloc = self_cell.veloc #自己对应的速度
        enemy_cell = allcells[1-self_cell.id] #敌方的cell
        dis_to_enemy = screen_cross([enemy_cell.pos[0]-self_cell.pos[0],enemy_cell.pos[1]-self_cell.pos[1]]) #与敌方的距离
        sorted_cells = sorted(allcells, key = lambda cell: norm(screen_cross(vector_toward(cell.pos,self_cell.pos))))[1:len(allcells)] #按距离对所有球排序
        #下列是根据需求筛选出的不同条件下的备选目标cell的list
        near_cells = [x for x in sorted_cells if norm(screen_cross(vector_toward(x.pos,self_cell.pos))) < 3*self_cell.radius]
        near_one_cells = [x for x in sorted_cells if norm(screen_cross(vector_toward(x.pos,self_cell.pos))) < 15*self_cell.radius]
        near_two_cells = [x for x in sorted_cells if norm(screen_cross(vector_toward(x.pos,self_cell.pos))) < 40*self_cell.radius]
        near_three_cells = [x for x in sorted_cells if norm(screen_cross(vector_toward(x.pos,self_cell.pos))) < 3*self_cell.radius]
        nearscells = [x for x in near_cells if 0.3*self_cell.radius<x.radius<self_cell.radius]
        near_one_scells = [x for x in near_one_cells if 0.3*self_cell.radius<x.radius<self_cell.radius]
        near_two_scells = [x for x in near_two_cells if 0.3*self_cell.radius<x.radius<self_cell.radius]
        nearbcells = [x for x in near_cells if x.radius>self_cell.radius]
        nearb_three_bcells = [x for x in near_three_cells if x.radius>self_cell.radius]
        other_cells = [x for x in allcells if x.id > 1 and x.dead == False]

        #基本全图预测
        def cell_predict(allcells, predict_frame): #定义全图预测函数
            predict_cells = [cell_redefine(x) for x in allcells] #做压缩、解压的操作，防止干扰到原始的allcells
            for cell in predict_cells: #模拟cell的运动
                if not cell.dead:
                    cell.move(Consts["FRAME_DELTA"])
            def absorb(collision): #根据源代码，定义吸收函数
                mass = sum(predict_cells[ele].area() for ele in collision)
                px = sum(predict_cells[ele].area() * predict_cells[ele].veloc[0] for ele in collision)
                py = sum(predict_cells[ele].area() * predict_cells[ele].veloc[1] for ele in collision)
                collision.sort(key = lambda ele: predict_cells[ele].radius)
                biggest = collision.pop()
                predict_cells[biggest].radius = (mass / math.pi) ** 0.5
                predict_cells[biggest].veloc[0] = px / mass
                predict_cells[biggest].veloc[1] = py / mass
                for ele in collision:
                    predict_cells[ele].dead = True
            #根据project的源代码定义collision，检测并执行碰撞
            collisions = []
            for i in range(len(predict_cells)):
                if predict_cells[i].dead:
                    continue
                for j in range(i + 1, len(predict_cells)):
                    if not predict_cells[j].dead and predict_cells[i].collide(predict_cells[j]):
                        if predict_cells[i].collide_group == None == predict_cells[j].collide_group:
                            predict_cells[i].collide_group = predict_cells[j].collide_group = len(collisions)
                            collisions.append([i, j])
                        elif predict_cells[i].collide_group != None == predict_cells[j].collide_group:
                            collisions[predict_cells[i].collide_group].append(j)
                            predict_cells[j].collide_group = predict_cells[i].collide_group
                        elif predict_cells[i].collide_group == None != predict_cells[j].collide_group:
                            collisions[predict_cells[j].collide_group].append(i)
                            predict_cells[i].collide_group = predict_cells[j].collide_group
                        elif predict_cells[i].collide_group != predict_cells[j].collide_group:
                            collisions[predict_cells[i].collide_group] += collisions[predict_cells[j].collide_group]
                            for ele in collisions[predict_cells[j].collide_group]:
                                predict_cells[ele].collide_group = predict_cells[i].collide_group
                            collisions[predict_cells[j].collide_group] = []
            for collision in collisions:
                if collision != []:
                    absorb(collision)
            predict_cells = [cell for cell in predict_cells if not cell.dead]
            #执行递归
            if predict_frame == 1:
                return predict_cells
            else:
                return cell_predict(predict_cells, predict_frame-1)        

        
        #对target的球做预测
        def loss_predict(self_cell, target): #给定吃球函数情况下通过模拟cell的运动预测吃球时间和收益         
            #通过cell_redefine对输入的cell重定义，防止干扰到后续计算
            self_cell_p = cell_redefine(self_cell)
            target = cell_redefine(target)
            frame_count = 1 #计时
            eject_count = 0 #喷射计数
            while self_cell_p.collide(target) != True and frame_count < 60 and eject_count < 20: #当未相撞且时间、质量损失在可接受范围内时
                frame_count += 1
                if static_one(self_cell_p, target) == 0: #如果static认为不适合吃，直接返回None
                    return [None, None]
                elif static_one(self_cell_p, target) == 1: #如果static认为需要喷射，则调用喷射函数
                    eject_count += 1 #记一次喷射
                    self_cell_p = cell_redefine(self_cell_p)
                    target = cell_redefine(target)
                    self_cell_p.radius = 0.99**0.5*self_cell_p.radius #喷射损失
                    chaise_theta = chaise(self_cell_p, target) #确定喷射角度
                    #确定喷射后的速度
                    self_cell_p.veloc = [self_cell_p.veloc[0]-Consts["DELTA_VELOC"] * math.sin(chaise_theta) * Consts["EJECT_MASS_RATIO"],
                                       self_cell_p.veloc[1]-Consts["DELTA_VELOC"] * math.cos(chaise_theta) * Consts["EJECT_MASS_RATIO"]]
                #执行运动与喷射
                self_cell_p.move(Consts["FRAME_DELTA"])                
                target.move(Consts["FRAME_DELTA"])
            if self_cell_p.collide(target) != True or self_cell_p.radius < target.radius: #喷射过去后产生较大损失
                return [None, None]
            else:
                #计算相撞后的质量与速度
                mass = self_cell_p.area()+target.area()
                px = self_cell_p.area() * self_cell_p.veloc[0]+target.area() * target.veloc[0]
                py = self_cell_p.area() * self_cell_p.veloc[1]+target.area() * target.veloc[1]
                self_cell_p.veloc = [px/mass,py/mass]
                self_cell_p.radius = (mass / math.pi) ** 0.5                
                return [self_cell_p,frame_count] #返回相撞后的新cell与时间预测
        
        def eject_1(): #第一帧时候进行目标的判定
            nonlocal near_two_scells, other_cells, self_cell
            theta = None
            measure = -100 
            save_near_cells = zipcells(near_two_scells) #将cells打包成元组防止函数外变量也改变
            save_other_cells = zipcells(other_cells)
            for i in range(len(near_two_scells)):
                target = near_two_scells[i]
                save_tar = zipcell(target)
                new_lst = loss_predict(cell_redefine(self_cell),cell_redefine(target))
                other_cells = unpackcells(save_other_cells) #解压打包元组
                if new_lst == [None, None]:
                    #print(1)
                    continue                
                else: #在用loss_predict函数预测的值有效时，采用全图预测确定目标不会死亡
                    predictcells = cell_predict(near_two_scells, new_lst[1])
                    other_cells = unpackcells(save_other_cells)
                    allcells = unpackcells(save)
                    self_cell = allcells[self.id]
                    target = unpackcell(save_tar)
                    if target.id not in [x.id for x in predictcells]:
                        continue
                    elif ((new_lst[0].radius)**2-(self_cell.radius)**2-new_lst[1]) > measure: #找到给定罚函数最优的目标
                        allcells = unpackcells(save)
                        other_cells = [x for x in allcells if x.id > 1 and x.dead == False]
                        self_cell = allcells[self.id]
                        target = other_cells[i]
                        measure = ((new_lst[0].radius)**2-(self_cell.radius)**2) - new_lst[1]
                        self.target = target.id
   
        def build(self_cell, allcells):#将附近几个可以迟到的球存入一个图
            g = Graph()
            g.addVertex(self_cell.id)#把自己的id存入图
            second_id = []
            near_one_cells = [x for x in allcells if norm(screen_cross(vector_toward(x.pos,self_cell.pos))) < 20*self_cell.radius and x.id != self_cell.id]
            near_one_scells = [x for x in near_one_cells if 0.4*self_cell.radius<x.radius<0.95*self_cell.radius]
            for i in near_one_scells:#和自己距离在十倍自己半径之内的球存入图
                g.addVertex(i.id)
                second_id.append(i.id)
            for j in second_id:
                second_temp_lst = [x for x in allcells if x.id == j]
                g.addEdge(self_cell.id, j, norm(screen_cross(vector_toward(self_cell.pos, second_temp_lst[0].pos))))#将自己与和自己距离近的球节点进行连接
            for k in second_id:#每个第二层球和其周围距离其较近的球存入图并且和其连接
                second_temp_lst = [x for x in allcells if x.id == k]
                second_near_cells = [x for x in allcells if norm(screen_cross(vector_toward(x.pos,second_temp_lst[0].pos))) < 7*self_cell.radius and x.id != second_temp_lst[0].id]
                second_near_scells = [x for x in second_near_cells if 0.4*self_cell.radius<x.radius<self_cell.radius]
                for third_ball in second_near_scells:
                    g.addVertex(third_ball.id)
                    g.addEdge(k, third_ball.id, norm(screen_cross(vector_toward(second_temp_lst[0].pos, third_ball.pos))))
            return g#返回这个图

        def search_road(self_cell,g,allcells):#根据给定的图找到最合适的路径
            allcells = unpackcells(zipcells(allcells))
            road_value = {}#初始化一个字典，用来存放各条路径的价值
            start = g.getVertex(self_cell.id)#自己对应的顶点
            for second_Vertex in start.getConnections():#对第二层顶点进行遍历
                second_id = second_Vertex.getId()
                second_cell = [x for x in allcells if x.id == second_id][0]#找到顶点对应的cell
                target = cell_redefine(second_cell)
                save_tar = zipcell(target)
                new_lst = loss_predict(cell_redefine(self_cell),cell_redefine(target))
                if new_lst == [None, None]:
                    value = -30
                else:
                    value = (new_lst[0].area()-self_cell.area())/new_lst[1]#value的第一部分，迟到第二层球的质量比需要的时间
                
                total_third_mass = 0#用来储存第三层球的总质量
                total_third_distance = 0#存放第三层球的总距离
                third_count = 0
                for third_Vertex in second_Vertex.getConnections():#对第三层球进行遍历
                    third_id = third_Vertex.getId()
                    third_count += 1
                    third_cell = [x for x in allcells if x.id == third_id][0]#根据顶点找到这个球
                    total_third_mass += third_cell.area()
                    total_third_distance += norm(screen_cross(vector_toward(third_cell.pos, second_cell.pos)))
                if third_count == 0:#没有第三层球的情况
                    average_distance = 100
                else:
                    average_distance = total_third_distance/third_count
                value += total_third_mass/(3*average_distance)#value函数的第二部分，和第二层球距离近的第三层球的总质量比平均距离
                road_value[second_id] = value#将value存入字典的对应位置
            target_id = None
            target_value = 0
            for second_Vertex in start.getConnections():#找到最大的value对应的id作为taget的id
                if road_value[second_Vertex.getId()] > target_value:
                    target_value = road_value[second_Vertex.getId()]
                    target_id = second_Vertex.getId()
            return target_id
          
        def main():
            if self.first == 1: #第一帧执行eject_1，确定开局喷射方向
                self.first = 0
                return eject_1()                        
            if safe(self_cell, nearbcells)[0] == 1: #球不安全
                #print('escape') 
                return escape(self_cell, safe(self_cell, nearbcells)[1]) #执行逃跑函数
            if safe(self_cell, nearbcells)[0] == 0: #确认安全时
                if self.target != None and self.target in [x.id for x in allcells]: #继承上一帧的target，并检测其是否存在
                    #print('chase')
                    #print(self.target)
                    target = [x for x in allcells if x.id == self.target][0] #指定喷射目标
                    if static_one(self_cell, target) == 1: #判断是否需要喷射
                        return chaise(self_cell, target) #执行喷射
                    else:
                        return None #不执行喷射
                else:
                    target_id = search_road(cell_redefine(self_cell),build(self_cell, allcells),allcells) #分析目标
                    if [x for x in allcells if x.id == target_id] != []: #检验是否符合吃球条件
                        self.target = target_id #登录目标id
                        target = [x for x in allcells if x.id == self.target][0] #确定cell
                        #print('chase')
                        if static_one(self_cell, target) == 1: #判断是否需要喷射
                            return chaise(self_cell, target) #执行喷射
                        else:
                            return None #不执行喷射
                    else:
                        return None #不执行喷射

        return main()