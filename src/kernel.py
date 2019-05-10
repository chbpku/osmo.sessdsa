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

import time

from consts import Consts
from player import Player
from world import World

if __name__ == "__main__":
    world = World()
    # For timer
    frame_delta = None
    last_tick = int(round(time.time() * 1000))

    while not world.result:
        # Advance timer
        current_tick = int(round(time.time() * 1000))
        frame_delta = (current_tick - last_tick) * Consts["FPS"] / 1000
        last_tick = current_tick
        world.update(Consts["FRAME_DELTA"])
