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

import time

from consts import Consts
from settings import Settings
from world import World

from sample.brownian_motion import Player as Player0
from sample.cxk import Player as Player1

from database import Database

if __name__ == "__main__":
    world = World(Player0(0), Player1(1))
    # For timer
    frame_delta = None
    last_tick = int(round(time.time() * 1000))

    while not world.result:
        # Advance timer
        current_tick = int(round(time.time() * 1000))
        frame_delta = (current_tick - last_tick) * Consts["FPS"] / 1000
        last_tick = current_tick
        world.update(Consts["FRAME_DELTA"])
    else:
        if Settings["ENABLE_DATABASE"] and not world.result["saved"]:
            database = Database()
            database.save_game(world.result["data"])
            world.result["saved"] = True
