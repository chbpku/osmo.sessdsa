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
import math
fr=0
lst_veloc=[]
js=0
lst_r=[]
lst_al=[]
lst_direc=[]
id_temp=-1
bigger_cell_lst=[]
class Player():
    def __init__(self, id, arg = None):
        self.id = id

    def canshu(self,cell,allcells):
        vx_rela = 5*(cell.veloc[0] - allcells[self.id].veloc[0])  # x方向相对速度
        vy_rela = 5*(cell.veloc[1] - allcells[self.id].veloc[1])  # y方向相对速度
        x0 = allcells[self.id].pos[0]
        y0 = allcells[self.id].pos[1]
        x1 = cell.pos[0]
        flag1 = True
        if abs(x0 - x1) > abs(x0 - x1 - 1000):
            xx1 = x1 + 1000
            flag1 = False
        elif abs(x0 - x1) > abs(x0 - x1 + 1000):
            xx1 = x1 - 1000
            flag1 = False
        if flag1 == False:
            x1 = xx1
        y1 = cell.pos[1]
        flag2 = True
        if abs(y0 - y1) > abs(y0 - y1 - 500):
            yy1 = y1 + 500
            flag2 = False
        elif abs(y0 - y1) > abs(y0 - y1 + 500):
            yy1 = y1 - 500
            flag2 = False
        if flag2 == False:
            y1 = yy1
        lst_return=[x1,y1,vx_rela,vy_rela]
        return lst_return

    def decide_danger(self,allcells):
        global bigger_cell_lst
        bigger_cell_lst=[]
        x0 = allcells[self.id].pos[0]
        y0 = allcells[self.id].pos[1]
        for i in allcells:
            x1 = self.canshu(i, allcells)[0]
            y1 = self.canshu(i, allcells)[1]
            if i.radius > allcells[self.id].radius and (x0-x1)**2+(y0-y1)**2 < 2500:
                bigger_cell_lst.append(i)
        for cell in bigger_cell_lst:
            x1 = self.canshu(cell,allcells)[0]
            y1 = self.canshu(cell,allcells)[1]
            vx_rela = self.canshu(cell,allcells)[2]
            vy_rela = self.canshu(cell,allcells)[3]
            t=(vx_rela*(x0-x1)+vy_rela*(y0-y1))**2 / ( (vx_rela**2+vy_rela**2) * ((x0-x1)**2+(y0-y1)**2) )   #t等于cos方theta
            if (1-t)*((x0-x1)**2+(y0-y1)**2) > (cell.radius + allcells[self.id].radius)**2:
                bigger_cell_lst.remove(cell)  #暂不考虑这一秒从路径上来看根本没有相撞危险的大球
            if t*((x0-x1)**2+(y0-y1)**2) > 900*(vx_rela**2+vy_rela**2) and cell in bigger_cell_lst:
                bigger_cell_lst.remove(cell)  #暂不考虑还没有紧迫的相撞危险的大球
        if len(bigger_cell_lst)!=0:
            print(len(bigger_cell_lst))
            cell_boss=bigger_cell_lst[0]
            return(cell_boss)  #需要躲避
        else:
            return False  #safe

    def escape(self,boss,allcells):
        boss=self.decide_danger(allcells)
        x0 = allcells[self.id].pos[0]
        y0 = allcells[self.id].pos[1]
        x1 = self.canshu(boss, allcells)[0]
        y1 = self.canshu(boss, allcells)[1]
        vx_rela = self.canshu(boss,allcells)[2]
        vy_rela = self.canshu(boss,allcells)[3]
        if x1-x0 >=0:
            direction= math.atan((y1-y0)/(x1-x0))
        else:
            direction = math.atan((y1-y0)/(x1-x0)) + math.pi
        return math.pi/2 - direction

    def decide_target(self,allcells):
        global lst_al
        smaller_cell_lst=[]
        for i in allcells:
            dx= i.pos[0]-allcells[self.id].pos[0]
            dy= i.pos[1]-allcells[self.id].pos[1]
            if fr>200:
                if i.radius < 0.95 * allcells[self.id].radius:    #质量不超过自己质量0.95*0.95倍的小球
                    smaller_cell_lst.append(i)
            else:
                if i.radius < 0.95 * allcells[self.id].radius and dx**2+dy**2<=40000:    #质量不超过自己质量0.9*0.9倍的小球
                    smaller_cell_lst.append(i)
        max_radi=0
        # nearest_r=3000

        for cell in smaller_cell_lst:
            cell_target=smaller_cell_lst[0]
            x0 = allcells[self.id].pos[0]
            y0 = allcells[self.id].pos[1]
            x1=self.canshu(cell,allcells)[0]
            y1 = self.canshu(cell,allcells)[1]
            vx_rela=self.canshu(cell,allcells)[2]
            vy_rela=self.canshu(cell,allcells)[3]
            v1=(vx_rela**2+vy_rela**2)**0.5
            d=((x1-x0)**2+(y1-y0)**2)**0.5
            if fr <= 200:
                if( abs((vx_rela * (x0 - x1) + vy_rela * (y0 - y1)) / ((vx_rela ** 2 + vy_rela ** 2) ** 0.5 * ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5))>1):
                    continue
                theta = math.acos((vx_rela * (x0 - x1) + vy_rela * (y0 - y1)) / ((vx_rela ** 2 + vy_rela ** 2) ** 0.5 * ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5))
                if abs(0.378 * math.sin(theta) * v1) > 1:
                    continue
                alpha = math.asin(0.378 * math.sin(theta) * v1)
                t_expectation = 0.378*d*math.sin(theta)/math.sin(alpha+theta)

            if fr>200:
                if vx_rela*(x0-x1)+vy_rela*(y0-y1) > 0.5 *   (vx_rela**2+vy_rela**2)**0.5 * ((x0-x1)**2+(y0-y1)**2)**0.5 and cell.radius>max_radi:
                    max_radi=cell.radius
                    cell_target=cell
            else:
                if vx_rela*(x0-x1)+vy_rela*(y0-y1) > 0 *   (vx_rela**2+vy_rela**2)**0.5 * ((x0-x1)**2+(y0-y1)**2)**0.5 and cell.radius>max_radi and t_expectation<=50:
                    max_radi=cell.radius
                    cell_target=cell
        return cell_target

    def fire_five(self, allcells):
        # try to eat cells that are smaller than player cell
        cell_target=self.decide_target(allcells)
        global lst_al
        global lst_direc
        global fr
        global js
        x0 = allcells[self.id].pos[0]
        y0 = allcells[self.id].pos[1]
        x1 = self.canshu(cell_target,allcells)[0]
        y1 = self.canshu(cell_target,allcells)[1]
        vx_rela = self.canshu(cell_target,allcells)[2]
        vy_rela = self.canshu(cell_target,allcells)[3]
        v1=(vx_rela**2 + vy_rela**2)**0.5
        if len(lst_direc)!=0 and lst_direc[-1]!=None:
            return lst_direc[-1]
        theta=math.acos((vx_rela*(x0-x1)+vy_rela*(y0-y1))/((vx_rela**2+vy_rela**2)**0.5 * ((x0-x1)**2+(y0-y1)**2)**0.5))
        if abs(0.776*math.sin(theta)*v1)<=1:
            alpha = math.asin(0.776*math.sin(theta)*v1)
            lst_al.append(alpha)
        else:
            if len(lst_al) != 0:
                alpha = lst_al[-1]
            else:
               alpha=0
        dir1=math.atan((y0-y1)/(x0-x1))
        if x0-x1<0:
            dir1= dir1+math.pi
        dir2=math.atan(vy_rela/vx_rela)
        if vx_rela<0:
            dir2= dir2+math.pi
        if abs(dir1-dir2)>=math.pi/2:
            if dir1>dir2:
                #while abs(dir1-dir2)>math.pi/2:
                dir1-=2*math.pi
            if dir1<dir2:
                #while abs(dir1-dir2)>math.pi/2:
                dir1+=2*math.pi

        if vx_rela<=0:
            if dir2<=dir1:
                direction=alpha+theta+math.atan(vy_rela/vx_rela)+math.pi
            else:
                direction = math.atan(vy_rela / vx_rela)-alpha-theta + math.pi
        else:
            if dir2<=dir1:
                direction = alpha + theta + math.atan(vy_rela / vx_rela)
            else:
                direction = math.atan(vy_rela / vx_rela) - alpha - theta
        lst_direc.append(direction)
        return math.pi/2 - direction

    def fire_ten(self, allcells):
        # try to eat cells that are smaller than player cell
        cell_target=self.decide_target(allcells)
        global lst_al
        global fr
        global js
        global lst_direc
        x0 = allcells[self.id].pos[0]
        y0 = allcells[self.id].pos[1]
        x1 = self.canshu(cell_target,allcells)[0]
        y1 = self.canshu(cell_target,allcells)[1]
        vx_rela = self.canshu(cell_target,allcells)[2]
        vy_rela = self.canshu(cell_target,allcells)[3]
        v1=(vx_rela**2 + vy_rela**2)**0.5
        if len(lst_direc)!=0 and lst_direc[-1]!=None:
            return lst_direc[-1]
        theta=math.acos((vx_rela*(x0-x1)+vy_rela*(y0-y1))/((vx_rela**2+vy_rela**2)**0.5 * ((x0-x1)**2+(y0-y1)**2)**0.5))
        if abs(0.378*math.sin(theta)*v1)<=1:
            alpha = math.asin(0.378*math.sin(theta)*v1)
            lst_al.append(alpha)
        else:
            if len(lst_al) != 0:
                alpha = lst_al[-1]
            else:
               alpha=0
        dir1 = math.atan((y0 - y1) / (x0 - x1))
        if x0 - x1 < 0:
            dir1 = dir1 + math.pi
        dir2 = math.atan(vy_rela / vx_rela)
        if vx_rela < 0:
            dir2 = dir2 + math.pi
        if abs(dir1 - dir2) >= math.pi / 2:
            if dir1 > dir2:
                #while abs(dir1 - dir2) >= math.pi / 2:
                dir1 -= 2 * math.pi
            if dir1 < dir2:
                #while abs(dir1 - dir2) >= math.pi / 2:
                dir1 += 2 * math.pi
        if vx_rela <= 0:
            if dir2 <= dir1:
                direction = alpha + theta + math.atan(vy_rela / vx_rela) + math.pi
            else:
                direction = math.atan(vy_rela / vx_rela) - alpha - theta + math.pi
        else:
            if dir2 <= dir1:
                direction = alpha + theta + math.atan(vy_rela / vx_rela)
            else:
                direction = math.atan(vy_rela / vx_rela) - alpha - theta
        lst_direc.append(direction)
        return math.pi/2 - direction

    def strategy(self, allcells):
        global fr
        global js
        global lst_r
        if self.decide_danger(allcells)!=False:
            fr+=1
            lst_r.append(allcells[self.id].radius)
            js=0
            boss=self.decide_danger(allcells)
            return self.escape(boss,allcells)

        if fr>200:
            fr+=1
            lst_r.append(allcells[self.id].radius)
            if js==0:
                js+=1
                return self.fire_five(allcells)
            if js%5!=0:
                js+=1
                return self.fire_five(allcells)
            if js%5==0 and lst_r[-2]*1.05 >= lst_r[-1]:
               # if   #判定是否要重新定向
                if fr% 120==0:
                    js=0
                lst_direc.append(None)
                return None
            if lst_r[-2]*1.05 < lst_r[-1]:
                js = 0
                lst_direc.append(None)
                return None
        else:
            fr += 1
            lst_r.append(allcells[self.id].radius)
            if fr < 11:
                js = 10
                return self.fire_ten(allcells)
            if js == 0:
                js += 1
                return self.fire_ten(allcells)
            if js % 10 != 0:
                js += 1
                return self.fire_ten(allcells)
            if js % 10 == 0 and lst_r[-2]*1.05 >= lst_r[-1]:
                #if fr% 101==0:
                 #   js=0
                lst_direc.append(None)
                return None
            if lst_r[-2] * 1.05 < lst_r[-1]:
                js = 0
                lst_direc.append(None)
                return None

        #考虑增加：100帧如果没有显著增加就立即“重定向”
        #考虑增加：开局抢吃战术