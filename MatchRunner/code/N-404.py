#  GNU General Public License for more details.
#No_chi
#dv2=5edition
from consts import Consts
from math import*
from random import randrange

class Player():
    def __init__(self, id, arg = None):
    	self.id = id
    	self.target=None
    	self.pretarget=None
    	
    

    def strategy(self, allcells):
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
        riv=allcells[1-self.id]

        da_li=[]
        for x in allcells:
            if x.radius>selr and x.dead==False:
                da_li.append(x)

        cxl=[]
        for x in allcells[2:]:
            if x.radius>selr*0.7 and x.radius<selr:
                cxl.append(x)
                
        searchran=max(400-240/4*len(da_li),160)
        maxv=max(0.55-0.3/10*len(cxl),0.25)
        
        
        def norm(v):#return v的2范数
            return sqrt(v[0]**2+v[1]**2)
        
        def dianz(a,b,c):#3列表a,b,c;返回a到直线bc的距离
            u1=[c[0]-b[0],c[1]-b[1]]
            u2=[a[0]-b[0],a[1]-b[1]]
            u=abs(u1[0]*u2[0]+u1[1]*u2[1])/norm(u1)
            a=u2[0]**2+u2[1]**2-u**2
            if a<1e-6:
                return 0
            else:
                return sqrt(a)

        def thet(a,b):#向量a到b的有向角([0,2pi))
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

        def jia(a,b):
            theta=thet(a,b)
            return pi-abs(pi-theta)

        def distance(sel,cel):#穿
            selp=sel.pos
            celp=cel.pos
            return norm(chuan([selp[0]-celp[0],selp[1]-celp[1]]))
            
                    
                    

        def dang(r1,r2,dist,v1):#相撞距离
            dist=chuan(dist)
            return norm(dist)-r1-r2

        def time(r1,r2,dist,v1):#相撞时间
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
                return (l2-l1)/norm(v1)

        def qie(sel,cel):#time距离版#chuan
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

        def stra1(sel,cel):#A3#chuan
            nonlocal dv2
            p1=sel.pos
            p2=cel.pos
            v1=[sel.veloc[0]-cel.veloc[0],sel.veloc[1]-cel.veloc[1]]
            a=[p2[0]-p1[0],p2[1]-p1[1]]
            a=chuan(a)
            p2=[p1[0]+a[0],p1[1]+a[1]]
            p3=[p1[0]+v1[0],p1[1]+v1[1]]
            
            b=[p3[0]-p1[0],p3[1]-p1[1]]
            c=[p2[0]-p3[0],p2[1]-p3[1]]
            theta1=thet([-v1[0],-v1[1]],c)
            if theta1>pi:
                theta1=theta1-2*pi
                
            if norm(v1)<0.2:
                return thet([0,1],a)+pi
            #比
            r=abs(theta1/pi)
            if r>0.9:
                r1=1-5*(1-r)
            else:
                r1=r**3
            theta=theta1*r1
            return thet([0,1],[-v1[0],-v1[1]])+theta+pi

        def stra1_J(sel,cel):#A3#chuan#J
            def duan(t):
                if t<0.7:
                    return t**2
                else:
                    return t
                
            nonlocal dv2
            p1=sel.pos
            p2=cel.pos
            v1=[sel.veloc[0]-cel.veloc[0],sel.veloc[1]-cel.veloc[1]]
            a=[p2[0]-p1[0],p2[1]-p1[1]]
            a=chuan(a)
            p2=[p1[0]+a[0],p1[1]+a[1]]
            p3=[p1[0]+v1[0],p1[1]+v1[1]]
            
            b=[p3[0]-p1[0],p3[1]-p1[1]]
            c=[p2[0]-p3[0],p2[1]-p3[1]]
            theta1=thet([-v1[0],-v1[1]],c)

            if norm(v1)<0.3:
                return thet([0,1],a)+pi
            
            if theta1>pi:
                theta1=theta1-2*pi

            #比
            r=abs(theta1/pi)
            
            r1=r
            theta=theta1*duan(r1)
            return thet([0,1],[-v1[0],-v1[1]])+theta+pi
            

        def stra2(p1,p2,v1,dv2):#规避策略
            v=[p2[0]-p1[0],p2[1]-p1[1]]
            v=chuan(v)
            v3=[v[0]-v1[0],v[1]-v1[1]]
            return thet([0,1],v3)

        def guibi(sel,cell):#规避函数简写
            nonlocal dv2
            selp=sel.pos
            selv=sel.veloc
            celp=cell.pos
            celv=cell.veloc
            return stra2(selp,celp,[selv[0]-celv[0],selv[1]-celv[1]],dv2)

        def time_li_x(cel):#返回time,deltar函数列表,只看比自己小的求
            nonlocal allcells
            lst1=[]
            lst2=[]
            r1=cel.radius
            for i in range(len(allcells)):
                cel1=allcells[i]
                if cel1.dead==True or cel1==cel or cel1.radius>=cel.radius:
                    lst1.append(None)
                    lst2.append(None)
                    continue
                r2=cel1.radius
                dist=[cel1.pos[0]-cel.pos[0],cel1.pos[1]-cel.pos[1]]
                v1=[cel.veloc[0]-cel1.veloc[0],cel.veloc[1]-cel1.veloc[1]]
                t=time(r1,r2,dist,v1)
                lst1.append(t)
                if t!=None:
                    lst2.append(sqrt(r1**2+r2**2)-r1)
                else:  
                    lst2.append(None)

            return [lst1,lst2]

        def time_li_x_c(cel):#返回time,deltar函数列表,只看比自己小的求,带上c
            nonlocal allcells,riv
            lst1=[]
            lst2=[]
            lst3=[]
            r1=cel.radius
            clst=[riv]+allcells[2:]
            for i in range(len(clst)):
                cel1=clst[i]
                if cel1.dead==True or cel1==cel or cel1.radius>=cel.radius:
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
                    lst2.append(r2)
                    lst3.append(jiehe_yu(cel,cel1))
                else:  
                    lst2.append(None)
                    lst3.append(None)
                

            return [lst1,lst2,lst3]

        def time_li_all_c(cel):#返回time,deltar函数列表,带上c
            nonlocal allcells
            lst1=[]
            lst2=[]
            lst3=[]
            r1=cel.radius
            clst=[riv]+allcells[2:]
            for i in range(len(clst)):
                cel1=clst[i]
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
                    lst2.append(r2)
                    lst3.append(jiehe_yu(cel,cel1))
                else:  
                    lst2.append(None)
                    lst3.append(None)
                

            return [lst1,lst2,lst3]

        def qie_li_x(cel):#返回qie,deltar函数列表,只看比自己小的求
            nonlocal allcells
            lst1=[]
            lst2=[]
            
            for i in range(len(allcells)):
                cel1=allcells[i]
                if cel1.dead==True or cel1==cel or cel1.radius>=cel.radius:
                    lst1.append(None)
                    lst2.append(None)
                    continue
                
                t=qie(cel,cel1)
                lst1.append(t)
                r1=cel.radius
                r2=cel1.radius
                if t!=None:
                    lst2.append(sqrt(r1**2+r2**2)-r1)
                else:  
                    lst2.append(None)

            return [lst1,lst2]

        def chuan1(cel):#返回cel的chuan坐标
            nonlocal sel
            dist=[cel.pos[0]-sel.pos[0],cel.pos[1]-sel.pos[1]]
            dist=chuan(dist)
            p=[sel.pos[0]+dist[0],sel.pos[1]+dist[1]]
            return p

        def time1(sel,cel):#time简写版,chuan
            r1=sel.radius
            r2=cel.radius
            dist=[cel.pos[0]-sel.pos[0],cel.pos[1]-sel.pos[1]]
            dist=chuan(dist)
            v1=[sel.veloc[0]-cel.veloc[0],sel.veloc[1]-cel.veloc[1]]

            return time(r1,r2,dist,v1)

        def jiehe(cel1,cel2):#返回结合后的r和v
            r1=cel1.radius
            r2=cel2.radius
            v1=cel1.veloc
            v2=cel2.veloc
            r=sqrt(r1**2+r2**2)
            v=[(r1**2*v1[0]+r2**2*v2[0])/(r1**2+r2**2),(r1**2*v1[1]+r2**2*v2[1])/(r1**2+r2**2)]
            return r,v

        def jiehe_yu(cel1,cel2):#Nochuan#p,r,v#time!=None
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

        def jiao(l1,l2):#p,r,v or p,r#chuan
            p1=l1[0]
            p2=l2[0]
            dist=[p2[0]-p1[0],p2[1]-p1[1]]
            dist=chuan(dist)
            r1=l1[1]
            r2=l2[1]
            return norm(dist)<r1+r2

        def dang1(sel,cel):
            r1=sel.radius
            r2=cel.radius
            dist=[cel.pos[0]-sel.pos[0],cel.pos[1]-sel.pos[1]]
            return dang(r1,r2,dist,0)


        def loss(sel,cel):#chuan
            nonlocal dv2,maxv
            dist=[cel.pos[0]-sel.pos[0],cel.pos[1]-sel.pos[1]]
            dist=chuan(dist)
            v=[sel.veloc[0]-cel.veloc[0],sel.veloc[1]-cel.veloc[1]]
            theta1=(sel.radius+cel.radius)/norm(dist)
            if theta1<1:
                theta1=asin(theta1)
            jiao=jia(v,dist)
            if jiao<theta1:
                return 0

            #参数
            pl=0
            if norm(v)<maxv:
                pl=(maxv-norm(v))/dv2
            #参数#速度越大loss越大
            return abs(jiao-theta1)*norm(v)/dv2*(1+norm(v)**2)+pl

        def shouyi(sel,cel):
            nonlocal rat
            los=loss(sel,cel)
            #参数
            if (1-rat)**los<1.1*cel.radius**2/sel.radius**2:
                return None
            else:
                return (1-rat)**los/1.1+(cel.radius/sel.radius)**2

        def howl(sel,cel):#预测chi球时间#粗略
            v=[sel.veloc[0]-cel.veloc[0],sel.veloc[1]-cel.veloc[1]]
            dist=[cel.pos[0]-sel.pos[0],cel.pos[1]-sel.pos[1]]
            dist=chuan(dist)
            vs=(v[0]*dist[0]+v[1]*dist[1])/norm(dist)
            t1=dang1(sel,cel)/max(vs,0.3)
            t2=loss(sel,cel)
            return t1+t2

        #*lst([p,r,v])
        def attran(sellst,rivlst,blst):
            dist1=[sellst[0][0]-rivlst[0][0],sellst[0][1]-rivlst[0][1]]
            dist2=[blst[0][0]-rivlst[0][0],blst[0][1]-rivlst[0][1]]
            dist1=chuan(dist1)
            dist2=chuan(dist2)
            if (dist1[0]*dist2[0]+dist1[1]*dist2[1]<0 and
                dianz(blst[0],sellst[0],rivlst[0])<blst[1]/2):
                return True
            else:return False

        def yu(cel,t):#预测时间t后sel的[p,r,v]
            p=[cel.pos[0]+cel.veloc[0]*t,cel.pos[1]+cel.veloc[1]*t]
            r=cel.radius
            v=cel.veloc
            return p,r,v

        def fashe():#相对于riv返回角度和喷射速度大小(相对riv)
            nonlocal sel,riv
            dist=chuan([riv.pos[0]-sel.pos[0],riv.pos[1]-sel.pos[1]])
            v=[sel.veloc[0]-riv.veloc[0],sel.veloc[1]-riv.veloc[1]]
            v1r=(v[0]*dist[0]+v[1]*dist[1])/norm(dist)**2#水平
            v1=[v1r*dist[0],v1r*dist[1]]
            v2=[v[0]-v1[0],v[1]-v1[1]]
            if norm(v2)>dv1-1e-4:
                return None
            else:
                l=sqrt(dv1**2-norm(v2)**2)/norm(dist)
                x=[-v2[0]+l*dist[0],-v2[1]+l*dist[1]]
                return thet([0,1],x),(v1r+l)*norm(dist)

        def chuan1(cel):#返回cel的chuan坐标
            nonlocal sel
            dist=[cel.pos[0]-sel.pos[0],cel.pos[1]-sel.pos[1]]
            dist=chuan(dist)
            p=[sel.pos[0]+dist[0],sel.pos[1]+dist[1]]
            return p

        def C(cellst):
            class Cell():
                def __init__(self, pos = [0, 0], veloc = [0, 0], radius = 0, isplayer = False):
                    # Variables to hold current position
                    self.pos = pos
                    # Variables to hold current velocity
                    self.veloc = veloc
                    # Variables to hold size
                    self.radius = radius
                    
            if cellst==[]:
                return None
            lst1=[]
            lst2=[]
            lst3=[]
            for x in cellst:
                lst1.append(chuan1(x))
                lst2.append(x.radius)
                lst3.append(x.veloc)
            P=[0,0]
            for i in range(len(cellst)):
                P[0]=P[0]+lst1[i][0]*lst2[i]**2
                P[1]=P[1]+lst1[i][1]*lst2[i]**2
            P[0]=P[0]/sum(r**2 for r in lst2)
            P[1]=P[1]/sum(r**2 for r in lst2)

            R=sqrt(sum(r**2 for r in lst2))

            V=[0,0]
            for i in range(len(cellst)):
                V[0]=V[0]+lst3[i][0]*lst2[i]**2
                V[1]=V[1]+lst3[i][1]*lst2[i]**2
            V[0]=V[0]/sum(r**2 for r in lst2)
            V[1]=V[1]/sum(r**2 for r in lst2)

            Cel=Cell()
            Cel.pos=P
            Cel.radius=R
            Cel.veloc=V

            return Cel

        def juji(cel,dt):
            nonlocal xiao_li,selr
            s=0
            celv=cel.veloc
            celp=cel.pos
            for x in xiao_li:
                if x!=cel and x.radius>selr*0.3:
                    xp=x.pos
                    xv=x.veloc
                    dist=chuan([xp[0]-celp[0],xp[1]-celp[1]])
                    v=[xv[0]-celv[0],xv[1]-celv[1]]
                    dist=[dist[0]+v[0]*dt,dist[1]+v[1]*dt]
                    
                    s+=(x.radius/selr)**2/(1+(norm(dist)/75)**2)            

            return s
            
            
                
                
            
        
        
        
        #规避
        
        i2_min=None
        min2=None
        i1_min=None
        min1=None
        for i in range(len(da_li)):
            celp=da_li[i].pos
            celv=da_li[i].veloc
            t1=time1(sel,da_li[i])
            t2=qie(sel,da_li[i])

            if t2!=None:
                if i2_min==None:
                    i2_min=i
                    min2=t2
                else:
                    if t2<min2:
                        i2_min=i
                        min2=t2

            if t1!=None:
                if i1_min==None:
                    i1_min=i
                    min1=t2
                else:
                    if t1<min2:
                        i1_min=i
                        min1=t2
        #参数
        if len(da_li)>5:
            if min2!=None and min2/sqrt(selr)<5:
                self.target=None
                cell=da_li[i2_min]
                celp=cell.pos
                celv=cell.veloc
                return stra2(selp,celp,[selv[0]-celv[0],selv[1]-celv[1]],dv2)
        if min1!=None and min1<60:
            self.target=None
            cell=da_li[i1_min]
            celp=cell.pos
            celv=cell.veloc
            return stra2(selp,celp,[selv[0]-celv[0],selv[1]-celv[1]],dv2)
        

        
        
                            
                    

                        

        

        

                        

        #chi
        target=None
        if len(da_li)<100:
            
            xiao_li=[]
            for x in allcells[2:]:
                if x.radius<selr:
                    xiao_li.append(x)

            chi_li=[]#[[cel,shouyi]...]
            for cel in xiao_li:
                if cel.radius>0.38*selr:
                    #参数
                    if dang1(sel,cel)<searchran:
                        los=loss(sel,cel)
                        dt=howl(sel,cel)
                        
                        zhuang_li_r=[]
                        for y in da_li:
                            a=chuan([y.pos[0]-selp[0],y.pos[1]-selp[1]])
                            b=chuan([cel.pos[0]-selp[0],cel.pos[1]-selp[1]])
                            if (dianz(chuan1(y),selp,chuan1(cel))<selr+y.radius+40 and
                                a[0]*b[0]+a[1]*b[1]>0 and a[0]*b[0]+a[1]*b[1]<norm(b)**2):
                                break
                        else:
                                
                            lst=time_li_all_c(cel)
                            for i in range(len(lst[0])):
                                if lst[0][i]!=None and lst[0][i]<dt*5:
                                    zhuang_li_r.append(lst[1][i])
                            
                            
                            ####----------------------
                            if los<20:
                                area1=cel.radius**2+sum([x**2 for x in zhuang_li_r])
                                if selr**2*(1-rat)**los>area1:
                                    shouyi1=shouyi(sel,cel)
                                    t=howl(sel,cel)
                                    j=juji(cel,dt)
                                    if shouyi1!=None:
                                        #参数
                                        if cel==self.pretarget:
                                            chi_li.append([cel,shouyi1,t,j])
                                        else:chi_li.append([cel,shouyi1,t,j])

            x_ma=None
            max1=None
            for u in chi_li:
                if u[1]+u[3]>1.07:
                
                    if x_ma==None:
                        x_ma=u[0]
                        max1=u[1]+u[3]-u[2]/1000
                    else:
                        if max1<u[1]+u[3]-u[2]/1000:
                            max1=u[1]+u[3]-u[2]/1000
                            x_ma=u[0]

            if x_ma!=None:
                    
                    target=x_ma
                    self.pretarget=target
                    
                    v=[sel.veloc[0]-target.veloc[0],sel.veloc[1]-target.veloc[1]]
                    if norm(v)<maxv or loss(sel,target)>0:
                        return stra1_J(sel,target)

        if target==None:

            d_lst=[]
        
            for x in allcells:
                if x!=sel and x.radius>selr*0.38:
                    celp=x.pos
                    celv=x.veloc
                    t1=dang(selr,x.radius,chuan([celp[0]-selp[0],celp[1]-selp[1]]),[selv[0]-celv[0],selv[1]-celv[1]])
                    if t1<300:
                        d_lst.append([x,t1])

            #进化1  
            for x in d_lst:
                t_l,r_l,c_l=time_li_x_c(x[0])
                for i in range(len(t_l)):
                    #参数
                    if t_l[i]!=None and c_l[i][1]>selr:
                        p_=[selp[0]+t_l[i]*selv[0],selp[1]+t_l[i]*selv[1]]
                        if jiao([p_,selr,selv],c_l[i])==True:
                            return guibi(sel,x[0])
                        else:
                            t=dang(selr,c_l[i][1],chuan([c_l[i][0][0]-p_[0],c_l[i][0][1]-p_[1]]),[selv[0]-c_l[i][2][0],selv[1]-c_l[i][2][1]])
                            if t!=None and t<20:
                                return guibi(sel,x[0])
                            
                            
                                
                                
                                 
                                

            #进化2
            t_l,r_l,c_l=time_li_x_c(sel)
            for x in d_lst:
                for i in range(len(t_l)):
                    if t_l[i]!=None:
                        if c_l[i][1]<x[0].radius:
                            p_=[x[0].pos[0]+t_l[i]*x[0].veloc[0],x[0].pos[1]+t_l[i]*x[0].veloc[1]]
                            if jiao(c_l[i],[p_,x[0].radius])==True:
                                return guibi(sel,x[0])
                            else:
                                t=dang(c_l[i][1],x[0].radius,chuan([p_[0]-c_l[i][0][0],p_[1]-c_l[i][0][1]]),
                                       [c_l[i][2][0]-x[0].veloc[0],c_l[i][2][1]-x[0].veloc[1]])
                                if t!=None and t<12:
                                    return guibi(sel,x[0])
            #Ju
            
            dist=[riv.pos[0]-selp[0],riv.pos[1]-selp[1]]
            dist=chuan(dist)
            v=[selv[0]-riv.veloc[0],selv[1]-riv.veloc[1]]
            if riv.radius>5:
                if (riv.radius<selr*0.8 and 
                    distance(sel,riv)<220 and jia(dist,v)<pi/5 or
                    riv.radius<selr*0.65 and 
                    distance(sel,riv)<400 and jia(dist,v)<pi/3 or
                    riv.radius<selr*0.75 and norm(v)<0.3 and distance(sel,riv)<220 or
                    riv.radius<selr*0.55 and norm(v)<0.6 and distance(sel,riv)<400):
                    
                    
                    for y in da_li:
                        #参数
                        a=chuan([y.pos[0]-selp[0],y.pos[1]-selp[1]])
                        b=chuan([riv.pos[0]-selp[0],riv.pos[1]-selp[1]])
                        if (dianz(chuan1(y),selp,chuan1(riv))<selr+y.radius+40 and
                            a[0]*b[0]+a[1]*b[1]>0 and a[0]*b[0]+a[1]*b[1]<norm(b)**2):
                            break
                    else:
                        if len(da_li)>1:
                            if norm(selv)<0.5 and (qie(sel,riv)==None or norm(v)<0.7):
                                return stra1_J(sel,riv)
                        elif len(da_li)==1:
                            if norm(selv)<1 and (qie(sel,riv)==None or norm(v)<1):
                                return stra1_J(sel,riv)
                            
                        else:
                            if qie(sel,riv)==None or norm(v)<1.8:
                                return stra1_J(sel,riv)

            da_li_riv=[]
            for x in allcells[2:]:
                if x.radius>riv.radius:
                    da_li_riv.append(x)

            dist=[sel.pos[0]-riv.pos[0],sel.pos[1]-riv.pos[1]]
            dist=chuan(dist)
            flst=fashe()
            if flst!=None and flst[1]*selr**2/riv.radius**2>2*dv1:
                for x in allcells[2:]:
                    xdist=[x.pos[0]-riv.pos[0],x.pos[1]-riv.pos[1]]
                    dian=xdist[0]*dist[0]+xdist[1]*dist[1]
                    #参数
                    if dianz(x.pos,sel.pos,riv.pos)<40 and dian>0 and dian<norm(dist)**2:
                        break

                else:
                    t=norm(dist)/flst[1]
                    sellst=[selp,selr,selv]
                    rivlst=[riv.pos,riv.radius,riv.veloc]
                    
                    for b in da_li_riv:
                        blst1=[b.pos,b.radius,b.veloc]
                        blst2=yu(b,t)
                        if attran(sellst,rivlst,blst1)==True and attran(sellst,rivlst,blst2)==True:
                            #参数
                            if norm(chuan([blst2[0][0]-rivlst[0][0],blst2[0][1]-rivlst[0][1]]))-blst1[1]-rivlst[1]<200:
                                return flst[0]


            #远处规划
            Cel=C(xiao_li)

            #参数
            if Cel!=None:
                if Cel.radius>selr*0.5 and distance(sel,Cel)>300:
                    for y in da_li:
                        a=chuan([y.pos[0]-selp[0],y.pos[1]-selp[1]])
                        b=chuan([Cel.pos[0]-selp[0],Cel.pos[1]-selp[1]])
                        if (dianz(chuan1(y),selp,chuan1(Cel))<selr+y.radius+40 and
                            a[0]*b[0]+a[1]*b[1]>0 and a[0]*b[0]+a[1]*b[1]<norm(b)**2):
                            break
                    else:
                        v=[sel.veloc[0]-Cel.veloc[0],sel.veloc[1]-Cel.veloc[1]]
                        if norm(v)<0.4 or loss(sel,Cel)>0:
                            
                            return stra1_J(sel,Cel)

                    


        
                
                
        

