from consts import Consts
from math import*
import random

class Player():
    def __init__(self, id, arg = None):
        self.id = id
        self.target = None

    def strategy(self, allcells):
        #基本几何函数
        def vecn(v):#返回v的值
            return sqrt(v[0]**2+v[1]**2)

        def vecp(v1,v2):#向量和
            return [v1[0]+v2[0],v1[1]+v2[1]]

        def vecm(v1,v2):#向量差
            return [v1[0]-v2[0],v1[1]-v2[1]]

        def vecmul1(v1,v2):#向量的内积
            return v1[0]*v2[0]+v1[1]*v2[1]

        def vecmu2(v1,v2):#向量外积
            return v1[0]*v2[1]-v2[0]*v1[1]

        def vecmu3(v,n):#向量数乘
            return [v[0]*n,v[1]*n]

        def d2z(a,b,c):#3坐标a,b,c,返回a到直线bc的距离
            u1=vecm(c,b)
            u2=vecm(a,b)
            u=abs(vecmul1(u1,u2))/vecn(u1)
            a=u2[0]**2+u2[1]**2-u**2
            if a<1e-6:
                return 0
            else:
                return sqrt(a)

        def d2v(a,b,v):#坐标a,b以及过b的向量v，求a与直线的距离r
            u = chuan(vecm(a,b))
            if vecn(v)!=0:
                dis = abs(vecmul1(u,v))/vecn(v)
            else:
                return None
            r = sqrt(vecn(u)**2 - dis**2)
            if dis<1e-6:
                return [0,r]
            else:
                return [dis,r]

        def t1(a,b):#向量a到b的有向角([0,2pi))
            if sqrt((a[0]**2+a[1]**2)*(b[0]**2+b[1]**2))<1e-6:
                return 0
            det=a[0]*b[1]-a[1]*b[0]
            jia=(a[0]*b[0]+a[1]*b[1])/sqrt((a[0]**2+a[1]**2)*(b[0]**2+b[1]**2))
            if abs(jia)>1-1e-3:
                if jia<0:
                    return pi
                else:
                    return 0
            jia=acos(jia)
            if det>0:
                return 2*pi-jia
            else:
                return jia

        def t2(a,b):#向量a,b的无向角[0,pi)
            t=t1(a,b)
            return pi-abs(pi-t)

        def t3(a):
            if a<0:
                while a<0:
                    a+=2*pi
            if a>2*pi:
                while a>2*pi:
                    a-=2*pi
            return a

        def chuan(v):#穿屏最小向量
            nonlocal WX,WY
            lst=[v[0]-WX,v[0],v[0]+WX]
            min1=abs(lst[0])
            i_min=0
            for i in range(3):
                if abs(lst[i])<min1:
                    i_min=i
                    min1=abs(lst[i])
            v0=lst[i_min]

            lst=[v[1]-WY,v[1],v[1]+WY]
            min1=abs(lst[0])
            i_min=0
            for i in range(3):
                if abs(lst[i])<min1:
                    i_min=i
                    min1=abs(lst[i])
            v1=lst[i_min]
            return [v0,v1]

        #有关两个球的函数
        def distance(sel,cel):#两球sel和cel的距离
            selp=sel.pos
            celp=cel.pos
            return vecn(chuan(vecm(selp,celp)))

        def collision(cel,sel,r0 = 1):
            selp = sel.pos
            celp = cel.pos
            selv = sel.veloc
            celv = cel.veloc
            r1=sel.radius
            r2=cel.radius
            dis = chuan(vecm(celp,selp))
            v = vecm(celv,selv)
            if vecn(v) == 0:
                return [7777777,"E1"]
            d = -vecmul1(dis,v)/vecn(v)
            if d<0:
                return [7777777,"E2"]
            r = sqrt(abs(vecn(dis)**2 - d**2))
            if r <1e-3:
                r = 0
            if r>r1+r2+r0:
                return [7777777,"E3"]
            else:
                celp_post = vecp(dis, vecmu3(v, d / vecn(v)))
                time = (d - sqrt((r1+r2+r0)**2 - r**2))/vecn(v)
                if cel.id == 1-self.id and time<25:
                    return [time,t1([0,1],dis)]
                return [time, t1([0, 1], celp_post)]

        def chase(cel,sel,time0 = 200):
            selp = sel.pos
            celp = cel.pos
            selv = sel.veloc
            celv = cel.veloc
            r1=sel.radius
            r2=cel.radius
            dis = chuan(vecm(celp,selp))
            v = vecm(celv,selv)
            if vecn(v) == 0:

                return t3(t1([0,1],dis)+pi)
            d = -(vecmul1(dis,v))/vecn(v)
            r = sqrt(abs(vecn(dis)**2 - d**2))
            if r <1e-3:
                r = 0
            if r < r1+r2-0.01:
                if d>1e-3:
                    time = (abs(d) - sqrt((r1 + r2) ** 2 - r ** 2)) / vecn(v)
                    if time <=time0:
                        return None
                    else:
                        return t1([0,1],v)
                elif d<-1e-3:
                    return t1([0,1],v)
                else:
                    return t3(t1([0,1],dis)+pi)
            else:
                cel_post = vecp(dis,vecmu3(v,25))
                return t3(t1([0,1],cel_post)+pi)


        def goal(cel,sel,rat,dv2,time0 = 200):
            selp = sel.pos
            celp = cel.pos
            selv = sel.veloc
            celv = cel.veloc
            r1=sel.radius
            r2=cel.radius
            dis = chuan(vecm(celp,selp))
            v = vecm(celv,selv)
            if vecn(v) == 0:
                print(1)
                return t3(t1([0,1],dis)+pi)
            d = -(vecmul1(dis,v))/vecn(v)
            r = sqrt(abs(vecn(dis)**2 - d**2))
            if r <1e-3:
                r = 0
            if r < r1+r2:
                l = abs(d) - sqrt((r1 + r2) ** 2 - r ** 2)
                if d>0:
                    v1 = max(l/time0-vecn(v),0)
                else :
                    v1 = abs(l)/time0+vecn(v)
                v2 = 0
            else:
                theta1 = acos((r1+r2)/vecn(dis))
                decision = t1(dis,v)
                l = abs(vecn(dis)*sin(theta1))
                vnorm = vecn(v)
                if decision<theta1:
                    vt = abs(vnorm*cos(decision-pi/2+theta1))
                    vn = abs(vnorm*sin(decision-pi/2+theta1))
                elif decision<pi:
                    vt = -abs(vnorm*cos(-decision+pi/2+theta1))
                    vn = abs(vnorm*sin(-decision+pi/2+theta1))
                elif decision<2*pi-theta1:
                    vt = -abs(vnorm*cos(decision-1.5*pi+theta1))
                    vn = abs(vnorm*sin(decision-1.5*pi+theta1))
                else:
                    vt = abs(vnorm * cos(-decision + 1.5*pi + theta1))
                    vn = abs(vnorm * sin(-decision + 1.5*pi + theta1))
                v1 = max(l / time0 + vt, 0)
                v2 = vn

            loss = ((1-rat)**((v1+v2)/dv2))
            if loss*r1<=r2:
                return 0
            else:
                loss = (loss**2)*r1
                gain = sqrt(loss**(2)+(r2**2))/r1
                return gain

        # 常数导入
        WX = Consts["WORLD_X"]
        WY = Consts["WORLD_Y"]
        dv1 = Consts["DELTA_VELOC"]  # 喷射速度
        rat = Consts["EJECT_MASS_RATIO"]
        dv2 = dv1 * Consts["EJECT_MASS_RATIO"]  # 得到速度
        if len(allcells) < 2:
            return None
        sel = allcells[self.id]
        selp = sel.pos
        selv = sel.veloc
        selr = sel.radius

        bigs = []
        smalls = []
        Found = False
        for cel in allcells:
            if self.target:
                if abs(self.target.radius-cel.radius)<0.01 and vecn(vecm(self.target.veloc,cel.veloc))<0.01:
                    self.target = self.target
                    Found = True

            if cel.radius>selr and cel.dead == False:
                bigs.append(cel)
            elif cel.radius<selr and cel.dead == False:
                smalls.append(cel)

        if Found and self.target.dead == False:
            if self.target.radius>selr:
                self.target = None

        else:
            self.target = None


        # 如果没有目标，就从小球里选择一个球做目标
        if smalls and (not self.target):
            smalls2 = []
            for small in smalls:
                if collision(small,cel)[0]!=777777 or vecn(vecm(small.pos,sel.pos))<300:
                    smalls2.append(small)
            smalls =smalls2
            absorblist = []
            for small in smalls:
                absorblist.append([small,goal(small, sel, rat, dv2)])
            absorblist = sorted(absorblist,key= lambda small:small[1])
            target = absorblist[-1][0]
            g = absorblist[-1][1]

            if g>1:
                self.target = target



        #这是躲避大球的部分，检测在场大球的数量以及可能的威胁来选择躲避角度
        #考虑到计算时间限制，因此并没有引入rumia中的进化算法，因为那种情况出现较少，但是相对来说计算量较大，非常不划算
        if bigs:
            collisionlist = []
            for big in bigs:
                collisionlist.append([big,collision(big,sel)])
            collisionlist = sorted(collisionlist,key= lambda x :x[1][0])
            cel = collisionlist[0][0]
            time = collisionlist[0][1]

            # ***mintime为重要参数，根据场上大球数目控制苟的程度
            mintime = 50 + sqrt(25 * len(bigs))

            if time[0]!=7777777:
                if len(bigs)>=2:    #防止被两个球夹击骑脸
                    cel2 = collisionlist[1][0]
                    time2 = collisionlist[1][1]
                    if time[0]<mintime/2 and time2[0] < mintime/2:
                        return t1([0,1],vecmu3(vecp(cel.pos,cel2.pos),2))

                r0 = 1
                for cell in allcells:#检测大球突然吃球变大的情况
                    if cell.id!=self.id:
                        if collision(cell,cel)[0]<mintime:
                            r10 = sqrt(cell.radius**2+cel.radius**2)-cel.radius
                            if r10>r0:
                                r0 = r10
                for cell in smalls:#检测自己突然吃球变大的情况
                    if collision(cell, sel)[0] < mintime:
                        r10 = sqrt(cell.radius ** 2 + sel.radius ** 2) - sel.radius
                        if r10 > r0:
                            r0 = r10
                time = collision(cel, sel, r0)
                if time[0]<=mintime:
                    return time[1]


        if self.target:
            if len(allcells)>2:
                return chase(self.target,sel)




