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
                'radius':cell.radius,'area':cell.area(),'x':cell.pos[0],'y':cell.pos[1]}
                temp.append(data)
            self.polar_data.append(temp)
            
    def runaway(self,allcells):
        pi=math.pi
        self.polar_data.clear()
        self.polar(allcells)
        for cell in self.polar_data[self.id]:
            if cell['distance']>self.myself.radius+cell['radius'] and cell['radius']>self.myself.radius and cell['distance']/(cell['polar_veloc']*math.sin(cell['polar_veloc_angle']))<5:
                theta1=math.asin((self.myself.radius+cell['radius'])/cell['distance'])
                angle_diffience=(cell['polar_veloc_angle']-cell['polar_angle'])
                while True:
                    if angle_diffience<-math.pi:
                        angle_diffience+=2*math.pi
                    elif angle_diffience>math.pi:
                        angle_diffience-=2*math.pi
                    else:
                        break
                min_distance=cell['distance']*math.sin(abs(angle_diffience))
                if min_distance<self.myself.radius+cell['radius']:
                    return cell['polar_angle']
        return None
    def strategy(self, allcells):
        danger=self.runaway(allcells)
        return danger