from consts import Consts
import math
import world
from cell import Cell


def eject(allcells, theta):
    # Reduce force in proportion to area
    fx = math.sin(theta)
    fy = math.cos(theta)
    new_veloc_x = allcells[0].veloc[0] + Consts["DELTA_VELOC"] * fx * (1 - Consts["EJECT_MASS_RATIO"])
    new_veloc_y = allcells[0].veloc[1] + Consts["DELTA_VELOC"] * fy * (1 - Consts["EJECT_MASS_RATIO"])
    # Push player
    allcells[0].veloc[0] -= Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
    allcells[0].veloc[1] -= Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
    # Shoot off the expended mass in opposite direction
    newrad = allcells[0].radius * Consts["EJECT_MASS_RATIO"] ** 0.5
    # Lose some mass (shall we say, Consts["EJECT_MASS_RATIO"]?)
    allcells[0].radius *= (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5
    # Create new cell
    new_pos_x = allcells[0].pos[0] + fx * (allcells[0].radius + newrad)
    new_pos_y = allcells[0].pos[1] + fy * (allcells[0].radius + newrad)
    new_cell = Cell(len(allcells), [new_pos_x, new_pos_y], [new_veloc_x, new_veloc_y], newrad)
    new_cell.stay_in_bounds()
    new_cell.limit_speed()
    allcells.append(new_cell)


class State():
    def __init__(self, allcells):
        self.theta = 0
        self.dep = 1
        self.score = 0
        self.allcells = allcells

    def copy(self, other):
        self.theta = other.theta
        self.dep = other.dep
        self.score = other.score
        self.allcells = other.allcells

x = 1
class Player():
    def __init__(self, id, arg=None):
        self.id = id
        self.enemy_id = 1 - id
        self.n = 12

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
            dis = (px ** 2 + py ** 2) ** 0.05
            running_dis = dis - cell.radius - allcells[self.id].radius
            p.append([px, py, dis, cell.radius, running_dis])
        p.pop(self.id)
        return p

    def V(self, allcells):
        # 相对速度
        v0 = allcells[self.id].veloc
        v = [[cell.veloc[0] - v0[0], cell.veloc[1] - v0[1]] for cell in allcells]

        v.pop(self.id)
        return v

    def V_R(self, allcells):
        # 相对径向速度
        v_r = []
        for i in range(len(allcells) - 1):
            vel = self.V(allcells)[i][0] * self.P(allcells)[i][0] / self.P(allcells)[i][2] \
                  + self.V(allcells)[i][1] * self.P(allcells)[i][1] / self.P(allcells)[i][2]
            v_r.append(-vel)
        return v_r

    def V_T(self, allcells):
        # 相对切向速度
        v_t = []
        for i in range(len(allcells) - 1):
            vel = - self.V(allcells)[i][1] * self.P(allcells)[i][0] / self.P(allcells)[i][2] \
                  + self.V(allcells)[i][0] * self.P(allcells)[i][1] / self.P(allcells)[i][2]
            v_t.append(vel)
        return v_t

    def section(self, allcells, n=4):
        # 把每个cell分到不同的区域，并且按照和我的距离从小到大排序
        self.n = n
        sectionList = [[] for i in range(n)]
        for i in range(len(allcells) - 1):  # 将每一个cell（除了自己）按幅角分区，每个区域就是一个数组，每个cell的各种信息就是这个数组中的一个元素？
            temp = self.P(allcells)[i]
            temp.append(self.V_R(allcells)[i])
            temp.append(self.V_T(allcells)[i])
            if self.P(allcells)[i][0] > 0:
                theta = math.atan(self.P(allcells)[i][1] / self.P(allcells)[i][0])
                m = int(theta * n // (2 * math.pi))
                if m > 0 or m==0:
                    sectionList[m].append(temp)
                elif m<0 and m>-n:
                    sectionList[m + n].append(temp)
            elif self.P(allcells)[i][0] < 0:
                theta = math.atan(self.P(allcells)[i][1] / self.P(allcells)[i][0]) + math.pi / 2
                m = int(theta * n // (2 * math.pi))
                if m > 0 or m == 0:
                    sectionList[m].append(temp)
                elif m < 0 and m > -n:
                    sectionList[m + n].append(temp)
            elif self.P(allcells)[i][1] > 0:
                sectionList[0].append(temp)
            else:
                sectionList[int(n / 2)].append(temp)
        for sec in sectionList:  # 将每个section中的cell按distance-radius排序
            sec.sort(key=lambda factor: factor[4])
        return sectionList

    def sect(self, p_others):
        # 给出x,y坐标，确定质心属于哪个section
        n = self.n
        if p_others[0] > 0:
            theta = math.atan(p_others[1] / p_others[0])
            m = theta * n // (2 * math.pi)
            if m > 0 or m==0:
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

    def chasing_enemy(self, allcells, delta_v=1, delta_p=1):
        # 决定要不要直接追敌人，只有当我和他连线上没有捕食者，并且他就算把比他跑得慢的小球全吃了也没我大才追
        # delta_v 和 p是考虑误差玄学调参
        if allcells[self.id].radius <= allcells[self.enemy_id].radius:
            return False
        choosing_cells = []
        n = self.n
        delta_section=min(n/2,3)
        section_enemy = self.sect(self.P(allcells)[0])
        for j in range(int(section_enemy - delta_section),int(section_enemy - delta_section + 1)):
            for cell in self.section(allcells)[j]:
                choosing_cells.append(cell)
        tempted_myr = allcells[self.id].radius
        tempted_enr = allcells[self.enemy_id].radius
        while tempted_myr > tempted_enr:
            for cell in choosing_cells:
                v_d = self.vertical_distance(self.P(allcells)[0], cell)
                p_d = self.parallel_distance(self.P(allcells)[0], cell)
                if v_d <= cell[3] + allcells[self.id].radius + delta_v and \
                        p_d <= cell[3] - allcells[self.enemy_id].radius + self.P(allcells)[0][2] + delta_p:
                    if cell[3] > allcells[self.id].radius:
                        # 如果有比我还大的在我和敌人的道路中间
                        return False
                    else:
                        # 如果是个小的，判断这位终将被谁吃掉
                        # 严格一点，只有向我走来比敌人向我走来更快的会被我吃掉
                        if cell[-2] > self.V_R(allcells)[0]:
                            tempted_myr = (tempted_myr ** 2 + cell[3] ** 2) ** 0.5
                        else:
                            tempted_enr = (tempted_enr ** 2 + cell[3] ** 2) ** 0.5
        if tempted_myr > tempted_enr:
            return True
        return False

    def worth(self, allcells, s1, s2, s3, s4, s5, c, d1, d2):
        # 算每个区域离我最近的两个球的权重
        # 比我小的的权重正比于其面积，对他到我的时间平方指数下降（他越难到达我权重越小）
        # 比我大的权重为-，对他到我的时间平方是指数下降
        # 第一圈整体权重比第二圈大
        # 如果可以直接追敌人，加一个很大很大的权重，这个权重也有和时间相关指数加权
        #
        # 算法其实有问题，再议
        print('哈哈哈')
        W1 = 0  # 第一圈的分数和
        W2 = 0  # 第二圈的分数和
        w1 = 0
        w2 = 0
        n = self.n
        W_chase = 100
        sectionList = self.section(allcells, n)
        for i in range(n):
            if len(sectionList[i])>0:
                cell1 = sectionList[i][0]
                if cell1[3] < allcells[self.id].radius * 0.9 and cell1[-2] > 0:
                    w1 = cell1[3] * cell1[3] * math.exp(-(cell1[4] / (cell1[-2] * s1)))
                elif cell1[3] < allcells[self.id].radius * 0.9 and cell1[-2] < 0:
                    w1 = d1 * cell1[3] * cell1[3] * math.exp((cell1[4] / (cell1[5] * s1)))
                elif cell1[3] > allcells[self.id].radius * 0.9 and cell1[-2] > 0:
                    w1 = -math.exp(-(cell1[4] / (cell1[-2] * s2)) ** 2)
                W1 += w1
                if len(sectionList[i]) > 1:
                    cell2 = sectionList[i][1]
                    if cell2[-1] * cell1[-1] <= 0:
                        if cell2[3] < allcells[self.id].radius * 0.9 and cell2[-2]:
                            w2 = cell2[3] * cell2[3] * math.exp(-(cell2[4] / (cell2[-2] * s3)) ** 2)
                        elif cell2[3] < allcells[self.id].radius * 0.9 and cell2[-2] < 0:
                            w2 = d2 * cell2[3] * cell2[3] * math.exp((cell2[4] / (cell2[-2] * s2)))
                        elif cell2[3] > allcells[self.id].radius * 0.9 and cell2[-2] > 0:
                            w2 = -math.exp(-(cell2[4] / (cell2[-2] * s4)) ** 2)
                        W2 += w2
        W3 = 0
        if self.chasing_enemy(allcells):
            W3 += W_chase * math.exp(s5 * self.V_R(allcells)[0])
        return c * W1 + W2 + W3
    '''
    def strategy(self, allcells):
        q = []
        finalq = []
        q.append(State(allcells))
        q = sorted(q, key=lambda cell: cell.score)
        # 拿出分最高的/拿出第一个
        q1 = q.pop()
        depth = 0
        while depth < 3:

            for i in range(0, 360, 30):
                temp = State(None)
                temp.copy(q1)
                if q1.dep == 1:
                    temp.theta = i
                tempcell = allcells.copy()
                eject(tempcell, (i / 180.0) * math.pi)
                #print(len(tempcell))
                for cell in tempcell:
                    #print(len(tempcell), '----------',len(q),'---------', depth)
                    if cell.id == 0:
                        continue
                    cell.move(1)
                temp.allcells = tempcell.copy()
                # temp.score = self.worth(temp.allcells, s1=1, s2=1, s3=1, s4=1, s5=1, c=1, d1=1, d2=1)
                # 考虑母节点的评估，最后得到的是一个对整体过程的评估分
                # temp.score += q1.score

                q.append(temp)
                # 每放进去一个 还是按分从小到大排
                q = sorted(q, key=lambda state: state.score)
                # 最终状态
                if depth == 3:
                    finalq.append(temp)
                    finalq = sorted(finalq, key=lambda cell: cell.score)
            # 每次拿最后一个出来，用完就删掉
            q1 = q.pop()
            depth += 1
        if len(finalq) > 0:
            return finalq[-1].theta
        else:
            return 3
    '''
    def strategy(self, allcells):
        return 1
    





