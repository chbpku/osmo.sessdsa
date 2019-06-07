from consts import Consts
import math


class simulated_cell:
    def __init__(self, id=None, pos=[0, 0], veloc=[0, 0], radius=0):
        self.id = id
        self.pos = pos
        self.veloc = veloc
        self.radius = radius
        self.dead = False

    def distance_from(self, other):
        dx = self.pos[0] - other.pos[0]
        dy = self.pos[1] - other.pos[1]
        min_x = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
        min_y = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
        return (min_x ** 2 + min_y ** 2) ** 0.5

    def crash(self, other):
        return self.radius + other.radius < self.distance_from(other)

    def forward(self, num=1):
        for _ in [0] * num:
            self.pos[0] = (self.veloc[0] + self.pos[0]) % Consts["WORLD_X"]
            self.pos[1] = (self.veloc[1] + self.pos[1]) % Consts["WORLD_Y"]

    def weight(self):
        return math.pi * self.radius ** 2

    def eat(self, other):
        other.dead = True
        self.veloc[0] = (self.weight() * self.veloc[0] + other.weight() * other.veloc[0]) / (
                self.weight() + other.weight())
        self.veloc[1] = (self.weight() * self.veloc[1] + other.weight() * other.veloc[1]) / (
                self.weight() + other.weight())
        self.radius = ((self.weight() + other.weight()) / math.pi) ** (1 / 2)

class Player:
    def __init__(self, id, arg=None):
        self.id = id
        self.prev = 0
        self.target=None
        self.frame=0

    def strategy(self, allcells):
        def __differ_speed(cell1, cell2):
            op_velocity = cell2.veloc
            my_velocity = cell1.veloc
            differ_velocity = [op_velocity[0] - my_velocity[0], op_velocity[1] - my_velocity[1]]
            speed = [(differ_velocity[0] ** 2 + differ_velocity[1] ** 2) ** (1 / 2),
                     math.pi + math.atan2(differ_velocity[0], differ_velocity[1]), differ_velocity]
            return speed

        def __position(cell):
            return cell.pos

        def __distance(cell1, cell2):
            dx = cell1.pos[0] - cell2.pos[0]
            dy = cell1.pos[1] - cell2.pos[1]
            min_x = min(abs(dx), abs(dx + Consts["WORLD_X"]), abs(dx - Consts["WORLD_X"]))
            min_y = min(abs(dy), abs(dy + Consts["WORLD_Y"]), abs(dy - Consts["WORLD_Y"]))
            if min_x == abs(dx):
                k_x = -dx
            elif min_x == abs(dx + Consts["WORLD_X"]):
                k_x = -dx - Consts["WORLD_X"]
            else:
                k_x = -dx + Consts["WORLD_X"]
            if min_y == abs(dy):
                k_y = -dy
            elif min_y == abs(dy + Consts["WORLD_Y"]):
                k_y = -dy - Consts["WORLD_Y"]
            else:
                k_y = -dy + Consts["WORLD_Y"]
            return (min_x ** 2 + min_y ** 2) ** 0.5, math.pi + math.atan2(k_x, k_y), [k_x, k_y]

        def __eat():
            return self.prev and self.prev < my_radius

        def __big_eat():
            return self.prev and self.prev ** 2 * 1.2 < my_radius ** 2

        def away(cell):
            return __distance(my_cell,cell)[1]+math.pi

        def move(cell1, cell2):
            nonlocal direction
            global n, certain_direction
            try:
                if n:
                    pass
            except:
                n = -1
            if n == -1 or (not n and __big_eat()):
                distance = __distance(cell1, cell2)[2]
                differ_speed = __differ_speed(cell1, cell2)
                included_angle = math.pi - distance[1] + differ_speed[1]
                v1 = differ_speed[0]
                n = v1 * abs(math.sin(included_angle)) // delta_veloc + 1
                if n <= 10:
                    v2 = delta_veloc * n
                    alpha = math.asin(math.sin(included_angle) * v1 / v2)
                    direction = distance[1] - alpha + math.pi
                certain_direction = direction
            elif n > 0:
                if n >= 10:
                    n = 0
                else:
                    n -= 1
                direction = certain_direction

        def change_target(cell):
            self_simulated=simulated_cell(my_cell.id,my_cell.pos,my_cell.veloc,my_cell.radius)
            cell_simulated=simulated_cell(cell.id,cell.pos,cell.veloc,my_cell.radius)
            for _ in [0]*60:
                self_simulated.forward()
                cell_simulated.forward()
                if self_simulated.crash(cell_simulated):
                    return True
            else:
                return False

        def count(allcells):
            return sum([not cell.dead and cell.radius<8 for cell in allcells])


        my_cell = allcells[self.id]
        op_cell = allcells[1 - self.id]
        my_radius = my_cell.radius
        op_differ_speed = __differ_speed(my_cell, op_cell)
        cells = sorted(allcells, key=lambda cell: __distance(my_cell, cell)[0])
        delta_veloc = (Consts["EJECT_MASS_RATIO"] / (1 - Consts["EJECT_MASS_RATIO"])) * Consts["DELTA_VELOC"]
        op_distance=__distance(my_cell,op_cell)

        closest_big = closest_small = 0
        id = 0
        while not (closest_big and closest_small) and id < len(cells):
            if cells[id].radius > my_radius and not closest_big:
                closest_big = cells[id]
            if 0.2 * my_radius < cells[id].radius < 0.95 * my_radius and not closest_small:
                closest_small = cells[id]
            id += 1
        direction = 0
        if self.prev==0:
            self.prev=my_radius
            return 1
        if op_differ_speed[0] > 0.1 and op_distance[0] < 70+op_differ_speed[0]*100 and op_cell.radius > my_radius:
            v_ver = op_differ_speed[0] * math.sin(op_differ_speed[1] - op_distance[1])
            v_bel = op_differ_speed[0] * math.cos(op_differ_speed[1] - op_distance[1])
            if -v_bel / (15 * (1 - math.cos(math.atan(op_cell.radius / op_distance[0]) + 0.3))) + (
                    v_bel ** 2 + 2 * (15 * (1 - math.cos(math.atan(op_cell.radius / op_distance[0]) + 0.3))) * op_distance[0]) ** (1 / 2) > 1.5:
                self.prev=my_radius
                return op_distance[1] + math.atan(op_cell.radius / op_distance[0]) * v_ver / abs(v_ver)+math.pi + 0.3
            else:
                return op_distance[1]+math.pi
        if closest_big:
            if __distance(my_cell,closest_big)[0]<2*my_radius+closest_big.radius:
                direction=away(closest_big)
        if __eat():
            self.target = None
            self.frame=0
        if (not self.target) and closest_small:
            if __distance(my_cell,closest_small)[0]<(6+4*(count(allcells)<10))*my_radius:
                self.target=closest_small
        if self.target:
            move(my_cell,self.target)
            self.frame+=1
            if (not direction and not change_target(self.target)) or self.frame > 8*self.target.radius:
                self.target=None
                self.frame=0
        self.prev=my_radius
        return direction if direction else None