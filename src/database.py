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

import sqlite3
import time
import os


def _repr_e(e):
    """Save the state of the cells in a frame.

    Args:
        e: an Exception object or not.

    Returns:
        Exception: "(Line X) {type}: {contnet}"
        else: e itself
            
    """
    if not isinstance(e, Exception):
        return e
    res = '%s: %s' % (type(e).__name__, e)
    if e.__traceback__:
        tb = e.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        res = 'Line %s %s' % (tb.tb_lineno, res)
    return res


class Database():
    def __init__(self, filename, arg=None):
        self.connect = sqlite3.connect("data/" + filename + ".db")
        self.cursor = self.connect.cursor()
        self.cursor.execute("""CREATE TABLE META
        (
            ID TEXT NOT NULL PRIMARY KEY,
            CONTENT TEXT
        );""")

    def save_frame(self, frame_count, allcells):
        """Save the state of the cells in a frame.

        Args:
            frame_count: the index of current frame.
            allcells: list of all cells.
        Returns:
            

        """
        self.cursor.execute("""CREATE TABLE FRAME_{}
        (
            ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            X  REAL    NOT NULL,
            Y  REAL    NOT NULL,
            VX REAL    NOT NULL,
            VY REAL    NOT NULL,
            R  REAL    NOT NULL
        );""".format(frame_count))
        for cell in allcells:
            if not cell.dead:
                self.cursor.execute(
                    "INSERT INTO FRAME_{} (X, Y, VX, VY, R) VALUES (?, ?, ?, ?, ?);".
                    format(frame_count), [
                        cell.pos[0], cell.pos[1], cell.veloc[0], cell.veloc[1],
                        cell.radius
                    ])
        # self.connect.commit()

    def save_game(self, world):
        """Save the state of the cells in the game.

        Args:
            world: the world to save.
        Returns:
            

        """
        data = world.result['data']
        for i in range(len(data)):
            self.save_frame(i, data[i])
        self.save_meta('size', len(data))
        world.result["detail"] = [_repr_e(x) for x in world.result["detail"]]
        for x in "players", "winner", "cause", "detail":
            self.save_meta(x, world.result[x])
        self.connect.commit()
        self.connect.close()

    def save_meta(self, type, obj):
        """Save the meta information of the game.

        Args:
            type: information type.
            obj: info object to save.
        Returns:
            

        """
        self.cursor.execute("INSERT INTO META (ID, CONTENT) VALUES (?, ?);",
                            [type, repr(obj)])
