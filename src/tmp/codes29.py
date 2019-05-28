import math
import random
from consts import Consts

class Player():

    def __init__(self, id, arg=None):
        self.id = id

    def strategy(self, allcells):
        WX = Consts["WORLD_X"]
        WY = Consts["WORLD_Y"]
        dv1 = Consts["DELTA_VELOC"]  # 喷射速度
        rat = Consts["EJECT_MASS_RATIO"]
        dv2 = dv1 * Consts["EJECT_MASS_RATIO"]  # 得到速度

        def norm(v):  # 返回v的2范数
            return math.sqrt(v[0] ** 2 + v[1] ** 2)

        def loss(sel, cel):  # 吃球损失估计，返回吃到cel需要喷球的次数，显然不能精确返回具体数值，看成是一个估计就好
            nonlocal dv2
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            dist = cross(dist)
            v = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            theta1 = (sel.radius + cel.radius) / norm(dist)
            if theta1 < 1:
                theta1 = math.asin(theta1)
            jiao = angle(v, dist)
            if jiao < theta1:
                return 0
            # 参数#速度越大loss越大
            else:
                return abs(jiao - theta1) * norm(v) / dv2 * (1 + norm(v) ** 2) + 3

        def shouyi(sel, cel):  # 吃球收益估计，返回预测吃到该球后自身质量会变成现在质量的倍数，同上，估计就好
            nonlocal rat
            los = loss(sel, cel)
            # 参数
            if (1 - rat) ** los < 1.1 * cel.radius ** 2 / sel.radius ** 2:
                return None
            else:
                return (1 - rat) ** los / 1.1 + cel.radius ** 2 / sel.radius ** 2

        def dang(r1, r2, dist, v1):  # 相撞距离,参数为两球半径，dist是相距’向量‘，v1是相对速度,dang1函数是该函数参数为sel,cel
            # 的版本
            return norm(dist) - r1 - r2

        def dang1(sel, cel):  #
            r1 = sel.radius
            r2 = cel.radius
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            return dang(r1, r2, dist, 0)

        def angle(a, b):  # 向量a到b的有向角([0,2pi))
            if math.sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2)) < 1e-6:
                return 0
            det = a[0] * b[1] - a[1] * b[0]
            jia = (a[0] * b[0] + a[1] * b[1]) / math.sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2))
            if abs(jia) > 1 - 1e-3:
                if jia < 0:
                    return math.pi
                else:
                    return 0
            jia = math.acos(jia)
            if det > 0:
                return 2 * math.pi - jia
            else:
                return jia

        def survive():
            count=0
            opid=findop()
            for i in allcells[0:100:1]:
                if i.dead == True:
                    count+=1
            return 100-count

        def cross(v):  # 穿屏最小向量(例如坐标[1,1]到坐标[999,499]之间不穿屏向量是[998,498]穿屏向量则是[-2,-2])
            # 只有坐标会用到穿屏函数，速度无论穿不穿都是一样的，不需要穿屏
            nonlocal WX, WY
            lst = [v[0] - WX, v[0], v[0] + WX]
            min1 = abs(lst[0])
            i_min = 0
            for i in range(3):
                if abs(lst[i]) < min1:
                    i_min = i
                    min1 = abs(lst[i])
            v0 = lst[i_min]

            lst = [v[1] - WY, v[1], v[1] + WY]
            min1 = abs(lst[0])
            i_min = 0
            for i in range(3):
                if abs(lst[i]) < min1:
                    i_min = i
                    min1 = abs(lst[i])
            v1 = lst[i_min]

            return [v0, v1]

        def danger_condition(sel,hunter):
            space = sel.distance_from(hunter)
            vx1 = hunter.veloc[0]
            vy1 = hunter.veloc[1]
            vx2 = sel.veloc[0]
            vy2 = sel.veloc[1]
            x1 = hunter.pos[0]
            y1 = hunter.pos[1]
            x2 = sel.pos[0]
            y2 = sel.pos[1]
            rx, ry = x2 - x1, y2 - y1
            posangle=math.atan2( ry , rx )
            #不要让速度过快
            if math.sqrt(vx2**2+vy2**2)>30 or math.sqrt(vx2**2+vy2**2)>1.6*allcells[self.id].radius**0.7:
                return None
            #尝试处理边界
            else:
                if ((abs(rx)>min(abs(rx + 1000), abs(rx - 1000)) or abs(ry)>min(abs(ry + 500), abs(ry - 500)))) and space<2.5*(hunter.radius+sel.radius):
                    if abs(rx)>min(abs(rx + 1000), abs(rx - 1000)) and not abs(ry)>min(abs(ry + 500), abs(ry - 500)):
                        if rx < 0:
                            xnewposangle = math.atan2(ry,rx + 1000)
                        else:
                            xnewposangle = math.atan2(ry,rx - 1000)
                        if vx1 * math.cos(xnewposangle) + vy1 * math.sin(xnewposangle) >= (vx2 * math.cos(xnewposangle) + vy2 * math.sin(xnewposangle)):
                            if rx < 0:
                                return math.atan2(-rx - 1000, -ry)
                            else:
                                return math.atan2(-rx + 1000, -ry)
                        else:
                            return None
                    elif abs(ry)>min(abs(ry + 500), abs(ry - 500)) and not abs(rx)>min(abs(rx + 1000), abs(rx - 1000)):
                        if  ry > 0:
                            ynewposangle = math.atan2(ry - 500,rx)
                        else:
                            ynewposangle = math.atan2(ry + 500,rx)
                        if  vx1 * math.cos(ynewposangle) + vy1 * math.sin(ynewposangle) >= (vx2 * math.cos(ynewposangle) + vy2 * math.sin(ynewposangle)):
                            if ry < 0:
                                return math.atan2(-rx, -ry - 500)
                            else:
                                return math.atan2(-rx, -ry + 500)
                    else:
                        if rx > 0 and ry > 0:
                            qnewposangle = math.atan2(ry - 500, rx - 1000)
                        elif rx > 0 and ry < 0:
                            qnewposangle = math.atan2(ry + 500, rx - 1000)
                        elif rx < 0 and ry > 0:
                            qnewposangle = math.atan2(ry - 500, rx + 1000)
                        else:
                            qnewposangle = math.atan2(ry + 500, rx + 1000)
                        if vx1 * math.cos(qnewposangle) + vy1 * math.sin(qnewposangle) >= (
                                vx2 * math.cos(qnewposangle) + vy2 * math.sin(qnewposangle)):
                            if rx < 0 and ry < 0:
                                return math.atan2(-rx - 1000, -ry - 500)
                            elif rx < 0 and ry > 0:
                                return math.atan2(-rx - 1000, -ry + 500)
                            elif rx > 0 and ry < 0:
                                return math.atan2(-rx + 1000, -ry - 500)
                            else:
                                return math.atan2(-rx + 1000, -ry + 500)
                else:
                    if vx1 * math.cos(posangle) + vy1 * math.sin(posangle) >=(vx2 * math.cos(posangle) + vy2 * math.sin(posangle)) and space<1.15**(hunter.radius+sel.radius):
                        return math.atan2(-rx, -ry)
                    else:
                        return None





        def attack(sel,cel):  # 吃球函数
            # sel不会朝着目标的方向加速，而是与该方向呈一定夹角的角度，该夹角的计算依赖于相对速度与该方向的夹角
            # 具体详见下面代码
            # p1,p2分别为自己和目标的坐标，v1位相对速度，a为自己朝向目标的向量，其他参数则不需要使用



            p1 = sel.pos
            p2 = cel.pos
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            a = [p2[0] - p1[0], p2[1] - p1[1]]
            a = cross(a)
            p2 = [p1[0] + a[0], p1[1] + a[1]]
            p3 = [p1[0] + v1[0], p1[1] + v1[1]]

            b = [p3[0] - p1[0], p3[1] - p1[1]]
            c = [p2[0] - p3[0], p2[1] - p3[1]]
            theta1 = angle([-v1[0], -v1[1]], c)
            if theta1 > math.pi:
                theta1 = theta1 - 2 * math.pi

            # r1即为所说的修正系数，下面的stra3函数修改了此处的r1
            # r1为重要参数(函数参数)*****************，不同的r1意味着不同的吃球速度和开销
            r = abs(theta1 / math.pi)
            if r > 0.9:
                r1 = 1 - 5 * (1 - r)
            else:
                r1 = r ** 3
            theta = theta1 * r1

            t=angle([0, 1], [-v1[0], -v1[1]]) + theta + math.pi
            if shouyi(sel,cel)!=None and shouyi(sel,cel) > 0.89 and survive()>70:
                return t
            elif shouyi(sel,cel)!=None and shouyi(sel,cel) > 0.91 and survive()>20:
                return t
            elif shouyi(sel,cel)!=None and shouyi(sel,cel) > 1.15 and survive()<=20:
                return t
            else:
                return None
        def findop():

            alist=[0,1]
            alist.remove(self.id)
            opid=alist[0]
            return opid

        opid = findop()
        j = 1
        if allcells[opid]==sorted(allcells, key=lambda cell: cell.radius)[0]:
            return None
        while j:
            if j >= len(allcells):
                return None
            mindistance_cell = sorted(allcells, key=lambda cell: cell.distance_from(allcells[self.id]) - cell.radius)[j]
            if (mindistance_cell.radius < 0.2 * allcells[self.id].radius)  or mindistance_cell.dead==True:
                j=j+1
                continue
            elif  mindistance_cell.radius > allcells[self.id].radius:
                return danger_condition(allcells[self.id],mindistance_cell)
            elif allcells[opid].distance_from(allcells[self.id])-allcells[opid].radius-allcells[self.id].radius<3* allcells[self.id].radius and allcells[opid].radius<(1-0.1*(allcells[opid].distance_from(allcells[self.id])-allcells[opid].radius-allcells[self.id].radius)/allcells[self.id].radius)*allcells[self.id].radius:
                return attack(allcells[self.id],allcells[opid])
            elif mindistance_cell.radius <0.9* allcells[self.id].radius and mindistance_cell.radius >0.2* allcells[self.id].radius or mindistance_cell.radius>4:
                return attack(allcells[self.id],mindistance_cell)
            j += 1

