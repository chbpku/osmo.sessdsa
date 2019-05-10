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

import random
import math

from consts import Consts
from cell import Cell

class World():
    def __init__(self):
        # Variables and setup
        self.cells = [] # Array of cells
        self.result = None
        # Init
        self.load_game()

    # Methods
    def load_game(self):
        self.cells = []
        # Define the players first
        self.cells.append(Cell([Consts["WORLD_X"] / 4, Consts["WORLD_Y"] / 2], [0, 0], 30, isplayer = True))
        self.cells.append(Cell([Consts["WORLD_X"] / 4 * 3, Consts["WORLD_Y"] / 2], [0, 0], 30, isplayer = True))
        # Generate a bunch of random cells
        for i in range(Consts["CELLS_COUNT"]):
            if i < 4:
                rad = 3 + (random.random() * 3) # Small cells
            elif i < 6:
                rad = 20 + (random.random() * 8) # Big cells
            else:
                rad = 4 + (random.random() * 18) # Everything else
            ang = random.random() * 2 * math.pi
            x = Consts["WORLD_X"] * random.random()
            y = Consts["WORLD_Y"] * random.random()
            cell = Cell([x, y], [(random.random() - 0.5) * 0.35, (random.random() - 0.5) * 0.35], rad)
            self.cells.append(cell)

    def eject(self, player, theta):
        # Reduce force in proportion to area
        fx = math.sin(theta)
        fy = math.cos(theta)
        # DELTA_VELOC
        delta_veloc_x = Consts["DELTA_VELOC"] * fx / Consts["EJECT_MASS_RATIO"]
        delta_veloc_y = Consts["DELTA_VELOC"] * fy / Consts["EJECT_MASS_RATIO"]
        # Push player
        new_veloc_x = player.veloc[0] + delta_veloc_x * (1 - Consts["EJECT_MASS_RATIO"])
        new_veloc_y = player.veloc[1] + delta_veloc_y * (1 - Consts["EJECT_MASS_RATIO"])
        player.veloc[0] -= delta_veloc_x * Consts["EJECT_MASS_RATIO"]
        player.veloc[1] -= delta_veloc_y * Consts["EJECT_MASS_RATIO"]
        # Shoot off the expended mass in opposite direction
        newrad = player.radius * Consts["EJECT_MASS_RATIO"] ** 0.5
        # Lose some mass (shall we say, Consts["EJECT_MASS_RATIO"]?)
        player.radius *= (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5
        new_pos_x = player.pos[0] + fx * (player.radius + newrad)
        new_pos_y = player.pos[1] + fy * (player.radius + newrad)
        newcell = Cell([new_pos_x, new_pos_y], [new_veloc_x, new_veloc_y], newrad)
        newcell.stay_in_bounds()
        newcell.limit_speed()
        self.cells.append(newcell)

    def absorb(self, collision):
        # Calculate total momentum and mass
        mass = sum(self.cells[ele].area() for ele in collision)
        px = sum(self.cells[ele].area() * self.cells[ele].veloc[0] for ele in collision)
        py = sum(self.cells[ele].area() * self.cells[ele].veloc[1] for ele in collision)
        # Determine the biggest cell
        collision.sort(key = lambda ele: self.cells[ele].radius)
        biggest = collision.pop()
        self.cells[biggest].radius = (mass / math.pi) ** 0.5
        self.cells[biggest].veloc[0] = px / mass
        self.cells[biggest].veloc[1] = py / mass
        for ele in collision:
            self.cells[ele].dead = True
            # If we just killed the player, Game over
            if self.cells[ele].isplayer:
                self.game_over(ele)

    def game_over(self, loser):
        self.result = True
        print("Player {} lost".format(loser))

    def update(self, frame_delta):
        # New frame
        for cell in self.cells:
            if not cell.dead:
                cell.move(frame_delta)
        # Detect collisions
        collisions = []
        for i in range(len(self.cells)):
            if self.cells[i].dead:
                continue
            for j in range(i + 1, len(self.cells)):
                if not self.cells[j].dead and self.cells[i].collide(self.cells[j]):
                    if self.cells[i].collide_group == None == self.cells[j].collide_group:
                        self.cells[i].collide_group = self.cells[j].collide_group = len(collisions)
                        collisions.append([i, j])
                    elif self.cells[i].collide_group != None == self.cells[j].collide_group:
                        collisions[self.cells[i].collide_group].append(j)
                        self.cells[j].collide_group = self.cells[i].collide_group
                    elif self.cells[i].collide_group == None != self.cells[j].collide_group:
                        collisions[self.cells[j].collide_group].append(i)
                        self.cells[i].collide_group = self.cells[j].collide_group
                    elif self.cells[i].collide_group != self.cells[j].collide_group:
                        collisions[self.cells[i].collide_group] += collisions[self.cells[j].collide_group]
                        for ele in collisions[self.cells[j].collide_group]:
                            self.cells[ele].collide_group = self.cells[i].collide_group
                        collisions[self.cells[j].collide_group] = []
        # Run absorbs
        for collision in collisions:
            if collision != []:
                self.absorb(collision)
