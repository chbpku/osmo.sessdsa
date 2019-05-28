#!/usr/bin/env python3

#####################################################
#                                                   #
#     ______        _______..___  ___.   ______     #
#    /  __  \      /       ||   \/   |  /  __  \    #
#   |  |  |  |    |   (----`|  \  /  | |  |  |  |   #
#   |  |  |  |     \   \    |  |\/|  | |  |  |  |   #
#   |  `--"  | .----)   |   |  |  |  | |  `--"  |   #
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

from multiprocessing import Process, Queue, cpu_count
from platform import system

import time
import json
import os, sys
# 屏蔽AI自带print
class null_stream:
    def read(*args):
        pass

    def write(*args):
        pass

    def flush(*args):
        pass

console = sys.stdout
def log(*args):
    console.write(*args)
    console.flush()
console.log = log
sys.stdout = null_stream

from consts import Consts
from world import World, WorldStat
from database import Database

rounds = 20
max_name_length = 10

class Match():
    def __init__(self, players):
        self.players = players
        self.player_names = [all_players[players[i][0]][players[i][1]] for i in [0, 1]]
        self.no_opponent = "" in self.player_names
        self.match_id = None
        self.result = []
        self.score = [0, 0]
        self.finished = False

    def run_match(self, data_queue, rounds):
        """
        子进程执行两玩家多局对决
    
        params:
            data_queue - 数据队列
            path - 玩家模块所在路径
            names - 玩家名称
            log_format - 记录文件名格式
                比赛记录将保存为log_format % (*names, index)路径
        """
        # 读取玩家
        if self.no_opponent:
            data_queue.put((self.match_id, "FINISHED"))
            return
        players = [__import__(n).Player for n in self.player_names]
        storages = [{}, {}]
        for i in range(rounds):
            # Recorders
            recorders = [WorldStat(Consts["MAX_FRAME"]) for i in "xx"]
            for s, r in zip(storages, recorders):
                s["world"] = r
            # Random seed
            if rounds % 2 == 0:
                seed = int(time.time())
            # World
            world = World(
                players[0](0, storages[0]), players[1](1, storages[1]), ["Plr1", "Plr2"], recorders, seed
            )
    
            while not world.result:
                # Advance timer
                world.update(Consts["FRAME_DELTA"])
            else:
                #database = Database()
                #database.save_game(world.result["data"])
                data_queue.put((self.match_id, world.result))
        data_queue.put((self.match_id, "FINISHED"))

    def __str__(self):
        return self.player_names[0].ljust(max_name_length + 1) \
            + str(self.score[0]) + ":" + str(self.score[1]) \
            + self.player_names[1].rjust(max_name_length + 1) + "\n"

class MultiTask():
    # 初始化环境
    def __init__(self, team, matches):

        # 常量参数
        self.MAX_TASKS = 16  # 最大子进程数
        #self.LOG_FORMAT = team + "/log/%s-%s(%d).zlog"
        #self.AI_PATH = os.path.abspath(team)

        # 数据结构
        # 进程队列初始化
        self.data_queue = Queue()

        self.all_tasks = []
        self.waiting_tasks = []
        # 生成赛制顺序
        for index, players in enumerate(matches):
            match = Match(players)
            match.match_id = index
            self.all_tasks.append(match)
            self.waiting_tasks.append(match)

        # 当前任务池
        self.running_tasks = []

    # 函数定义
    def flush_queue(self):
        """
        清空队列内容并进行统计
        """
        while not self.data_queue.empty():
            match_id, result = self.data_queue.get()
            if result == "FINISHED":
                self.all_tasks[match_id].finished = True
            else:
                self.all_tasks[match_id].result.append(result)
                if result["winner"] != -1:
                    self.all_tasks[match_id].score[result["winner"]] += 1

    def visualize(self, file = sys.__stdout__):
        """
        可视化比赛过程

        params:
            file - 输出流
        """

    def run(self):
        # 主事件循环
        while True:

            # 0. 清空队列缓冲区
            self.flush_queue()

            # 1. 移除已结束任务
            for process in self.running_tasks:
                if not process.is_alive():
                    task = None
            self.running_tasks = [task for task in self.running_tasks if task]

            # 2. 加入新任务
            while self.waiting_tasks and len(self.running_tasks) < self.MAX_TASKS:
                match = self.waiting_tasks.pop()
                process = Process(
                    target = match.run_match, args = (self.data_queue, rounds)
                )
                process.start()
                self.running_tasks.append(process)

            # 3. 可视化
            self.visualize()
            time.sleep(0.5)
            for match in self.all_tasks:
                console.log(str(match))

            # 4. 若运行完毕则跳出
            if not self.running_tasks:
                break

if __name__ == "__main__":
    console.log("使用方法")
    all_players = json.loads(open("schedule/group.json", "r").read())
    for group, members in all_players.items():
        members += [""] * (8 - len(members))
    all_matches = {
        "group_stage": {
            "round1": [],
            "round2": [],
            "round3": []
        },
        "final_stage": {
            "8th_final": [],
            "quarter_final": [],
            "semi_final": [],
            "final": []
        }
    }
    for i in [chr(65 + j) for j in range(8)]:
        all_matches["group_stage"]["round1"] += [[[i, 0], [i, 1]], [[i, 2], [i, 3]]]
        all_matches["group_stage"]["round2"] += [[[i, 0], [i, 2]], [[i, 1], [i, 3]]]
        all_matches["group_stage"]["round3"] += [[[i, 0], [i, 3]], [[i, 1], [i, 2]]]
    while True:
        console.log("\n>>> ")
        command = input()
        path = os.path.abspath("./tmp")
        sys.path.append(path)
        if (command == "L"):
            console.write(str(all_matches))
            console.flush()
        if (command == "R1"):
            multitask = MultiTask("F", all_matches["group_stage"]["round1"])
            multitask.run()
