#todo:
#估价函数三球问题
#开局的小体力策略
#结尾的ai对战策略
#一些报错都要自己兜一下
#整个代码要结构好看一些
#什么predict写成predict的有一堆
#FRAME_DELTA的意思是帧与帧之间的时间吗？
#找什么样的目标比较好？
#估值函数要改进吗

from consts import Consts
from cell import Cell
import math

class Player():
    
    def __init__(self, id, arg = None):
        self.id = id
        self.count = 0

    #================以自我为中心的辅助函数===============
    def self_centered_coord(self, other):
        #返回以自我为中心时other的坐标
        dx = other.pos[0] - self.me.pos[0]
        dy = other.pos[1] - self.me.pos[1]
        real_dx = min([dx, dx - Consts["WORLD_X"], dx + Consts["WORLD_X"]], key = abs)
        real_dy = min([dy, dy - Consts["WORLD_Y"], dy + Consts["WORLD_Y"]], key = abs)
        return [real_dx, real_dy]

    def distance_from(self, other):
        #自己到other的距离
        [dx, dy] = self.self_centered_coord(other)
        return (dx ** 2 + dy ** 2) ** 0.5

    def gap_from(self, other):
        #自己到other的gap
        gap = self.distance_from(other) - self.me.radius - other.radius
        #撞上了就返回-1
        return gap if gap > 0 else -1

    def predict_min_distance(self, other):
        #基于简单数学预测最近的距离，还没有考虑跨屏（跨屏很难考虑），故靠谱的距离半径是Consts["WORLD_Y"] / 2，应该够用了
        #如果是越来越远就不存在最小距离，返回None
        [dx, dy] = self.self_centered_coord(other)
        dvx = other.veloc[0] - self.me.veloc[0]
        dvy = other.veloc[1] - self.me.veloc[1]
        #用内积判断是否越来越远
        if dx * dvx + dy * dvy > 0:
            return None
        elif dvx**2 + dvy ** 2 == 0:
            return None
        else:
            return abs(dx * dvy - dy * dvx) / math.sqrt(dvx**2 + dvy ** 2) 

    def predict_is_safe(self, other, safe_distance):
        #预测将来是否安全
        #之后的最小gap比save_distance大就是安全
        if not self.predict_min_distance(other):
            return True
        else:
            min_gap = self.predict_min_distance(other) - self.me.radius - other.radius 
            return min_gap > safe_distance

    def predict_can_eat(self, target):
        #预测这样下去是否能吃到
        if not self.predict_min_distance(target):
            return None
        else:
            min_gap = self.predict_min_distance(target) - self.me.radius - target.radius 
            return min_gap < -5

    def predict_collide_time(self, other):
        #预测过多久一个球会撞上自己，碰不上返回None
        [dx, dy] = self.self_centered_coord(other)
        dr = math.sqrt(dx**2 + dy**2)
        dvx = other.veloc[0] - self.me.veloc[0]
        dvy = other.veloc[1] - self.me.veloc[1]
        dv = math.sqrt(dvx**2 + dvy**2)
        #之后最近的距离
        h = self.predict_min_distance(other)
        if not h:
            return None
        #之后最小的间隔
        min_gap = h - self.me.radius - other.radius 
        if min_gap > 0:
            return None
        elif dv == 0:
            return None
        else:
            l1 = math.sqrt(abs(dr**2 - h**2))
            l2 = math.sqrt(abs((self.me.radius + other.radius)**2 - h**2))
            return (l2 - l1) / dv

    #====================全局辅助函数=================================
    def distance_between(self,cell1,cell2):
        #两者球心间的距离
        dx = cell1.pos[0] - cell2.pos[0]
        dy = cell1.pos[1] - cell2.pos[1]
        real_dx = min(abs(dx), Consts["WORLD_X"] - abs(dx))
        real_dy = min(abs(dy), Consts["WORLD_Y"] - abs(dy))
        return  math.sqrt(real_dx**2 + real_dy**2)

    def gap_between(self,cell1,cell2):
        #两者之间的gap，撞上了就返回-1
        gap = self.distance_between(cell1, cell2) - cell1.radius - cell2.radius
        return gap if gap > 0 else -1

    def mass(self,cell):
        #返回质量
        return math.pi * cell.radius**2

    def predict(self, frame_number, predict_cells):
        #预测除自己以外的其他球走frame_number帧之后的坐标
        #不要把自己传进来，不预测碰撞
        #传出去一个cell的list
        import copy
        copy = copy.deepcopy(predict_cells)
        #移动frame_number帧
        for cell in copy:
            cell.pos[0] += cell.veloc[0] * frame_number * Consts["FRAME_DELTA"]
            cell.pos[1] += cell.veloc[1] * frame_number * Consts["FRAME_DELTA"]
            #穿屏
            if cell.pos[0] < 0:
                cell.pos[0] += Consts["WORLD_X"]
            elif cell.pos[0] > Consts["WORLD_X"]:
                cell.pos[0] -= Consts["WORLD_X"]
            if cell.pos[1] < 0:
                cell.pos[1] += Consts["WORLD_Y"]
            elif cell.pos[1] > Consts["WORLD_Y"]:
                cell.pos[1] -= Consts["WORLD_Y"]
        return copy

    #=============策略辅助函数（调参的任务在此，将直接决定效果）=====================================    
    def detect_danger(self, danger_gap, allcells):
        #检测会碰到且大的球
        #靠近的大cell
        danger_cells = [cell for cell in allcells if cell.id != self.id and\
                        cell.radius > self.me.radius * 0.95 and\
                        self.gap_from(cell) < danger_gap]        
        #若会碰上
        if danger_cells and False in [self.predict_is_safe(cell, 10) for cell in danger_cells]:
                return danger_cells
        else:
            #若没大的
            return None

    '''
    def detect_danger(self, danger_gap, allcells):
        #检测危险的球
        #大，gap小于danger_gap 且 会碰上自己
        danger_cells = [cell for cell in allcells if\
                        cell != self.me and\
                        cell.radius > self.me.radius * 0.95 and\
                        self.gap_from(cell) < danger_gap and\
                        self.predict_is_safe(cell, 10)]        
        return danger_cells if danger_cells else None
    '''

    def predict_loss_time(self, target):
        #基于简单数学预测吃球体力（面积）消耗和时间消耗
        #由于是贪心算法，为了避免游戏里面写游戏，这里暂时认为r不变
        #有些情况下会不准
        #相对分量
        [dx, dy] = self.self_centered_coord(target)
        dr = math.sqrt(dx**2 + dy**2)
        dvx = target.veloc[0] - self.me.veloc[0]
        dvy = target.veloc[1] - self.me.veloc[1]
        #靠近速度，切向速度
        v_closer = -(dx * dvx + dy * dvy) / dr
        v_side = math.sqrt(abs(dvx**2 + dvy**2 - v_closer**2))
        #喷一次速度改变
        delta_v = Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"]
        #喷一次的时间
        delta_t = Consts["FRAME_DELTA"]
        #喷一次的损失
        delta_m = self.mass(self.me) * Consts["EJECT_MASS_RATIO"] 
        #第一部分：切向速度减为零的消耗
        n1 = math.sqrt(2) * v_side // delta_v + 1#-------------------保守
        t1 = n1 * delta_t
        #靠近了多少
        l1 = v_closer * t1 + (math.sqrt(2)/4) * t1 * n1 * delta_v
        #这个代表吃不到，返回大数
        if l1 >= dr:
            return [99999 * delta_m, 99999 * delta_t]
        #第二部分：暂时做保守估计一直径向喷球加速
        else:
            r_remain = dr - l1
            n2 = 0
            v2 = v_closer + (math.sqrt(2)/2) * delta_v * n1
            while r_remain > 0:
                r_remain -= v2 * delta_t
                v2 += delta_v
                n2 += 1
            return [(n1+n2) * delta_m, (n1 + n2) * delta_t]

    def give_up(self, target):
        #年轻人要学会放弃
        [dx, dy] = self.self_centered_coord(target)
        dr = math.sqrt(dx**2 + dy**2)
        dvx = target.veloc[0] - self.me.veloc[0]
        dvy = target.veloc[1] - self.me.veloc[1]
        #靠近速度，切向速度
        v_closer = -(dx * dvx + dy * dvy) / dr
        v_side = math.sqrt(abs(dvx**2 + dvy**2 - v_closer**2))
        #放弃切向分量过大的球
        if v_side > 5:
            return True
        if v_closer < -10:
            return True
        else:
            return None

    def can_eat(self, target, search_distance):####################重要！！！！！！！！！
        #判断是否能吃(不是对手，大小合适，靠近，去了能吃, 吃了能赚， 不放弃)
        return target != self.opponent and\
                self.me.radius * 0.3 < target.radius < self.me.radius and\
                self.gap_from(target) < search_distance and\
                self.mass(self.me) - self.predict_loss_time(target)[0] > self.mass(target) * 1.1 and\
                self.mass(self.me) - self.predict_loss_time(target)[0] + self.mass(target) > self.mass(self.me) * 0.1 and\
                (not self.give_up(target))

    def search_target(self, search_distance, allcells):
        #在search_distance范围内找profit最大的-----------------------------------------profit = grow / time
        target_list = [cell for cell in allcells if self.can_eat(cell, search_distance)]
        if target_list:
            result = []
            for target in target_list:
                profit = (self.mass(self.me) - self.predict_loss_time(target)[0] + self.mass(target)) / self.predict_loss_time(target)[1]
                result.append(profit)
            return target_list[result.index(max(result))]
        else:
            return None

    #==================元策略=======================
    def eval_func(self, me, other_cells):
        #估价函数
        #传入自己和待估价的其它cell
        gaps = [self.gap_between(me, cell) for cell in other_cells]
        distances = [self.distance_between(me, cell) for cell in other_cells]
        if -1 in gaps:
            #会撞上返回None
            return None
        else:
            #不会撞上返回distance之和
            return sum(distances)
 
    def clever_dodge(self, danger_cells):
        #走一帧之后大球的情况
        new_danger_cells = self.predict(1, danger_cells)
        result = []       
        for i in range(0,100):
            theta = i * math.pi*2 / 100
            #按theta喷之后走一帧后自己的情况
            fx = math.sin(theta)
            fy = math.cos(theta)
            new_vx = self.me.veloc[0] - Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
            new_vy = self.me.veloc[1] - Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
            new_rad = self.me.radius * math.sqrt(1 - Consts["EJECT_MASS_RATIO"])
            new_x = self.me.pos[0] + new_vx * Consts["FRAME_DELTA"]
            new_y = self.me.pos[1] + new_vy * Consts["FRAME_DELTA"]
            #穿屏
            if new_x < 0:
                new_x += Consts["WORLD_X"]
            elif new_x > Consts["WORLD_X"]:
                new_x -= Consts["WORLD_X"]
            if new_y < 0:
                new_y += Consts["WORLD_Y"]
            elif new_y > Consts["WORLD_Y"]:
                new_y -= Consts["WORLD_Y"]
            #一帧以后的自己
            new_me = Cell(None, [new_x, new_y], [new_vx, new_vy], new_rad)
            #估价
            value = self.eval_func(new_me, new_danger_cells)
            result.append(value)
        result_without_none = [i for i in result if i]
        if result_without_none:
            print('hide')
            return result.index(max(i for i in result if i)) * math.pi*2 / 100
        else:
            print('fuck!!!!!!!!!!!!!!')
            return None

    def clever_eat(self, target, stop_gap, stop_time):
        #如果不喷能吃到就不喷了
        if self.predict_can_eat(target) and (self.predict_collide_time(target) < stop_time or self.gap_from(target) < stop_gap):
            print('ok')
            return None
        else:
            #换到自己的参考系
            [dx, dy] = self.self_centered_coord(target)
            dr = math.sqrt(dx**2 + dy**2)
            dvx = target.veloc[0] - self.me.veloc[0]
            dvy = target.veloc[1] - self.me.veloc[1]
            #假设以theta喷的结果
            result = []
            for i in range(0,100):
                theta = i * math.pi*2 / 100
                fx = math.sin(theta)
                fy = math.cos(theta)
                #自己参考系里的新球速
                new_dvx = dvx + Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
                new_dvy = dvy + Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
                new_v = math.sqrt(new_dvx**2 + new_dvy**2)
                #沿着[dx, dy]的分量靠近为正                            
                v_closer = -(dx * new_dvx + dy * new_dvy) / dr
                v_side = math.sqrt(abs(new_v**2 - v_closer**2))
                #以此为估值
                result.append(v_closer - v_side)
            
            print('eat',target.id)  
            return result.index(max(result)) * math.pi*2 / 100 
 
    #==============总策略========================
    def strategy(self, allcells):
        #在这里更新自己
        self.me = allcells[self.id]
        #在这里更新敌人
        self.opponent = allcells[1 - self.id]
        #在这里更新危险细胞
        danger_cells = self.detect_danger(100, allcells)
        #有危险得躲
        if danger_cells:
            return self.clever_dodge(danger_cells)
        #没危险就吃
        else:
            target = self.search_target(100, allcells)
            if target:
                return self.clever_eat(target, 2, 2)
            else:
                danger_cells_ = self.detect_danger(300, allcells)
            #有危险得躲
            if danger_cells:
                return None
            #没危险就吃
            else:
                target = self.search_target(300, allcells)
                if target:
                    return self.clever_eat(target, 2, 2)
                


        



