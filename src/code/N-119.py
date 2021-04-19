from consts import Consts
import math
import world
from cell import Cell
import copy
import random

class Player():
    def __init__(self, id, args= None):
        self.id = id
        self.enemy_id = 1 - id
        self.n = 12
        self.v0 = Consts["DELTA_VELOC"]/99
        self.args = args

    def V_theta(self,allcells):
        Vx=allcells[self.id].veloc[0]
        Vy = allcells[self.id].veloc[1]
        if Vx != 0:
            theta = math.atan(Vy / Vx)
            if Vx < 0:
                theta += math.pi
        else:
            if Vy > 0:
                theta = math.pi / 2
            else:
                theta = -math.pi / 2
        return -theta-math.pi/2

    def P(self, allcells):
        # 在考虑出框的情况下算出每个点的相对位置、半径等
        p0 = allcells[self.id].pos
        p = []
        for cell in allcells:
            dx, dy = cell.pos[0] - p0[0], cell.pos[1] - p0[1]
            px, py = dx, dy
            if abs(dx) > abs(dx - Consts["WORLD_X"]):
                px = dx - Consts["WORLD_X"]
            if abs(dx) > abs(dx + Consts["WORLD_X"]):
                px = dx + Consts["WORLD_Y"]
            if abs(dy) > abs(dy - Consts["WORLD_Y"]):
                py = dy - Consts["WORLD_Y"]
            if abs(dy) > abs(dy + Consts["WORLD_Y"]):
                py = dy + Consts["WORLD_Y"]
            dis = math.sqrt(px ** 2 + py ** 2)
            running_dis = dis - cell.radius - allcells[self.id].radius
            p.append([px, py, dis, cell.radius, running_dis])
        p.pop(self.id)
        return p

    def clear(self, allcells):
        output = []
        r0 = allcells[self.id].radius * 0.6
        output.append(allcells.pop(0))
        output.append(allcells.pop(0))
        while allcells:
            cell = allcells.pop()
            if cell.radius > r0:
                output.append(cell)
        return output

    def V(self, allcells):
        # 相对速度
        v0 = allcells[self.id].veloc
        v = [[cell.veloc[0] - v0[0], cell.veloc[1] - v0[1]] for cell in allcells]
        v.pop(self.id)
        return v

    def V_R(self, allcells):
        # 相对径向速度
        v_r = []
        p_allcells = self.P(allcells)
        v_allcells = self.V(allcells)
        for i in range(len(allcells) - 1):
            vel = v_allcells[i][0] * p_allcells[i][0] / p_allcells[i][2] \
                  + v_allcells[i][1] * p_allcells[i][1] / p_allcells[i][2]
            v_r.append(-vel)
        return v_r

    def V_T(self, allcells):
        # 相对切向速度
        v_t = []
        p_allcells = self.P(allcells)
        v_allcells = self.V(allcells)
        for i in range(len(allcells) - 1):
            vel = - v_allcells[i][1] * p_allcells[i][0] / p_allcells[i][2] \
                  + v_allcells[i][0] * p_allcells[i][1] / p_allcells[i][2]
            v_t.append(vel)
        return v_t

    def section(self, allcells):
        # 把每个cell分到不同的区域，并且按照和我的距离从小到大排序
        n = self.n
        p_allcells = self.P(allcells)
        sectionList = [[] for i in range(n)]
        for i in range(len(p_allcells)):  # 将每一个cell（除了自己）按幅角分区，每个区域就是一个数组，每个cell的各种信息就是这个数组中的一个元素？
            temp = p_allcells[i]
            y = temp[1]
            x = temp[0]
            temp.append(self.V_R(allcells)[i])
            temp.append(self.V_T(allcells)[i])
            if x != 0:
                theta = math.atan(y / x)
                if x < 0:
                    theta += math.pi
            else:
                if y > 0:
                    theta = math.pi / 2
                else:
                    theta = -math.pi / 2
            m = int(theta * n / (2 * math.pi))
            sectionList[m].append(temp)
        for sec in sectionList:  # 将每个section中的cell按distance-radius排序
            sec.sort(key=lambda factor: factor[-3])
        return sectionList

    def sect(self, p_others):
        # 给出x,y坐标，确定质心属于哪个section
        n = self.n
        if p_others[0] > 0:
            theta = math.atan(p_others[1] / p_others[0])
            m = theta * n // (2 * math.pi)
            if m > 0 or m == 0:
                return m
            elif m < 0 and m > -n:
                return m + n
        elif p_others[0] < 0:
            theta = math.atan(p_others[1] / p_others[0])
            m = theta * n // (2 * math.pi)
            return m + n / 2
        elif p_others[1] > 0:
            return 0
        else:
            return n / 2

    def vertical_distance(self, p_enemy, p_other):
        # 某一点到我和敌人连线的垂直距离
        return abs((p_enemy[1] * p_other[0] - p_enemy[0] * p_other[1]) / p_enemy[2])

    def parallel_distance(self, p_enemy, p_other):
        # 某一点到我和敌人连线的平行距离
        return abs((p_enemy[1] * p_other[1] + p_enemy[0] * p_other[0]) / p_enemy[2])

    def chasing_someone(self, target, allcells, sectionList, delta_v=10, delta_p=10):
        # 决定要不要直接追敌人，只有当我和他连线上没有捕食者，并且他就算把比他跑得慢的小球全吃了也没我大才追
        # delta_v 和 p是考虑误差玄学调参
        if allcells[self.id].radius * 0.95 <= target[3]:
            return False
        choosing_cells = []
        n = self.n
        delta_section = n/4
        section_target = self.sect(target)
        smallest_section = int(section_target - delta_section)
        if smallest_section<0: smallest_section += n
        biggest_section = int(section_target + delta_section + 1)
        if biggest_section > n: biggest_section -= n
        for j in range(smallest_section, biggest_section):
            for cell in sectionList[j]:
                choosing_cells.append(cell)
        tempted_myr = allcells[self.id].radius * 0.95
        tempted_tgr = target[3]
        for cell in choosing_cells:
            if tempted_tgr >= tempted_myr:
                return False
            v_d = self.vertical_distance(target, cell)
            p_d = self.parallel_distance(target, cell)
            if v_d <= cell[3] + allcells[self.id].radius + delta_v and \
                    p_d <= cell[3] - target[3] + target[2] + delta_p:
                if cell[3] > allcells[self.id].radius * 0.95:
                    # 如果有比我还大的在我和敌人的道路中间
                    return False
                else:
                    # 如果是个小的，判断这位终将被谁吃掉
                    # 严格一点，只有向我走来比敌人向我走来更快的会被我吃掉
                    if cell[-2] > target[-2]:
                        tempted_myr = math.sqrt(tempted_myr ** 2 + cell[3] ** 2)
                    else:
                        tempted_tgr = math.sqrt(tempted_tgr ** 2 + cell[3] ** 2)
        if tempted_myr > tempted_tgr:
            return True
        return False

    def chase_someone(self, target, r0):
        x = target[0]
        y = target[1]
        if x != 0:
            theta_0 = math.atan(y / x)
            if x < 0:
                theta_0 += math.pi
        else:
            if y > 0:
                theta_0 = math.pi / 2
            else:
                theta_0 = -math.pi / 2
        for f in range(1,6):
            a = self.caculate_theta(f, r0, target)
            if a == 'wrong':
                continue
            temp_theta = theta_0 - math.atan2(a[0], a[1])
            temp_vr = math.cos(temp_theta) * x + math.sin(temp_theta) * y
            if temp_vr > 0:
                temp_theta += math.pi
            return -temp_theta + 1 * math.pi / 2
        return 'wrong'

    def caculate_theta(self, f, r, otherCell):
        v0 = f * self.v0
        r0 = r*0.9 + otherCell[3]
        dis = otherCell[2]
        vr = otherCell[-2]
        vt = otherCell[-1]
        v = math.sqrt(vr ** 2 + vt ** 2)
        tmp = vr * dis + v0 * r0
        delta = 4 * (v0 ** 2 * r0 ** 2 + v0 ** 2 * dis ** 2 + 2 * vr * v0 * dis * r0 - vt ** 2 * dis ** 2)
        if v == v0 and tmp > 0:
            t = dis ** 2 / (2 * tmp)
        elif v == v0 and tmp <= 0:
            return 'wrong'
        elif v != v0:
            if delta >= 0:
                t1 = (tmp + math.sqrt(delta / 4)) / (v ** 2 - v0 ** 2)
                t2 = (tmp - math.sqrt(delta / 4)) / (v ** 2 - v0 ** 2)
                if t1 < 0:
                    t1 = 10000
                if t2 < 0:
                    t2 = 10000
                t = min(t1, t2)
            elif delta < 0:
                return 'wrong'
        return [vt * t, dis - vr*t]

    def already_enough(self,allcells,time):
        stop=False
        myr = allcells[self.id].radius
        p = self.P(allcells)
        v = self.V(allcells)
        for i in range(len(p)):
            x = p[i][0]
            y = p[i][1]
            vx = v[i][0]
            vy = v[i][1]
            hisr = p[i][3]
            if hisr < myr * 0.95:
                if math.sqrt(vx ** 2 + vy ** 2) != 0:
                    d = (y - x * (vy / vx)) * (vx / math.sqrt(vx ** 2 + vy ** 2))
                    if abs(d) < myr + hisr:
                        t = -((x * vx + y * vy) + math.sqrt(
                            ((x * vx + y * vy) ** 2) - (vx ** 2 + vy ** 2) * (x ** 2 + y ** 2 - (myr + hisr) ** 2))) / (
                                        vx ** 2 + vy ** 2)
                        # t = (x*vx+y*vy)/math.sqrt(vx**2+vy**2)
                        # t = -((x * vx + y * vy) + math.sqrt((myr+hisr)**2-d**2))/ (vx ** 2 + vy ** 2)
                        if t>=0 and t<=time:
                            print("enough!!")
                            stop=True
        return stop

    def chasing_enemy(self, allcells, sectionList, delta_v=20, delta_p=10):
        if allcells[self.id].radius*0.9 <= allcells[self.enemy_id].radius:
            return False
        choosing_cells = []
        n = self.n
        delta_section=n/4
        p_allcells = self.P(allcells)
        section_enemy = self.sect(p_allcells[0])
        smallest_section = int(section_enemy - delta_section)
        if smallest_section<0: smallest_section += n
        biggest_section = int(section_enemy + delta_section + 1)
        if biggest_section>n: biggest_section -= n
        for j in range(smallest_section, biggest_section):
            for cell in sectionList[j]:
                choosing_cells.append(cell)
        tempted_myr = allcells[self.id].radius*0.9
        tempted_enr = allcells[self.enemy_id].radius
        for cell in choosing_cells:
            if tempted_enr >= tempted_myr:
                return False
            v_d = self.vertical_distance(p_allcells[0], cell)
            p_d = self.parallel_distance(p_allcells[0], cell)
            if v_d <= cell[3] + allcells[self.id].radius + delta_v and \
                    p_d <= cell[3] + p_allcells[0][2] + delta_p:
                if cell[3] > allcells[self.id].radius*0.9:
                    # 如果有比我还大的在我和敌人的道路中间
                    return False
                else:
                    # 如果是个小的，判断这位终将被谁吃掉
                    # 严格一点，只有向我走来比敌人向我走来更快的会被我吃掉
                    if cell[-2] > self.V_R(allcells)[0]:
                        tempted_myr = math.sqrt(tempted_myr ** 2 + cell[3] ** 2)
                    else:
                        tempted_enr = math.sqrt(tempted_enr ** 2 + cell[3] ** 2)
        if tempted_myr > tempted_enr:
            return True
        return False

    def chase_enemy(self, allcells):
        x = self.P(allcells)[0][0]
        y = self.P(allcells)[0][1]
        target = [x, y, self.P(allcells)[0][2], self.P(allcells)[0][3], self.P(allcells)[0][4]]
        target.append(self.V_R(allcells)[0])
        target.append(self.V_T(allcells)[0])
        if x != 0:
            theta_0 = math.atan(y / x)
            if x < 0:
                theta_0 += math.pi
        else:
            if y > 0:
                theta_0 = math.pi / 2
            else:
                theta_0 = -math.pi / 2
        for f in range(1, 6):
            a = self.caculate_theta(f, allcells[self.id].radius, target)
            if a == 'wrong':
                continue
            temp_theta = theta_0 - math.atan2(a[0], a[1])
            temp_vr = math.cos(temp_theta) * x + math.sin(temp_theta) * y
            if temp_vr > 0:
                temp_theta += math.pi
            return -temp_theta + 1 * math.pi / 2
        return 'wrong'

    def  escape_onecell(self, nearest):
        print("jytescaping")
        if nearest!=None:
            print("I am gonna run")
            x=nearest[0]
            y=nearest[1]
            if x!=0:
                theta_0 = math.atan(y / x)
                if x<0:
                   theta_0 += math.pi
            else:
                if y>0:
                    theta_0 = math.pi/2
                else:
                    theta_0 = -math.pi/2
            return -theta_0 + math.pi / 2
        else:
            return None

    def escaping(self, allcells):
        myr = allcells[self.id].radius*1.1
        p = self.P(allcells)
        v = self.V(allcells)
        bigmoster = []
        for i in range(len(p)):
            x = p[i][0]
            y = p[i][1]
            vx = v[i][0]
            vy = v[i][1]
            hisr = p[i][3]*1.1
            if hisr>myr*0.95:
                if math.sqrt(vx ** 2 + vy ** 2) != 0:
                    d = (y*vx - x * vy) / math.sqrt(vx ** 2 + vy ** 2)
                    if abs(d) < myr + hisr:
                        t = -((x * vx + y * vy)+math.sqrt(((x * vx + y * vy)**2)-(vx ** 2 + vy ** 2)*(x**2+y**2-(myr+hisr)**2))) / (vx ** 2 + vy ** 2)
                        #t = (x*vx+y*vy)/math.sqrt(vx**2+vy**2)
                        #t = -((x * vx + y * vy) + math.sqrt((myr+hisr)**2-d**2))/ (vx ** 2 + vy ** 2)
                        cell = p[i] + v[i]
                        cell.append(t)
                        print(t)
                        if t>=0:
                            bigmoster.append(cell)
        bigmoster.sort(key=lambda factor: factor[-1])
        if len(bigmoster) > 0:
            biggestmonster = bigmoster[0]
            x0 = biggestmonster[0]
            y0 = biggestmonster[1]
            r=biggestmonster[3]
            t = abs(biggestmonster[-1])
            vx = biggestmonster[-3]
            vy = biggestmonster[-2]
            new_x = x0 + t * vx
            new_y = y0 + t * vy
            biggestmonster[0] = new_x
            biggestmonster[1] = new_y
            print(t)
            print(x0,y0)
            if t<=100:
                print("gonna run")
                return biggestmonster
        else:
            return None

    def strategy(self, allcells):
        print(allcells[self.id].radius, 'radius')
        allcells = self.clear(allcells)
        #eatingme=self.ones_eatingme(allcells)
        sectionList = self.section(allcells)
        #sectionList1=self.section(eatingme)
        #print(len(eatingme))
        escaping = self.escaping(allcells)
        if escaping != None:
            print("time to run")
            return self.escape_onecell(escaping)
        if self.chasing_enemy(allcells, sectionList) and self.P(allcells)[0][4]<= 7*allcells[self.id].radius:
            if allcells[self.id].radius<40:
                x=self.chase_enemy(allcells)
                if x != 'wrong':
                    return x
        if self.already_enough(allcells, 50):
            return None
        targets = []
        for sections in sectionList:
            for cell in sections:
                if cell[4] <= 6 * allcells[self.id].radius and cell[3] <= allcells[self.id].radius * 0.95:
                    targets.append(cell)
        targets.sort(key=lambda factor: factor[4])
        for target in targets:
            if not self.chasing_someone(target, allcells, sectionList):
                continue
            a = self.chase_someone(target, allcells[self.id].radius)
            if a != 'wrong':
                print('eat')
                return a
        return None