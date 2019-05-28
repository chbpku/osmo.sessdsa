from consts import Consts
from math import *


class Player():
    def __init__(self, id, arg = None):
        self.id = id
        self.target=None

    def strategy(self, allcells):
        # 基本几何函数---------------------------------

        def norm(v):
            return sqrt(v[0]**2+v[1]**2)
        
        def dianz(a, b, c):  # 坐标a,b,c,返回a到直线bc的距离
            u1 = [c[0]-b[0], c[1]-b[1]]
            u2 = [a[0]-b[0], a[1]-b[1]]
            u = abs(u1[0]*u2[0]+u1[1]*u2[1])/norm(u1)
            a = u2[0]**2+u2[1]**2-u**2
            if a < 1e-6:
                return 0
            else:
                return sqrt(a)

        def thet(a, b):  # 向量a到b的有向角([0,2pi))
            if sqrt((a[0]**2+a[1]**2)*(b[0]**2+b[1]**2)) < 1e-6:
                return 0
            det = a[0]*b[1]-a[1]*b[0]
            jia = (a[0]*b[0]+a[1]*b[1])/sqrt((a[0]**2+a[1]**2)*(b[0]**2+b[1]**2))
            if abs(jia) > 1-1e-3:
                if jia < 0:
                    return pi
                else:
                    return 0
            jia = acos(jia)
            if det > 0:
                return 2*pi-jia
            else:
                return jia

        def chuan(v):
            nonlocal WX,WY
            lst = [v[0]-WX,v[0],v[0]+WX]
            min1 = abs(lst[0])
            i_min=0
            for i in range(3):
                if abs(lst[i]) < min1:
                    i_min = i
                    min1 = abs(lst[i])
            v0 = lst[i_min]

            lst = [v[1]-WY, v[1], v[1]+WY]
            min1 = abs(lst[0])
            i_min=0
            for i in range(3):
                if abs(lst[i])<min1:
                    i_min=i
                    min1=abs(lst[i])
            v1=lst[i_min]

            return [v0, v1]

        def jia(a,b):#向量a,b的无向角[0,pi)
            theta=thet(a,b)
            return pi-abs(pi-theta)

        def distance(sel,cel):#两球sel和cel的距离
            selp=sel.pos
            celp=cel.pos
            return norm(chuan([selp[0]-celp[0],selp[1]-celp[1]]))

        def dang(r1,r2,dist,v1):  # 相撞距离,参数为两球半径，dist是相距’向量‘，v1是相对速度,dang1函数是该函数参数为sel,cel
            # 的版本
            return norm(dist)-r1-r2

        def time(r1,r2,dist,v1):  # 预测两球的相撞时间，同样time1函数是该函数参数为sel,cel的版本
            dist=chuan(dist)
            if norm(v1)<(norm(dist)-r1-r2)*0.01:  # 最大速度是100，这是撞不上的情况
                return None
            
            if v1[0]*dist[0]+v1[1]*dist[1]<0:  # 方向相反
                return None
            h=dianz(dist,[0,0],v1)
            if r1+r2<h+1e-3:
                return None
            else:
                l1=sqrt((r1+r2)**2-h**2)
                l2=norm(dist)**2-h**2
                if l2<1e-4:
                    return None
                l2=sqrt(l2)
                return (l2-l1)/norm(v1)

        def qie(sel,cel):  # 该函数考虑相对于目标cel相撞还需行进的距离(time1(sel,cel)*norm(v))
            r1=sel.radius
            r2=cel.radius
            dist=[cel.pos[0]-sel.pos[0],cel.pos[1]-sel.pos[1]]
            dist=chuan(dist)
            v1=[sel.veloc[0]-cel.veloc[0],sel.veloc[1]-cel.veloc[1]]

            #参数
            dist=chuan(dist)
            if norm(v1)<(norm(dist)-r1-r2)*0.01:
                return None
                    
            if v1[0]*dist[0]+v1[1]*dist[1]<0:
                return None
            h=dianz(dist,[0,0],v1)
            if r1+r2<h+1e-3:
                return None
            else:
                l1=sqrt((r1+r2)**2-h**2)
                l2=norm(dist)**2-h**2
                if l2<1e-4:
                    return None
                l2=sqrt(l2)
                return (l2-l1)
        # 策略函数-----------------------------------
        def stra3(sel, cel):
            def duan(t):
                if t < 0.1:
                    return t**3
                elif t < 0.7:
                    return t ** 2
                else:
                    return t

            nonlocal dv2
            p1 = sel.pos
            p2 = cel.pos
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            a = [p2[0] - p1[0], p2[1] - p1[1]]
            a = chuan(a)
            p2 = [p1[0] + a[0], p1[1] + a[1]]
            p3 = [p1[0] + v1[0], p1[1] + v1[1]]
            c = [p2[0] - p3[0], p2[1] - p3[1]]
            theta1 = thet([-v1[0], -v1[1]], c)
            if norm(v1) < 0.3:
                return thet([0, 1], a) + pi

            if theta1 > pi:
                theta1 = theta1 - 2 * pi
            r = abs(theta1 / pi)
            theta = theta1 * duan(r)
            return thet([0, 1], [-v1[0], -v1[1]]) + theta + pi

        def stra2(sel,cel):#躲球函数，直接对着目标喷球
            p1 = sel.pos
            p2 = cel.pos
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            v=[p2[0]-p1[0],p2[1]-p1[1]]
            v=chuan(v)
            v3=[v[0]-v1[0],v[1]-v1[1]]
            return thet([0,1],v3)

        #预测函数-----------------------------------------
        def chi_time(cel):
            nonlocal allcells
            lst1=[]
            lst2=[]
            lst3=[]
            r1=cel.radius
            for i in range(2,len(allcells)):
                cel1=allcells[i]
                if cel1.dead==True or cel1==cel:
                    lst1.append(None)
                    lst2.append(None)
                    lst3.append(None)
                    continue
                r2=cel1.radius
                dist=[cel1.pos[0]-cel.pos[0],cel1.pos[1]-cel.pos[1]]
                v1=[cel.veloc[0]-cel1.veloc[0],cel.veloc[1]-cel1.veloc[1]]
                t=time(r1,r2,dist,v1)
                lst1.append(t)
                if t!=None:
                    lst2.append(sqrt(r1**2+r2**2))
                    lst3.append(jiehe_yu(cel,cel1))
                else:  
                    lst2.append(None)
                    lst3.append(None)

            return [lst1,lst2,lst3]  # 时间、半径和位置

        def time1(sel,cel):
            r1=sel.radius
            r2=cel.radius
            dist=[cel.pos[0]-sel.pos[0],cel.pos[1]-sel.pos[1]]
            dist=chuan(dist)
            v1=[sel.veloc[0]-cel.veloc[0],sel.veloc[1]-cel.veloc[1]]

            return time(r1,r2,dist,v1)
        
        def jiehe(cel1,cel2):#返回两球结合后的半径和速度
            r1=cel1.radius
            r2=cel2.radius
            v1=cel1.veloc
            v2=cel1.veloc
            r=sqrt(r1**2+r2**2)
            v=[(r1**2*v1[0]+r2**2*v2[0])/(r1**2+r2**2),(r1**2*v1[1]+r2**2*v2[1])/(r1**2+r2**2)]
            return r,v

        def jiehe_yu(cel1,cel2):#返回两球结合后的位置，半径，速度
            t=time1(cel1,cel2)
            if t!=None:
                if cel1.radius>cel2.radius:
                    p1=cel1.pos
                    v1=cel1.veloc
                    p=[p1[0]+v1[0]*t,p1[1]+v1[1]*t]
                    r,v=jiehe(cel1,cel2)

                else:
                    p2=cel2.pos
                    v2=cel2.veloc
                    p=[p2[0]+v2[0]*t,p2[1]+v2[1]*t]
                    r,v=jiehe(cel1,cel2)
                return p,r,v

        def dang1(sel,cel):
            r1=sel.radius
            r2=cel.radius
            dist=[cel.pos[0]-sel.pos[0],cel.pos[1]-sel.pos[1]]
            return dang(r1,r2,dist,0)

        def loss(sel,cel):  # 吃球损失估计，返回吃到cel需要喷球的次数，显然不能精确返回具体数值，看成是一个估计就好
            nonlocal dv2
            dist=[cel.pos[0]-sel.pos[0],cel.pos[1]-sel.pos[1]]
            dist=chuan(dist)
            v=[sel.veloc[0]-cel.veloc[0],sel.veloc[1]-cel.veloc[1]]
            theta1=(sel.radius+cel.radius)/norm(dist)
            jiao=jia(v,dist)
            if jiao<theta1:
                return 0
            #参数 #速度越大loss越大
            else:
                return abs(jiao-theta1)*norm(v)/dv2*(1+norm(v)**2)+3

        def shouyi(sel,cel):  # 吃球收益估计，返回预测吃到该球后自身质量会变成现在质量的倍数
            nonlocal rat
            los=loss(sel,cel)
            #参数
            if (1-rat)**los<1.1*cel.radius**2/sel.radius**2:
                return None
            else:
                return (1-rat)**los/1.1+cel.radius**2/sel.radius**2

        def howl(sel,cel):#预测吃到球cel所需花费时间，估计就好
            t1=dang1(sel,cel)/max(norm(
                [sel.veloc[0]-cel.veloc[0],sel.veloc[1]-cel.veloc[1]]),0.2)
            t2=loss(sel,cel)
            return t1+t2

        def jiao(l1,l2):#判断两球是否已经相交
            p1=l1[0]
            p2=l2[0]
            dist=[p2[0]-p1[0],p2[1]-p1[1]]
            dist=chuan(dist)
            r1=l1[1]
            r2=l2[1]
            return norm(dist)<r1+r2

        def chuan1(cel):
            nonlocal sel
            dist=[cel.pos[0]-sel.pos[0],cel.pos[1]-sel.pos[1]]
            dist=chuan(dist)
            p=[sel.pos[0]+dist[0],sel.pos[1]+dist[1]]
            return p

        #常数导入
        WX=Consts["WORLD_X"]
        WY=Consts["WORLD_Y"]
        dv1=Consts["DELTA_VELOC"]#喷射速度
        rat=Consts["EJECT_MASS_RATIO"]
        dv2=dv1*Consts["EJECT_MASS_RATIO"]#得到速度
        if len(allcells)<2:
            return None
        sel=allcells[self.id]
        selp=sel.pos
        selv=sel.veloc
        selr=sel.radius

        # 躲球部分
        # 躲避对手
        cel = allcells[1-self.id]
        dist = [cel.pos[0]-selp[0],cel.pos[1]-selp[1]]
        dist=chuan(dist)
        if norm(dist)<100 and selr<cel.radius:
            return stra2(sel,cel)

        da_li = []
        for x in allcells:
            if x.radius > selr and x.dead == False:
                da_li.append(x)
        i2_min = None
        min2 = None
        i1_min = None
        min1 = None
        for i in range(len(da_li)):
            celp = da_li[i].pos
            celv = da_li[i].veloc
            t1 = time1(sel, da_li[i])
            t2 = qie(sel, da_li[i])

            if t2 != None:
                if i2_min == None:
                    i2_min = i
                    min2 = t2
                else:
                    if t2 < min2:
                        i2_min = i
                        min2 = t2

            if t1 != None:
                if i1_min == None:
                    i1_min = i
                    min1 = t2
                else:
                    if t1 < min2:
                        i1_min = i
                        min1 = t2
        # 在场上存在较多大球时采用更为保守的多球方法
        if len(da_li) > 5:
            if min2 != None and min2 / sqrt(selr) < 5:
                self.target = None
                cell = da_li[i2_min]
                return stra2(sel,cel)
        if min1 != None and min1 < 60:
            self.target = None
            cell = da_li[i1_min]
            return stra2(sel,cel)

        # 进化算法
        d_lst = []

        for i in range(len(da_li)):
            if allcells[i] != sel:
                celp = da_li[i].pos
                celv = da_li[i].veloc
                t1 = dang(selr, da_li[i].radius, chuan([celp[0] - selp[0], celp[1] - selp[1]]),
                          [selv[0] - celv[0], selv[1] - celv[1]])
                if t1 < 160:
                    d_lst.append([da_li[i], t1])

        # 进化1
        for x in d_lst:
            t_l, r_l, c_l = chi_time(x[0])
            for i in range(len(t_l)):
                # 参数
                if t_l[i] != None and c_l[i][1] > selr:
                    p_ = [selp[0] + t_l[i] * selv[0], selp[1] + t_l[i] * selv[1]]
                    if jiao([p_, selr, selv], c_l[i]) == True:
                        return stra2(sel, x[0])
                    else:
                        t = dang(selr, c_l[i][1], chuan([c_l[i][0][0] - p_[0], c_l[i][0][1] - p_[1]]),
                                 [selv[0] - c_l[i][2][0], selv[1] - c_l[i][2][1]])
                        if t != None and t < 50:
                            return stra2(sel, x[0])

        # 吃球部分
        target = None
        def chiqiu(sel,cel):
            dist = [cel.pos[0]-selp[0],cel.pos[1]-selp[1]]
            dist = chuan(dist)
            v = [sel.veloc[0], sel.veloc[1]]
            if pi/4 <= thet(dist,v) < 3*pi/4 or 5*pi/4<thet(dist,v)<=7*pi/4:
                return 200
            elif 3*pi/4 <= thet(dist,v) <= 5*pi/4:
                return 150
            else:
                return 270

        chi_li = []
        for cel in allcells[2:]:
            if cel.radius<selr and dang1(sel,cel)<chiqiu(sel,cel):
                chi_li.append(cel)
        # 此时chi_li中包含所有在sel一定范围内的球
        # 下面剔除chi_li中不合适的球
        # 首先记录chi_li中每个球在dt的状态
        kechi = []
        for x in chi_li:
            dt = howl(sel,x)
            cel_chi = chi_time(x)  # cel_chi时间、半径和位置
            # 如果在dt时间内吃球后半径大于selr
            cel_chi_time = cel_chi[0]
            r_list = []
            for t in range(len(cel_chi_time)):
                if cel_chi_time[t] is None:
                    pass
                elif cel_chi_time[t] < dt:
                    r_list.append(cel_chi[1][t])
            R = 0
            for r in r_list:
                R += r**2
            if sqrt(R) < selr*0.8:  # 能吃，参数考虑到体积减小
                kechi.append(x)
        # 检查完cel在dt的情况，kechi中剩下的都是在dt时刻半径小于sel球
        # 然后继续检查吃球的路上有没有大球
        kechi2 = []
        da = []
        for cel in allcells[2:]:
            if cel.radius>selr:
                da.append(cel)
        for x in kechi:
            dis = [x.pos[0]-selp[0], x.pos[1]-selp[1]]
            dis = chuan(dis)
            flag = True
            for cel in da:
                dis_da = [cel.pos[0]-selp[0], cel.pos[1]-selp[1]]
                dis_da = chuan(dis_da)
                # 大球在60度范围内
                if -pi/6<thet(dis_da, dis)<pi/6:
                    flag = False
            if flag:
                kechi2.append(x)
        # 这样kechi2就是最终的吃球列表
        # 然后评估吃球的收益
        # 收益的评估主要是体积变化
        # 选出最大收益球
        maxpayoff = 0
        for cel in kechi2:
            if shouyi(sel,cel) is None:
                continue
            else:
                if shouyi(sel,cel)> maxpayoff:
                    maxpayoff = shouyi(sel,cel)
                    if maxpayoff-distance(sel,cel)*0.005 > 0.65:
                        target = cel
        if target is not None:
            v = [sel.veloc[0] - target.veloc[0], sel.veloc[1] - target.veloc[1]]
            if norm(v) < 0.3 or loss(sel, target) > 0:
                return stra3(sel, target)

        if target == None:
            # riv用来记录对手的球,dist位置向量，v相对速度
            riv = allcells[1 - self.id]
            dist = [riv.pos[0] - selp[0], riv.pos[1] - selp[1]]
            dist = chuan(dist)
            v = [selv[0] - riv.veloc[0], selv[1] - riv.veloc[1]]
            if riv.radius > 5:  # 在对手的半径已经毫无希望的时候不再追击，因为对手半径越小，狙击越难
                # 下面的一对条件判别采用了分段判别，因为连续的判别并不好做，故分段调参
                # 条件中所有参数均为重要参数*********************过大会导致胜率降低
                if (riv.radius < selr * 0.8 and
                        distance(sel, riv) < 200 and jia(dist, v) < pi / 6 or
                        riv.radius < selr * 0.65 and
                        distance(sel, riv) < 300 and jia(dist, v) < pi / 3 or
                        riv.radius < selr * 0.75 and norm(v) < 0.3 and distance(sel, riv) < 200 or
                        riv.radius < selr * 0.55 and norm(v) < 0.6 and distance(sel, riv) < 300):

                    # 同样在狙击的路上不存在大球的时候才选择狙击
                    for y in da_li:
                        # 参数
                        a = chuan([y.pos[0] - selp[0], y.pos[1] - selp[1]])
                        b = chuan([riv.pos[0] - selp[0], riv.pos[1] - selp[1]])
                        if (dianz(chuan1(y), selp, chuan1(riv)) < selr + y.radius + 80 and
                                a[0] * b[0] + a[1] * b[1] > 0 and a[0] * b[0] + a[1] * b[1] < norm(b) ** 2):
                            break
                    else:  # 在场上大球数量不同时采用不同的狙击方案，大球数量<=1时追击更为狂野
                        # 在己方速度不大(避免追球使自己进入高速状态，速度越大意味着危险越大)时，相对riv速度不大
                        # 或者角度不对就进行追击
                        # 此处选择stra1为追击函数，实际上选哪个意义不大，因为追击一般都发生在一条直线上
                        # norm(selv)后的参数为重要参数****************过大会导致胜率降低
                        if len(da_li) > 1:
                            if norm(selv) < 0.5 and (qie(sel, riv) == None or norm(v) < 0.7):
                                return stra3(sel, riv)
                        elif len(da_li) == 1:
                            if norm(selv) < 1 and (qie(sel, riv) == None or norm(v) < 1):
                                return stra3(sel, riv)

                        else:
                            if qie(sel, riv) == None or norm(v) < 1.8:
                                return stra3(sel, riv)



















        

        

                        























