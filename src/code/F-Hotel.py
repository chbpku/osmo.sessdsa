#version 1.10.0
#1.0.0  仅能运行，bug一堆
#1.0.1  采取枚举相遇刻数的类贪心算法，避免唯一选定垂线的单一决策
#1.0.2  寄存当前路径，减少决策用时
#1.0.2.1修复元组越界bug
#1.0.3  修复关键帧计算问题(内核的计算方式是关键帧计算而不是每帧计算)
#1.0.4  完全修复寻路问题
#1.0.4.1修复last_cost返回为NoneType问题
#1.0.5  终于比较全了
#1.0.5.1防御补全
#1.0.5.2防御预测加入
#1.0.5.3防御启动机制修改为以时间为准
#1.0.6  加入路径调整功能，防止被他人射出球破坏路径
#1.0.7  估值函数加入
#1.0.8  危险预测机制修正
#1.0.8.1危险预测和估值bug修复
#1.0.9  暂时移除runaway(),改用较为稳定但是低端的defend()
#1.0.9.1修复超时bug
#1.10.0 最终版

from consts import Consts
import math

class Player():
    def __init__(self, _id, arg = None):
        self.id=_id
        self.myself=None
        self.enemy=None
        self.polar_data=[]
        self.aim=None
        self.shot_dire=None
        self.shot_tick=None
        self.sleep_tick=None
        self.cxkcell=[]
        self.aimcell=None
        self.sleep=False
    
    def polar(self,allcells):
        for cell in allcells:
            if cell.id==self.id:
                self.myself=cell
                break
        for cell in allcells:
            if self.id==0:
                if cell.id==1:
                    self.enemy=cell
                    break
            else:
                if cell.id==0:
                    self.enemy=cell
                    break
        for i in range(2):
            for cell in allcells:
                if cell.id==i:
                    _myself=cell
                    break
            temp=[]
            areacount=0
            for cell in allcells:
                if cell.id==i:
                    continue
                if cell.dead:
                    continue
                #转换参考系
                relative_x=cell.pos[0]-_myself.pos[0]
                if relative_x>Consts['WORLD_X']/2:
                   relative_x=relative_x-Consts['WORLD_X']
                elif relative_x<-Consts['WORLD_X']/2:
                    relative_x=relative_x+Consts['WORLD_X']
                relative_y=cell.pos[1]-_myself.pos[1]
                if relative_y>Consts['WORLD_Y']/2:
                    relative_y=relative_y-Consts['WORLD_Y']
                elif relative_y<-Consts['WORLD_Y']/2:
                    relative_y=relative_y+Consts['WORLD_Y']
                relative_veloc_x=cell.veloc[0]-_myself.veloc[0]
                relative_veloc_y=cell.veloc[1]-_myself.veloc[1]
                #极坐标变换
                distance=_myself.distance_from(cell)
                polar_angle=math.atan2(relative_x,relative_y)
                polar_veloc=(relative_veloc_x**2+relative_veloc_y**2)**0.5
                polar_veloc_angle=math.atan2(relative_veloc_x,relative_veloc_y)
                #寄存为字典列表
                data={'id':cell.id,'distance':distance,'polar_angle':polar_angle,
                'polar_veloc':polar_veloc,'polar_veloc_angle':polar_veloc_angle,
                'radius':cell.radius,'area':cell.area(),'x':cell.pos[0],'y':cell.pos[1],'vx':relative_veloc_x,'vy':relative_veloc_y}
                temp.append(data)
                if i==self.id:
                    areacount+=data['area']
            if i==self.id and areacount<self.myself.area():
                self.sleep=True
            self.polar_data.append(temp)
        
    #粗略估计各球价值并排序
    def value_and_cost(self):
        for i in range(2):
            for cell in (self.polar_data)[i]:
                if  cell['polar_angle']<0:
                    self.de1=cell['polar_angle']+2*math.pi
                else:
                    self.de1=cell['polar_angle']
                if cell['polar_veloc_angle']<0:
                    self.de2=cell['polar_veloc_angle']+2*math.pi
                else:
                    self.de2=cell['polar_veloc_angle']
                ''' 假设速度变化一瞬间完成，估算视为匀速追击'''
                if self.de1==self.de2:
                    pushtime=int(2*cell['polar_veloc']/Consts["DELTA_VELOC"])
                    cell['value']=(cell['area']-self.myself.area()*(1-(1-Consts['EJECT_MASS_RATIO'])**pushtime))*cell['polar_veloc']/cell['distance']
                elif abs(self.de2-self.de1)==math.pi:
                    cell['value']=cell['area']*cell['polar_veloc']/cell['distance']    
                elif abs(self.de2-self.de1)<=0.5*math.pi or abs(self.de2-self.de1)>=1.5*math.pi:
                    alp=min (0.5*abs(self.de2-self.de1),2*math.pi-abs(self.de2-self.de1))
                    pushtime=int(2*cell['polar_veloc']*math.cos(alp)/Consts["DELTA_VELOC"])
                    cell['value']=(cell['area']-self.myself.area()*(1-(1-Consts['EJECT_MASS_RATIO'])**pushtime))*cell['polar_veloc']/cell['distance']
                else:
                    alp=abs(abs(self.de2-self.de1)-math.pi)
                    pushtime=int(cell['polar_veloc']/Consts["DELTA_VELOC"])
                    cell['value']=(cell['area']-self.myself.area()*(1-(1-Consts['EJECT_MASS_RATIO'])**pushtime))*cell['polar_veloc']/(math.sin(alp)*cell['distance'])
            self.polar_data[i].sort(key=lambda arg:arg['value'],reverse=True)

    #寻找最优路径
    def path(self,cell):
        acceleration=Consts['FRAME_DELTA']*Consts["DELTA_VELOC"]*(Consts["EJECT_MASS_RATIO"]/(1-Consts["EJECT_MASS_RATIO"]))
        #调整到0-pi,-pi-0
        angle_diffience=(cell['polar_veloc_angle']-cell['polar_angle'])
        while True:
            if angle_diffience<-math.pi:
                angle_diffience+=2*math.pi
            elif angle_diffience>math.pi:
                angle_diffience-=2*math.pi
            else:
                break
        time=1
        min_distance=cell['distance']*math.sin(abs(angle_diffience))
        distance=cell['distance']-self.myself.radius
        value_speed=None
        last_cost=None
        last_value_speed=None
        #枚举可能的相遇时间
        while True:
            #分6个情况计算射击角
            if angle_diffience>0:
                if abs(angle_diffience)>math.pi/2:
                    if abs(cell['distance']*math.cos(angle_diffience))>cell['polar_veloc']*time*Consts["FRAME_DELTA"]:
                        shot_dire=cell['polar_angle']+angle_diffience+math.pi/2-math.acos(min_distance/(distance+self.myself.radius))
                    else:
                        shot_dire=cell['polar_angle']+angle_diffience+math.pi/2+math.acos(min_distance/(distance+self.myself.radius))
                else:
                    shot_dire=cell['polar_angle']+angle_diffience+math.pi/2+math.acos(min_distance/(distance+self.myself.radius))
            else:
                if abs(angle_diffience)>math.pi/2:
                    if abs(cell['distance']*math.cos(angle_diffience))>cell['polar_veloc']*time*Consts["FRAME_DELTA"]:
                        shot_dire=cell['polar_angle']+angle_diffience-math.pi/2+math.acos(min_distance/(distance+self.myself.radius))
                    else:
                        shot_dire=cell['polar_angle']+angle_diffience-math.pi/2-math.acos(min_distance/(distance+self.myself.radius))
                else:
                    shot_dire=cell['polar_angle']+angle_diffience-math.pi/2-math.acos(min_distance/(distance+self.myself.radius))
            #计算此时的距离
            if abs(angle_diffience)>math.pi/2:
                distance=(min_distance**2+(cell['distance']*math.cos(math.pi-abs(angle_diffience))-Consts["FRAME_DELTA"]*time*cell['polar_veloc'])**2)**0.5-self.myself.radius
            else:
                distance=(min_distance**2+(cell['distance']*math.cos(abs(angle_diffience))+Consts["FRAME_DELTA"]*time*cell['polar_veloc'])**2)**0.5-self.myself.radius
            #解二次方程得加速次数
            #先求delta看是否有解
            delta=(acceleration/2-acceleration*time)**2-2*acceleration*distance
            if distance<0:
                return (None,0,time)
            if delta<0:
                cost=None
            else:
                cost=int((acceleration*(time-0.5)-delta**0.5)/acceleration)
            #类贪心算法，取得较优解则退出以节省时间
            if cost!=None:
                value_speed=(cell['area']-(1-(1-Consts["EJECT_MASS_RATIO"])**cost)*self.myself.area())/time*Consts["FRAME_DELTA"]
                if last_value_speed!=None and value_speed<last_value_speed:
                    break
            last_cost=cost
            last_value_speed=value_speed
            time+=1
            if time>1000:
                return (None,1000,1000)
        if last_cost!=None and last_cost>0:
            return (shot_dire,last_cost,time)
        else:
            return (None,0,time)

    def forecast(self, allcells):
        shot_tick = 0
        if self.shot_tick:
            shot_tick = self.shot_tick
        sleep_tick = 0
        if self.sleep_tick:
            sleep_tick = self.sleep_tick
        time_sum = shot_tick + sleep_tick
        square = 0
        aim_cell = None
        success = False
        for cell in allcells:
            if self.aim == cell.id:
                self.aimcell = cell
                aim_cell = cell
                square = math.pi * aim_cell.radius * aim_cell.radius
                success = True
                break
        if not success:
            return False
        for cell in (self.polar_data)[self.id]:  # 防御大球
            if self.shot_dire:
                if cell["distance"]>1.5*self.myself.distance_from(self.aimcell):
                    continue
                if cell['area'] < self.myself.area() * (1 - Consts["EJECT_MASS_RATIO"]) ** shot_tick:
                    continue
                move_angle = math.pi + self.shot_dire
                while True:
                    if move_angle < -math.pi:
                        move_angle += 2 * math.pi
                    elif move_angle > math.pi:
                        move_angle -= 2 * math.pi
                    else:
                        break
                cell_move_angle = cell['polar_veloc_angle']
                while True:
                    if cell_move_angle < -math.pi:
                        cell_move_angle += 2 * math.pi
                    elif cell_move_angle > math.pi:
                        cell_move_angle -= 2 * math.pi
                    else:
                        break
                cell_polar_angle = cell['polar_angle']
                while True:
                    if cell_polar_angle < -math.pi:
                        cell_polar_angle += 2 * math.pi
                    elif cell_polar_angle > math.pi:
                        cell_polar_angle -= 2 * math.pi
                    else:
                        break
                dis_cell = cell["distance"]
                re_move_angle = cell_move_angle - cell['polar_angle']
                re_self_move_angle = move_angle - cell['polar_angle']
                dx_self = math.cos(re_self_move_angle)
                dy_self = math.sin(re_self_move_angle)
                if dx_self:
                    k = dy_self / dx_self
                else:
                    if dy_self>0:
                        k = 100
                    else:
                        if dy_self==0:
                            k=0
                        else:
                            k=-100
                dx_big = math.cos(re_move_angle) * cell['polar_veloc']
                if dx_big == 0:
                    dx_big = 1e-5
                if dx_self == 0:
                    dx_self = 1e-5
                if dy_self == 0:
                    if dx_big * dx_self >= 0 :
                        continue
                    else:
                        dy_self = 1e-5
                dy_big = math.sin(re_move_angle) * cell['polar_veloc']
                if dx_big * dx_self < 0 or math.fabs(dy_big / dx_big) < math.fabs(dy_self / dx_self):
                    lim_dis =self.myself.radius + cell['radius']
                    xnow = dis_cell
                    ynow = 0
                    time_sumlast = time_sum
                    while time_sumlast:
                        time_sumlast -= 1
                        xnow += dx_big * Consts['FRAME_DELTA']
                        ynow += dy_big * Consts['FRAME_DELTA']
                        if math.fabs(k * xnow + ynow) / math.sqrt(k ** 2 + 1) < lim_dis:
                            if dy_self > 0:
                                if dx_self > 0:
                                    if ynow > -lim_dis or xnow > -lim_dis:
                                        return True
                                else:
                                    if ynow > -lim_dis or xnow < lim_dis:
                                        return True
                            else:
                                if dx_self > 0:
                                    if ynow < lim_dis or xnow > -lim_dis:
                                        return True
                                else:
                                    if ynow < lim_dis or xnow < lim_dis:
                                        return True
                            break
            else:
                if cell['area'] < self.myself.area() * (1 - Consts["EJECT_MASS_RATIO"]) ** shot_tick:
                    continue
                cell_move_angle = cell['polar_veloc_angle']
                while True:
                    if cell_move_angle < -math.pi:
                        cell_move_angle += 2 * math.pi
                    elif cell_move_angle > math.pi:
                        cell_move_angle -= 2 * math.pi
                    else:
                        break
                cell_polar_angle = cell['polar_angle']
                while True:
                    if cell_polar_angle < -math.pi:
                        cell_polar_angle += 2 * math.pi
                    elif cell_polar_angle > math.pi:
                        cell_polar_angle -= 2 * math.pi
                    else:
                        break
                abs_angle = math.fabs(cell_move_angle - cell_polar_angle)
                if math.pi * 3 / 2 > abs_angle > math.pi / 2:
                    if abs_angle > math.pi:
                        abs_angle = math.pi * 2 - abs_angle
                    if cell['distance'] * math.cos(math.pi - abs_angle) < time_sum * cell['polar_veloc'] * Consts[
                        "FRAME_DELTA"]:
                        if cell['distance'] * math.sin(math.pi - abs_angle) < self.myself.radius + 1.2 * cell['radius']:
                            return True
        for cell in allcells:
            if cell.id == self.myself.id or cell.id == self.aim:
                continue
            if cell.dead:
                continue
            # 转换参考系
            relative_x = cell.pos[0] - aim_cell.pos[0]
            if relative_x > Consts['WORLD_X'] / 2:
                relative_x = relative_x - Consts['WORLD_X']
            elif relative_x < -Consts['WORLD_X'] / 2:
                relative_x = relative_x + Consts['WORLD_X']
            relative_y = cell.pos[1] - aim_cell.pos[1]
            if relative_y > Consts['WORLD_Y'] / 2:
                relative_y = relative_y - Consts['WORLD_Y']
            elif relative_y < -Consts['WORLD_Y'] / 2:
                relative_y = relative_y + Consts['WORLD_Y']
            relative_veloc_x = cell.veloc[0] - aim_cell.veloc[0]
            relative_veloc_y = cell.veloc[1] - aim_cell.veloc[1]
            # 极坐标变换
            distance = aim_cell.distance_from(cell)
            polar_angle = math.atan2(relative_x, relative_y)
            polar_veloc = (relative_veloc_x ** 2 + relative_veloc_y ** 2) ** 0.5
            polar_veloc_angle = math.atan2(relative_veloc_x, relative_veloc_y)
            if distance - cell.radius - aim_cell.radius > time_sum * polar_veloc * Consts["FRAME_DELTA"]:
                continue
            abs_angle = math.fabs(polar_angle - polar_veloc_angle)
            if abs_angle <= math.pi / 2 or abs_angle >= math.pi * 3 / 2:
                continue
            if abs_angle > math.pi:
                abs_angle = math.pi * 2 - abs_angle
            if distance * math.sin(math.pi - abs_angle) > (1.2*cell.radius + aim_cell.radius):
                continue
            if distance * math.cos(math.pi - abs_angle)>time_sum * polar_veloc * Consts["FRAME_DELTA"]:
                continue
            square += cell.area()
            if square > self.myself.area() * (1 - Consts["EJECT_MASS_RATIO"]) ** shot_tick:
                return True
        return False

    def runaway(self,allcells):
        pi=math.pi
        self.polar_data.clear()
        self.polar(allcells)
        self.polar_data[self.id].sort(key=lambda arg:arg['distance'],reverse=False)
        for cell in self.polar_data[self.id]:
            if cell['radius']>self.myself.radius and self.myself.radius+cell['radius']<cell['distance']: 
                theta1=math.asin((self.myself.radius+cell['radius'])/cell['distance'])
                angle_diffience=(cell['polar_veloc_angle']-cell['polar_angle'])
                while True:
                    if angle_diffience<-math.pi:
                        angle_diffience+=2*math.pi
                    elif angle_diffience>math.pi:
                        angle_diffience-=2*math.pi
                    else:
                        break
                min_distance=cell['distance']*math.sin(abs(angle_diffience))#下面计算相接触的最短时间
                if min_distance<self.myself.radius+cell['radius'] and self.myself.radius+cell['radius']>cell['distance']-10:
                    t0=(math.sqrt(cell['distance']**2-min_distance**2)-math.sqrt((self.myself.radius+cell['radius'])**2-min_distance**2))/cell['polar_veloc']
                    delta_v1=Consts["DELTA_VELOC"]*(Consts["EJECT_MASS_RATIO"])/(1-Consts["EJECT_MASS_RATIO"])
                    delta_v2=Consts["DELTA_VELOC"]*(Consts["EJECT_MASS_RATIO"])*self.myself.area()/cell['area']
                    v4=delta_v1+delta_v2
                    theta3=cell['polar_angle']-pi/2+theta1
                    theta4=cell['polar_angle']+pi/2-theta1
                    if -pi/2<cell['polar_angle']<0:#下面分四种情况进行讨论
                        theta2=pi+cell['polar_angle']-theta1
                        t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                        if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                            theta5=theta4
                        else: theta5=theta3
                        t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                        if t2<=t1:
                            return theta5
                        else:
                            return cell['polar_angle']
                    elif cell['polar_angle']<=-pi/2:
                            theta2=pi+cell['polar_angle']-theta1
                            t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                            if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                                theta5=theta4
                            else: theta5=theta3
                            t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                            if t2<=t1:
                                return theta5
                            else:
                                return cell['polar_angle']
                    elif pi/2>cell['polar_angle']>=0:
                            theta2=-pi+cell['polar_angle']+theta1
                            t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                            if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                                theta5=theta3
                            else: theta5=theta4
                            t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                            if t2<=t1:
                                return theta5
                            else:
                                return cell['polar_angle']
                    else:
                            theta2=-pi+cell['polar_angle']+theta1
                            t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                            if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                                theta5=theta3
                            else: theta5=theta4
                            t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                            if t2<=t1:
                                return theta5
                            else:
                                return cell['polar_angle']
                elif min_distance<self.myself.radius+cell['radius'] and cell['id']+self.id!=1:
                    t0=(math.sqrt(cell['distance']**2-min_distance**2)-math.sqrt((self.myself.radius+cell['radius'])**2-min_distance**2))/cell['polar_veloc']
                    a=0.8*t0#死亡时间，在其上限
                    if cell['polar_veloc']>10:
                        a=0.85*t0
                    if t0<105 and 2*(self.myself.radius+cell['radius'])>cell['distance']:#这个地方是防御的上限，修改了半径
                        delta_v1=Consts["DELTA_VELOC"]*(Consts["EJECT_MASS_RATIO"])/(1-Consts["EJECT_MASS_RATIO"])
                        delta_v2=Consts["DELTA_VELOC"]*(Consts["EJECT_MASS_RATIO"])*self.myself.area()/cell['area']
                        v4=delta_v1+delta_v2
                        theta3=cell['polar_angle']-pi/2+theta1
                        theta4=cell['polar_angle']+pi/2-theta1
                        if -pi/2<cell['polar_angle']<0:#下面分四种情况进行讨论
                            theta2=pi+cell['polar_angle']-theta1
                            t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                            if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                                theta5=theta4
                            else: theta5=theta3
                            t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                            if t2<a:
                                return theta5
                            elif t1<a:
                                return cell['polar_angle']
                        elif cell['polar_angle']<=-pi/2:
                            theta2=pi+cell['polar_angle']-theta1
                            t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                            if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                                theta5=theta4
                            else: theta5=theta3
                            t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                            if t2<a:
                                return theta5
                            elif t1<a:
                                return cell['polar_angle']
                        elif pi/2>cell['polar_angle']>=0:
                            theta2=-pi+cell['polar_angle']+theta1
                            t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                            if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                                theta5=theta3
                            else: theta5=theta4
                            t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                            if t2<a:
                                return theta5
                            elif t1<a:
                                return cell['polar_angle']
                        else:
                            theta2=-pi+cell['polar_angle']+theta1
                            t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                            if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                                theta5=theta3
                            else: theta5=theta4
                            t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                            if t2<a:
                                return theta5
                            elif t1<a:
                                return cell['polar_angle']
                elif min_distance<self.myself.radius+cell['radius'] and cell['id']+self.id==1:
                    t0=(math.sqrt(cell['distance']**2-min_distance**2)-math.sqrt((self.myself.radius+cell['radius'])**2-min_distance**2))/cell['polar_veloc']
                    b=t0
                    if 2*(self.myself.radius+cell['radius'])>cell['distance'] or t0<105 :
                        delta_v1=Consts["DELTA_VELOC"]*(Consts["EJECT_MASS_RATIO"])/(1-Consts["EJECT_MASS_RATIO"])
                        delta_v2=Consts["DELTA_VELOC"]*(Consts["EJECT_MASS_RATIO"])*self.myself.area()/cell['area']
                        v4=delta_v1+delta_v2
                        theta3=cell['polar_angle']-pi/2+theta1
                        theta4=cell['polar_angle']+pi/2-theta1
                        if -pi/2<cell['polar_angle']<0:#下面分四种情况进行讨论
                            theta2=pi+cell['polar_angle']-theta1
                            t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                            if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                                theta5=theta4
                            else: theta5=theta3
                            t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                            if t2<b:
                                return theta5
                            elif t1<b:
                                return cell['polar_angle']
                        elif cell['polar_angle']<=-pi/2:
                            theta2=pi+cell['polar_angle']-theta1
                            t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                            if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                                theta5=theta4
                            else: theta5=theta3
                            t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                            if t2<b:
                                return theta5
                            elif t1<b:
                                return cell['polar_angle']
                        elif pi/2>cell['polar_angle']>=0:
                            theta2=-pi+cell['polar_angle']+theta1
                            t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                            if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                                theta5=theta3
                            else: theta5=theta4
                            t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                            if t2<b:
                                return theta5
                            elif t1<b:
                                return cell['polar_angle']
                        else:
                            theta2=-pi+cell['polar_angle']+theta1
                            t1=(cell['vx']-cell['vy']*math.tan(theta2))/(v4*math.cos(cell['polar_angle'])*math.tan(theta2)-v4*math.sin(cell['polar_angle']))
                            if abs(cell['polar_veloc_angle'])+abs(cell['polar_angle'])<pi:
                                theta5=theta3
                            else: theta5=theta4
                            t2=(cell['vx']-cell['vy']*math.tan(theta2))/(delta_v1*math.cos(theta5)*math.tan(theta2)-delta_v1*math.sin(theta5))
                            if t2<b:
                                return theta5
                            elif t1<b:
                                return cell['polar_angle']
        return None

    #调整当前路径
    def adjust(self):
        if self.aim==None:
            return
        success=False
        for cell in (self.polar_data)[self.id]:
            if cell['id']==self.aim:
                success=True
                break
        if success:
            acceleration=Consts['FRAME_DELTA']*Consts["DELTA_VELOC"]*(Consts["EJECT_MASS_RATIO"]/(1-Consts["EJECT_MASS_RATIO"]))
            angle_diffience=(cell['polar_veloc_angle']-cell['polar_angle'])
            while True:
                if angle_diffience<-math.pi:
                    angle_diffience+=2*math.pi
                elif angle_diffience>math.pi:
                    angle_diffience-=2*math.pi
                else:
                    break
            min_distance=cell['distance']*math.sin(abs(angle_diffience))
            #理论路径长
            if abs(angle_diffience)>math.pi/2:
                distance=(min_distance**2+(cell['distance']*math.cos(math.pi-abs(angle_diffience))-Consts["FRAME_DELTA"]*(self.shot_tick+self.sleep_tick)*cell['polar_veloc'])**2)**0.5
            else:
                distance=(min_distance**2+(cell['distance']*math.cos(abs(angle_diffience))+Consts["FRAME_DELTA"]*(self.shot_tick+self.sleep_tick)*cell['polar_veloc'])**2)**0.5
            if angle_diffience>0:
                if abs(angle_diffience)>math.pi/2:
                    if abs(cell['distance']*math.cos(angle_diffience))>cell['polar_veloc']*(self.shot_tick+self.sleep_tick)*Consts["FRAME_DELTA"]:
                        shot_dire=cell['polar_angle']+angle_diffience+math.pi/2-math.acos(min_distance/(distance))
                    else:
                        shot_dire=cell['polar_angle']+angle_diffience+math.pi/2+math.acos(min_distance/(distance))
                else:
                    shot_dire=cell['polar_angle']+angle_diffience+math.pi/2+math.acos(min_distance/(distance))
            else:
                if abs(angle_diffience)>math.pi/2:
                    if abs(cell['distance']*math.cos(angle_diffience))>cell['polar_veloc']*(self.shot_tick+self.sleep_tick)*Consts["FRAME_DELTA"]:
                        shot_dire=cell['polar_angle']+angle_diffience-math.pi/2+math.acos(min_distance/(distance))
                    else:
                        shot_dire=cell['polar_angle']+angle_diffience-math.pi/2-math.acos(min_distance/(distance))
                else:
                    shot_dire=cell['polar_angle']+angle_diffience-math.pi/2-math.acos(min_distance/(distance))
            #实际路径长
            path_distance=0.5*acceleration*(self.shot_tick-1)*self.shot_tick+acceleration*self.shot_tick*self.sleep_tick
            if self.shot_dire!=None:
                #余弦定理
                if (self.myself.radius+cell['radius'])**2<distance**2+path_distance**2-2*distance*path_distance*math.cos(shot_dire-self.shot_dire):
                    result=self.path(cell)#重新计算
                    if result[0]==None:
                        self.aim=cell['id']
                        self.shot_dire=result[0]
                        self.shot_tick=result[1]
                        self.sleep_tick=result[2]-result[1]
                    else:
                        self.aim=cell['id']
                        self.shot_dire=result[0]
                        self.shot_tick=result[1]
                        self.sleep_tick=result[2]-result[1]
            else:
                if self.myself.radius+cell['radius']<min_distance:
                    result=self.path(cell)#重新计算
                    if result[0]==None:
                        self.aim=cell['id']
                        self.shot_dire=result[0]
                        self.shot_tick=result[1]
                        self.sleep_tick=result[2]-result[1]
                    else:
                        self.aim=cell['id']
                        self.shot_dire=result[0]
                        self.shot_tick=result[1]
                        self.sleep_tick=result[2]-result[1]
        else:
            self.aim=None
            self.shot_dire=None
            self.shot_tick=None
            self.sleep_tick=None
        return

    def strategy(self, allcells):
        if self.sleep:
            return None
        self.polar_data.clear()
        self.polar(allcells)
        #首先考虑防御
        danger=self.runaway(allcells)
        if danger!=None:
            self.aim=None
            self.shot_dire=None
            self.shot_tick=None
            self.sleep_tick=None
            return danger
        #无目标时寻找目标
        if self.aim==None:
            self.value_and_cost()
            for cell in (self.polar_data)[self.id]:
                if cell['distance']>=15*self.myself.radius:
                    continue
                if cell['area']<self.myself.area()*Consts["EJECT_MASS_RATIO"]*5:
                    continue
                if cell['id']==self.enemy.id or cell['id'] in self.cxkcell:
                    continue
                result=self.path(cell)
                #有可行解则记录该目标与已计算路径
                if result[0]==None and cell['area']+self.myself.area()*0.05<self.myself.area()*(1-Consts["EJECT_MASS_RATIO"])**result[1] and cell['area']>self.myself.area()*(1-(1-Consts["EJECT_MASS_RATIO"])**result[1])+self.myself.area()*0.05:
                    self.aim=cell['id']
                    self.shot_dire=result[0]
                    self.shot_tick=result[1]
                    self.sleep_tick=result[2]-result[1]
                    if self.forecast(allcells):
                        self.cxkcell.append(self.aim)
                        self.aim=None
                        self.shot_dire=None
                        self.shot_tick=None
                        self.sleep_tick=None
                        continue
                    else:
                        self.cxkcell.clear()
                        break
                elif cell['area']+self.myself.area()*0.05<self.myself.area()*(1-Consts["EJECT_MASS_RATIO"])**result[1] and cell['area']>self.myself.area()*(1-(1-Consts["EJECT_MASS_RATIO"])**result[1])+self.myself.area()*0.05:
                    self.aim=cell['id']
                    self.shot_dire=result[0]
                    self.shot_tick=result[1]
                    self.sleep_tick=result[2]-result[1]
                    if self.forecast(allcells):
                        self.cxkcell.append(self.aim)
                        self.aim=None
                        self.shot_dire=None
                        self.shot_tick=None
                        self.sleep_tick=None
                        continue
                    else:
                        self.cxkcell.clear()
                        break
        if self.aim!=None and self.forecast(allcells):
            self.cxkcell.append(self.aim)
            self.aim=None            
            self.shot_dire=None
            self.shot_tick=None
            self.sleep_tick=None
        else:
            self.cxkcell.clear()                      
        self.adjust()
        #按已计算结果进行
        if self.shot_tick==None or self.sleep_tick==None:
            return None
        if self.shot_tick>0:
            self.shot_tick-=1
            return self.shot_dire
        elif self.sleep_tick>0:
            self.sleep_tick-=1
            return None
        else:
            self.aim=None
            self.shot_tick=None
            self.sleep_tick=None
            self.shot_dire=None
            return None
