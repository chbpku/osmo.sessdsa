#!/usr/bin/env python3

#####################################################
#                                                   #
#     ______        _______..___  ___.   ______     #
#    /  __  \      /       ||   \/   |  /  __  \    #
#   |  |  |  |    |   (----`|  \  /  | |  |  |  |   #
#   |  |  |  |     \   \    |  |\/|  | |  |  |  |   #
#   |  `--'  | .----)   |   |  |  |  | |  `--'  |   #
#    \______/  |_______/    |__|  |__|  \______/    #
#                                                   #
#                                                   #
#####################################################

# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

from consts import Consts
from cell import Cell
from copy import deepcopy
from math import sin, cos, tan, asin, acos, atan, pi, isclose


class Player():
    accelerate = Consts["EJECT_MASS_RATIO"] * Consts["DELTA_VELOC"] / Consts["FRAME_DELTA"]
    eject_mass_ratio = Consts["EJECT_MASS_RATIO"]

    def __init__(self, id, arg=None):
        self.id = id

    def polarize(self, direc):
        length = lambda direc: (direc[1] ** 2 + direc[0] ** 2) ** 0.5
        if isclose(direc[1], 0):
            if direc[0] >= 0:
                return [pi / 2, direc[0]]
            else:
                return [pi * 3 / 2, -direc[0]]
        else:
            if direc[1] >= 0 and direc[0] >= 0:
                return [atan(direc[0] / direc[1]), length(direc)]
            elif direc[1] < 0:
                return [atan(direc[0] / direc[1]) + pi, length(direc)]
            else:
                return [atan(direc[0] / direc[1]) + 2 * pi, length(direc)]

    def re_veloc(self, target, myself):
        target = target.veloc
        myself = myself.veloc
        return [target[0] - myself[0], target[1] - myself[1]]

    def min_vector(self, target, myself):
        dx = myself[0] - target[0]
        dy = myself[1] - target[1]
        min_x = min(dx, dx + Consts["WORLD_X"], dx - Consts["WORLD_X"], key=lambda x: abs(x))
        min_y = min(dy, dy + Consts["WORLD_Y"], dy - Consts["WORLD_Y"], key=lambda x: abs(x))
        return [min_x, min_y]

    def _sign(self, number):
        if number > 0:
            return 1
        elif number < 0:
            return -1
        else:
            return 0

    def p_l_distance(self, target, myself, re_veloc):
        min_vector = self.min_vector(target.pos, myself.pos)
        alpha_p, distance = self.polarize(min_vector)
        alpha_v, speed = self.polarize(re_veloc)
        if isclose(speed, 0):
            return {'distance': distance, 'time': float('inf'), 'close': float('inf'), 'theta': None}
        else:
            delta_alpha = (alpha_p - alpha_v) % (2 * pi)
            dcosa = distance * cos(delta_alpha)
            time = dcosa / speed
            close = abs(distance * sin(delta_alpha))
            if target.radius + myself.radius <= close:
                time = dcosa / speed
            else:
                if dcosa >= 0:
                    time = (dcosa - ((target.radius + myself.radius) ** 2 - close ** 2) ** 0.5) / speed
                else:
                    time = -(dcosa - ((target.radius + myself.radius) ** 2 - close ** 2) ** 0.5) / speed
            if delta_alpha <= pi:
                theta = (alpha_v - pi / 2) % (2 * pi)
            else:
                theta = (alpha_v + pi / 2) % (2 * pi)
            return {'distance': distance, 'dcosa': dcosa, 'speed': speed,
                    'time': time, 'close': close, 'theta': theta}

    def fleeting(self, dangers, myself):
        warning_close = 0.9
        noticed_size = 0.9
        real_dangers = []
        for cell in dangers:
            timelimit = 4 * (2 * (myself.radius + cell.radius) / Player.accelerate) ** 0.5
            if cell.id != self.id and cell.radius > myself.radius * noticed_size:
                indexes = self.p_l_distance(cell, myself, self.re_veloc(cell, myself))
                if (indexes['close'] * warning_close <= myself.radius + cell.radius) and \
                        (timelimit > indexes['time'] >= 0) and (cell.radius >= myself.radius):
                    real_dangers.append([indexes['theta'], indexes['time']])
        if real_dangers == []:
            return None
        else:
            return min(real_dangers, key=lambda lst: lst[1])[0]

    def attack(self, target, myself, indexes):
        ensure_close = 1.1
        if myself.radius > target.radius and indexes['time'] > 0:
            how_far = indexes['close'] * ensure_close - (myself.radius + target.radius)
            if how_far < 0:
                delta_m = target.radius ** 2
                delta_m_rate = delta_m / indexes['time']
                return [None, delta_m_rate]
            elif how_far < 1500:
                need_time = (how_far * 2 / Player.accelerate) ** 0.5
                if indexes['time'] > need_time:
                    speed_up_time = indexes['time'] - (how_far / Player.accelerate) ** 0.5
                    m_decrease = Player.eject_mass_ratio * myself.radius ** 2 * speed_up_time
                    if myself.radius ** 2 - m_decrease > target.radius ** 2:
                        delta_m_rate = (target.radius ** 2 - m_decrease) / indexes['time']
                        theta = (indexes['theta'] + pi) % (2 * pi)
                        return [theta, delta_m_rate]

    def fleet(self, danger, myself, indexes):
        war_timelimit = 2.5 * (2 * (myself.radius + danger.radius) / Player.accelerate) ** 0.5
        warning_close = 0.9
        if (war_timelimit > indexes['time'] > 0) and (myself.radius <= danger.radius) and \
                (indexes['close'] * warning_close <= myself.radius + danger.radius):
            return [indexes['theta'], indexes['time']]

    def attack_and_fleet(self, dangers_targets, myself):
        noticed_size = myself.radius * 0.3
        minspeed_if_nothing = 5
        dangers = []
        targets = []
        for cell in dangers_targets:
            if (cell.id != self.id and cell.radius > noticed_size) or cell.id == abs(1 - self.id):
                indexes = self.p_l_distance(cell, myself, self.re_veloc(cell, myself))
                attack_plan = self.attack(cell, myself, indexes)
                fleet_plan = self.fleet(cell, myself, indexes)
                if attack_plan:
                    targets.append(attack_plan)
                elif fleet_plan:
                    dangers.append(fleet_plan)
        if dangers != []:
            return min(dangers, key=lambda lst: lst[1])[0]
        elif targets != []:
            return max(targets, key=lambda lst: lst[1])[0]
        else:
            theta, speed = self.polarize(myself.veloc)
            if speed < minspeed_if_nothing:
                # return (theta + pi) % (2 * pi)
                return None
            else:
                return None

    def strategy(self, allcells):
        myself = allcells[self.id]
        return self.attack_and_fleet(allcells, myself)
        # return self.fleeting(allcells,myself)
