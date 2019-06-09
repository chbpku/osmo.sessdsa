from consts import Consts
import random
import math
import cell

class Player():
    def __init__(self, id, arg = None):

        self.id = id
    def diren(self,allcells):
        danger_xingti=[]
        #找到临近的比自己大的星体
        for x in allcells:
            if x.distance_from(allcells[self.id])<x.radius+allcells[self.id].radius+20\
                    and x.radius > allcells[self.id].radius:
                danger_xingti.append(x)
        return danger_xingti
    def weixian(self,allcells):
        danger_xingti = self.diren(allcells)
        #找到最近的一个比自己大的星体
        x = sorted(danger_xingti, key=lambda cell: cell.distance_from(allcells[self.id]) \
                                                   - cell.radius - allcells[self.id].radius)[0]
        #确定这个星体是否危险
        s1=x.distance_from(allcells[self.id])**2
        s2=(x.pos[1]+x.veloc[1]-allcells[self.id].pos[1]-allcells[self.id].veloc[1])**2\
        +(x.pos[0]+x.veloc[0]-allcells[self.id].pos[0]-allcells[self.id].veloc[0])**2
        #false表示危险，true为安全
        if s1>s2:
            return False
        else:
            return True


    def fan(self,fanhui):
        #角度转向
        if fanhui>=math.pi:
            return fanhui-math.pi
        else:
            return fanhui+math.pi
    #改写atan2函数
    def arctan(self,a,b):
        if a!=0 and b!=0:
            if b>0:
                return math.atan2(b,a)
            else:
                return math.pi*2+math.atan2(b,a)
        elif a==0 and b!=0:
            if b<0:
                return 1.5*math.pi
            else:
                return 0.5*math.pi
        elif b==0 and a!=0:
            if a<0:
                return math.pi
            else:
                return 0
        else:
                return 0
            
    def strategy(self, allcells):
        danger_xingti = self.diren(allcells)

        # 弹射后本体获得的速度值
        v1 = Consts['EJECT_MASS_RATIO'] * Consts['DELTA_VELOC'] / (1 - Consts['EJECT_MASS_RATIO'])
        # 最近的一个危险星体
        if len(danger_xingti) != 0:
            x = sorted(danger_xingti, key=lambda cell: cell.distance_from(allcells[self.id]) \
                                                       - cell.radius - allcells[self.id].radius)[0]

        # 周围没有大星体或大星体在原理自己，则不输出
        if len(danger_xingti) == 0 or self.weixian(allcells):
            return None
        #jiao1为从危险星体到自己的连线与x轴夹角
        jiao1=self.arctan(allcells[self.id].pos[1]-x.pos[1],allcells[self.id].pos[0]-x.pos[0])
        jiao3=self.arctan(allcells[self.id].veloc[1],allcells[self.id].pos[0])
        if abs(self.fan(jiao1)-jiao3)>math.pi:
            t=abs(self.fan(jiao1)-jiao3)-math.pi
        else:
            t=abs(self.fan(jiao1)-jiao3)
        if t<math.pi/12:
            return self.fan(jiao1)
        shan=100
        sha=100
        for i in range(360):
            j=i*math.pi/180
            jiao2=self.arctan(allcells[self.id].veloc[1]+v1*math.cos(j),allcells[self.id].veloc[0]+v1*math.sin(j))
            if jiao2==None:
                continue
            if abs(jiao1-jiao2)>math.pi:
                t=abs(jiao1-jiao2)-math.pi
            else:
                t=abs(jiao1-jiao2)
            if t<shan:
                shan=t
                sha=j
        # return fan.(sha) # 原始版本，无法启动比赛(SyntaxError)
        return fan(sha)


