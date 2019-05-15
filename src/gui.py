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

import tkinter as tk
from platform import system
import math
import time

from consts import Consts
from settings import Settings
from world import World

from sample.brownian_motion import Player as Player0
from sample.cxk import Player as Player1

from database import Database

class Application(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.master = master
        self.master.title("Osmo")
        if Settings["ENABLE_DATABASE"]:
            self.world = World(Player0(0), Player1(1), Database())
        else:
            self.world = World(Player0(0), Player1(1))
        self.paused = False
        # For timer
        self.frame_delta = None
        self.last_tick = int(round(time.time() * 1000))
        # For GUI
        self.pack()
        self.create_widgets()
        self.create_canvas()
        self.create_event_listener()
        # Loop
        self.master.after(int(1000 / Consts["FPS"]), self.refresh_screen)

    def play(self):
        self.paused = not self.paused
        self.widget["play"]["text"] = "PLAY" if self.paused else "PAUSE"

    def reset(self):
        self.world.new_game()

    def create_widgets(self):
        self.widget = {}
        self.widget["play"] = tk.Button(self, text = "PAUSE", command = self.play)
        self.widget["play"].pack(side = "left")
        self.widget["reset"] = tk.Button(self, text = "RESET", command = self.reset)
        self.widget["reset"].pack(side = "left")
        self.cells_count = tk.StringVar()
        self.widget["cells_count"] = tk.Label(self, textvariable = self.cells_count)
        self.widget["cells_count"].pack(side = "left")
        self.frame_count = tk.StringVar()
        self.widget["frame_count"] = tk.Label(self, textvariable = self.frame_count)
        self.widget["frame_count"].pack(side = "left")

    def create_canvas(self):
        self.canvas = tk.Canvas(self.master, bg = "blue", width = Consts["WORLD_X"], height = Consts["WORLD_Y"])
        self.canvas.pack()

    def create_event_listener(self):
        self.canvas.bind("<Button-1>", self.on_click)
        if system() != "Darwin":
            self.canvas.bind("<MouseWheel>", self.on_mousewheel)

    def on_click(self, event):
        cell = self.world.cells[0]
        theta = math.atan2(event.x - cell.pos[0], event.y - cell.pos[1])
        self.world.eject(cell, theta)

    def on_mousewheel(self, event):
        print(event.delta)

    def refresh_screen(self):
        # Advance timer
        current_tick = int(round(time.time() * 1000))
        self.frame_delta = (current_tick - self.last_tick) * Consts["FPS"] / 1000
        self.last_tick = current_tick
        self.master.after(int(1000 / Consts["FPS"]), self.refresh_screen)
        if self.paused:
            return
        # Update Label
        self.cells_count.set("COUNT:" + str(self.world.cells_count))
        self.frame_count.set("FRAME:" + str(self.world.frame_count))
        # Update World
        self.world.update(Consts["FRAME_DELTA"])
        # Clear canvas
        self.canvas.delete("all")
        for cell in self.world.cells:
            if cell.dead:
                continue
            color = "green" if cell.id <= 1 else "cyan"
            coords = [
                cell.pos[0] - cell.radius,
                cell.pos[1] - cell.radius,
                cell.pos[0] + cell.radius,
                cell.pos[1] + cell.radius
            ]
            range_x = [0]
            range_y = [0]
            if coords[0] < 0:
                range_x.append(1)
            if coords[1] < 0:
                range_y.append(1)
            if coords[2] > Consts["WORLD_X"]:
                range_x.append(-1)
            if coords[3] > Consts["WORLD_Y"]:
                range_y.append(-1)
            for i in range_x:
                for j in range_y:
                    self.canvas.create_oval(
                        coords[0] + i * Consts["WORLD_X"],
                        coords[1] + j * Consts["WORLD_Y"],
                        coords[2] + i * Consts["WORLD_X"],
                        coords[3] + j * Consts["WORLD_Y"],
                        fill = color, outline = ""
                    )
            #self.canvas.create_text(cell.pos, fill = "darkblue", font = "Times 20 italic bold", text = "@")

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master = root)
    app.mainloop()
