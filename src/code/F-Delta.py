from consts import Consts
from cell import Cell
import math


class Player():
    def __init__(self, id, arg=None):
        self.id = id

    def watch_allcells(self, allcells):
        # 先得到自己的cell的一些参数，半径，速度，位置
        myradius = allcells[self.id].radius
        myveloc = allcells[self.id].veloc
        mypos = allcells[self.id].pos

        # watch_distance是探测距离
        bigger_cells = []
        danger_cells = []  # 存放有威胁的cell，不包含自己
        food_cells = []  # 存放可吃的cell，不包含自己
        food_cells2 = []
        watch_distance = 250 - len(allcells)  # 选定探测距离与cell的数量负相关且最大为250
        move_x = Consts["WORLD_X"] * 0.5 - mypos[0]  # 使自己处于中央所需的坐标平移量
        move_y = Consts["WORLD_Y"] * 0.5 - mypos[1]
        # 遍历allcells，在检测范围内得到bigger_cells,smaller_cells,danger_cells,food_cells
        for i in allcells:
            if i.radius > myradius:
                bigger_cells.append(i)  # 不包含自己

            # 每一步都需要考虑跨界情况
            if allcells[self.id].distance_from(i) < watch_distance:  # 只考虑检测范围内的cell
                temp_pos = [i.pos[0] + move_x, i.pos[1] + move_y]
                if temp_pos[0] < 0:
                    temp_pos[0] += Consts["WORLD_X"]
                elif temp_pos[0] > Consts["WORLD_X"]:
                    temp_pos[0] -= Consts["WORLD_X"]

                if temp_pos[1] < 0:
                    temp_pos[1] += Consts["WORLD_Y"]
                elif temp_pos[1] > Consts["WORLD_Y"]:
                    temp_pos[1] -= Consts["WORLD_Y"]

                dx = Consts["WORLD_X"] * 0.5 - temp_pos[0]
                dy = Consts["WORLD_Y"] * 0.5 - temp_pos[1]
                dp = (dx ** 2 + dy ** 2) ** 0.5  # 两cell圆心距离
                dp_theta = math.atan2(dx, dy)  # 由i指向自己的向量的角度

                v = ((i.veloc[0] - myveloc[0]) ** 2 + (i.veloc[1] - myveloc[1]) ** 2) ** 0.5  # i相对自己，其速度的大小
                v_theta = math.atan2(i.veloc[0] - myveloc[0], i.veloc[1] - myveloc[1])  # i相对自己，其速度的指向

                d_theta = min(abs(dp_theta - v_theta), 2 * math.pi - abs(dp_theta - v_theta))  # 上述两者的夹角
                min_dp = dp - myradius - i.radius  # 两cell最近距离
                # 有把自己吞噬的可能的cell
                if i.radius > myradius:
                    t = max(0.4 * i.radius, myradius)
                    if (d_theta < math.pi / 2 and math.sin(d_theta) * dp <= i.radius + myradius) or min_dp < t:
                        danger_cells.append([i, min_dp, dp_theta, v])
                # 在自己半径的0.35到0.85倍的cell中找food_cells
                elif myradius * 0.35 < i.radius < myradius * 0.85:
                    if d_theta < math.pi / 2 and math.sin(d_theta) * dp <= i.radius + 3 * myradius:

                        # 检查是否需要小做调整
                        if math.sin(d_theta) * dp < (i.radius + myradius):
                            move_or_not = None
                        else:
                            move_or_not = True
                        # 把cell，用时，否需要小做调整，相对位置的指向，相对速度的指向存到food_cells
                        food_cells.append([i, min_dp, move_or_not, dp_theta, v_theta, v])
                    # 把在自己附近且相对速度较小的cell存到 food_cells2，参数都可调
                    elif min_dp < watch_distance * 0.5 and (v < 0.5 or min_dp < 5 - v):
                        food_cells2.append([i, dp, min_dp, dp_theta, v_theta])

        return bigger_cells, danger_cells, food_cells, food_cells2

    def escape_danger(self, cells_list):
        the_cell = sorted(cells_list, key=lambda x: x[1])[0]  # 得到有威胁cell中最近的那一个
        except_distance = 15 + the_cell[0].radius * 0.4 + 20 * the_cell[3]
        if the_cell[1] < except_distance:  # 当距离足够小时启动喷射，进行逃离
            return the_cell[2] + math.pi
        else:
            return None

        # 对于朝自己运动的可吃cell

    def eat_food(self, food_cells, food_cells2, bigger_cells, allcells):
        if len(food_cells) == 0 and len(food_cells2) == 0:
            return None
        elif len(food_cells) != 0 and len(food_cells2) == 0:
            the_cell = sorted(food_cells, key=lambda x: x[0].radius)[-1]  # 得到最大的那一个作为吞噬目标
            if the_cell[2]:  # 需要做小调整
                t = 2 * the_cell[3] - the_cell[4]  # 这个角度只是大致的，并非精确计算得到
                return t if self.foresee(allcells, bigger_cells, the_cell[0]) else None
            else:
                t = the_cell[3]
                if the_cell[5] < 0.75:
                    return t if self.foresee(allcells, bigger_cells, the_cell[0]) else None
                else:
                    return None
        elif len(food_cells) == 0 and len(food_cells2) != 0:
            the_cell2 = sorted(food_cells2, key=lambda x: x[0].radius)[-1]  # 得到最大的那一个
            t = the_cell2[3]

            return t if self.foresee(allcells, bigger_cells, the_cell2[0]) else None
        else:
            the_cell = sorted(food_cells, key=lambda x: x[0].radius)[-1]
            the_cell2 = sorted(food_cells2, key=lambda x: x[0].radius)[-1]
            if the_cell[0].radius < the_cell2[0].radius:  # 得到最大的那一个
                t = the_cell2[3]

                return t if self.foresee(allcells, bigger_cells, the_cell2[0]) else None

            else:
                if the_cell[2]:  # 需要做小调整
                    t = 2 * the_cell[3] - the_cell[4]  # 这个角度只是大致的，并非精确计算得到
                    return t if self.foresee(allcells, bigger_cells, the_cell[0]) else None
                else:
                    t = the_cell[3]
                    if the_cell[5] < 0.75:
                        return t if self.foresee(allcells, bigger_cells, the_cell[0]) else None
                    else:
                        return None
    # 定义一个预判危险函数
    def foresee(self, allcells, bigger_cells, cell):
        t = True
        for i in bigger_cells:
            if allcells[self.id].distance_from(i) + cell.distance_from(i) < 1.5 * allcells[self.id].distance_from(cell):
                if cell.distance_from(i) < allcells[self.id].distance_from(cell):
                    t = False
        return t

    def strategy(self, allcells):
        bigger_cells, threat_list, food_list, food_list2 = self.watch_allcells(allcells)
        if len(threat_list) != 0:  # 有威胁时
            result = self.escape_danger(threat_list)
            if result != None:  # 需要逃离时
                return result

        # 若上面未通过返回参数而结束，则继续下面代码
        return self.eat_food(food_list, food_list2, bigger_cells, allcells)