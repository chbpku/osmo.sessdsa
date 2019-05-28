from consts import Consts
import math
import numpy as np


class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.me = None  # 包含我方信息的cell
        self.target = None  # target是目标本身,而不是它的id
        self.threats = None
        self.allcells = None
        self.grownum = 0  # 喷射次数
        self.iscal = False  # 用于判断grow是否重新计算
        self.angle = 0  # grow的喷射角度

    def strategy(self, allcells):
        # 更新Player的自身属性
        self.allcells = allcells
        for each in allcells:
            if each.id == self.id:
                self.me = each
                break
        # 确定目标.如果原目标不满足或者被吞噬则换一个目标,若满足则更新目标的信息
        if self.hasTarget() is False:
            print("Target changed!")
            self.target = self.selectTarget()
        else:
            for each in allcells:
                if each.id == self.target.id:
                    self.target = each
                    break
        # 更新威胁
        self.threats = self.findThreats()
        #print(len(self.threats))
        if len(self.threats) == 0:
            theta = None
            
            print("grow")
        else:
            theta = self.safe()
            print("safe")
        return theta

    def findThreats(self):
        threats = []
        for each in self.allcells:
            if self.me.distance_from(each)-self.me.radius-each.radius < 20:
                if each.radius > self.me.radius:
                    if self.calc_time(each) < Consts["FPS"]*2:
                        threats.append(each)
                    elif self.me.distance_from(each) < 10:
                        threats.append(each)
        return threats

    # 是否依旧追踪上一回合的target
    def hasTarget(self):
        result = True
        # 如果self.target已被吞噬
        
        for each in self.allcells:
            if each.id == self.id:
                result = False
            break
        # 如果self.target为None
        if self.target is None:
        
            result = False
        elif self.distance(self.target,self.me)[2]>150:
            result = False
                
        # 目标过小或者过大时self.target.radius < self.me.radius * 0.05 
        elif  self.target.radius >= self.me.radius:
            result = False
        #elif self.calc_time(self.target) >= Consts["FPS"]*5:
            #result = False
        return result

    # 在allcells里找出最优的目标
    def selectTarget(self):
        target = None
        vx = self.me.veloc[0]
        vy = self.me.veloc[1]
        mindistance = 1000
        maxweight = 0#权重因子，用于判断更容易吃的目标
        for each in self.allcells:

            weight = 0
            mes = self.distance(self.me,each)
            if each.radius < self.me.radius * 0.9:
                if math.sqrt(vx**2+vy**2) > 0.5:
                    #vx = vx - each.veloc[0]
                    #vy = vy - each.veloc[1]
                    if vx and vy:
                        angle = (mes[0]*vx + mes[1]*vy)/\
                                (math.sqrt((mes[0]**2+mes[1]**2)*(vx**2+vy**2)))
                    else:
                        angle = 2
                    if angle > 0.0:#在我的速度方向上的加权
                        weight+=2
                    if angle > 0.6:
                        weight+=3
                if mes[2] < 3*self.me.radius and each.radius < self.me.radius * 0.9:
                    weight+=4
                if self.me.radius * 0.3 < each.radius < self.me.radius * 0.7:#半径合适的加权
                    weight+=2
                if maxweight <= weight:
                    maxweight = weight
                    if mindistance > mes[2] and self.targetlife(each):
                        mindistance = mes[2]
                        target = each
        return target
    
    def targetlife(self,each):#判断目标是否快要死了
        for other in self.allcells:
            if each != other:
                mes = self.distance(each,other)
                vx = each.veloc[0] - other.veloc[0]
                vy = each.veloc[1] - other.veloc[1]
                angle = (mes[0]*vx + mes[1]*vy)/\
                        (math.sqrt((mes[0]**2+mes[1]**2)*(vx**2+vy**2)))
                newradius = math.sqrt(each.radius**2+other.radius**2)
                if angle > 0.9 and mes[2]<100 and newradius>self.me.radius:
                    return False
                else:
                    return True

    def selectTarget2(self):
        target = None
        mintime = 1000
        for each in self.allcells:
            if self.me.radius * 0.1 < each.radius < self.me.radius * 0.9:
                if self.calc_time(each) < mintime:
                    target = each
                    mintime = self.calc_time(each)
        return target

    # 返回最小距离,以及由我指向对方的位置矢量(包括跨屏)[x, y, distance]
    def distance(self, cell1, cell2):  # 输入顺序有要求,cell1应为自己的坐标
        lenth = 1000
        width = 500
        if cell2 != None and cell1!= None:
            dx = cell2.pos[0] - cell1.pos[0]
            dy = cell2.pos[1] - cell1.pos[1]
        else:
            return [0,0,1000]
        min_x = min(abs(dx), abs(dx + lenth), abs(dx - lenth))
        min_y = min(abs(dy), abs(dy + width), abs(dy - width))
        if min_x == abs(dx):
            x = dx
        elif min_x == abs(dx + lenth):  # 此时我方在屏幕右端,对方在左端
            x = dx + lenth
        else:  # 此时我方在屏幕左端,对方在右端
            x = dx - lenth
        if min_y == abs(dy):
            y = dy
        elif min_y == abs(dy + width):  # 此时我方在x轴附近,对方在上端
            y = dy + width
        else:
            y = dy - width  # 此时对方在x轴附近我方在上端
        distance = math.sqrt(min_x ** 2 + min_y ** 2)
        Distance = [x, y, distance]  # 返回最小距离,以及由我指向对方的位置矢量(包括跨屏)
        return Distance


    def grow1(self, cell):
        if self.target is None:
            return None
        #mes = [cell.pos[0]-self.me.pos[0],cell.pos[1]-self.me.pos[1],\
         #   math.sqrt((cell.pos[0]-self.me.pos[0])**2+(cell.pos[1]-self.me.pos[1])**2)]
        mes = self.distance(self.me, cell)

        # 目标的参数
        r = cell.radius
        vx = cell.veloc[0]
        vy = cell.veloc[1]
        # 自己的参数
        selfvx = self.me.veloc[0]
        selfvy = self.me.veloc[1]
        selfr = self.me.radius
        # 径矢的模长
        rlen = mes[2]

        if rlen-r-selfr<5:
            print('ate')
            self.grownum = 0
        # 相对速度和径矢之间的夹角
        deltaangle = math.fabs(self.xangle(selfvx-vx,selfvy-vy)-self.xangle(mes[0],mes[1]))
        if deltaangle>=math.pi:
            deltaangle = 2*math.pi-deltaangle
        # 阈值根据对方的半径设置
        if rlen>r+selfr:
            upperangle = math.asin((r+selfr)/rlen)
        else:
            upperangle = 4
        # 如果相对速度和径矢之间的夹角不够小，就对速度进行调整
        a = math.fabs(self.xangle(mes[0],mes[1])-self.xangle(selfvx-vx,selfvy-vy))
        print(str(min(2*math.pi-a,a))\
            +'   '+str((self.distance(self.me,cell)[2])))
        #if mes[2]>r+selfr:
            #return self.xangle(-mes[0],-mes[1])
        if deltaangle > upperangle and math.sqrt((selfvx-vx)**2+(selfvy-vy)**2)>0.3:
            u = min(3,math.sqrt((selfvx-vx)**2+(selfvy-vy)**2)/math.fabs(math.cos(deltaangle)))
            anvx = 1.3*u*mes[0]/rlen-(selfvx-vx)
            anvy = 1.3*u*mes[1]/rlen-(selfvy-vy)
            if math.fabs(self.xangle(-anvx,-anvy)-self.xangle(-selfvx,-selfvy))<0.2:
                return None
            if math.sqrt(selfvx**2+selfvy**2)<2:
                return self.xangle(-anvx,-anvy)
        #elif deltaangle > upperangle and math.sqrt((selfvx-vx)**2+(selfvy-vy)**2)<=0.3:
            #print('speed')
            #return self.xangle(-selfvx+vx,-selfvy+vy)
        else:
            return None

    def grow2(self, cell):
        if self.target is None:
            return None
        mes = self.distance(self.me, cell)
        # 目标的参数
        r = cell.radius
        vx = cell.veloc[0]
        vy = cell.veloc[1]
        # 自己的参数
        selfvx = self.me.veloc[0]
        selfvy = self.me.veloc[1]
        selfr = self.me.radius
        # 径矢的模长
        rlen = mes[2]
        # 相对追击速度大小为abu,保证喷射次数最小
        angleu = self.xangle(selfvx - vx, selfvy - vy)
        angler = self.xangle(mes[0], mes[1])
        abu = math.sqrt((selfvx - vx) ** 2 + (selfvy - vy) ** 2) * math.cos(angleu - angler)
        deltavx = 2 * vx + abu * mes[0] / rlen - selfvx  # 总的速度变化量
        deltavy = 2 * vy + abu * mes[1] / rlen - selfvy
        opangle = self.xangle(-deltavx, -deltavy)  # 喷射角度
        # 喷射次数
        opnum = -(1 - 1 / Consts["EJECT_MASS_RATIO"]) * \
                math.sqrt(deltavx ** 2 + deltavy ** 2) // Consts["DELTA_VELOC"]
        return [opangle, opnum]

    # 输入一个矢量，求出该矢量和y轴正向的夹角，0到2π
    def xangle(self, x, y):
        if x == 0:
            if y > 0:
                return 0.0
            else:
                return math.pi
        elif x > 0:
            if y == 0:
                return 0.5 * math.pi
            elif y > 0:
                return math.atan2(x, y)
            else:
                return math.pi - math.atan2(x, -y)
        else:
            if y == 0:
                return 1.5 * math.pi
            elif y > 0:
                return math.atan2(y, -x) + 1.5 * math.pi
            else:
                return math.pi + math.atan2(x, y)

    # 返回两点最短连线与x轴的夹角, start/end为[x, y]列表
    def calc_angle(self, start, end):
        # end的另外四种可能位置
        end1 = [end[0], end[1] - Consts["WORLD_Y"]]
        end2 = [end[0], end[1] + Consts["WORLD_Y"]]
        end3 = [end[0] - Consts["WORLD_X"], end[1]]
        end4 = [end[0] + Consts["WORLD_X"], end[1]]
        end5 = [end[0] + Consts["WORLD_X"], end[1] - Consts["WORLD_Y"]]
        end6 = [end[0] - Consts["WORLD_X"], end[1] - Consts["WORLD_Y"]]
        end7 = [end[0] - Consts["WORLD_X"], end[1] + Consts["WORLD_Y"]]
        end8 = [end[0] + Consts["WORLD_X"], end[1] + Consts["WORLD_Y"]]
        distance = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        angle = math.atan2(end[0] - start[0], end[1] - start[1])
        for each in (end1, end2, end3, end4, end5, end6, end7, end8):
            if math.sqrt((each[0] - start[0]) ** 2 + (each[1] - start[1]) ** 2) < distance:
                distance = math.sqrt((each[0] - start[0]) ** 2 + (each[1] - start[1]) ** 2)
                angle = math.atan2(each[0] - start[0], each[1] - start[1])
        # 把angle转化到区间[0, 2pi)中
        if angle < 0:
            angle = 2 * math.pi + angle
        return angle

    def safe(self):
        thetalist = []
        weightlist = []
        for each in self.threats:
            direction = self.calc_angle(self.me.pos, each.pos)
            # if (each.radius-self.me.radius)/self.me.radius > 0.5 and self.calc_time(each) > Consts["FPS"]:
            thetalist.append(direction)
            weightlist.append((3*Consts["FPS"])**2/(self.calc_time(each))**2)
            # else:
            #     theta = direction + math.pi/2
            #     if theta > 2*math.pi:
            #         theta -= 2*math.pi
            #     thetalist.append(theta)
            #     weightlist.append(each.radius)
        average_theta = self.average(thetalist, weightlist)
        return average_theta

    def calc_time(self, cell):
        r_vx = self.me.veloc[0] - cell.veloc[0]
        r_vy = self.me.veloc[1] - cell.veloc[1]
        r_v = math.sqrt(r_vx**2 + r_vy**2)
        distance = self.me.distance_from(cell)
        alpha = abs(self.calc_angle([0, 0], [r_vx, r_vy]) - self.calc_angle(self.me.pos, cell.pos))
        if alpha >= math.pi/2:
            time = 10000000000
        else:
            md = distance * math.sin(alpha)
            if md - self.me.radius - cell.radius > 0:
                time = distance*math.cos(alpha)/r_v
            else:
                x = distance*math.cos(alpha) -\
                    math.sqrt((self.me.radius+cell.radius)**2-(distance*math.sin(alpha))**2)
                time = x/r_v
        return time

    def checkBug(self):
        for each in self.allcells:
            if each.radius > self.me.radius and self.calc_time(each) < Consts["FPS"]:
                if each not in self.threats:
                    print("BUG!")

    def average(self, thetalist, weightlist):
        X = []
        Y = []
        for i in range(len(thetalist)):
            X.append(math.sin(thetalist[i])*weightlist[i])
            Y.append(math.cos(thetalist[i])*weightlist[i])
        x = np.mean(X)
        y = np.mean(Y)
        average = self.calc_angle([0, 0], [x, y])
        return average
    def grow(self, cell):
        mes = self.distance(self.me, cell)
        # 目标的参数
        if cell != None:
            r = cell.radius
            vx = cell.veloc[0]
            vy = cell.veloc[1]
        else:
            return None
        # 自己的参数
        selfvx = self.me.veloc[0]
        selfvy = self.me.veloc[1]
        selfr = self.me.radius
        # 径矢的模长
        rlen = mes[2]
        if rlen-r-selfr<50:
        # 相对追击速度大小为abu需要自行设定
            abu = 1
            if not self.iscal:  # 如果尚未计算就计算一次，返回角度和喷射次数
                deltavx = 2 * vx + abu * mes[0] / rlen - selfvx  # 总的速度变化量
                deltavy = 2 * vy + abu * mes[1] / rlen - selfvy
                self.angle = self.xangle(-deltavx, -deltavy)
                self.iscal = True
                mid = -(1 - 1 / Consts["EJECT_MASS_RATIO"]) * \
                            math.sqrt(deltavx ** 2 + deltavy ** 2) // Consts["DELTA_VELOC"]
                self.grownum = min(mid,10)
            elif ((selfr**2)*(1-Consts["EJECT_MASS_RATIO"])**self.grownum>r**2 and self.grownum > 0) and math.sqrt(selfvx ** 2 + selfvy ** 2) < abu:  # 如果计算过，就继续喷
                self.grownum -= 1
                return self.angle
            elif self.grownum == 0 and rlen < 10 + r + selfr:  # 如果目标死亡就让下次计算继续
                self.iscal = False
                print('ate')
            elif rlen > 150:  # 如果暂时丢失目标，重新计算
                self.iscal = False
