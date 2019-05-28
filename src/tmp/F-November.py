from consts import Consts
from math import *
from copy import *


class Player:
    def __init__(self, id, args=None):
        self.id = id
        self.cell = None

    def other_id(self):
        # Return my opponent's id
        if self.id == 0:
            return 1
        else:
            return 0

    def strategy(self, starList):
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
            cell2.dead = True
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
                        if cellList[i].dead or cellList[j].dead:
                            # if it has been dead
                            continue
                        separation_d = distance(cellList[i].pos, cellList[j].pos) - \
                                       (cellList[i].radius + cellList[j].radius)
                        if separation_d < 1e-6:
                            if fabs(cellList[i].radius - cellList[j].radius) > 1e-6:
                                if cellList[i].radius > cellList[j].radius:
                                    cellList[i] = absorb(cellList[i], cellList[j])
                                else:
                                    cellList[j] = absorb(cellList[j], cellList[i])
                            elif fabs(norm(cellList[i].veloc) - norm(cellList[j].veloc)) > 1e-6:
                                if norm(cellList[i].veloc) > norm(cellList[j].veloc):
                                    cellList[i] = absorb(cellList[i], cellList[j])
                                else:
                                    cellList[j] = absorb(cellList[j], cellList[i])
                            else:
                                if cellList[i].id > cellList[j].id:
                                    cellList[i] = absorb(cellList[i], cellList[j])
                                else:
                                    cellList[j] = absorb(cellList[j], cellList[i])
                new_cells = list()
                for cell in cellList:
                    if not cell.dead or \
                            cell.id == SELF.id or cell.id == OTHER.id:
                        new_cells.append(cell)
                return update(new_cells, frame_delta - 1)

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
            limit_angle = asin((me.radius+enemy.radius)/distance(me.pos, enemy.pos))
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
                    xdistance = ((norm(radius)-me.radius-enemy.radius)/norm(vr))*dv
                    if xdistance > 2*(enemy.radius + me.radius) and \
                            norm(vr)**2/dv < 0.5*norm(radius):
                        # loosened judgment condition
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
            else:
                limit_angle_1 = veloc_angle(radius) - limit_angle
                limit_angle_2 = veloc_angle(radius) + limit_angle
                x1 = fabs(limit_angle_1 - veloc_angle(vr))
                x2 = fabs(limit_angle_2 - veloc_angle(vr))
                if angle_between_vectors(vr, radius) < limit_angle/5:
                    return radius_angle(me.pos, enemy.pos)
                    # returns the direction from me to the enemy
                else:
                    if x1 > x2:
                        return (limit_angle_2 - pi / 2) % (2 * pi)
                    else:
                        return (limit_angle_1 + pi / 2) % (2 * pi)
                    # it returns the direction perpendicular to vr, away from enemy

        eject_rate = Consts['EJECT_MASS_RATIO']
        delta_v = Consts['DELTA_VELOC']
        limit_speed = Consts['MAX_VELOC']
        SELF = starList[self.id]
        ID = self.id
        OTHER = starList[self.other_id()]
        # RUN!!!
        # most basic run judgement: if I am dying now, there is no need to think more
        runList = list()
        for Monster in starList:
            if Monster.radius > SELF.radius:
                runList.append(Monster)
        result = None
        for obj in runList:
            if distance(obj.pos, SELF.pos) - obj.radius - SELF.radius <= 5*(norm(SELF.veloc) + norm(obj.veloc)):
                    return radius_angle(SELF.pos, obj.pos)
            if not CanEscape(SELF, obj):
                if distance(obj.pos, SELF.pos) - obj.radius - SELF.radius <= \
                        20*(norm(SELF.veloc) + norm(obj.veloc))+10:
                    t = Escape(SELF, obj)
                    if t is not None:
                        result = t
                if result is not None:
                    return result
        # If it seems that I am safe now, calculate the situation three ticks later, see if any absorption shall occur:
        # following code can be deleted when Chase is mature
        posList1 = SELF.pos
        tttttList = starList.copy()
        tempstarList = []
        for item in tttttList:
            if distance(item.pos, SELF.pos) < 200:
                tempstarList.append(item)
        tempstarList = update(tempstarList, 19)
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
            for th in aList:
                if th.id == SELF.id:
                    meee = th
                    break
            for thing in aList:
                if (distance(meee.pos, thing.pos) - myradius) ** 2 < \
                        2*(thing.radius**2 - myradius**2):
                    for item in starList:
                        if item.id == thing.id:
                            posList2 = item.pos
                            break
                    return radius_angle(posList1, posList2)
        # RUN!!!
        return None
