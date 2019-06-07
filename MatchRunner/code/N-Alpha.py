from consts import Consts
import random
import math
import cell

class Score(object):
    # ) config
    # ) 面积比 对半径
    area_distance = 3
    

    def __init__(self,cell_,local_):
        self.cell = cell_
        self.local = local_
        self.score0 = self.cell.radius/self.local.radius
        self.score =  (self.cell.radius/self.local.radius)**(self.area_distance)/(self.cell.distance_from(self.local)-self.cell.radius-self.local.radius)

class Player(object):
    # ) config
    min_score_rate = 0.01
    max_score_rate = 0.99
    # ) 最大相对速度
    max_veloc_aqrt = 30000
    # ) 最大速度
    abs_veloc_aqrt = 600
    # ) 捕食半径
    capture_rate = 6 
    # ) 预警半径
    resist_rate = 3.5
    @staticmethod
    def if_desire(cell1,cell2):
        if (cell1.veloc[0]-cell2.veloc[0])**2 + (cell1.veloc[1]-cell2.veloc[1])**2 < Player.max_veloc_aqrt  \
            and cell2.radius*0.95 < cell1.radius < cell2.radius* 0.97:
            print('size fit')
            return True
        elif (cell1.veloc[0]-cell2.veloc[0])**2 + (cell1.veloc[1]-cell2.veloc[1])**2 < Player.max_veloc_aqrt  \
            and cell1.radius >  cell2.radius/10 \
            and (cell2.veloc[0]**2+cell2.veloc[1]**2) < Player.abs_veloc_aqrt \
            and cell2.radius*0.95 > cell1.radius > cell2.radius*0.5 :
            print('veloc fit')
            return True
        # ) 需要添加正负的判定 反向意义不大
        # elif (cell1.veloc[0]-cell2.veloc[0])**2 + (cell1.veloc[1]-cell2.veloc[1])**2 < Player.max_veloc_aqrt/4  \
        #     and cell1.radius >  cell2.radius/10 \
        #     and (cell2.veloc[0]**2+cell2.veloc[1]**2) < Player.abs_veloc_aqrt/4 \
        #     # and (cell2.radius[0]-cell1.radius[0])*(cell2.veloc[0] -cell1.veloc[0]) > 0\
        #     # and (cell2.radius[1]-cell1.radius[1])*(cell2.veloc[1] -cell1.veloc[1]) > 0\
        #     and cell2.radius*0.5 > cell1.radius > cell2.radius*0.3 :
        #     print('eat nearby fit')
        #     return True
        return False 

    def __init__(self, id, arg = None):
        self.id = id
        self.target_id = 1 - id

        self.target = None

        self.total_area = None
        self.local_ = None
        self.final = 0

    @property 
    def Rate(self):
        # ) rate the local occur
        r = self.local_.radius
        return r**2 / self.total_area

    def calculate_total_area(self, allcells):
        # ) sum 
        total_ = 0 
        for cell in allcells:
            total_ += cell.radius**2
        self.total_area = total_

    def find(self, allcells):
        target = []
        for cell in allcells:
            if cell.distance_from(self.local_) < self.capture_rate*self.local_.radius:
                target.append(Score(cell,self.local_))

        print(list(map(lambda x:x.cell.id,target)))
        try:
            a = list(filter(lambda x:x.score0 <self.max_score_rate,target ))
            a = sorted(a, key=lambda x: x.score)
            return a
        except:
            return None
 
    def distancetarget(self, mypos, targetpostlist):
        min = 1000 ** 2 + 500 ** 2
        last = targetpostlist[0]
        for i in range(len(targetpostlist)):
            dist = (targetpostlist[i][0] - mypos[0]) ** 2 + (targetpostlist[i][1] - mypos[1]) ** 2
            if dist < min:
                last = targetpostlist[i]
                min = dist
        return last

    def distance2(self, mypos, targetpos):
        dx = mypos[0] - targetpos[0]
        dy = mypos[1] - targetpos[1]
        min_x = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
        min_y = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
        return math.sqrt((min_x) ** 2 + (min_y) ** 2)

    def hunt(self, allcells, targetcelllist): 
        if not targetcelllist:
            return None
        elif type(targetcelllist) == list:
            targetcell = targetcelllist[-1].cell
        else:
            targetcell = targetcelllist
        # ) 速度足够大不在加速
        if not self.if_desire(targetcell,self.local_):
            return
        targetpos = targetcell.pos  # 定点
        targetposlist = [targetpos, [targetpos[0] + 1000, targetpos[1] + 500],
                         [targetpos[0] - 1000, targetpos[1] + 500], \
                         [targetpos[0] + 1000, targetpos[1]], [targetpos[0] - 1000, targetpos[1]], \
                         [targetpos[0], targetpos[1] + 500], [targetpos[0], targetpos[1] - 500],
                         [targetpos[0] - 1000, targetpos[1] - 500], \
                         [targetpos[0] + 1000, targetpos[1] - 500]]
        targetv = targetcell.veloc
        mypos = self.local_.pos
        myv = self.local_.veloc
        targetpos = self.distancetarget(mypos, targetposlist)
        newtargetpos = targetpos
        targetpos[0] = targetpos[0] - mypos[0]
        targetpos[1] = targetpos[1] - mypos[1]
        xiangduiv = [targetv[0] - myv[0], targetv[1] - myv[1]]
        R = self.local_.radius + targetcell.radius
        if xiangduiv[0] != 0:
            k = xiangduiv[1] / xiangduiv[0]  # 函数
            # y-targetpos[1]=k*(x-targetpos[0])
            # -kx+y-targetpos[1]+targetpos[0]*k=0
            d = abs(((-k * targetpos[0]) + (targetpos[1]) + (-targetpos[1] + targetpos[0] * k)) / math.sqrt(k ** 2 + 1))
        else:
            d = targetpos[0] - mypos[0]
        newtargetpos = [targetpos[0] + xiangduiv[0], targetpos[1] + xiangduiv[1]]

        if d <= R and self.distance2(mypos, newtargetpos) - self.distance2(mypos,
                                                                           targetpos) < -2:  # 判断函数到定点的距离  小于 则不发射
            # print("yes")
            return None
        else:
            # d=(targetpos[0]+xiangduiv[0]*t)**2+(targetpos[1]+xiangduiv[1]*t)**2-(5/99)*(t-1)*t/2
            final = (targetpos[0]) ** 2 + (targetpos[1]) ** 2
            flag = 1
            for t in range(100):
                d = ((targetpos[0] + xiangduiv[0] * t) ** 2 + (targetpos[1] + xiangduiv[1] * t) ** 2) - (
                        (5 / 99) * (t - 1) * t / 2) ** 2
                # print(d)
                if d == 0:
                    time = t
                    flag = 3
                    # print("flag=3")
                    break
                elif final * d < 0:
                    final1 = t - 1
                    final2 = t
                    flag = 2
                    # print("flag=2")
                    break
                else:
                    final = d
            if flag == 1:
                # print("haha")
                return None  # 需要换target
            elif flag == 2:
                test = ((targetpos[0] + xiangduiv[0] * final1) ** 2 + (targetpos[1] + xiangduiv[1] * final1) ** 2) - (
                        (5 / 99) * (final1 - 1) * final1 / 2) ** 2
                t = final1
                for a in range(21):
                    t = t + 0.05
                    d = (targetpos[0] + xiangduiv[0] * t) ** 2 + (targetpos[1] + xiangduiv[1] * t) ** 2 - (
                            (5 / 99) * (t - 1) * t / 2) ** 2
                    if d == 0:
                        time = t
                        # print("final1")
                        break
                    elif test * d < 0:
                        time = t
                        # print("final2")
                        break
                    else:
                        test = d
            # 此时求出了相遇的时间time
            newtargetpos = [newtargetpos[0] + xiangduiv[0] * time, newtargetpos[1] + xiangduiv[1] * time]
            degree = math.atan2(-newtargetpos[0], -newtargetpos[1])
            if self.local_.radius>50:  #够大不发射
                return None
            else:
                return degree

        # newpos=[mypos[0]+myv[0]+math.sin(degree)**0.05,mypos[1]+myv[1]+math.cos(degree)**0.05]下一帧自己的位置

    def danger1(self, me, other, allcells):
        t = self.hunt(allcells, other)[1]
        newpos = self.hunt(allcells, other)[2]
        vx = newpos[0] - self.local_.pos[0]
        vy = newpos[1] - self.local_.pos[1]
        flag = False
        for i in range(t):
            for cell in allcells:
                if cell.radius > self.local_.radius * (0.99 ** i):
                    if cell != self.local_ and math.sqrt(
                            (self.local_.pos[0] + i * vx - cell.pos[0] - i * cell.veloc[0]) ** 2 + \
                            (self.local_.pos[1] + i * vx - cell.pos[0] - i * cell.veloc[1]) ** 2) <= cell.radius + \
                            self.local_.radius:
                        flag = True
                        break
        return flag

    # def defense(self.allcells):
    #     # you should break that you will have time to escapt 
    #     target = []
    #     for cell in allcells:
    #         if cell.distance_from(self.local_) < self.resist_rate*self.local_.radius:
    #             target.append(Score(cell,self.local_))
    #     print(list(map(lambda x:x.cell.id,target)))
    #     try:
    #         a = list(filter(lambda x:x.score0 > self.max_score_rate,target ))
    #         a = sorted(a, key=lambda x: x.score)
    #         return a
    #     except:
    #         return None

    def strategy(self, allcells):
        '''if self.local_.veloc[0]**2 + self.local_.veloc[1]**2 > 100.0:  # 限制最大速度
            return math.atan2(self.local_.veloc[0], self.local_.veloc[1]) + math.pi'''
        
        if self.total_area is None:
            self.calculate_total_area(allcells)
        self.local_ = allcells.pop(self.id)
        
        
        # 直接躲避优先
        # 旧版danger
        '''for cell in allcells:
            if cell.radius > allcells[self.id].radius and\
                ((cell.distance_from(allcells[self.id]) < 50 + cell.radius + allcells[self.id].radius and \
                cell.veloc[0] * allcells[self.id].veloc[0] < 0 and \
                cell.veloc[1] * allcells[self.id].veloc[1] < 0) or \
                cell.distance_from(allcells[self.id]) < 30 + cell.radius + allcells[self.id].radius):
                dx = cell.pos[0] - allcells[self.id].pos[0]
                dy = cell.pos[1] - allcells[self.id].pos[1]
                return math.atan2(dx, dy)'''

        # 新版danger
        for cell in allcells:
            k = cell.radius / self.local_.radius
            if k > 2:
                duobi1, duobi2 = k * 30, k * 15
            else:
                duobi1, duobi2 = 50, 30
            '''if k > 1 and (self.distance2(self.local_.pos, cell.pos) < duobi1 + cell.radius + allcells[
                self.id].radius and \
                          cell.veloc[0] * self.local_.veloc[0] < 0 and cell.veloc[1] * self.local_.veloc[
                              1] < 0):
                dx = cell.pos[0] - self.local_.pos[0]
                dy = cell.pos[1] - self.local_.pos[1]
                if self.distance2(self.local_.pos, cell.pos) == cell.distance_from(self.local_):  # 未跨边界
                    return math.atan2(dx, dy) + math.pi / 4
                else:  # 跨边界则返向喷球
                    return math.atan2(-dx, dy) + math.pi / 4
            el'''
            if cell.radius > self.local_.radius and \
                    self.distance2(self.local_.pos, cell.pos) < duobi2 + cell.radius + self.local_.radius:
                dx = cell.pos[0] - self.local_.pos[0]
                dy = cell.pos[1] - self.local_.pos[1]
                if self.distance2(self.local_.pos, cell.pos) == cell.distance_from(self.local_):
                    # 未跨边界
                    return math.atan2(dx, dy)
                else:  # 跨边界则返向喷球
                    return math.atan2(-dx, dy)

        for cell in allcells: # 水平方向上有大球靠近，停止竖向喷
            if allcells[self.id].radius < 27 or (cell.id != self.id and cell.radius > allcells[self.id].radius and \
                -(cell.radius+allcells[self.id].radius+80)< cell.pos[0] - allcells[self.id].pos[0]<(cell.radius+allcells[self.id].radius+80)):
                self.final = 0
        if self.final == 1:
            if allcells[self.id].radius > 40:
                sss = 1/48
            else:
                sss = 1/72
            if allcells[self.id].veloc[0] > 0:
                return (1+sss) * math.pi if random.random() > 0.5 else None
            else:
                return (1-sss) * math.pi if random.random() > 0.5 else None
        elif self.final == 2:
            if allcells[self.id].radius > 40:
                sss = 1/48
            else:
                sss = 1/72
            if allcells[self.id].veloc[0] > 0:
                return (2-sss) * math.pi if random.random() > 0.5 else None
            else:
                return sss * math.pi if random.random() > 0.5 else None
        if allcells[self.id].radius > 27 and -0.3 < allcells[self.id].veloc[0] < 0.3:
            if allcells[self.id].veloc[1] > 0:
                self.final = 1
            else:
                self.final = 2

        if self.Rate > 0.36:
            # ) 追击 
            for cell in allcells:
                if cell.id == self.target_id:
                    self.target = cell
                    break
        else:
            self.target = self.find(allcells.copy())
            print(len(self.target))
        result = self.hunt(allcells,self.target)

        return result 


