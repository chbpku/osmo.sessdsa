from consts import Consts
import math

class Player():
    def __init__(self, id, arg = None):
        self.id = id
        self.turn=0                         #统计帧数，实际应用意义不太大
        self.temp=0
    
    def deltaxy(self,allcells,herid):       #处理穿墙，获得她相对我的最近的坐标，herid=her id，她的id
        dx=allcells[herid].pos[0]-allcells[self.id].pos[0]
        dy=allcells[herid].pos[1]-allcells[self.id].pos[1]
        if abs(dx)<=500:
            deltax=dx
        elif abs(dx-1000)<=500:
            deltax=dx-1000
        else:
            deltax=dx+1000
        if abs(dy)<=250:
            deltay=dy
        elif abs(dy-500)<=250:
            deltay=dy-500
        else:
            deltay=dy+500
        return [deltax,deltay]
    
    def distance(self,allcells,herid):      #我和她的圆心距
        [dx,dy]=self.deltaxy(allcells,herid)
        return (dx**2+dy**2)**0.5
    
    def realdv(self,allcells,herid):        #相对速度在连线方向的投影，负值表示远离，正值表示靠近
        [dx,dy]=self.deltaxy(allcells,herid)
        dvx=allcells[herid].veloc[0]-allcells[self.id].veloc[0]
        dvy=allcells[herid].veloc[1]-allcells[self.id].veloc[1]
        return -(dvx*dx+dvy*dy)/self.distance(allcells,herid)
        
    def crisis(self,allcells,herid):        #根据她和自己的相对速度、位置关系、距离、半径比，估算她的重要性
        ratio=allcells[herid].radius/allcells[self.id].radius
        d=self.distance(allcells,herid)-allcells[herid].radius-allcells[self.id].radius
        realdv=self.realdv(allcells,herid)
        dv=((allcells[herid].veloc[0]-allcells[self.id].veloc[0])**2+(allcells[herid].veloc[1]-allcells[self.id].veloc[1])**2)**0.5
        if dv==0 :
            cos=1
        else:
            cos=realdv/dv                               #cos是相对速度和连线方向的夹角余弦，负值表示远离，正值表示靠近
        if ratio>=1 and realdv>0:                       #比我大，而且向我靠近，需要引起注意
            return (1.9-cos)**(-3*dv)/d                 #此处处理得不好，常常痴迷于远处的诱惑，忽略了眼前的危险，突然死亡
        elif ratio>0.3+allcells[self.id].radius*0.005:  #比我小，可以去追求，但是太小的也不值得
            prefer=1-25*(ratio-0.8)**2/16               #我觉得0.8是我心仪的尺寸
            return (2-cos)**(-3*dv)*prefer**4/d         #她的尺寸越合适，相对速度越小、越接近我的正前方（改变运行方向是比较费劲的，高速状态下尤甚），离我越近，我就越想得到她
        return 0
 
    def maxcrisis(self,allcells):           #哪个她对我最重要呢？如果都不重要，那么就做好我自己
        maxcrisis=0
        maxid=-1
        num=len(allcells)
        for i in range(0,num):
            if not i==self.id and not allcells[i].dead and self.crisis(allcells,i)>maxcrisis:
                maxcrisis=self.crisis(allcells,i)
                maxid=i
        if maxid==-1:
            maxid=self.id
        return maxid

    def mindistance(self,allcells,herid,m): #如果我们都不改变轨迹，我能否与她相遇？若否，我何时离她最近？
        [dx,dy]=self.deltaxy(allcells,herid)
        dvx=allcells[herid].veloc[0]-allcells[self.id].veloc[0]
        dvy=allcells[herid].veloc[1]-allcells[self.id].veloc[1]
        k=1
        minm=0
        mindistance=1500
        while k<=m:
            dk=((dx+k*dvx)**2+(dy+k*dvy)**2)**0.5-(allcells[herid].radius+allcells[self.id].radius)
            if dk<mindistance:
                mindistance=dk
                minm=k
            if mindistance<0:
                break
            k+=1
        return [minm,mindistance]
    
    def judge(self,allcells):               #对我最重要的那个她，究竟是威胁，还是美餐？
        herid=self.maxcrisis(allcells)
        ratio=allcells[herid].radius/allcells[self.id].radius
        [dx,dy]=self.deltaxy(allcells,herid)
        dvx=allcells[herid].veloc[0]-allcells[self.id].veloc[0]
        dvy=allcells[herid].veloc[1]-allcells[self.id].veloc[1]
        if self.turn<=100:                  #刚开始场地较为混乱，预判困难，故减少预判
            m=50+0.5*self.turn
        else:
            m=100
        [minm,mind]=self.mindistance(allcells,herid,m)
        if ratio<=1:                        
            if herid<=1 or ratio>0.95 or mind<0: #不追杀我的对手；如果她尺寸与我太接近就放弃，怕她变大；若能相遇就不去费力追求
                return None
            else:
                c=max(50,minm)                   #朝她将要经过的地方追去
                return math.atan2(-dx-c*dvx, -dy-c*dvy)
        else:
            if self.realdv(allcells,herid)<=0 or mind>0.3*allcells[herid].radius:   #她太大了，但是没有向我靠近，或者我们仍有不小的安全距离，就不理她
                return None
            else:
                c=minm                           #背离最有可能死掉时的相对位置方向逃跑
                return math.atan2(dx+c*dvx, dy+c*dvy)

    def strategy(self, allcells):
        self.turn+=1
        flag=False
        if allcells[self.id].radius>self.temp:
            flag=True
        self.temp=allcells[self.id].radius
        if flag:
            return None                          #处理吞完后乱喷的bug，吞完一个球后强制不动一帧
        return self.judge(allcells)

