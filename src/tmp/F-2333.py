from consts import Consts
from math import *
from copy import copy


class Player:
    def __init__(self, id, args=None):
        self.id = id
        self.target = None

    def other_id(self):
        # Return my opponent's id
        if self.id == 0:
            return 1
        else:
            return 0

    def strategy(self, all_cells):
        # these 9 functions below are used for basic running.
        def norm(vec):
            # calculate the normal number of vector
            return sqrt(vec[0] ** 2 + vec[1] ** 2)

        def min_distance_way(pos1, pos2):
            # Figure out what the Min-distance way is
            axis_D = [pos2[0] - pos1[0], pos2[1] - pos1[1]]
            x0 = fabs(axis_D[0])
            x1 = fabs(axis_D[0] + 1000)
            x2 = fabs(axis_D[0] - 1000)
            if x1 <= x0 and x1 <= x2:
                axis_D[0] += 1000
            elif x2 <= x0 and x2 <= x1:
                axis_D[0] -= 1000
            y0 = fabs(axis_D[1])
            y1 = fabs(axis_D[1] + 500)
            y2 = fabs(axis_D[1] - 500)
            if y1 <= y0 and y1 <= y2:
                axis_D[1] += 500
            elif y2 <= y0 and y2 <= y1:
                axis_D[1] -= 500
            return axis_D

        def distance(pos1, pos2):
            # Considering it capable of going through boundaries
            # Return Min-distance between two stars
            axis_D = min_distance_way(pos1, pos2)
            return norm(axis_D)

        def angle_cal(vec):
            # To calculate the angle of the vector
            if vec[1] < 0:
                return pi / 2 + acos(vec[0] / norm(vec))
            elif vec[0] < 0:
                return 5 * pi / 2 - acos(vec[0] / norm(vec))
            else:
                return pi / 2 - acos(vec[0] / norm(vec))

        def radius_angle(pos1, pos2):
            # Considering crossing boundaries
            # Return the angle of radius vector(pos1, pos2)
            # the plus direction of y-axis
            # the start edge of angle
            axis_D = min_distance_way(pos1, pos2)
            return angle_cal(axis_D)

        def veloc_angle(veloc):
            # Return the angle of velocity vector
            return angle_cal(veloc)

        def absorb(cell1, cell2):
            # Object cell1 absorbs object cell2
            m1 = cell1.radius ** 2
            m2 = cell2.radius ** 2
            cell1.veloc[0] = (m1 * cell1.veloc[0] + m2 * cell2.veloc[0]) / (m1 + m2)
            cell1.veloc[1] = (m1 * cell1.veloc[1] + m2 * cell2.veloc[1]) / (m1 + m2)
            # Law of Conservation of Momentum
            if cell1.veloc[0] > limit_speed:
                cell1.veloc[0] = limit_speed
            if cell1.veloc[1] > limit_speed:
                cell1.veloc[1] = limit_speed
            cell1.radius = sqrt(m1 + m2)
            cell2.radius = 0
            return cell1

        def through_boundaries(pos):
            # To deal with the boundary-through condition
            new_pos = copy(pos)
            if new_pos[0] > 1000:
                new_pos[0] -= 1000
            elif new_pos[0] < -1000:
                new_pos[0] += 1000
            if new_pos[1] > 500:
                new_pos[1] -= 500
            elif new_pos[1] < -500:
                new_pos[1] += 500
            return new_pos

        def update(cellList, frame_delta):
            # frame_delta represents the number of ticks that has been used
            if frame_delta == 0:
                return cellList
            else:
                for cell in cellList:
                    cell.pos = [cell.pos[0] + cell.veloc[0], cell.pos[1] + cell.veloc[1]]
                    cell.pos = through_boundaries(cell.pos)
                for i in range(len(cellList) - 1):
                    for j in range(i + 1, len(cellList)):
                        if cellList[i].radius == 0 or cellList[j].radius == 0:
                            # if it has been dead
                            continue
                        separation_d = distance(cellList[i].pos, cellList[j].pos) - \
                                       (cellList[i].radius + cellList[j].radius)
                        if separation_d < 1e-6:
                            if fabs(cellList[i].radius - cellList[j].radius) > 1e-6:
                                if cellList[i].radius > cellList[j].radius:
                                    cellList[i] = absorb(cellList[i], cellList[j])
                                    cellList[j].radius = 0
                                else:
                                    cellList[j] = absorb(cellList[j], cellList[i])
                                    cellList[i].radius = 0
                            elif fabs(norm(cellList[i].veloc) - norm(cellList[j].veloc)) > 1e-6:
                                if norm(cellList[i].veloc) > norm(cellList[j].veloc):
                                    cellList[i].veloc = absorb(cellList[i], cellList[j])
                                    cellList[j].radius = 0
                                else:
                                    cellList[j] = absorb(cellList[j], cellList[i])
                                    cellList[i].radius = 0
                            else:
                                if cellList[i].id > cellList[j].id:
                                    cellList[i] = absorb(cellList[i], cellList[j])
                                    cellList[j].radius = 0
                                else:
                                    cellList[j] = absorb(cellList[j], cellList[i])
                                    cellList[i].radius = 0
                new_cells = list()
                for cell in cellList:
                    if cell.radius > 1e-6 or \
                            cell.id == SELF.id or cell.id == OTHER.id:
                        new_cells.append(cell)
                return update(new_cells, frame_delta - 1)

        # these 5 functions below are used for catching.
        def eject(cell, theta):
            # Object cell ejects at certain angle theta
            cell.veloc[0] -= eject_rate * delta_v * sin(theta)
            cell.veloc[1] -= eject_rate * delta_v * cos(theta)
            if cell.veloc[0] > limit_speed:
                cell.veloc[0] = limit_speed
            if cell.veloc[1] > limit_speed:
                cell.veloc[1] = limit_speed
            cell.radius *= sqrt(1 - eject_rate)
            cell.pos = [cell.pos[0] + cell.veloc[0], cell.pos[1] + cell.veloc[1]]
            cell.pos = through_boundaries(cell.pos)
            return cell

        def value_cal(mine, target):
            r0 = mine.radius
            r1 = target.radius
            d = distance(mine.pos, target.pos)
            phi = radius_angle(target.pos, mine.pos)
            relative_v = [mine.veloc[0] - target.veloc[0], mine.veloc[1] - target.veloc[1]]
            dv = relative_v[0] * sin(phi) + relative_v[1] * cos(phi)
            if r1 > r0 and dv > 0:
                return 0
            elif r1 > r0:
                return -10000 * r1 ** 2 * (-dv) / d
            else:
                return 10 * r1 ** 2 * (-dv) / d

        def mass_predict(mine, target):
            # Predict the relative changing masses (m / t) if mine has chased and absorbed the target
            delta_m = mine.radius ** 2
            if target.radius > mine.radius:
                return delta_m * -100000
            else:
                dv = eject_rate * delta_v
                d = distance(mine.pos, target.pos)
                relative_v = [mine.veloc[0] - target.veloc[0], mine.veloc[1] - target.veloc[1]]
                phi = radius_angle(target.pos, mine.pos)
                vy = relative_v[0] * sin(phi) + relative_v[1] * cos(phi)
                vx = relative_v[0] * cos(phi) - relative_v[1] * sin(phi)
                tick_used = 0
                while fabs(vx) > dv:
                    if vx > 0:
                        vx -= dv
                    else:
                        vx += dv
                    tick_used += 1
                    d -= vy
                vy -= dv * cos(asin(vx / dv))
                tick_used += 1
                while d > 0:
                    if d / (-vy) > 30 and \
                            target.radius < (mine.radius * sqrt(1 - eject_rate) ** (tick_used + 2)):
                        vy -= dv
                    d -= -vy
                    tick_used += 1
                delta_m *= (1 - eject_rate) ** tick_used
                delta_m += target.radius ** 2
                delta_m -= mine.radius ** 2
                delta_m /= tick_used
                return delta_m * 100

        def chase(mine, target):
            # Return the most appropriate angle to chase my target
            dv = eject_rate * delta_v
            relative_v = [mine.veloc[0] - target.veloc[0], mine.veloc[1] - target.veloc[1]]
            phi = radius_angle(target.pos, mine.pos)
            vy = relative_v[0] * sin(phi) + relative_v[1] * cos(phi)
            vx = relative_v[0] * cos(phi) - relative_v[1] * sin(phi)
            if vy > 0:
                # Actually maybe I want to chase it.
                return None
            else:
                if fabs(vx) < 1:
                    if distance(mine.pos, target.pos) / (-vy) < 100:
                        return 'unnecessary'
                    else:
                        return phi
                else:
                    self.target = target.id
                    if fabs(vx) > dv:
                        dphi = asin(vx / fabs(vx))
                    else:
                        dphi = asin(vx / dv)
                    return (phi + dphi) % (2 * pi)

        def evaluate(mine, visible_cells, invisible_cells):
            # evaluation function
            # Try to work out the theta to gain most mass
            theta = None
            beta = None
            found = False
            max_value = 0
            for monster in visible_cells:
                max_value += value_cal(mine, monster)
            if TARGET is not None:
                found = True
                beta = chase(mine, TARGET)
                if beta == 'unnecessary':
                    beta = None
            if found:
                theta = beta
            else:
                for monster in visible_cells:
                    temp_value = 0
                    if chase(mine, monster) is None:
                        continue
                    elif chase(mine, monster) == 'unnecessary':
                        theta = None
                    else:
                        alpha = chase(mine, monster)
                        new_me = eject(mine, alpha)
                        new_cells = copy(visible_cells + invisible_cells)
                        new_cells.append(new_me)
                        new_cells = update(new_cells, 5)
                        for cell in new_cells:
                            if cell.id == ID:
                                new_me = cell
                                break
                        if new_me.radius < mine.radius or new_me.radius < 1e-6:
                            continue
                        else:
                            divide = distinguish(new_me, new_cells)
                            new_visible = divide[1]
                            for new_monster in new_visible:
                                temp_value += value_cal(new_me, new_monster)
                            if max_value < temp_value:
                                max_value = temp_value
                                theta = alpha
            return theta

        def distinguish(mine, all_cells):
            # intend to divide cells into 2 groups
            # to choose appropriate ones to reduce computation
            sight_range = 3.6 * mine.radius
            visible_cells = list()  # cells within my sight
            invisible_cells = list()  # cells out of my sight
            divide = list()
            divide.append(mine)
            for cell in all_cells:
                if cell.id != ID:
                    if distance(mine.pos, cell.pos) <= sight_range and \
                            cell.radius / mine.radius >= min_rate:
                        visible_cells.append(cell)
                    else:
                        invisible_cells.append(cell)
            divide.append(visible_cells)
            divide.append(invisible_cells)
            return divide

        # these 4 functions below are used for escaping.
        def angle_between_vectors(vec1, vec2):
            alpha = veloc_angle(vec1)
            beta = veloc_angle(vec2)
            theta = fabs(alpha - beta)
            if theta > pi:
                theta = 2 * pi - theta
            return theta

        def CanEscape(me, enemy):
            # there are times when you are destined to die, just in next tick
            if enemy.radius < me.radius:
                return True
            # avoid stupid mistakes in main function
            if distance(me.pos, enemy.pos) < me.radius + enemy.radius + 1e-7:
                return False
            # avoid math domain error which occurs when we have been overlapped
            vr = Vr(me, enemy)
            # relative velocity
            dv = Consts['EJECT_MASS_RATIO'] * Consts['DELTA_VELOC']
            radius = min_distance_way(me.pos, enemy.pos)
            # radius vector of the centers of two cells, from me to enemy
            limit_angle = asin((me.radius + enemy.radius) / distance(me.pos, enemy.pos))
            if angle_between_vectors(radius, vr) > limit_angle:
                return True
            # which means I am not heading for the enemy, so nothing will happen
            else:
                alpha = angle_between_vectors(radius, vr)
                beta = limit_angle - alpha
                # beta is the angle between vr and the limit line,
                # so if the max angle between vr and dv is larger than beta, I am sure to escape
                if dv > norm(vr):
                    return True
                else:
                    xdistance = ((norm(radius) - me.radius - enemy.radius) / norm(vr)) * dv
                    if xdistance > enemy.radius + me.radius:
                        return True
                    else:
                        return False

        def Vr(x1, y1):
            # x, y are cells, suppose y is still and return vx relative to y
            vr = list()
            vr.append(x1.veloc[0] - y1.veloc[0])
            vr.append(x1.veloc[1] - y1.veloc[1])
            return vr

        def Escape(me, enemy):
            # return the most economic angle to escape
            vr = Vr(me, enemy)
            # relative velocity
            dv = Consts['EJECT_MASS_RATIO'] * Consts['DELTA_VELOC']
            radius = min_distance_way(me.pos, enemy.pos)
            # radius vector of the centers of two cells, from me to enemy
            if me.radius + enemy.radius > distance(me.pos, enemy.pos):
                return None
            # avoid bug
            limit_angle = asin((me.radius + enemy.radius) / distance(me.pos, enemy.pos))
            if angle_between_vectors(vr, radius) > limit_angle:
                return None
            # which means I am not heading for the enemy, so nothing need to be done
            if angle_between_vectors(vr, radius) < limit_angle / 5:
                return radius_angle(me.pos, enemy.pos)
            else:
                limit_angle_1 = veloc_angle(radius) - limit_angle
                limit_angle_2 = veloc_angle(radius) + limit_angle
                x1 = fabs(limit_angle_1 - veloc_angle(vr))
                x2 = fabs(limit_angle_2 - veloc_angle(vr))
                if x1 > x2:
                    return (limit_angle_2 - pi / 2) % (2 * pi)
                else:
                    return (limit_angle_1 + pi / 2) % (2 * pi)
                # it returns the direction perpendicular to vr, away from enemy

        eject_rate = Consts['EJECT_MASS_RATIO']
        delta_v = Consts['DELTA_VELOC']
        limit_speed = Consts['MAX_VELOC']
        ID = self.id
        SELF = all_cells[self.id]
        OTHER = all_cells[self.other_id()]
        found = False
        TARGET = None
        for monster in all_cells:
            if monster.id == self.target and not monster.dead:
                found = True
                TARGET = monster
                break
        if not found:
            self.target = None

        '''copyList = copy(all_cells)
        copyList = update(copyList, 10)
        for i in range(len(copyList)):
            if copyList[i].id == id:
                copy_id = i
        if copyList[copy_id].radius == 0:'''
        # RUN!!!
        # most basic run judgement: if I am dying now, there is no need to think more
        runList = list()
        for Monster in all_cells:
            if Monster.radius > SELF.radius:
                runList.append(Monster)
        result = None
        for obj in runList:
            if distance(obj.pos, SELF.pos) - obj.radius - SELF.radius <= 5 * (norm(SELF.veloc) + norm(obj.veloc)):
                return radius_angle(SELF.pos, obj.pos)
            if not CanEscape(SELF, obj):
                # 相向而行时，还是会被吃掉。
                if distance(obj.pos, SELF.pos) - obj.radius - SELF.radius \
                        <= 10 * (norm(SELF.veloc) + norm(obj.veloc)):
                    t = Escape(SELF, obj)
                    if t is not None:
                        result = t
                if result is not None:
                    return result
        # If it seems that I am safe now, calculate the situation three ticks later,
        # see if any absorptions shall occur:
        '''tempList = []
        for c in all_cells:
            if 2 * c.radius > SELF.radius and distance(c.pos, SELF.pos) < 150:
                tempList.append(c)
        for t in range(10):
            Found = False
            prevList = tempList.copy()
            tempList = update(tempList, 1)
            for item in tempList:
                if item.id == SELF.id:
                    Found = True
                    break
            if not Found:
                badassList = []
                for cell in prevList:
                    if cell.id == SELF.id:
                        meee = cell
                    else:
                        badassList.append(cell)
                badassList = update(badassList, 1)
                meee.pos[0] += meee.veloc[0]
                meee.pos[1] += meee.veloc[1]
                for item in badassList:
                    if distance(item.pos, meee.pos) < SELF.radius + item.radius + 1:
                        x = item.id
                        for j in starList:
                            if j.id == x:
                                badass = j
                                break
                        return radius_angle(SELF.pos, badass.pos)'''
        posList1 = SELF.pos
        tempstarList = all_cells.copy()
        tempstarList = update(tempstarList, 9)
        myradius = 0
        for item in tempstarList:
            if item.id == SELF.id:
                myradius = item.radius
                break
        aList = tempstarList.copy()
        aList = update(aList, 1)
        Found = True
        for item in aList:
            if item.id == SELF.id:
                if item.radius == 0:
                    Found = False
                    break
        if not Found:
            for thing in aList:
                if thing.id == SELF.id:
                    meee = thing
            for thing in aList:
                if (distance(meee.pos, thing.pos) - myradius) ** 2 < thing.radius ** 2 - myradius ** 2:
                    for item in all_cells:
                        if item.id == thing.id:
                            posList2 = item.pos
                            break
                    return radius_angle(posList1, posList2)
        # RUN!!!
        # return None

        test_list = copy(all_cells)
        min_rate = 0.2
        divide = distinguish(SELF, test_list)
        return evaluate(SELF, divide[1], divide[2])
