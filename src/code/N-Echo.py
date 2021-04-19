from consts import Consts
import math
from cell import Cell

max_veloc = Consts["MAX_VELOC"]
eject_mass_ratio = Consts["EJECT_MASS_RATIO"]
delta_veloc = Consts["DELTA_VELOC"]
world_x = Consts['WORLD_X']
world_y = Consts['WORLD_Y']
  # 得到速度

class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.target = None

    def strategy(self, allcells):
        
        default_radius = Consts['DEFAULT_RADIUS']
        max_veloc = Consts["MAX_VELOC"]
        eject_mass_ratio = Consts["EJECT_MASS_RATIO"]
        delta_veloc = Consts["DELTA_VELOC"]
        world_x = Consts['WORLD_X']
        world_y = Consts['WORLD_Y']
        WX = Consts["WORLD_X"]
        WY = Consts["WORLD_Y"]
        delta_veloc = Consts["DELTA_VELOC"]  # 喷射速度
        rat = Consts["EJECT_MASS_RATIO"]
        delta_mv = delta_veloc * Consts["EJECT_MASS_RATIO"]

        
        def cell_copy(cell):
            new = Cell()
            new.id = cell.id
            new.pos = cell.pos.copy()
            new.veloc = cell.veloc.copy()
            new.radius = cell.radius
            new.dead = cell.dead
            return new
        
        mycell = None
        for cell in allcells:
            if cell.id == self.id:
                mycell = cell
                break
        
        #找到自己的cell
        
        # 基本几何函数---------------------------------
        def norm(vec):  # 返回v的2范数
            return math.sqrt(vec[0] ** 2 + vec[1] ** 2)

        def perpendicular(a, b, c):  # 3坐标a,b,c,返回a到直线bc的距离
            u1 = [c[0] - b[0], c[1] - b[1]]
            u2 = [a[0] - b[0], a[1] - b[1]]
            u = abs(u1[0] * u2[0] + u1[1] * u2[1]) / norm(u1)
            a = u2[0] ** 2 + u2[1] ** 2 - u ** 2
            if a < 1e-6:
                return 0
            else:
                return math.sqrt(a)

        def thet(a, b):  # 向量a到b的有向角([0,2pi))
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
            
        def shortest_vec(v):  # 穿屏最小向量(例如坐标[1,1]到坐标[999,499]之间不穿屏向量是[998,498]穿屏向量则是[-2,-2])
            # 只有坐标会用到穿屏函数，速度无论穿不穿都是一样的，不需要穿屏
            nonlocal world_x,world_y
            
            x_list = [v[0]-world_x,v[0],v[0]+world_x]
            x0 = sorted(x_list, key = lambda x: abs(x))[0]
            y_list = [v[1]-world_y,v[1],v[1]+world_y]
            y0 = sorted(y_list, key = lambda x: abs(x))[0]

            return [x0, y0]
        
        def shortest_vec_self(cell):  # 返回cel相对sel的穿屏坐标(即sel.pos+chuan(cel.pos-sel.pos))
            nonlocal mycell
            dist = [cell.pos[0] - mycell.pos[0], cell.pos[1] - mycell.pos[1]]
            dist = shortest_vec(dist)
            p = [mycell.pos[0] + dist[0], mycell.pos[1] + dist[1]]
            return p
        
        def chuan(v):  # 穿屏最小向量(例如坐标[1,1]到坐标[999,499]之间不穿屏向量是[998,498]穿屏向量则是[-2,-2])
            # 只有坐标会用到穿屏函数，速度无论穿不穿都是一样的，不需要穿屏
            WX, WY=world_x,world_y
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

        def jia(a, b):  # 向量a,b的无向角[0,pi)
            theta = thet(a, b)
            return math.pi - abs(math.pi - theta)

        def distance(cellA, cellB):  # 两球sel和cel的距离
            if type(cellA) != type([1,2,3]):
            
                Ap = cellA.pos
                Bp = cellB.pos
            else:
                Ap = cellA
                Bp = cellB
                
            return norm(shortest_vec([Ap[0] - Bp[0], Ap[1] - Bp[1]]))

        def time(r1, r2, dist, v1):  # 预测两球的相撞时间，同样time1函数是该函数参数为sel,cel的版本
            # 参数(为避免出现math domain error)
            dist = shortest_vec(dist)
            if norm(v1) < (norm(dist) - r1 - r2) * 0.01:
                return None

            if v1[0] * dist[0] + v1[1] * dist[1] < 0:
                return None
            h = perpendicular(dist, [0, 0], v1)
            if r1 + r2 < h + 1e-3:
                return None
            else:
                l1 = math.sqrt((r1 + r2) ** 2 - h ** 2)
                l2 = norm(dist) ** 2 - h ** 2
                if l2 < 1e-4:
                    return None
                l2 = math.sqrt(l2)
                return (l2 - l1) / norm(v1)
            
        def time1(sel, cel):  #
            r1 = sel.radius
            r2 = cel.radius
            dist = [cel.pos[0] - sel.pos[0], cel.pos[1] - sel.pos[1]]
            dist = shortest_vec(dist)
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]

            return time(r1, r2, dist, v1)
            
        #更新位置函数
        def renew_pos(pos):
            nonlocal world_x,world_y
            if pos[0] < 0:
                while pos[0] < 0:
                    pos[0] += world_x
            elif pos[0] > world_x:
                while pos[0] > world_x:
                    pos[0] -= world_x
            if pos[1] < 0:
                while pos[1] < 0:
                    pos[0] += world_y
            elif pos[1] > world_y:
                while pos[1] > world_y:
                    pos[1] -= world_y
            return pos
        
        
        #向前预测n步函数
        
                
        #计算射出后半径
        def calc_radius(radius,eject):
            if eject:
                return 0.99**(1/2)*radius
            else:
                return radius
            
        #限制速度最大    
        def limit_speed(v,max_veloc):
            vm = (v[0]**2+v[1]**2)**(1/2)
            if vm >= max_veloc:
                v[0] = v[0]*max_veloc/vm
                v[1] = v[1]*max_veloc/vm
            return v
        
        #根据发射角度计算发射后速度
        def calc_veloc(cell, theta):
            if theta:
                old_vx = cell.veloc[0]
                old_vy = cell.veloc[1]
                eject_vx = delta_veloc*math.sin(theta)
                eject_vy = delta_veloc*math.cos(theta)
                new_vx = (old_vx-eject_vx)/0.99
                new_vy = (old_vy-eject_vy)/0.99
                return limit_speed([new_vx,new_vy],max_veloc)
            else:
                return cell.veloc
            
            
        #两个球融合函数
        def merge(cellA,cellB):
            ra = cellA.radius
            rb = cellB.radius
            newcell = Cell()
            rn = (ra**2 + rb**2)**(1/2)
            vxa,vya=cellA.veloc
            vxb,vyb=cellB.veloc
            vxn = ((ra**2)*vxa+(rb**2)*vxb)/(rn**2)
            vyn = ((ra**2)*vya+(rb**2)*vyb)/(rn**2)
            vn = limit_speed([vxn,vyn],max_veloc)
            if ra > rb:
                newcell.pos = cellA.pos.copy()
                newcell.id = cellA.id
            elif rb > ra:
                newcell.pos = cellB.pos.copy()
                newcell.id = cellB.id
            else:
                if cellA.id < cellB.id:
                    newcell.pos = cellA.pos.copy()
                    newcell.id = cellA.id
                else:
                    newcell.pos = cellB.pos.copy()
                    newcell.id = cellB.id
            newcell.veloc = vn
            newcell.radius = rn
            newcell.dead = False
            return newcell
            
         
        #找寻r倍半径和内的大球和小球        
        def in_range(r,mycell,cellist):
            res_big = [cell for cell in cellist if distance(cell,mycell) < r*(cell.radius+mycell.radius) \
                       and cell.radius >= mycell.radius and cell.id != mycell.id]
            res_small = [cell for cell in cellist if distance(cell,mycell) < r*(cell.radius+mycell.radius) \
                         and cell.radius < mycell.radius and cell.id != mycell.id]
            return res_big, res_small
        
        #判断是否接触
        def is_collision(cellA,cellB):
            return distance(cellA,cellB) < cellA.radius+cellB.radius
        
        #判断是否足够接近
        def is_in_range(r,cellA,cellB):
            return distance(cellA,cellB) < r*(cellA.radius)+cellB.radius

        

    # 可以根据实际计算精度调整保留位数
    
    
    
        thresh_ratio = 0.2
        #防止考虑那种被射出来的很小的球，设置一个门槛值
        
        mycell = None
        
        for cell in allcells:
            if cell.id == self.id:
                mycell = cell
                break
        cell_alive = [cell for cell in allcells if cell.dead == False]
        #比自己大的
        larger_self = [cell for cell in cell_alive if cell.radius >= mycell.radius and cell.id != mycell.id]
        if not larger_self:
            return None
        #比自己小的
        smaller_self = [cell for cell in cell_alive if cell.radius < mycell.radius and \
                        cell.radius > thresh_ratio * mycell.radius and cell.id != mycell.id]
        
        rival_id = 1-self.id
        #寻找敌方cell
        for cell in allcells:
            if cell.id == rival_id:
                rivalcell = cell
                break
        #比对手大的
        larger_rival = [cell for cell in cell_alive if cell.radius >= rivalcell.radius and cell.id != rival_id]
        #比对手小的
        smaller_rival = [cell for cell in cell_alive if cell.radius < rivalcell.radius and cell.id != rival_id]
        
        
        def forward(n,cell,method='ignore_collision'):
            newcell = cell_copy(cell)
            if method=='ignore_collision':
                newcell.pos[0] += cell.veloc[0]*n
                newcell.pos[1] += cell.veloc[1]*n
                newcell.pos = renew_pos(cell.pos)
                return newcell
            else:
                raise ValueError('Method does not exist.')
        
                #向前预测一步函数
        def forward_1(celllist):
            forward_1 = sorted([forward(1,cell) for cell in celllist if cell.dead == False],key=lambda x:x.radius,reverse=True)
            predator_id = []
            dead = False
            for i in range(len(forward_1)):
                for j in range(i+1,len(forward_1)):
                    if forward_1[j].dead == False and is_collision(forward_1[i],forward_1[j]):
                        forward_1[i] = merge(forward_1[i],forward_1[j])
                        forward_1[j].dead = True
                        if forward_1[j].id == self.id:
                            predator_id.append(forward_1[i].id)
                            dead = True
                    if dead:
                        break
                if dead:
                    break
              
            return [cell for cell in forward_1 if not cell.dead],predator_id
        #第一个list是一步之后的所有cell。第二个list是被哪些cell吃掉（如果被吃掉）
        
        #设置copy防止改动原来的cell属性导致实际运行的时候出错（因为不清楚这会不会直接改动了比赛中相应的cell）
        

        
#预测碰撞的时间
        def collision_prediction(cell1, cell2,f):
            x = time1(cell1,cell2)
            if not x:
                return f+1
            elif x <= f:
                return x
            else:
                return f+1
        

#预测接近的时间        
        
        def prediction(f1,allcells,method='simple',width=10):
            if method == 'full':
                nonlocal thresh_ratio
                all_cell_copy_for_iteration = [cell_copy(cell) for cell in allcells if cell.radius >= mycell.radius*thresh_ratio and cell.dead == False]
                dead_time = None
                predator_id = []
                for i in range(f1):
                    all_cell_copy_for_iteration, predator_id = forward_1(all_cell_copy_for_iteration)
                    if predator_id:
                        dead_time = i
                        return all_cell_copy_for_iteration,dead_time,predator_id 
                return all_cell_copy_for_iteration,dead_time,predator_id
            elif method == 'part':
                if not width:
                    raise ValueError('Please enter the width needed for this method.')
                all_cell_copy_for_iteration = [cell_copy(cell) for cell in allcells \
                                               if cell.radius >= mycell.radius*thresh_ratio and cell.dead == False \
                                               and distance(mycell,cell) <= width*mycell.radius]
                dead_time = None
                predator_id = []
                for i in range(f1):
                    all_cell_copy_for_iteration, predator_id = forward_1(all_cell_copy_for_iteration)
                    if predator_id:
                        dead_time = i
                        return all_cell_copy_for_iteration,dead_time,predator_id 
                return all_cell_copy_for_iteration,dead_time,predator_id
            elif method == 'simple':
                nonlocal thresh_ratio,smaller_self,larger_self,mycell
                time_collision = sorted([(collision_prediction(cell1=mycell,cell2=cell,f=f1),cell) \
                                         for cell in larger_self],key=lambda x:x[0])
                dead_time = time_collision[0][0]

                if dead_time > f1:

                    s = mycell.radius**2

                    for cell in smaller_self:

                        if collision_prediction(cell1=mycell,cell2=cell,f=f1) <= f1:

                            if cell.radius < mycell.radius:
                                s += cell.radius**2
                    s = s**(1/2)

                    return s,None,None
                else:  

                    return None,time_collision[0][0],[cell.id for time,cell in time_collision if time <= dead_time]
            else:
                raise ValueError('Method does not exist.')
                
                
        def dodge(mycell, predator_id, closer_id, method='ignore_closer'):
            
            if method == 'ignore_closer':
                for cell in allcells:
                    if cell.id in predator_id:
                        predator = cell
                        break
                return dodge_1(mycell,predator)
            # 直接对躲避目标喷球
            else:
                vec_list = []
                for i in closer_id:
                    for cell in allcells:
                        if cell.id == i:
                            vec_list.append(shortest_vec([cell.pos[0] - mycell.pos[0], cell.pos[1] - mycell.pos[1]]))
                theta_sum = 0
                for i in vec_list:
                    theta_sum += math.atan2(i[1], i[0])
                theta = theta_sum/len(vec_list)
                return theta
            # 考虑附近所有有危险的，求出平均角度喷球

        def dodge_1(cellA, cellB):  # 躲球函数(参数为sel,cel)
            pA = cellA.pos
            vA = cellA.veloc
            pB = cellB.pos
            vB = cellB.veloc
            dAB = shortest_vec([pB[0]-pA[0],pB[1]-pA[1]])
            dvAB = [vA[0]-vB[0],vA[1]-vB[1]]
            v = [dAB[0]-dvAB[0],dAB[1]-dvAB[1]]
            return thet([0,1],v)
        
 
        
        
        #下面a代表被吃球在t时间之后的位置，b为自己球的位置，c为以原速度前进的位置
        def find_1(mycell, allcells,r_time):
            if not r_time:
                raise ValueError('Please enter the parameter r required for this method.')
                
            pre_selection = [cell for cell in smaller_self if is_in_range(r_time,mycell,cell)]
            if not pre_selection:
                return None
            
            cells_id_time_list = []
            target_id = None

            for cell in pre_selection:
                if cell.id != mycell and cell.radius <= 0.9 * mycell.radius and cell.radius >= 0.5 * mycell.radius:  # 还可以考虑改变目标球大小限制
                    min_dist = shortest_vec([cell.pos[0] - mycell.pos[0], cell.pos[1] - mycell.pos[1]])
                    relative_speed = [mycell.veloc[0] - cell.veloc[0], mycell.veloc[1] - cell.veloc[1]] # 相对于场上的球，我方球的速度
                    jiajiao = jia(min_dist, relative_speed)
                    if jiajiao < math.pi / 4 or norm(relative_speed)<1:  # 参数可改，假设只吃相对速度和直线距离夹脚为小锐角的；还可以考虑加入距离限制，场地大小为1000*500
                        time_needed = norm(min_dist) / (norm(relative_speed) * math.cos(jiajiao))
                    else:
                        time_needed = 2500 # 随便设定一个大数
                    cells_id_time_list.append((cell, time_needed))
            priority_list = sorted(cells_id_time_list, key = lambda x: x[1]) # 以吃球时间作为判断标准，给出 priority
        # 下面是进一步判断在移动向目标球过程中，是否会被吃
        # 思路为：设目标球在被吃时刻的位置为a，己方球在当前时刻的位置为b，假设不喷射球（即不改变速度），
        # 己方球在当前速度下经过相同时间到位置为c，则 a，b，c 构成三角形（或者说扇形），若没有其他更大
        # 的球在己方移动时间内进入这个扇形，则认为不会被吃
            target_available = []


            for i in range(len(priority_list)):
                cell_i = priority_list[i][0]
                cell_time_needed = int(priority_list[i][1]) + 1
                if cell_time_needed >= 50:
                    break
                a = forward(cell_time_needed, cell_i, method='ignore_collision').pos  # 目标球在被吃时刻的位置
                b = mycell.pos
                c = forward(cell_time_needed, mycell, method='ignore_collision').pos  # 自己如果保持速度不变的位置
                dist1 = shortest_vec([a[0] - b[0], a[1] - b[1]])    # 扇形的两直边
                dist2 = shortest_vec([c[0] - b[0], c[1] - b[1]])
                a_b_theta = jia(dist1, dist2)   # 两边夹角
                find = True
                for enemy in allcells:
                    
                    for j in range(1, int(cell_time_needed) + 1):
                        if enemy.radius > 0.98 * mycell.radius and enemy.dead == False:
                            enemy_pos_at_j = forward(j, enemy, method='ignore_collision').pos
                            dist3 = shortest_vec([enemy_pos_at_j[0] - b[0], enemy_pos_at_j[1] - b[1]])
                            if jia(dist1, dist3) < a_b_theta and jia(dist2, dist3) < a_b_theta \
                                    and norm(dist3) < norm(dist1) + enemy.radius and norm(dist3) < norm(dist2) + enemy.radius: #夹角在两边之间且距离小于两边长
                                find = False
                                break  # 若存在一个enemy在移动过程中进入，则认为失败，重新找target，故两层break跳出
                    if not find:
                        break
                if find:
                    target_id = cell_i.id  # 这里先只写找到一个的，多个可以循环到底保存列表
                    target_available.append(cell_i)
                target_available = sorted([cell for cell in target_available], \
                                          key=lambda x: 1/x.radius*(distance(x,mycell)-x.radius-mycell.radius))
            return [cell.id for cell in target_available]
        
        
        def find_2(mycell, allcells,r_dist):
            if not r_dist:
                raise ValueError('Please enter the parameter r required for this method.')
            pre_selection = []
            r = r_dist
            while not pre_selection:
                pre_selection = [cell for cell in cell_alive \
                                    if cell.id != self.id and cell.id != rivalcell.id and \
                                    distance(cell,mycell)-cell.radius-mycell.radius <= r * mycell.radius]
                r += 1
            if r >= r_dist+2:
                return None
            
            
            target = sorted([cell for cell in pre_selection if cell in smaller_self], \
                            key = lambda x:(distance(x, mycell)-x.radius-mycell.radius))
            if not target:
                return None
            target_id = [cell.id for cell in target]
            return target_id
        
        def find_3(mycell,allcells):
            target_list = []
            for cells in smaller_self:
                if distance(cells,mycell)-mycell.radius-cells.radius<250:
                    for celll in larger_self:
                        a = shortest_vec([celll.pos[0] - mycell.pos[0], celll.pos[1] - mycell.pos[1]])
                        b = shortest_vec([cells.pos[0] - mycell.pos[0], cells.pos[1] - mycell.pos[1]])
                        if (perpendicular(shortest_vec_self(celll), mycell.pos, shortest_vec_self(cells)) < \
                            mycell.radius + 4*celll.radius \
                            and a[0] * b[0] + a[1] * b[1] > 0 and a[0] * b[0] + a[1] * b[1] < norm(b) ** 2):
                            break
                        
                    else:
                        target_list.append(cells)
            selected = []
            for target in target_list:
                mr = mycell.radius
                tr = target.radius
                mv = mycell.veloc
                tv = target.veloc
                rv = [mv[0]-tv[0],mv[1]-tv[1]]
                mp = mycell.pos
                tp = target.pos
                rp = shortest_vec([tp[0]-mp[0],tp[1]-mp[1]])
                d = norm(rp)
                rv_norm = norm(rv)
                theta = thet(rp,rv)
                if theta > math.pi/2 and theta < math.pi*3/2:
                    if norm(mycell.veloc) >10 and d/(mr+tr) > 3:
                        continue
                jiaj = jia(rp,rv)
                rv_rp = rv_norm*math.cos(jiaj)
                if rv_rp > 0:
                    time_estimated = max((d-mr-tr)/rv_rp - 2,0)
                else:
                    time_estimated = max(d-mr-tr-rv_rp,0)
                mass_before_eat = (0.99**time_estimated)*(mr**2)*math.pi
                mass_after_eat = mass_before_eat + tr**2*math.pi
                r_after_eat = math.sqrt(mass_after_eat/math.pi)
                if r_after_eat < mr:
                    continue
                else:
                    selected.append((target,r_after_eat))      
            selected.sort(key=lambda x:x[1])
            return [cell.id for cell,r in selected]


        def find(mycell, allcells, method='2',r_t=4,r_d=2):
            if method == '1':
                return find_1(mycell,allcells,r_t)
            elif method == '2':
                return find_2(mycell,allcells,r_d)
            elif method == '3':
                return find_3(mycell,allcells)
            else:
                raise ValueError('Method does not exist.')


        def eat(mycell,target,method='4'):
            if method == '1':
                return eat_1(mycell,target)
            elif method == '2':
                return eat_2(mycell,target)
            elif method == '3':
                return eat_3(mycell,target)
            elif method == '4':
                return eat_4(mycell,target)
            else:
                raise ValueError('Method does not exist.')
            #回归速度方向，借用？

        def eat_1(mycell,target):
            mv = mycell.veloc
            tv = target.veloc
            rv = [mv[0]-tv[0],mv[1]-tv[1]]
            mp = mycell.pos
            tp = target.pos
            rp = shortest_vec([tp[0]-mp[0],tp[1]-mp[1]])
            theta = thet(rp,rv)
            rv_norm = norm(rv)
            if rv_norm < 1:  # *************
                t = thet([0, 1], rp) + math.pi
                if t > 2*math.pi:
                    t -= 2*math.pi
                return t
            rv_rp = rv_norm*math.cos(theta)
            rv_rp_p = rv_norm*math.sin(theta)
            d = norm(rp)
            if rv_rp_p < 0:
                
                new_v_if_y = (abs(rv_rp_p)-0.01*delta_veloc)
                if new_v_if_y < 0:
                    anglea = thet([0,1],rp)
                    angleb= anglea-math.pi/2
                    angle = angleb-math.acos(abs(rv_rp_p)/(0.01*delta_veloc))
                    if angle < 0:
                        angle += 2*math.pi
                    return angle
            
                else:
                    anglea = thet([0,1],rp)
                    angle = anglea - math.pi/2
                    if angle < 0:
                        angle += 2*math.pi
                    return angle
            if rv_rp_p >= 0:
                
                new_v_if_y = (abs(rv_rp_p)-0.01*delta_veloc)
                if new_v_if_y < 0:
                    anglea = thet([0,1],rp)
                    angleb= anglea+math.pi/2
                    angle = angleb+math.acos(rv_rp_p/(0.01*delta_veloc))
                    if angle >= 2*math.pi:
                        angle -= 2*math.pi
                    return angle
            
                else:
                    anglea = thet([0,1],rp)
                    angle = anglea + math.pi/2
                    if angle >= 2*math.pi :
                        angle -= 2*math.pi
                    return angle
                
        def eat_2(mycell, target):  # return theta
            myVeloc = mycell.veloc  # veloc[v_x,v_y]
            myPos = mycell.pos  # pos[x, y]
            tarVeloc = target.veloc
            tarPos = target.pos
    # 计算myPos和tarPos的位置差与速度差
            difVeloc = [tarVeloc[0] - myVeloc[0], tarVeloc[1] - myVeloc[1]]  # difVeloc = [dif_x, dif_y]
            difPos = shortest_vec(tarPos[0] - myPos[0], tarPos[1] - tarPos[1])  # difPos = [dif_x, dif_y] 考虑穿屏量
    # 需要满足的方程: Dx/Dy = (5*sin theta - Vx)/(5*cos theta - Vy)
            t = round(difPos[0] / difPos[1],1)
            for theta in range(0, 2 * math.pi, 0.05):
                if t == round((5 * math.sin(theta) - difVeloc[0]) / (5 * math.cos(theta) - difVeloc[1]),1):
                    return theta

        def eat_3(sel, cel):  # 分段吃球函数
            def duan(t):  # duan即位所说的分段函数,duan(r1)为修正系数
                if t < 0.7:
                    return t ** 2
                else:
                    return t

            p1 = sel.pos
            p2 = cel.pos
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            a = [p2[0] - p1[0], p2[1] - p1[1]]
            a = shortest_vec(a)
            p2 = [p1[0] + a[0], p1[1] + a[1]]
            p3 = [p1[0] + v1[0], p1[1] + v1[1]]

            b = [p3[0] - p1[0], p3[1] - p1[1]]
            c = [p2[0] - p3[0], p2[1] - p3[1]]
            theta1 = thet([-v1[0], -v1[1]], c)
            # 在己方速度过小时不采用该吃球函数而是直接飞向目标，因为小速度意味着必须要考虑加速度的离散性，控制不好就会乱喷
            if norm(v1) < 2:  # *************
                return thet([0, 1], a) + math.pi

            if theta1 > math.pi:
                theta1 = theta1 - 2 * math.pi

            # 比
            r = abs(theta1 / math.pi)
            # r1为重要参数(函数参数)******************，不同的r1意味着不同的吃球速度和开销
            r1 = r
            theta = theta1 * duan(r1)
            m = thet([0, 1], [-v1[0], -v1[1]]) + theta + math.pi-0.3
            if m <0:
                m+=2*math.pi
            return m
        
        def eat_4(sel,cel):
            p1 = sel.pos
            p2 = cel.pos
            v1 = [sel.veloc[0] - cel.veloc[0], sel.veloc[1] - cel.veloc[1]]
            a = [p2[0] - p1[0], p2[1] - p1[1]]
            a = chuan(a)
            p2 = [p1[0] + a[0], p1[1] + a[1]]
            p3 = [p1[0] + v1[0], p1[1] + v1[1]]

            b = [p3[0] - p1[0], p3[1] - p1[1]]
            c = [p2[0] - p3[0], p2[1] - p3[1]]
            theta1 = thet([-v1[0], -v1[1]], c)
            if theta1 > math.pi:
                theta1 = theta1 - 2 * math.pi

            # r1为重要参数******************
            r = abs(theta1 / math.pi)

            r1 = r
            theta = theta1 * r1 ** 3
            return thet([0, 1], [-v1[0], -v1[1]]) + theta + math.pi
                
        f = 100       
        
        r1=mycell.radius


        all_cell_copy_for_iteration, dead_time, predator_id = prediction(f,allcells)

        #test passed

        
        k=1.5

        #优化1 先判断cell.dead
        #找出距离近的几个
        #test passed
        rivalcell_biggest_radius = (sum([cell.radius**2 for cell in smaller_rival])+rivalcell.radius**2)**(1/2)
        
        
        if mycell.radius >= rivalcell_biggest_radius:
            #如果自己比对手最大的可能半径大（此处的criterion可以修改）
            if not larger_self:
                #自己最大，就可以佛
                return None
            else:
                if dead_time:
                    return dodge(mycell,predator_id,closer_id)
                else:
                    return None
        closer_id = []
        closer = [cell.id for cell in larger_self if distance(cell,mycell) -cell.radius-mycell.radius < 5 and cell.dead == False]
        
        
        if closer:
            return dodge(mycell,closer,closer_id)
        
        if dead_time:
            #如果预测步数内因为predator_id死了，那就想办法躲掉！
            #test passed

            return dodge(mycell,predator_id,closer_id)   
            
        if type(all_cell_copy_for_iteration) == type([1,2,3]):
            for cell in all_cell_copy_for_iteration:
                if cell.id == self.id:
                    r2 = cell.radius
                    break
        else:
            r2 = all_cell_copy_for_iteration
    
        bigger = 0.05
        if r2 >= r1*(1+bigger):
            #不动有收益
            return None
        else:
            target_id = find(mycell, allcells) #test passed

            if not target_id:
                return None
            target_id = target_id[0]
            target=None
            for cell in allcells:
                
                if cell.id == target_id:
                    target = cell
                    break
            if (not target) or target.dead:
                return None
            return eat(mycell,target)   
        
        
   
        