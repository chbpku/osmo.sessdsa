from consts import Consts
import random
import math

DELTA_VELOC=Consts['DELTA_VELOC']
EJECT_MASS_RATIO=Consts['EJECT_MASS_RATIO']
WORLD_X=Consts['WORLD_X']
WORLD_Y=Consts['WORLD_Y']

class Player():
    def __init__(self, id, arg = None):
        self.id = id

    def optimize(self,allcells,planet):
        food_item={'id':-1, 'number_need':0, 'tick_need':0, 'delta_r':0,'index':0,'theta':0}
        #提取自身信息
        my_pos_x=allcells[self.id].pos[0]
        my_pos_y=allcells[self.id].pos[1]
        my_veloc_x=allcells[self.id].veloc[0]
        my_veloc_y=allcells[self.id].veloc[1]
        my_radius=allcells[self.id].radius

        #在星体参考系中计算相对速度，并将相对速度投影到二者连线上
        delta_v_x=my_veloc_x-planet.veloc[0]
        delta_v_y=my_veloc_y-planet.veloc[1]
        delta_v=math.sqrt(delta_v_x*delta_v_x+delta_v_y*delta_v_y)

        #每次喷射改变的速度的大小
        need_v0=DELTA_VELOC*EJECT_MASS_RATIO/(1-EJECT_MASS_RATIO)

        r_x=planet.pos[0]-my_pos_x
        r_y=planet.pos[1]-my_pos_y
        r=math.sqrt(r_x*r_x+r_y*r_y)
        
        theta_rr=math.atan2(r_y,r_x)

        #如果相对速度过小，认为速度方向与相对位置方向一致，不再需要改变角度
        if 2*delta_v<need_v0:
            theta_vr=theta_rr
            if delta_v==0:
                delta_v=need_v0/10
        else:
            theta_vr=math.atan2(delta_v_y,delta_v_x)
        
        theta_projection=theta_vr-theta_rr
        temp1=(my_radius+planet.radius)/r
        if temp1>=1:
            temp1=1
        if temp1<=-1:
            temp1=-1
        theta_limit=math.asin(temp1)

        vr_parallel=delta_v*math.cos(theta_projection)
        vr_vertical=delta_v*math.sin(theta_projection)

        #是否需要改变速度方向
        if_noneed_direction=0
        if theta_projection > -theta_limit and theta_projection < theta_limit:
            if_noneed_direction=1
            number_need=0
            tick_need=r/vr_parallel
            delta_r=pow((math.sqrt(my_radius)+math.sqrt(planet.radius)),2)-my_radius
            theta=None
            my_radius_t=my_radius
        else:
            #粗略计算需要的喷射次数，如果喷射后的质量小于目标星体，不计入
            if vr_parallel > 0:
                #粗略的需要改变的速度大小
                need_v=min(abs(delta_v*math.sin(theta_projection-theta_limit)),abs(delta_v*math.sin(theta_projection+theta_limit)))           
                #粗略的改变次数
                number_need=int(need_v/need_v0)+1
                #粗略的运动所需时间
                tick_need=r/vr_parallel
                #改变完速度后的半径大小
                my_radius_t=my_radius*pow(math.sqrt(1-EJECT_MASS_RATIO),number_need)
                #若改变完速度后小于目标星体，或者在速度变化完成前已经越过星体，则不计入
                if my_radius_t<planet.radius or tick_need < number_need:
                    return 0
                            
            #若初始速度为远离，先不进行计算
            else:
                return 0

        delta_r=pow((math.sqrt(my_radius_t)+math.sqrt(planet.radius)),2)-my_radius
        index_0=self.index(number_need,tick_need,delta_r)
        r_left=r-vr_parallel*number_need
        flag=1
        if if_noneed_direction==0:
            theta=math.pi+theta_vr+theta_limit-theta_projection
        #试着在速度方向调对后进行加速，看结果是否变好
        while flag==1 and r_left>0:
            food_item['number_need']=number_need
            food_item['tick_need']=tick_need
            food_item['delta_r']=delta_r
            food_item['index']=index_0
            food_item['theta']=theta

            tick_need=r_left/(vr_parallel+need_v0)+number_need
            number_need=number_need+1
            my_radius_t=my_radius*pow(math.sqrt(1-EJECT_MASS_RATIO),number_need)
            delta_r=pow((math.sqrt(my_radius_t)+math.sqrt(planet.radius)),2)-my_radius

            index_t=self.index(number_need,tick_need,delta_r)            
            if my_radius_t<planet.radius or index_t<index_0:
                flag=0
            else:
                r_left=r_left-vr_parallel-need_v0
                vr_parallel=vr_parallel+need_v0
                index_0=index_t
                        
        return food_item

    def index(self,number_need,tick_need,delta_r):
        index=delta_r/(number_need+tick_need)
        return index

    def find_all_food(self,allcells):
        #找到所有理论上可以吞噬的星体，不考虑路上的碰撞，将其存入列表food_list中
        food_list=list()

        my_pos_x=allcells[self.id].pos[0]
        my_pos_y=allcells[self.id].pos[1]
        my_veloc_x=allcells[self.id].veloc[0]
        my_veloc_y=allcells[self.id].veloc[1]
        my_radius=allcells[self.id].radius

        #遍历所有星体进行计算
        id=0;
        for planet in allcells:
            id=id+1
            #仅计算半径比自己小的星体
            if my_radius < planet.radius or (id-1)==self.id:
                continue
            else:
                food_item=self.optimize(allcells,planet)
                if food_item!=0:
                    food_item['id']=id-1
                    food_list.append(food_item)

        food_list=sorted(food_list, key = lambda food: food['index'], reverse=True)
        return food_list 

    def if_collision(self,allcells,planet,tick):
        #判断在tick内是否会相撞
        my_pos_x=allcells[self.id].pos[0]
        my_pos_y=allcells[self.id].pos[1]
        my_veloc_x=allcells[self.id].veloc[0]
        my_veloc_y=allcells[self.id].veloc[1]
        my_radius=allcells[self.id].radius

        planet_pos_x=planet.pos[0]
        planet_pos_y=planet.pos[1]
        planet_veloc_x=planet.veloc[0]
        planet_veloc_y=planet.veloc[1]
        planet_radius=planet.radius

        for t in range(tick):
            my_pos_x=my_pos_x+my_veloc_x*t
            my_pos_y=my_pos_y+my_veloc_y*t
            planet_pos_x=planet_pos_x+planet_veloc_x*t
            planet_pos_y=planet_pos_y+planet_veloc_y*t
            delta_x=planet_pos_x-my_pos_x
            delta_y=planet_pos_y-my_pos_y
            delta_r=delta_x*delta_x+delta_y*delta_y
            if(delta_r<(my_radius+planet_radius)):
                theta=2*math.pi - math.atan2(planet.pos[0]-allcells[self.id].pos[0],planet.pos[1]-allcells[self.id].pos[1])           
                return theta

        return False

    def in_danger(self,allcells):
        my_pos_x=allcells[self.id].pos[0]
        my_pos_y=allcells[self.id].pos[1]
        my_veloc_x=allcells[self.id].veloc[0]
        my_veloc_y=allcells[self.id].veloc[1]
        my_radius=allcells[self.id].radius

        for planet in allcells:
            #仅计算半径比自己大的星体
            if my_radius < planet.radius:
                #若不进行改变，在n帧内是否会相撞
                flag=self.if_collision(allcells,planet,20)
                if flag !=False:
                    return flag           
        return False

    def strategy(self, allcells):
        flag=self.in_danger(allcells)
        if flag!=False:
            return flag
        else:
            food_list=self.find_all_food(allcells)
            if food_list != None:
                for food in food_list:
                    if food['number_need']<20:
                        return food['theta']

            else:
                return None
            return None

        
