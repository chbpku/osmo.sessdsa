from cell import Cell
from consts import Consts
from math import *


class Player:

    def __init__(self, id, arg=None):
        # 记录我方和对手的id
        self.id, self.enemy_id = id, 1 - id
        # 存储主目标和次级目标
        self.target = self.sub_target = None
        # 警惕状态
        self.alert = False
        # 是否主动进攻判定(最终没有采用)
        # self.attack = False

    def strategy(self, allcells):

        # 参数表
        Parameter = {
            # //////////////////////////////
            'DISADVANTAGE_RATIO': 0.99,  # 劣势敌我半径比值
            'ADVANTAGE_RATIO': 0.95,  # 优势敌我半径比值
            # //////////////////////////////
            'HOSTILE_DANGER_GAP': 20,  # 敌方危险间隔
            'HOSTILE_DANGER_REACT_TIME': 55,  # 敌方危险反应时间
            # //////////////////////////////
            'CERTAIN_ABSORB_DEPTH': 3,  # 确认陷入深度
            'DANGER_RADIUS_RATIO': 0.99,  # 危险半径比值
            'DANGER_GAP': 20,  # 危险间隔
            'DANGER_REACT_TIME': 50,  # 危险反应时间
            # //////////////////////////////
            'TARGET_AWAY_TOLERANCE': 0.5,  # 目标径向速度的最大容忍值
            'TARGET_LOW_TOLERANCE': 0.2,  # 目标半径比值的最小容忍值
            'TARGET_GAP_TOLERANCE': 190,  # 目标间隔的最大容忍值
            'SUB_TARGET_AWAY_TOLERANCE': 0.1,  # 次级目标径向速度的最大容忍值
            'SUB_TARGET_LOW_TOLERANCE': 0.1,  # 次级目标半径比值的最小容忍值
            'SUB_TARGET_GAP_TOLERANCE': 120,  # 次级目标间隔的最大容忍值
            # //////////////////////////////
            'EAT_LOW_RATIO': 0.2,  # 选定目标的最低半径比值
            'EAT_HIGH_RATIO': 0.98,  # 选定目标的最高半径比值
            'SEARCH_TARGET_GAP': 120,  # 搜索目标的间隔范围
            'NEIGHBOR_PREY_GAP': 30,  # 绝对邻近间距
            'SUB_TARGET_DEGREE': 40,  # 选定次级目标的相对速度与径向矢量夹角
            'EAT_NEIGHBOR_LOW_RATIO': 0.2,  # 选定绝对邻近目标的最小半径
            'SECOND_GAP':  150,  # 目标周围多次碰撞的间距搜索范围
            # //////////////////////////////
            'EVEN_EAT_TIME_LIMIT':  200,  # 均势限定的吃球时间
            'DISADVANTAGE_EAT_TIME_LIMIT':  200,  # 劣势限定的吃球时间
            'ADVANTAGE_EAT_TIME_LIMIT':  300,  # 优势限定的吃球时间
            'EAT_FORCE_TIME': 150,  # 强迫进食时间
            # //////////////////////////////
            'ATTACK_ABLE_GAP': 100,  # 可以发起进攻的间隔
            'ATTACK_DEGREE': 15,  # 可以发起进攻的相对速度与径向矢量的最大夹角
        }

        # 形势分析
        def situation_assess():
            ratio = allcells[self.enemy_id].radius / allcells[self.id].radius
            if ratio > Parameter['DISADVANTAGE_RATIO']:
                return -1  # 劣势
            elif ratio < Parameter['ADVANTAGE_RATIO']:
                return 1  # 优势
            else:
                return 0  # 均势

        # ==============================================================================================================
        # ==================================================基本数学函数==================================================
        # ==============================================================================================================

        def land_angle(angle):  # 将角度缩至0～2*pi的范围
            k = angle // (2 * pi)
            return angle - 2 * k * pi

        def rev_angle(angle):  # 角度反向
            return land_angle(angle + pi)

        def angle_dif_abs(angle1, angle2):  # 角度绝对差
            dif = angle1 - angle2
            if abs(dif) >= pi:
                dif = 2 * pi - abs(dif)
            return abs(dif)

        def magnitude(v):  # 向量模长
            return sqrt(v[0] ** 2 + v[1] ** 2)

        def argument(v):  # 向量辐角
            radius = sqrt(v[0] ** 2 + v[1] ** 2)
            if v[0] >= 0:
                theta = acos(v[1] / radius)
            else:
                theta = 2 * pi - acos(v[1] / radius)
            return theta

        def polar_to_xy(polar):  # 极坐标转为x-y坐标
            x = polar[0] * sin(polar[1])
            y = polar[0] * cos(polar[1])
            return [x, y]

        def xy_to_polar(v):  # x-y坐标转为极坐标
            return [magnitude(v), argument(v)]

        def vec_addition(v1, v2):  # 向量加法
            return [v1[0] + v2[0], v1[1] + v2[1]]

        def vec_negative(v):  # 负向量
            return [-v[0], -v[1]]

        def num_product(t, v):  # 向量数乘
            return [t * v[0], t * v[1]]

        def inner_product(v1, v2):  # 向量内积
            return v1[0] * v2[0] + v1[1] * v2[1]

        def dot_line_perpvec(r_pos, vec):
            # 点到直线的垂直向量，点在向量r_pos的起点，直线经过r_pos终点，方向为vec，输出与r_pos量纲一致的向量
            t = - inner_product(r_pos, vec) / inner_product(vec, vec)
            return vec_addition(r_pos, num_product(t, vec))

        def dot_line_distance(r_pos, vec):
            # dot_line_perpvec的模长
            return magnitude(dot_line_perpvec(r_pos, vec))

        def pull_back(pos):
            # 对于穿屏的坐标将其拉回
            # x方向
            if pos[0] < 0:
                pos[0] += Consts['WORLD_X']
            elif pos[0] > Consts['WORLD_X']:
                pos[0] -= Consts['WORLD_X']
            # y方向
            if pos[1] < 0:
                pos[1] += Consts['WORLD_Y']
            elif pos[1] > Consts['WORLD_Y']:
                pos[1] -= Consts['WORLD_Y']

        # ==============================================================================================================
        # ==================================================全局辅助函数==================================================
        # ==============================================================================================================

        # 返回两者的相对位置
        def centered_coord(cell1, cell2):
            # 返回以cell1为中心的cell2坐标
            dx = cell2.pos[0] - cell1.pos[0]
            dy = cell2.pos[1] - cell1.pos[1]
            real_dx = min([dx, dx - Consts["WORLD_X"], dx + Consts["WORLD_X"]], key=abs)
            real_dy = min([dy, dy - Consts["WORLD_Y"], dy + Consts["WORLD_Y"]], key=abs)
            return [real_dx, real_dy]

        # 返回两者速度差
        def veloc_dif(cell1, cell2):
            # 返回cell2相对于cell1的速度
            dvx = cell2.veloc[0] - cell1.veloc[0]
            dvy = cell2.veloc[1] - cell1.veloc[1]
            return [dvx, dvy]

        # 返回两者球心距离
        def distance_between(cell1, cell2):
            # 返回两者球心间的距离
            return magnitude(centered_coord(cell1, cell2))

        # 返回两者间隔 若撞上仍返回负数
        def gap_between(cell1, cell2):
            gap = distance_between(cell1, cell2) - cell1.radius - cell2.radius
            return gap

        # 返回预测最短距离 若越来越远则返回None
        def predict_distance_between(cell1, cell2):
            # 基于简单数学预测最近的距离，还没有考虑跨屏（跨屏很难考虑），故靠谱的距离半径是Consts["WORLD_Y"] / 2，应该够用了
            # 如果是越来越远就不存在最小距离，返回None
            r = centered_coord(cell1, cell2)
            v = veloc_dif(cell1, cell2)
            if inner_product(r, v) > 0 or magnitude(v) == 0:
                return None
            else:
                return abs(r[0] * v[1] - r[1] * v[0]) / magnitude(v)

        # 返回预测的最短距离对应位置 若越来越远则返回None
        def predict_close_pos_between(cell1, cell2):
            r = centered_coord(cell1, cell2)
            v = veloc_dif(cell1, cell2)
            if inner_product(r, v) > 0 or magnitude(v) == 0:
                return None
            else:
                return dot_line_perpvec(r, v)

        # 预测是否危险 输入危险间隔 返回bool
        def predict_is_danger_between(cell1, cell2, danger_gap):
            # gap比danger_gap大就是安全
            distance = predict_distance_between(cell1, cell2)
            if distance is not None:
                return distance - cell1.radius - cell2.radius < danger_gap
            else:
                return True

        # 预测能否碰撞 返回bool
        def predict_can_hit(cell1, cell2):
            distance = predict_distance_between(cell1, cell2)
            if distance is not None:
                return distance - cell1.radius - cell2.radius < - Parameter['CERTAIN_ABSORB_DEPTH']
            else:
                return False

        # 预测过多久会撞到，撞不到返回None
        def predict_hit_time(cell1, cell2):
            # 预测过多久会撞到，撞不到返回None
            r = centered_coord(cell1, cell2)
            v = veloc_dif(cell1, cell2)
            if not predict_can_hit(cell1, cell2) or magnitude(v) == 0:
                return None
            else:
                h = dot_line_distance(r, v)
                R = cell1.radius + cell2.radius
                t = (sqrt(magnitude(r) ** 2 - h ** 2) - sqrt(R ** 2 - h ** 2)) / magnitude(v)
                return t

        # 预测两者达到最近所用的时间，若越来越远则返回None
        def predict_close_time_between(cell1, cell2):
            if predict_distance_between(cell1, cell2) is None:
                return None
            else:
                if predict_can_hit(cell1, cell2):
                    return predict_hit_time(cell1, cell2)
                else:
                    return sqrt(distance_between(cell1, cell2) ** 2 - predict_distance_between(cell1, cell2) ** 2) /\
                           magnitude(veloc_dif(cell1, cell2))

        # 预测除自己以外的其他球走了frame_number帧之后的坐标
        def predict(frame_number, predict_cells):
            # 不要把自己传进来，不执行碰撞
            # 传出去cell的一个list
            if len(predict_cells) == 0:
                return []
            else:
                import copy
                copy = copy.deepcopy(predict_cells)
                # 移动frame_number帧
                for cell in copy:
                    cell.pos[0] += cell.veloc[0] * frame_number * Consts['FRAME_DELTA']
                    cell.pos[1] += cell.veloc[1] * frame_number * Consts['FRAME_DELTA']
                    # 穿屏
                    pull_back(cell.pos)
                return copy

        # ==============================================================================================================
        # ==============================================以自我为中心的辅助函数==============================================
        # ==============================================================================================================

        # 返回以自我为中心时other的坐标
        def self_centered_coord(other):
            return centered_coord(allcells[self.id], other)

        # 返回other相对于自己的速度
        def relative_veloc(other):
            return veloc_dif(allcells[self.id], other)

        # 返回自己到other的距离
        def distance_from(other):
            return distance_between(allcells[self.id], other)

        # 返回自己到other的gap
        def gap_from(other):
            return gap_between(allcells[self.id], other)

        # 还原最近距离,如果越来越远则返回None
        def predict_distance(other):
            return predict_distance_between(allcells[self.id], other)

        # 返回预测的最短距离对应位置 若越来越远则返回None
        def predict_close_pos(other):
            r = centered_coord(allcells[self.id], other)
            v = veloc_dif(allcells[self.id], other)
            if inner_product(r, v) > 0 or magnitude(v) == 0:
                return None
            else:
                return dot_line_perpvec(r, v)

        # 预测是否危险
        def predict_is_danger(other, danger_gap):
            return predict_is_danger_between(allcells[self.id], other, danger_gap)

        # 预测能否吃到
        def predict_can_eat(other):
            # 预测能否吃到
            return predict_can_hit(allcells[self.id], other)

        # 预测过多久会吃到，吃不到返回None
        def predict_eat_time(other):
            # 预测过多久会吃到，吃不到返回None
            return predict_hit_time(allcells[self.id], other)

        # 预测达到最近的时间，如果越来越远则返回None
        def predict_close_time(other):
            return predict_close_time_between(allcells[self.id], other)

        # 经过N次喷射损失的面积
        def estimate_mass_loss(N):
            # 经过N次喷射损失的面积
            return (1 - ((1 - Consts["EJECT_MASS_RATIO"]) ** N)) * allcells[self.id].area()

        # ==============================================================================================================
        # ==================================================目标判定相关==================================================
        # ==============================================================================================================

        # 对捕猎可能性的评判
        def hunt_judge(target, time_limit):
            import copy
            # 生成自己和待检验目标的副本
            mycopy = copy.deepcopy([allcells[self.id],  target])
            # 速度常数
            delta_speed = Consts['EJECT_MASS_RATIO'] * Consts['DELTA_VELOC']

            # 使用逐帧递归判定目标是否值得吃，返回值得与否，喷射次数以及时间
            def progress_test(mycopy, promise=False, count=0, time=0):
                if time > time_limit:
                    return [promise, count, time]
                else:
                    if predict_distance_between(mycopy[0], mycopy[1]) is None:  # 如果越来越远
                        dv = polar_to_xy([delta_speed, argument(centered_coord(mycopy[0], mycopy[1]))])
                        mycopy[0].veloc = vec_addition(mycopy[0].veloc, dv)
                        mycopy[0].pos = vec_addition(mycopy[0].pos, mycopy[0].veloc)
                        mycopy[0].radius *= sqrt(1 - Consts['EJECT_MASS_RATIO'])
                        mycopy[1].pos = vec_addition(mycopy[1].pos, mycopy[1].veloc)
                        pull_back(mycopy[0].pos)
                        pull_back(mycopy[1].pos)
                        count += 1
                        time += 1
                        return progress_test(mycopy, promise, count, time)
                    else:  # 在接近
                        if predict_can_hit(mycopy[0], mycopy[1]):  # 如果预测可碰撞
                            if predict_hit_time(mycopy[0], mycopy[1]) < Parameter['EAT_FORCE_TIME']:  # 在强迫进食时间内
                                if time + predict_hit_time(mycopy[0], mycopy[1]) < time_limit:
                                    promise = True
                                    return [promise, count, time + predict_hit_time(mycopy[0], mycopy[1])]
                                else:
                                    dv = polar_to_xy([delta_speed, argument(centered_coord(mycopy[0], mycopy[1]))])
                                    mycopy[0].veloc = vec_addition(mycopy[0].veloc, dv)
                                    mycopy[0].pos = vec_addition(mycopy[0].pos, mycopy[0].veloc)
                                    mycopy[0].radius *= sqrt(1 - Consts['EJECT_MASS_RATIO'])
                                    mycopy[1].pos = vec_addition(mycopy[1].pos, mycopy[1].veloc)
                                    pull_back(mycopy[0].pos)
                                    pull_back(mycopy[1].pos)
                                    count += 1
                                    time += 1
                                    return progress_test(mycopy, promise, count, time)
                            else:  # 受强迫进食的压迫
                                dv = polar_to_xy([delta_speed, argument(centered_coord(mycopy[0], mycopy[1]))])
                                mycopy[0].veloc = vec_addition(mycopy[0].veloc, dv)
                                mycopy[0].pos = vec_addition(mycopy[0].pos, mycopy[0].veloc)
                                mycopy[0].radius *= sqrt(1 - Consts['EJECT_MASS_RATIO'])
                                mycopy[1].pos = vec_addition(mycopy[1].pos, mycopy[1].veloc)
                                pull_back(mycopy[0].pos)
                                pull_back(mycopy[1].pos)
                                count += 1
                                time += 1
                                return progress_test(mycopy, promise, count, time)
                        else:  # 预测不可碰
                            v_side = vec_negative(dot_line_perpvec(veloc_dif(mycopy[0], mycopy[1]),
                                                                   centered_coord(mycopy[0], mycopy[1])))
                            if magnitude(v_side) <= delta_speed:
                                dv_argument = land_angle(argument(v_side) - acos(magnitude(v_side) / delta_speed))
                                dv = polar_to_xy([delta_speed, dv_argument])
                                mycopy[0].veloc = vec_addition(mycopy[0].veloc, dv)
                                mycopy[0].pos = vec_addition(mycopy[0].pos, mycopy[0].veloc)
                                mycopy[0].radius *= sqrt(1 - Consts['EJECT_MASS_RATIO'])
                                mycopy[1].pos = vec_addition(mycopy[1].pos, mycopy[1].veloc)
                                pull_back(mycopy[0].pos)
                                pull_back(mycopy[1].pos)
                                count += 1
                                time += 1
                                return progress_test(mycopy, promise, count, time)
                            else:
                                dv = polar_to_xy([delta_speed, argument(v_side)])
                                mycopy[0].veloc = vec_addition(mycopy[0].veloc, dv)
                                mycopy[0].pos = vec_addition(mycopy[0].pos, mycopy[0].veloc)
                                mycopy[0].radius *= sqrt(1 - Consts['EJECT_MASS_RATIO'])
                                mycopy[1].pos = vec_addition(mycopy[1].pos, mycopy[1].veloc)
                                pull_back(mycopy[0].pos)
                                pull_back(mycopy[1].pos)
                                count += 1
                                time += 1
                                return progress_test(mycopy, promise, count, time)

            # 递归
            return progress_test(mycopy)

        # 探测目标的邻域内有没有可能出现别的碰撞
        def detect_target_neighbor(other):
            # 检测目标附近可能会发生碰撞的漂移球（敌方不考虑）
            neighbor = [cell for cell in allcells if cell.id > 1 and
                        gap_between(other, cell) < Parameter['SECOND_GAP'] and
                        predict_can_hit(other, cell)]
            return neighbor

        # 评估可能的目标 辅助锁定最佳目标 在目标挑选的时候这是重要依据
        def hunt_sort_eval(other, time_limit):
            judge = hunt_judge(other, time_limit)
            if not judge[0]:
                return -1
            else:
                neighbor = detect_target_neighbor(other)
                if len(neighbor) == 0:
                    return other.area() - estimate_mass_loss(judge[1])
                else:
                    neighbor.sort(key=lambda cell: predict_hit_time(other, cell))
                    if predict_hit_time(other, neighbor[0]) < judge[2]:
                        if other.area() + neighbor[0].area() > (allcells[self.id].area() -
                           estimate_mass_loss(judge[1])) * Parameter['DANGER_RADIUS_RATIO']:
                            return -1
                        else:
                            return other.area() + neighbor[0].area() - estimate_mass_loss(judge[1])
                    else:
                        return other.area() - estimate_mass_loss(judge[1])

        # 生成目标吃球时限 根据形势判定 没什么用
        def generate_time_limit():
            assess = situation_assess()
            if assess == 0:
                return Parameter['EVEN_EAT_TIME_LIMIT']
            elif assess == -1:
                return Parameter['DISADVANTAGE_EAT_TIME_LIMIT']
            else:
                return Parameter['ADVANTAGE_EAT_TIME_LIMIT']

        # 寻找目标 通常是指比较近的目标 只会在非警惕状态下启用 返回目标或者None
        def search_target():
            # 考虑在search_distance范围内寻找目标进行锁定
            target_list = []
            for cell in allcells:
                if cell.id > 1 and allcells[self.id].radius * Parameter['EAT_LOW_RATIO'] < cell.radius < \
                   allcells[self.id].radius * Parameter['EAT_HIGH_RATIO']:
                    if gap_from(cell) < Parameter['SEARCH_TARGET_GAP']:
                        eval = hunt_sort_eval(cell, generate_time_limit())
                        if eval > 0:
                            target_list.append([cell, eval])
            if len(target_list) == 0:
                return None
            else:
                neighbor_prey = min(target_list, key=lambda a: gap_from(a[0]))[0]
                if gap_from(neighbor_prey) < Parameter['NEIGHBOR_PREY_GAP']:
                    return neighbor_prey
                else:
                    return max(target_list, key=lambda a: a[1])[0]

        # 寻找潜在目标 通常是在移动的过程中寻找可能路过的目标 在非警惕状态下和警惕状态下均可能启用
        # 在非警惕状态下实际上是搜索附带目标
        # 在警惕状态下实际上是搜索逃跑路线上可能的补给
        def search_potential_target():
            target_list = []
            for cell in allcells:
                if cell.id > 1 and allcells[self.id].radius * Parameter['EAT_LOW_RATIO'] < cell.radius < \
                   allcells[self.id].radius * Parameter['EAT_HIGH_RATIO'] and \
                   gap_from(cell) < Parameter['SEARCH_TARGET_GAP'] and \
                   angle_dif_abs(rev_angle(argument(self_centered_coord(cell))), argument(relative_veloc(cell))) < \
                   pi / 180 * Parameter['SUB_TARGET_DEGREE']:
                    target_list.append(cell)
            if len(target_list) == 0:
                return None
            else:
                return min(target_list, key=lambda a: gap_from(a))

        # 搜索绝对邻近的目标
        def search_neighbor_target():
            target_list = []
            for cell in allcells:
                if cell.id > 1 and allcells[self.id].radius * Parameter['EAT_NEIGHBOR_LOW_RATIO'] < cell.radius < \
                   allcells[self.id].radius * Parameter['EAT_HIGH_RATIO'] and \
                   gap_from(cell) < Parameter['NEIGHBOR_PREY_GAP'] and \
                   predict_distance(cell) is not None:
                    target_list.append(cell)
            if len(target_list) == 0:
                return None
            else:
                return max(target_list, key=lambda a: a.radius)

        # 判断目标是否应当放弃
        def check_abort_target():
            target = self.target
            # 绕过自己填位的环节 参见后面target_maintenance
            if target == allcells[self.id]:
                pass
            v = relative_veloc(target)
            r = self_centered_coord(target)
            if inner_product(v, r) / magnitude(r) > Parameter['TARGET_AWAY_TOLERANCE']:
                self.target = None
            else:
                if target.radius > allcells[self.id].radius * Parameter['DANGER_RADIUS_RATIO'] or \
                   target.radius < allcells[self.id].radius * Parameter['TARGET_LOW_TOLERANCE'] or \
                   gap_from(target) > Parameter['TARGET_GAP_TOLERANCE']:
                    self.target = None

        # 判断次级目标是否应当放弃
        def check_abort_sub_target():
            sub_target = self.sub_target
            v = relative_veloc(sub_target)
            r = self_centered_coord(sub_target)
            if inner_product(v, r) / magnitude(r) > Parameter['SUB_TARGET_AWAY_TOLERANCE']:
                self.sub_target = None
            else:
                if sub_target.radius > allcells[self.id].radius * Parameter['DANGER_RADIUS_RATIO'] or \
                   sub_target.radius < allcells[self.id].radius * Parameter['SUB_TARGET_LOW_TOLERANCE'] or \
                   gap_from(sub_target) > Parameter['SUB_TARGET_GAP_TOLERANCE']:
                    self.sub_target = None

        # 探测是否适合追杀目标 (没有使用)
        def should_attack():
            if gap_from(allcells[self.enemy_id]) < Parameter['ATTACK_ABLE_GAP'] and \
               angle_dif_abs(rev_angle(argument(self_centered_coord(allcells[self.enemy_id]))),
                             argument(relative_veloc(allcells[self.enemy_id]))) < pi / 180 * Parameter['ATTACK_DEGREE']:
                return True
            else:
                return False

        # ==============================================================================================================
        # ===================================================危险相关====================================================
        # ==============================================================================================================

        # 获取场上所有半径在我方半径的危险比例范围之上（大球）
        def get_large():
            large_list = [cell for cell in allcells if cell.id > 1 and
                          cell.radius > allcells[self.id].radius * Parameter['DANGER_RADIUS_RATIO']]
            return large_list

        # 某球是否在我方邻近危险范围内
        def is_nearby_threat(cell):
            if cell in get_large():
                if gap_from(cell) < Parameter['DANGER_GAP']:
                    return True
            return False

        # 敌方是否在我方邻近危险范围内
        def is_nearby_hostile():
            if gap_from(allcells[self.enemy_id]) < Parameter['HOSTILE_DANGER_GAP']:
                return True
            return False

        # 某球是否在高速对我方发起冲击
        def is_highspeed_threat(cell):
            if cell in get_large():
                # 在靠近，且在危险反应时间内会进入我方戒备区域
                if predict_distance(cell) is not None and \
                   predict_close_time(cell) < Parameter['DANGER_REACT_TIME'] and \
                   predict_is_danger(cell, Parameter['DANGER_GAP']):
                    return True
            return False

        # 敌方是否在高速对我方发起冲击
        def is_highspeed_hostile():
            enemy = allcells[self.enemy_id]
            if predict_distance(enemy) is not None and \
               predict_close_time(enemy) < Parameter['HOSTILE_DANGER_REACT_TIME'] and \
               predict_is_danger(enemy, Parameter['HOSTILE_DANGER_GAP']):
                return True
            return False

        # 获取对我方造成威胁的非玩家球
        def get_threats():
            threats = []
            for cell in get_large():
                if is_nearby_threat(cell) or is_highspeed_threat(cell):
                    threats.append(cell)
            return threats

        # 敌方是否有侵略意图
        def is_hostile():
            if situation_assess() == -1:
                if is_nearby_hostile() or is_highspeed_hostile():
                    return True
            return False

        # 非玩家球是否对我方不利
        def is_adverse():
            if len(get_threats()) == 0:
                return False
            else:
                return True

        # ==============================================================================================================
        # ===================================================行动方案====================================================
        # ==============================================================================================================

        # 躲避方案 邻近威胁采用对心距离值作为其权重躲避，高速威胁则采用球心至切点距离值作为其权重躲避 是一种侧向躲避策略
        def dodge(is_hostile):
            # 生成威胁球列表
            threats = get_threats()
            # 邻近威胁
            nearby_threats = []
            # 高速威胁
            highspeed_threats = []
            for threat in threats:
                if is_nearby_threat(threat):
                    nearby_threats.append(threat)
                else:
                    highspeed_threats.append(threat)
            if is_hostile:
                if is_nearby_hostile():
                    nearby_threats.append(allcells[self.enemy_id])
                else:
                    highspeed_threats.append(allcells[self.enemy_id])
                threats.append(allcells[self.enemy_id])
            new_nearby_threats = predict(1, nearby_threats)
            new_highspeed_threats = predict(1, highspeed_threats)
            new_threats = predict(1, threats)
            new_target = None
            if self.sub_target is not None:
                new_target = predict(1, [self.sub_target, ])
            result = []
            for i in range(0, 100):
                theta = i * pi * 2 / 100
                # 按theta喷之后走一帧后自己的情况
                fx = sin(theta)
                fy = cos(theta)
                new_vx = allcells[self.id].veloc[0] - Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
                new_vy = allcells[self.id].veloc[1] - Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
                new_radius = allcells[self.id].radius * sqrt(1 - Consts["EJECT_MASS_RATIO"])
                new_x = allcells[self.id].pos[0] + new_vx * Consts["FRAME_DELTA"]
                new_y = allcells[self.id].pos[1] + new_vy * Consts["FRAME_DELTA"]
                # 穿屏
                pull_back([new_x, new_y])
                # 一帧以后的自己
                new_me = Cell(None, [new_x, new_y], [new_vx, new_vy], new_radius)

                # 估价
                def dodge_eval_func(me, others, nearby_others, highspeed_others, target):
                    # 传入自己和待估价的其他cell
                    gaps = [gap_between(me, cell) for cell in others]

                    nearby_values = [gap_between(me, cell) for cell in nearby_others]
                    highspeed_values = [predict_distance_between(me, cell) for cell in highspeed_others if
                                        predict_close_time_between(me, cell) is not None]
                    if min(gaps) < 0:
                        # 会撞上返回None
                        return None
                    else:
                        if target is None:
                            return sum(nearby_values) + sum(highspeed_values)
                        else:
                            # 返回values之和减去到target间距
                            return sum(nearby_values) + sum(highspeed_values) - gap_between(me, target)

                if new_target is None:
                    value = dodge_eval_func(new_me, new_threats, new_nearby_threats, new_highspeed_threats, None)
                else:
                    value = dodge_eval_func(new_me, new_threats, new_nearby_threats, new_highspeed_threats, new_target[0])
                result.append(value)
            result_without_none = [i for i in result if i]
            if result_without_none:
                return result.index(max(i for i in result if i)) * pi * 2 / 100
            else:
                return None

        # 贪心吃法 永远是按照将速度摆正的方式 省体力耗时间
        def greedy_eat(target):
            # 速度常数
            delta_speed = Consts['EJECT_MASS_RATIO'] * Consts['DELTA_VELOC']
            if predict_can_eat(target):  # 如果可吃就不喷了
                return None
            else:  # 如果不可吃就贪心
                v_side = vec_negative(dot_line_perpvec(relative_veloc(target), self_centered_coord(target)))
                if magnitude(v_side) <= delta_speed:
                    dv_argument = land_angle(argument(v_side) - acos(magnitude(v_side) / delta_speed))
                    return rev_angle(dv_argument)
                else:
                    return argument(v_side)

        # 永远都是向着目标的方向奔 省时间耗体力
        def fast_eat(target):
            return rev_angle(argument(self_centered_coord(target)))

        # 锁定目标 进行狩猎
        def do_hunt(target):
            if predict_distance(target) is not None:  # 在靠近
                if predict_can_eat(target):
                    if predict_close_time(target) > Parameter['EAT_FORCE_TIME']:
                        return fast_eat(target)
                    else:
                        return greedy_eat(target)
                else:
                    return greedy_eat(target)
            else:
                return fast_eat(target)

        # 追杀敌人 （没有用到）
        def attack_enemy():
            if predict_can_eat(allcells[self.enemy_id]):
                return fast_eat(allcells[self.enemy_id])
            else:
                return greedy_eat(allcells[self.enemy_id])

        # 吃球方案
        def hunt():
            # if situation_assess() == 1 and should_attack():
                # return attack_enemy()
            # else:
                # 如果有次级目标
                if self.sub_target is not None:
                    # 先追次级目标
                    return do_hunt(self.sub_target)
                else:  # 如果没有次级目标
                    if self.target is not None:  # 如果有主目标
                        # 追主目标
                        return do_hunt(self.target)
                    else:
                        # 不作反应
                        return None

        # ==============================================================================================================
        # ===================================================最终策略====================================================
        # ==============================================================================================================

        # 目标维护
        def target_maintenance(get_alert):
            # 清除已逝目标
            if self.target is not None and self.target not in allcells:
                self.target = None
            if self.sub_target is not None and self.sub_target not in allcells:
                self.sub_target = None

            # 判断目标是否放弃并且进行抛弃环节
            if self.target is not None:
                check_abort_target()
            if self.sub_target is not None:
                check_abort_sub_target()

            # 若主目标不存在而次级目标仍然存在，并且如果次级目标可以成为主目标，就提升次级目标，否则删除
            if self.target is None and self.sub_target is not None:
                self.target, self.sub_target = self.sub_target, None
                check_abort_target()

            # ////////////////////////////////////////////////////////////

            # target 和 sub_target 位可以比作一个长度为2的栈[target, sub_target] 后面注释中用1表示位置满，0表示位置空
            if self.alert:  # 若之前处于警惕状态
                if not get_alert:  # 解除警惕 改变状态
                    if self.sub_target is None:  # [1, 0]
                        if self.target == allcells[self.id]:
                            self.target = None
                        else:
                            pass
                    else:  # [1, 1]
                        if self.target == allcells[self.id]:
                            self.target = self.sub_target
                            self.sub_target = None
                        else:
                            pass
                else:  # 继续保持警惕状态
                    if self.sub_target is None:  # [1, 0]
                        if search_potential_target() is not None:
                            self.sub_target = search_potential_target()
                        else:
                            pass
                    else:  # [1, 1]
                        pass

            else:  # 若之前不处于警惕状态
                if get_alert:  # 进入警惕 改变状态
                    if self.target is None and self.sub_target is None:  # [0, 0]
                        self.target = allcells[self.id]
                        if search_potential_target() is not None:
                            self.sub_target = search_potential_target()
                        else:
                            pass
                    elif self.target is not None and self.sub_target is None:  # [1, 0]
                        if search_potential_target() is not None:
                            self.sub_target = search_potential_target()
                        else:
                            pass
                    else:  # [1, 1]
                        self.target = self.sub_target
                        if search_potential_target() is not None:
                            self.sub_target = search_potential_target()
                        else:
                            self.sub_target = None

                else:  # 继续保持无警惕状态
                    if self.target is None and self.sub_target is None:  # [0, 0]
                        if search_target() is not None:
                            self.target = search_target()
                        else:
                            if search_potential_target() is not None:
                                self.target = search_potential_target()
                            else:
                                pass
                    elif self.target is not None and self.sub_target is None:  # [1, 0]
                        if search_neighbor_target() is not None:
                            self.sub_target = search_neighbor_target()
                        elif search_potential_target() is not None:
                            self.sub_target = search_potential_target()
                        else:
                            pass
                    else:  # [1, 1]
                        if search_neighbor_target() is not None:
                            self.target = self.sub_target
                            self.sub_target = search_neighbor_target()
                        else:
                            pass

            self.alert = get_alert

        # 最终策略
        def final_strategy():
            if is_hostile():  # 若监测到敌意
                target_maintenance(True)
                return dodge(is_hostile())
            elif is_adverse() and not is_hostile():  # 若受到来自非玩家的威胁
                target_maintenance(True)
                return dodge(is_hostile())
            else:  # 暂无威胁
                target_maintenance(False)
                return hunt()

        try:
            theta = final_strategy()
        except:
            return None
        else:
            return theta

