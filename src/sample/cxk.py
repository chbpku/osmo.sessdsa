#!/usr/bin/env python3

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
import random
import math

class Player():
    def __init__(self):
        pass

    def sing(self):
        print("MUSIC!!!")
        return None

    def jump(self, id, allcells):
        # Only move to the smallest cell
        min_cell = sorted(allcells, key = lambda cell: cell.radius)[0]
        dx = allcells[id].pos[0] - min_cell.pos[0]
        dy = allcells[id].pos[1] - min_cell.pos[1]
        # This can be adjusted, only uses the dx and dy
        return math.atan2(dx, dy)

    def rap(self, id, allcells):
        # Only avoid the largest cell
        max_cell = sorted(allcells, key = lambda cell: cell.radius)[-1]
        dx = max_cell.pos[0] - allcells[id].pos[0]
        dy = max_cell.pos[1] - allcells[id].pos[1]
        # This can be adjusted, only uses the dx and dy
        return math.atan2(dx, dy)

    def play_basketball(self):
        return 2 * math.pi * random.random()

    def strategy(self, id, allcells):
        rng = random.randint(0, 3)
        if rng == 0:
            return self.sing()
        elif rng == 1:
            return self.jump(id, allcells)
        elif rng == 2:
            return self.rap(id, allcells)
        else:
            return self.play_basketball()
