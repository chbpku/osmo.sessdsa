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

import random
import math
import traceback
import logging

from time import perf_counter as pf

from consts import Consts
from cell import Cell

class World():
    def __init__(self, player0, player1, names = None, recorders = None):
        # Variables and setup
        self.cells_count = 0
        # Bind stat recorders
        self.recorders = recorders
        # Init
        self.new_game()
        self.player = [player0, player1]
        self.names = names

    # Methods
    def new_game(self):
        """Create a new game.

        Args:
            
        Returns:
            

        """
        self.cells = [] # Array of cells
        self.frame_count = 0
        self.database = []
        self.timer = [Consts["MAX_TIME"], Consts["MAX_TIME"]]
        self.result = None
        # Define the players first
        self.cells.append(Cell(0, [Consts["WORLD_X"] / 4, Consts["WORLD_Y"] / 2], [0, 0], Consts["DEFAULT_RADIUS"]))
        self.cells.append(Cell(1, [Consts["WORLD_X"] / 4 * 3, Consts["WORLD_Y"] / 2], [0, 0], Consts["DEFAULT_RADIUS"]))
        # Generate a bunch of random cells
        for i in range(Consts["CELLS_COUNT"]):
            if i < 4:
                rad = 1.5 + (random.random() * 1.5) # Small cells
            elif i < 10:
                rad = 10 + (random.random() * 4) # Big cells
            else:
                rad = 2 + (random.random() * 9) # Everything else
            x = Consts["WORLD_X"] * random.random()
            y = Consts["WORLD_Y"] * random.random()
            cell = Cell(i + 2, [x, y], [(random.random() - 0.5) * 2, (random.random() - 0.5) * 2], rad)
            safe_dist = Consts["SAFE_DIST"] + rad
            while min(map(cell.distance_from, self.cells[:2])) < safe_dist:
                cell.pos = [
                    Consts["WORLD_X"] * random.random(),
                    Consts["WORLD_Y"] * random.random()
                ]
            self.cells.append(cell)
        # Update recorders
        self.update_recorders()

    def check_point(self, flag0, flag1, cause):
        """Checkpoint to determine if the game is over.

        Args:
            flag0: mark the status of player0.
            flag1: mark the status of player1.
            cause: reason for the end of the game.
        Returns:
            whether it's endgame.

        """
        if not flag0 and flag1:
            self.game_over(0, cause, (flag0, flag1))
        elif flag0 and not flag1:
            self.game_over(1, cause, (flag0, flag1))
        elif flag0 and flag1:
            self.game_over(-1, cause, (flag0, flag1))
        return bool(flag0 or flag1)

    def game_over(self, winner, cause, detail = None):
        """Game over.

        Args:
            winner: id of the winner.
            cause: reason for the end of the game.
        Returns:
            

        """
        self.result = {
            "players": self.names,
            "winner": winner,
            "cause": cause,
            "detail": detail,
            "data": self.database,
            "saved": False
        }
        print("Winner Winner Chicken Dinner!")
        if winner != -1:
            print("Winner: Player {}.".format(winner))
        else:
            print("Game ends in a draw.")
        print(cause)

    def eject(self, player, theta):
        """Create a new cell after the ejection process.

        Args:
            player: the player.
            theta: angle.
        Returns:
            

        """
        if player.dead or theta == None:
            return
        # Reduce force in proportion to area
        fx = math.sin(theta)
        fy = math.cos(theta)
        new_veloc_x = player.veloc[0] + Consts["DELTA_VELOC"] * fx * (1 - Consts["EJECT_MASS_RATIO"])
        new_veloc_y = player.veloc[1] + Consts["DELTA_VELOC"] * fy * (1 - Consts["EJECT_MASS_RATIO"])
        # Push player
        player.veloc[0] -= Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
        player.veloc[1] -= Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
        # Shoot off the expended mass in opposite direction
        newrad = player.radius * Consts["EJECT_MASS_RATIO"] ** 0.5
        # Lose some mass (shall we say, Consts["EJECT_MASS_RATIO"]?)
        player.radius *= (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5
        # Create new cell
        new_pos_x = player.pos[0] + fx * (player.radius + newrad)
        new_pos_y = player.pos[1] + fy * (player.radius + newrad)
        new_cell = Cell(len(self.cells), [new_pos_x, new_pos_y], [new_veloc_x, new_veloc_y], newrad)
        new_cell.stay_in_bounds()
        new_cell.limit_speed()
        self.cells.append(new_cell)

    def absorb(self, collision):
        """Performing the absorption process.

        Args:
            collision: all the cells that collided.
        Returns:
            

        """
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

    def update(self, frame_delta):
        """Create new frames.

        Args:
            frame_delta: time interval between two frames.
        Returns:
            

        """
        # Save
        self.database.append([c.copy() for c in self.cells])
        # New frame
        self.frame_count += 1
        if self.frame_count == Consts["MAX_FRAME"]: # Time's up
            self.check_point(self.cells[0].radius <= self.cells[1].radius, self.cells[0].radius >= self.cells[1].radius, "MAX_FRAME")
            return
        # Update recorders
        self.update_recorders()

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
        # If we just killed the player, Game over
        if self.check_point(self.cells[0].dead, self.cells[1].dead, "PLAYER_DEAD"):
            return
        # Eject!
        allcells = [cell for cell in self.cells if not cell.dead]
        self.cells_count = len(allcells)

        theta = [None, None]
        flag = [False, False]

        for i in 0, 1:
            try:
                ti = pf()
                theta[i] = self.player[i].strategy([c.copy() for c in allcells])
                tf = pf()
                self.timer[i] -= tf - ti
            except Exception as e:
                logging.error(traceback.format_exc())
                flag[i] = e

        if self.check_point(flag[0], flag[1], "RUNTIME_ERROR"):
            return

        if self.check_point(not isinstance(theta[0], (int, float, type(None))), not isinstance(theta[1], (int, float, type(None))), "INVALID_RETURN_VALUE"):
            return

        if self.check_point(self.timer[0] < 0, self.timer[1] < 0, "TIMEOUT"):
            return

        self.eject(self.cells[0], theta[0])
        self.eject(self.cells[1], theta[1])

    def update_recorders(self):
        """Put values into recorders.

        Args:
        
        Returns:
    
        """
        if not self.recorders:
            return
        for i, rec in enumerate(self.recorders):
            rec.frame = self.frame_count # Current frame
            rec.cells_count = len(self.cells)
            rec.timer = self.timer[:]


class WorldStat:
    def __init__(self, frames):
        self.total_frames = frames
        self.frame = 0
        self.timer = [Consts["MAX_TIME"]] * 2
