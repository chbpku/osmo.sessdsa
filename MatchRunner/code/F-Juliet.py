from consts import Consts
import math

#28锁定+18吃球
class Player():
    
    def __init__(self, id, arg = None):
        self.id = id
        self.targetid=None
        self.count=0

    def strategy(self,allcells):
        def getdistance(self, other):  # 距离
            '''
            dx = allcells[self.id].pos[0] - other.pos[0]
            dy = allcells[self.id].pos[1] - other.pos[1]
            return (dx ** 2 + dy ** 2) ** 0.5 # 两球边缘的最近距离
            '''
            dx = allcells[self.id].pos[0] - cell.pos[0]
            dy = allcells[self.id].pos[1] - cell.pos[1]
            #x、y方向最短距离
            min_x = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
            if min_x==abs(dx):
                a=1
            elif min_x==abs(dx + Consts["WORLD_X"]) :
                a=2
            elif min_x== abs(dx - Consts["WORLD_X"]):
                a=3
            min_y = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
            if min_y==abs(dy):
                b=1
            elif min_y==abs(dy + Consts["WORLD_Y"]) :
                b=2
            elif min_y== abs(dy - Consts["WORLD_Y"]):
                b=3
            distance = (min_x ** 2 + min_y ** 2) ** 0.5  # 两个球之间距离
            return (distance,a,b)

        def getangle(self, cell,a,b):
            dx = cell.pos[0] - allcells[self.id].pos[0]
            dy = cell.pos[1] - allcells[self.id].pos[1]
            if b==2:
                dy =dy-Consts["WORLD_Y"] 
            if b==3:
                dy =dy+Consts["WORLD_Y"]
            if a==2:
                dx=dx-Consts["WORLD_X"]
            if a==3:
                dx=dx+Consts["WORLD_X"]
            angle = math.atan2(dx, dy)  # dx/dy
            angle = angle%(2*math.pi)
            return angle
  
        #angle 正对逃跑，angle+pi 吃，本函数已加pi
        def shiftangle(self, angle, vt):
            v_lim = (Consts["EJECT_MASS_RATIO"]*Consts["DELTA_VELOC"])/(1-Consts["EJECT_MASS_RATIO"])            
            if vt == 0:
                return angle
            elif abs(vt)>=v_lim:
                newangle = math.asin(vt/abs(vt))
                a = (angle + newangle)%(2*math.pi)
                return a
            else:
                newangle = math.asin(vt/v_lim)  
                a = (angle + newangle)%(2*math.pi)
                return a
            
        def cost(self,dvn,dvt):
            r=allcells[self.id].radius
            if dvn>=0:
                return (r**2)*math.exp(-dvt/Consts["DELTA_VELOC"])*math.exp(-dvn/Consts["DELTA_VELOC"])
            else:
                return (r**2)*math.exp(-dvt/Consts["DELTA_VELOC"])

        def valuecorrect(self,newarea,radius):
            myradius=allcells[self.id].radius
            cost=myradius**2-newarea
            if radius**2-cost>=0:
                return math.sqrt(radius**2-cost)
            else:
                return 0
        
        def vrelative(self, cell):  # 相对速度
            # 径向，>0远离
            vrn = (cell.veloc[0] - allcells[self.id].veloc[0]) * math.sin(angle) + \
                  (cell.veloc[1] - allcells[self.id].veloc[1]) * math.cos(angle)
            # 切向，>0逆时针
            vrt = (cell.veloc[0] - allcells[self.id].veloc[0]) * math.cos(angle) - \
                  (cell.veloc[1] - allcells[self.id].veloc[1]) * math.sin(angle)
            # 返回元组
            return (vrn,vrt)

        def gettime(self, cell):  # 判断碰撞时间
            distance = getdistance(self,cell)[0]  # 相对距离
            veln = vrelative(self, cell)[0]
            if veln!=0:
                time_collision = distance / veln
                return time_collision
            else:
                return 0
        def bong(self,cell,status):#ststus==1,逃跑，status==-1，吃球，以便增加容错,status可调
            vrn=vrelative(self, cell)[0]
            vrt=vrelative(self, cell)[1]
            distance=getdistance(self, cell)[0]
            R=(1+status*0.05)*(cell.radius+allcells[self.id].radius)
            if vrn>=0:
                return False
            elif R>=distance*abs(math.sin(math.atan2(abs(vrt),abs(vrn)))):
                return True
            else:
                return False

        insrunlist = [] #紧急逃跑列表
        mutiple_run = 3
        runlist = [] #逃跑列表
        mutiple = 0.3 #吃东西参数
        inseatlist = [] #紧急吃东西列表
        eatlist = [] #吃东西
        threatenlist=[]
        enemylist=[]
        biggerlist=[]
        eattargetangle=None
        cell0=None
        dead=0#死亡参数，已死为0，未死为1
        fo=0#佛系吃球参数，可佛为1，其他情况为0
        theta=[]
        for a in range(360):
            theta.append([0,a])
        for cell in allcells:
            if cell != allcells[self.id]:
                distance = getdistance(self, cell)[0]
                a=getdistance(self, cell)[1]
                b=getdistance(self, cell)[2]
                # 二者之间碰撞角度
                angle = getangle(self, cell,a,b) 
                vrn,vrt = vrelative(self,cell)
                #吃东西的角度
                eatangle = shiftangle(self, angle+math.pi, vrt)
                distime = gettime(self, cell)
                newarea = cost(self,vrn,vrt)
                #防作死专用
                if allcells[1-self.id].radius < 0.2*allcells[self.id].radius:
                    continue
                
                if cell.id==self.targetid :
                    eattargetangle=eatangle
                    cell0=cell
                    dead=1
                if cell.radius > allcells[self.id].radius and bong(self,cell,1)==True:
                    threatenlist.append([angle,distance])
                if  0.3*newarea < cell.radius**2 < 0.9*newarea\
                   and (bong(self,cell,40)==True or abs(vrt)<1)\
                   and distance < 6*allcells[self.id].radius\
                   and cell.id!=1-self.id:
                    eatlist.append([distime/cell.radius,cell.id,distance,angle,eatangle,valuecorrect(self,newarea,cell.radius)])

                ###########run
                if cell.radius > allcells[self.id].radius and bong(self,cell,10)==True:
                    theta1=int(math.degrees(angle))
                    theta2=int(math.degrees(math.atan(cell.radius/distance)))
                    d=cell.radius/((theta1+80+theta2)*distance)
                    value=cell.radius/distance
                    if vrt>0:
                        if theta1-theta2<0:
                            for a in range(theta1-theta2+360,360):
                                value=value+d
                                theta[a][0]=theta[a][0]+value
                            for a in range(0,theta1+60):
                                value=value+d
                                theta[a][0]=theta[a][0]+value
                        elif theta1+60>360:
                            for a in range(theta1-theta2,360):
                                value=value+d
                                theta[a][0]=theta[a][0]+value
                            for a in range(0,theta1-300):
                                value=value+d
                                theta[a][0]=theta[a][0]+value
                        else:
                            for a in range(theta1-theta2,theta1+60):
                                value=value+d
                                theta[a][0]=theta[a][0]+value
                    else:
                        if theta1-theta2>360:
                            for a in range(359,theta1-59,-1):
                                value=value+d
                                theta[a][0]=theta[a][0]+value
                            for a in range(theta1-theta2-360,-1,-1):
                                value=value+d
                                theta[a][0]=theta[a][0]+value
                        elif theta1-60<0:
                            for a in range(359,theta1+300-1,-1):
                                value=value+d
                                theta[a][0]=theta[a][0]+value
                            for a in range(theta1-theta2-1,-1,-1):
                                value=value+d
                                theta[a][0]=theta[a][0]+value
                        else:    
                            for a in range(theta1-61,theta1+theta2-1,-1):
                                value=value+d
                                theta[a][0]=theta[a][0]+value
                            
                    biggerlist.append(cell)
                    if bong(self,cell,10)==True and self.id == None\
                       and (distance < 1.5*(cell.radius+allcells[self.id].radius) or (0 < (-distime) < 200)):
                        insrunlist.append([angle, cell.radius, distance, -distime])  # 将紧急逃跑的角度,半径以及距离汇总
                    elif bong(self,cell,10)==True and self.id != None\
                       and (distance < 1.3*(cell.radius+allcells[self.id].radius) or (0 < (-distime) < 150)):
                        insrunlist.append([angle, cell.radius, distance, -distime])  # 将紧急逃跑的角度,半径以及距离汇总

                    elif  (cell.id==1-self.id and ( 0 < (-distime) < 350)):       #面对敌人，走为上计                
                        enemylist.append([angle+math.pi/2, cell.radius, distance,-distime])  # 将逃跑的角度,半径以及距离汇总
                    elif (( 0 < (-distime) < 200) and bong(self,cell,1)==True):
                        runlist.append([angle, cell.radius, distance])

                ############eat
                if cell.radius < allcells[self.id].radius :
                    theta1=int(math.degrees(angle))
                    theta2=int(math.degrees(math.atan(cell.radius/distance)))
                    d=cell.radius/((theta1+80+theta2)*distance)
                    value=5*cell.radius/distance
                    if vrt>0:
                        if theta1-theta2<0:
                            for a in range(theta1-theta2+360,360):
                                value=value+d
                                theta[a][0]=theta[a][0]-value
                            for a in range(0,theta1+60):
                                value=value+d
                                theta[a][0]=theta[a][0]-value
                        elif theta1+60>360:
                            for a in range(theta1-theta2,360):
                                value=value+d
                                theta[a][0]=theta[a][0]-value
                            for a in range(0,theta1-300):
                                value=value+d
                                theta[a][0]=theta[a][0]-value
                        else:
                            for a in range(theta1-theta2,theta1+60):
                                value=value+d
                                theta[a][0]=theta[a][0]-value
                    else:
                        if theta1-theta2>360:
                            for a in range(359,theta1-59,-1):
                                value=value+d
                                theta[a][0]=theta[a][0]-value
                            for a in range(theta1-theta2-360,-1,-1):
                                value=value+d
                                theta[a][0]=theta[a][0]-value
                        elif theta1-60<0:
                            for a in range(359,theta1+300-1,-1):
                                value=value+d
                                theta[a][0]=theta[a][0]-value
                            for a in range(theta1-theta2-1,-1,-1):
                                value=value+d
                                theta[a][0]=theta[a][0]-value
                        else:    
                            for a in range(theta1-61,theta1+theta2-1,-1):
                                value=value+d
                                theta[a][0]=theta[a][0]-value
                if 0.4*allcells[self.id].radius < cell.radius < 0.96*allcells[self.id].radius\
                     and ((cell.radius+allcells[self.id].radius) < distance < 2*allcells[self.id].radius):
                    if cell.id==1-self.id and abs(vrt)<0.1\
                       and(0.5*allcells[self.id].radius < cell.radius < 0.75*allcells[self.id].radius):#对敌人赶尽杀绝
                       inseatlist.append([eatangle, cell.radius, distance, -distime])  # 紧急吃东西的角度，半径以及距离汇总
    
                    if bong(self,cell,-2)and( 0 < (-distime) < 100*(1+cell.radius /allcells[self.id].radius)):
                        fo=1
                    elif bong(self,cell,15)==True and vrn<0.8:
                        #print("EAT1!!")
                        inseatlist.append([angle+math.pi, cell.radius, distance, -distime])  # 紧急吃东西的角度，半径以及距离汇总
        
                        
    
                if 0.25*newarea < cell.radius**2 < 0.9*newarea\
                     and ((cell.radius+allcells[self.id].radius) < distance < 10*allcells[self.id].radius)\
                     and vrn<0.7 and (bong(self,cell,40)==True or abs(vrt)<0.6)\
                     and cell.id!=1-self.id:
                    
                    if 0<(-distime)<100 and bong(self,cell,-1)==True:
                        fo=1
                    else:
                     #and abs(vrt)<0.8:
                    #print("EAT2!!")
                        inseatlist.append([eatangle, valuecorrect(self,newarea,cell.radius), distance, -distime])  # 紧急吃东西的角度，半径以及距离汇总
                ################       
        if len(insrunlist) > 0:# 紧急逃跑列表不为空
            shorttime = insrunlist[0][3]  # 挑最紧急的反方向躲（如果有更好的策略可以重写这个方法）
            count = 0
            for dis in range(len(insrunlist)):
                if insrunlist[dis][3] < shorttime:  # 找到最快的大球
                    shorttime = insrunlist[dis][3]
                    count = dis
            a = insrunlist[count][0]%(2*math.pi)
            #print(a)
            self.targetid=None
            return a
        if len(enemylist)>0:
            if (enemylist[0][2] < 1.5*(enemylist[0][1]+allcells[self.id].radius) )or (0 < enemylist[0][3] < 200):
                self.targetid=None
                return enemylist[0][0]
        theta0=sorted(theta)
        if self.count<4:
            print('here')
            self.count=self.count+1
            if theta0[0][1]>180:
                return math.radians(theta0[0][1]-180)
            else:
                return math.radians(theta0[0][1]+180)
        
        if fo==1:
            return None
        if dead==0:
            self.targetid=None
        if self.targetid==None and len(eatlist)>0:
            eatid=sorted(eatlist)[0][1]
            eatdistance=sorted(eatlist)[0][2]
            eatangle=sorted(eatlist)[0][3]
            if sorted(eatlist)[0][5]>0.7*allcells[self.id].radius:
                id=0#锁定参数，0锁定，1不锁定
                for cell in threatenlist:
                    if abs(cell[0]-eatangle)<math.pi/3:
                        if cell[1]<eatdistance:
                            id=1
                            break
                        else:
                            if cell[1]-eatdistance>5*allcells[self.id].radius:#距离差阈值设为自身5倍半径
                                pass
                            else:
                                id=1
                                break
                if id==0:
                    self.targetid=sorted(eatlist)[0][1]
                    return sorted(eatlist)[0][4]
        elif self.targetid!=None:
            if cell0.radius>allcells[self.id].radius or cell0.dead==True:
                self.targetid=None
            elif bong(self,cell0,-1)==True and 0<(-distime)<100*(1+cell0.radius/allcells[self.id].radius):
                return None
            else:
                return eattargetangle
       # else:
       #     return None
        
        
        
        

        if len(biggerlist)==0:
            return None
        

        if len(inseatlist) > 0 :  # 紧急吃东西列表不为空
            largerad = inseatlist[0][1]  # 挑最大的吃（如果有更好的策略可以重写）
            origin = 0
            count = 0
            for rad in range(len(inseatlist)):
                if (inseatlist[rad][1] > largerad)and (inseatlist[rad][-1]<inseatlist[rad][-1]):
                    largerad = inseatlist[rad][1]
                    count = rad
            a = inseatlist[count][0]%(2*math.pi)
           # print(a)
            return a
        elif len(runlist) > 0 :  # 逃跑列表不为空
            selectlist = []  # 选择最密集的反方向逃跑（如果有更好的策略可以重写）
            count = 0
            for Aangle in runlist:
                selectlist.append([Aangle[0]])
                for Bangle in runlist:
                    if Bangle[0] >= Aangle[0] - 30 or Bangle[0] <= Aangle[0] - 30:
                        selectlist[count].append(Bangle[0])
                count += 1
            index = len(selectlist[0])
            count = 0
            for sumangle in range(len(selectlist)):  # 选出最密集的区域
                if len(selectlist[sumangle]) > index:
                    index = len(selectlist[sumangle])
                    count = sumangle
            angles = 0
            for sumangle in selectlist[count]:
                angles += sumangle # 计算出密集区的平均角
            a = (angles/index)%(2*math.pi)
           # print(a)
            return a

        

        elif len(eatlist) > 0:  # 吃东西列表不为空
            selectlist = []  # 选择最密集的方向进攻（如果有更好的策略可以重写）
            count = 0
            for Aangle in eatlist:
                selectlist.append([Aangle[0]])
                for Bangle in eatlist:
                    if Bangle[0] >= Aangle[0] - 30 or Bangle[0] <= Aangle[0] - 30:
                        selectlist[count].append(Bangle[0])
                count += 1
            index = len(selectlist[0])
            count = 0
            for sumangle in range(len(selectlist)):  # 选出最密集的区域
                if len(selectlist[sumangle]) > index:
                    index = len(selectlist[sumangle])
                    count = sumangle
            angles = 0
            for sumangle in selectlist[count]:
                angles += sumangle
            return angles / index + math.pi  # 计算出密集区的平均角度
        
        theta0=sorted(theta)
        if theta0[0][0]<-2 or theta0[-1][0]>0.5:
            if theta0[0][1]>180:
                return math.radians(theta0[0][1]-180)
            else:
                return math.radians(theta0[0][1]+180)
        else:
            return None
        
 














