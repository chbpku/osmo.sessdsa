from consts import Consts
import math

class Player():
    def __init__(self, id, arg = None):
        self.id = id
        self.frame = arg['world'].frame
        
    def strategy(self, allcells):
        global r0
        global shoot
        global gap
        self.frame+=1
        
        #躲避代码
        #距离列表distancelist                
        distancelist=sorted(allcells, key = lambda cell: cell.distance_from(allcells[self.id]))
        for s in range(1,min(5,len(distancelist))): #吐出来的三个球不会被视为需要躲避的球，只要大球是第四近或更近的球，都可以躲避
            if distancelist[s].radius>=allcells[self.id].radius:
                #求self和目标的位置差和速度差
                dx = allcells[self.id].pos[0] - distancelist[s].pos[0]
                if dx>500:
                    dx=dx-1000
                elif dx<-500:
                    dx=dx+1000
                dy = allcells[self.id].pos[1] - distancelist[s].pos[1]
                if dy>300:
                    dy=dx-500
                elif dy<-300:
                    dy=dx+500
                dvx = distancelist[s].veloc[0] - allcells[self.id].veloc[0]
                dvy = distancelist[s].veloc[1] - allcells[self.id].veloc[1]
                dv=(dvx**2+dvy**2)**0.5
                if ((dx-dvx)**2+(dy-dvy)**2)>(dx**2+dy**2) or \
                (dx**2+dy**2)**0.5>dv*10+1.8*(allcells[self.id].radius+distancelist[s].radius): #如果大球在远离玩家，或大球距离大于1.8
                    pass
                else:
                    r0=allcells[self.id].radius
                    gap=0
                    return math.atan2(-dx+dvx, -dy+dvy)
    
        if self.frame < 80:
            shoot = 0
            gap=0
            r0=allcells[self.id].radius
            return None
        
        gap+=1
        
        if (self.frame % 3) != 0:
            return None
        
        if r0*1.1<allcells[self.id].radius or gap==80:
            shoot = 0
        
        if shoot> 20:
            return None
            
    
        #找到可吞噬的、向自身接近的、最近的球（半径为自身的0.22倍~0.88倍,如果没有就别动了）
        found=False
        i=1
        while i < len(distancelist) and not found:
            if distancelist[i].radius > allcells[self.id].radius*0.9 or distancelist[i].radius < allcells[self.id].radius*0.4:
                i+=1
            else:
                dx = allcells[self.id].pos[0] - distancelist[i].pos[0]
                if dx>500:
                    dx=dx-1000
                elif dx<-500:
                    dx=dx+1000
                dy = allcells[self.id].pos[1] - distancelist[i].pos[1]
                if dy>250:
                    dy=dx-500
                elif dy<-250:
                    dy=dx+500
                dvx = distancelist[i].veloc[0] - allcells[self.id].veloc[0]
                dvy = distancelist[i].veloc[1] - allcells[self.id].veloc[1]
                if (dx-dvx)**2+(dy-dvy)**2 > (dx**2+dy**2)+50:
                    i+=1
                else:
                    nearest_cell=distancelist[i]
                    found = True
                    
        if not found:
            return None
        
        if allcells[self.id].distance_from(nearest_cell) > 10*r0:
            return None
        
        if shoot==0:
            gap=0
        
        r0=allcells[self.id].radius
        shoot+=1
        return math.atan2(dx-(20-shoot)*25*dvx, dy-(20-shoot)*25*dvy)

