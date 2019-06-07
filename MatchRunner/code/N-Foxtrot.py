##player4
#player3  只写进攻
from consts import Consts
import math
import numpy as np
from cell import Cell

#角转换函数
def comr(x):
    if x < 0:
        x += 2*math.pi
    elif x >= 2*math.pi:
        x -= 2*math.pi
    else:
        x = x
    return x

#给定两个cell，计算在t内能否相遇，可以跨边界
def meet(a1,a2,t=60):
        dis = 0  #表示两个星体间的距离
        time = t
        met = False  #记录指标
        while time >= 0:
            dis = a1.distance_from(a2)  #计算距离
            if dis < a1.radius + a2.radius:  #接触条件
                met = True 
                break
            else:
                time -= 1
                x = [a1.pos[0] + a1.veloc[0], a2.pos[0] + a2.veloc[0]]  #位置变化
                y = [a1.pos[1] + a1.veloc[1], a2.pos[1] + a2.veloc[1]]
                for a in x:  #对穿越边界的处理
                    if a >= 1000:
                        a -= 1000
                    if a < 0:
                        a += 1000
                for a in y:
                    if a >= 500:
                        a -= 500
                    if a < 0:
                        a += 500
                a1.pos[0], a1.pos[1] = x[0], y[0]  #位置变化
                a2.pos[0], a2.pos[1] = x[1], y[1]
        
        #位置变化的复原
        x = [a1.pos[0] + (time-t)*a1.veloc[0], a2.pos[0] + (time-t)*a2.veloc[0]]
        y = [a1.pos[1] + (time-t)*a1.veloc[1], a2.pos[1] + (time-t)*a2.veloc[1]]
        a1.pos[0], a1.pos[1] = x[0], y[0]  #位置变化
        a2.pos[0], a2.pos[1] = x[1], y[1]
        for a in x:
            if a >= 1000:
                a -= 1000
            if a < 0:
                a += 1000
        for a in y:
            if a >= 500:
                a -= 500
            if a < 0:
                a += 500                
        return met,t-time


#给定两个向量，计算第一个相对于第二个的夹角，默认v2为基准向量
def degree(vector1,vector2=(0, 1)):
    if np.linalg.norm(vector1)*np.linalg.norm(vector2) > 0:        
        cos_theta=np.dot(vector1,vector2)/(np.linalg.norm(vector1)*np.linalg.norm(vector2))
        theta=np.arccos(cos_theta) if np.cross(vector1,vector2) >= 0 else 2*math.pi-np.arccos(cos_theta)
        return theta
    else:
        return None

#给定两个向量，计算两个向量的夹角，无方向性
def degree2(vector1,vector2=(0, 1)):
    if np.linalg.norm(vector1)*np.linalg.norm(vector2) > 0:        
        cos_theta=np.dot(vector1,vector2)/(np.linalg.norm(vector1)*np.linalg.norm(vector2))
        theta=np.arccos(cos_theta)
        return theta
    else:
        return None

#评估目标的进攻价值，暂无
def value(player,target):
    pass

#计算单帧中的防御动作
def defend(player, target): 
    dx = target.pos[0] - player.pos[0]
    dy = target.pos[1] - player.pos[1]
    list_x=[abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"])]
    list_y=[abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"])]
    min_x = min(list_x)
    min_y = min(list_y)
    if min_x == list_x[0]:
        sign_x = np.sign(dx)
    elif min_x == list_x[1]:
        sign_x = np.sign(dx + Consts["WORLD_X"])
    else:
        sign_x = np.sign(dx - Consts["WORLD_X"])
    if min_y == list_y[0]:
        sign_y = np.sign(dy)
    elif min_y == list_y[1]:
        sign_y = np.sign(dy + Consts["WORLD_Y"])
    else:
        sign_y = np.sign(dy - Consts["WORLD_Y"])
    pos=np.array([sign_x*min_x, sign_y*min_y])
    return degree(pos)


#根据两个cell的状态，计算接下来第一个进攻角度,None表示无需发射，-1表示无法进攻
def attackd(player,cell): 
    degreelimit = 0.95*math.pi  #进攻限制角度
    meet_t = 60  #决定是否继续发射的meet时间参数
    ratio1, ratio2 = 0.5, 0.5  #进攻比 r1是收益决定的，r2是成本决定的
    ratio = (ratio2/(ratio1+ratio2))**0.5  #r1和r2计算方式的决定分界
    if player.radius*0.99**0.5 < cell.radius:
        return -1
    if player.radius*ratio < cell.radius:
        n0 = int(math.log(1-ratio2*(1-cell.radius**2/player.radius**2),0.99))
    else:
        n0 =  int(math.log(1-ratio1*cell.radius**2/player.radius**2,0.99))
    if meet(player,cell,meet_t)[0] == True:  #此时已经可以在meet_t内相遇,不再发射
        return None
    
    dx = cell.pos[0] - player.pos[0]
    dy = cell.pos[1] - player.pos[1]
    list_x=[abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"])]
    list_y=[abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"])]
    min_x = min(list_x)
    min_y = min(list_y)
    if min_x == list_x[0]:
        sign_x = np.sign(dx)
    elif min_x == list_x[1]:
        sign_x = np.sign(dx + Consts["WORLD_X"])
    else:
        sign_x = np.sign(dx - Consts["WORLD_X"])
    if min_y == list_y[0]:
        sign_y = np.sign(dy)
    elif min_y == list_y[1]:
        sign_y = np.sign(dy + Consts["WORLD_Y"])
    else:
        sign_y = np.sign(dy - Consts["WORLD_Y"])  #至此都是转换
    
    pos=np.array([sign_x*min_x, sign_y*min_y])  #真正的pos向量，player指向cell
    dv = np.array([player.veloc[0] - cell.veloc[0], player.veloc[1] - cell.veloc[1]]) #相对速度矢量    
    # print(n,pos,dv)
    if np.linalg.norm(dv) == 0:  #相对速度为0，直接发射向对方
        return degree(np.array([-1*sign_x*min_x, -1*sign_y*min_y]))
    else:
        #beta = math.asin(cell.radius/np.linalg.norm(pos))#不是朝向中心，而是与目标相切，beta即为宽容角度
        dvl = n0*0.05  #速度改变量长度
        ok = False #决定向量
        #下面是几何计算
        a = degree2(dv,pos)  #速度与位置矢量夹角，无方向
        if math.cos(a) <= math.cos(degreelimit):  #进攻限制角，如夹角为钝角时不进攻，默认为无限制
            return -1
        if a >= 0.5*math.pi:
            if dvl > np.linalg.norm(dv):  #可以构成钝角三角形
                ok = True
        else:
            if np.linalg.norm(dv)*math.sin(a) <= dvl: #可以构成锐角三角形
                ok = True
        # print(a,ok)
        if ok == False:
            return -1  #三角形不可计算，无法完成进攻
        else:
            b = math.asin(np.linalg.norm(dv)*math.sin(a)/dvl)
            if np.cross(dv,pos)>=0:
                return comr(degree(pos)-b+math.pi)#,n,pos,dv,dvl,a,b,comr
            else:
                return comr(degree(pos)+b+math.pi)#,n,pos,dv,dvl,a,b,comr


#主函数
class Player():
    def __init__(self, id, arg = None):
        self.id=id  #ID 调用使用self.id
        self.att=False  #进攻状态
        self.target=None  #目标指示
        self.dis = 0  #目标距离，用于受干扰下的进攻成败判断
        #self.atts = []
    
    def strategy(self, allcells):
        player=allcells[self.id]
        mass = 0  #记录总质量进行绝对优势判定
       
        #防御参数
        dcells = []
        #进攻参数
        acells = []
        tar = None
        target_find = False
        ara1, ara2 = 0.3, 1.0  #用于进攻目标的初筛，大小比较范围
        adis = 8*player.radius#*player.radius #用于进攻目标的初筛，距离

        #遍历过程
        for cell in allcells:
            mass += cell.radius**2
            if cell.id == self.target:
                target_find = True
                tar = cell  #本次的目标
            if ara1*player.radius < cell.radius < ara2*player.radius and player.distance_from(cell) < adis:
                acells.append(cell)  #进攻目标初筛列表
            if cell.radius > player.radius:
                dcells.append([cell,player.distance_from(cell) - player.radius - cell.radius])
        
        if player.radius**2 >= 0.5*mass:  #占据了全屏幕超过一半的质量，绝对优势，飞球骑脸怎么输？
            return None
        if len(acells) > 0:  #按照目标大小对目标列表排序
            acells.sort(key = lambda cell: cell.radius, reverse = True) #列表内从大到小排序  
        
        #防御逻辑部分
        if dcells:
            dtar = None
            dcells.sort(key=lambda x: x[1])
            for x in dcells:
                if meet(player,x[0])[0] == True:
                    dtar = x[0]
            if dtar == None:  #加了一个最小安全距离
                for x in dcells:
                    if x[1] <= 5:  #设定为5
                        dtar = x[0]
            if dtar:
                return defend(player,dtar)

        #进攻逻辑部分
            #进攻状态的处理
        if self.att == True and target_find == True:  #正在进攻，目标存活
            if attackd(player,tar) == -1:  #进攻已经失败
                self.target = None
                self.att = False
                return None  #取消进攻，本帧不进行动作
            elif attackd(player,tar) == None:  #认为已经可以接触
                return None
            else:  #有返回值
                return attackd(player,tar)
        if self.att == True and target_find == False:  #正在进攻，目标暴毙
            self.target = None
            self.att = False  #取消进攻，准备选取目标
        
            #非进攻状态的目标选取
        if self.att == False:  #不是进攻状态
            if acells:  #列表不空，有潜在目标
                for cell in acells:  #遍历寻找目标
                    if attackd(player,cell) != -1:
                        self.target = cell.id
                        self.att = True
                        target_find = True
                        tar = cell
                if tar:
                    return attackd(player,tar)
        
        return None
