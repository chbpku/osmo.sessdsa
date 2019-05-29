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
from settings import Settings
from world import World, WorldStat

from sample.brownian_motion import Player as Player0
from sample.cxk import Player as Player1

from database import Database

if __name__ == "__main__":
    # Storage across rounds
    storages = [{}, {}]

    while True:
        # Recorders
        recorders = [WorldStat(Consts["MAX_FRAME"]) for i in 'xx']
        for s, r in zip(storages, recorders):
            s['world'] = r
        # World
        world = World(
            Player0(0, storages[0]), Player1(1, storages[1]), ['Plr1', 'Plr2'],
            recorders)

        while not world.result:
            # Advance timer
            world.update(Consts["FRAME_DELTA"])
        else:
            if Settings["ENABLE_DATABASE"] and not world.result["saved"]:
                database = Database()
                database.save_game(world.result["data"])
                world.result["saved"] = True
