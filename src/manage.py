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
import os, sys, shutil
import traceback, time, json, requests

from consts import Consts
from world import World, WorldStat
from database import Database

ROUNDS_COUNT = 20
ROUNDS_COUNT_K = 50
GROUP_OP = 2

max_name_length = 10


def reset_folder(path):
    shutil.rmtree(path, True)
    os.makedirs(path, exist_ok=True)


def run_match(data_queue, task_queue, is_k=False):
    """
        子进程执行两玩家多局对决

        params:
            data_queue - 数据队列
            task_queue - 
    """
    while not task_queue.empty():
        try:
            rounds_count, rounds, player_index, player_names = task_queue.get()
            # 读取玩家
            codes = [__import__(n) for n in player_names]
            for n in codes:
                n.print = lambda *a, **kw: 0
            players = [n.Player for n in codes]
            storages = [{}, {}]
            counter = {0: 0, 1: 0, -1: 233}
            seed = None
            i = 0
            while i < rounds_count:
                # Recorders
                recorders = [WorldStat(Consts["MAX_FRAME"]) for i in "xx"]
                for s, r in zip(storages, recorders):
                    s["world"] = r
                # Random seed
                if seed is None:
                    seed = int(time.time())
                    # World
                    world = World(players[0](0, storages[0]), players[1](
                        1, storages[1]), player_names, recorders, seed)
                else:
                    seed = None
                    world = World(players[1](0, storages[1]), players[0](
                        1, storages[0]), player_names[::-1], recorders, seed)

                while not world.result:
                    # Advance timer
                    world.update(Consts["FRAME_DELTA"])
                else:
                    database = Database(
                        rounds + "/" + str(player_names) + "-" + str(i))
                    database.save_game(world)
                    del world.result["data"]
                    data_queue.put((player_index, world.result))
                i += 1

                # 加赛
                if is_k:
                    res = world.result["winner"]
                    if i % 2:
                        res = 1 - res
                    counter[res] += 1
                    if i == rounds_count and counter[0] == counter[1]:
                        rounds_count += 2
            data_queue.put((player_index, "FINISHED"))

        except:
            print("WORKER ERROR")
            traceback.print_exc()
    print("WORKER END")


class Match():
    def __init__(self, players, rounds):
        self.players = players
        self.rounds = rounds
        self.index = players.split("-")
        self.player_names = [
            PLAYER_NAMES[self.index[i][0]][int(self.index[i][1])]
            for i in [0, 1]
        ]
        self.no_opponent = "" in self.player_names
        self.score = [0, 0]
        self.finished = False
        self.started = False

    def __str__(self):
        if self.no_opponent:
            return ''

        if not self.started:
            return self.player_names[0].ljust(max_name_length + 2) \
            + "-----" \
            + self.player_names[1].rjust(max_name_length + 2)

        if self.finished:
            return self.player_names[0].ljust(max_name_length + 2) \
            + str(self.score[0]).ljust(2) + ":" + str(self.score[1]).rjust(2) \
            + self.player_names[1].rjust(max_name_length + 2)

        return self.player_names[0].ljust(max_name_length + 1) \
            + '>' + str(self.score[0]).ljust(2) + ":" + str(self.score[1]).rjust(2) + '<' \
            + self.player_names[1].rjust(max_name_length + 1)


class MultiTask():
    # 初始化环境
    def __init__(self, team, all_matches, stage, rounds):
        # 进程队列初始化
        self.data_queue = Queue()
        reset_folder('data/' + rounds)
        self.all_tasks = {}
        self.waiting_tasks = []
        self.all_matches = all_matches
        self.stage = stage
        self.rounds = rounds
        # 生成赛制顺序
        for players in self.all_matches[self.stage][self.rounds]:
            match = Match(players, self.rounds)
            self.all_tasks[players] = match
            self.waiting_tasks.append(match)

        # 当前任务池
        self.running_tasks = []

    # 函数定义
    def flush_queue(self):
        """
        清空队列内容并进行统计
        """
        if self.data_queue.empty():
            return

        while not self.data_queue.empty():
            players, result = self.data_queue.get()
            self.all_tasks[players].started = True
            if result == "FINISHED":
                self.all_tasks[players].finished = True

            elif result["winner"] != -1:
                if result["players"][0] == self.all_tasks[
                        players].player_names[0]:
                    self.all_tasks[players].score[result["winner"]] += 1
                else:
                    self.all_tasks[players].score[1 - result["winner"]] += 1

        self.visualize("obs/record.txt")

    def visualize(self, filename=None):
        """
        可视化比赛过程

        params:
            filename - 输出流
        """
        output = ''
        for players, match in self.all_tasks.items():
            self.all_matches[self.stage][self.rounds][players] = match.score
            tmp = str(match)
            output += tmp
            if tmp:
                output += "\n"
        with open(filename, "w") as f:
            f.write(output)
        with open("schedule/all_matches.json", "w") as f:
            json.dump(self.all_matches, f)
        try:
            requests.get('http://162.105.17.143:9580/billboard', {
                'op': GROUP_OP,
                'data': output
            })
        except:
            pass

    def run(self, is_k=False):
        # task queue
        task_queue = Queue()
        rounds = ROUNDS_COUNT_K if is_k else ROUNDS_COUNT
        while self.waiting_tasks:
            match = self.waiting_tasks.pop()
            if match.no_opponent:
                self.data_queue.put((match.players, "FINISHED"))
                continue
            task_queue.put((rounds, match.rounds, match.players,
                            match.player_names))

        # workers
        workers = [
            Process(
                target=run_match, args=(self.data_queue, task_queue, is_k))
            for i in range(cpu_count())
        ]

        for proc in workers:
            proc.start()

        while sum(proc.is_alive() for proc in workers):
            print(sum(proc.is_alive() for proc in workers))
            self.flush_queue()

            print("\n" + str(time.time()) + "\n===========================")
            output = ''
            for players, match in self.all_tasks.items():
                tmp = str(match)
                output += tmp
                if tmp:
                    output += "\n"
            print(output)
            time.sleep(2)
        self.flush_queue()


if __name__ == "__main__":
    path = os.path.abspath("./code")
    sys.path.append(path)
    #print("使用方法")
    try:
        PLAYER_NAMES = json.loads(open("schedule/group.json", "r").read())
    except:
        PLAYER_NAMES = {}
    for group, members in PLAYER_NAMES.items():
        members += [""] * (8 - len(members))

    try:
        ALL_MATCHES = json.loads(open("schedule/all_matches.json", "r").read())
    except:
        ALL_MATCHES = {
            "group_stage": {
                "round1": {},
                "round2": {},
                "round3": {}
            },
            "final_stage": {
                "8th_final": {},
                "quarter_final": {},
                "semi_final": {},
                "3_4_final": {},
                "final": {}
            }
        }
        for i in [chr(65 + j) for j in range(8)]:
            ALL_MATCHES["group_stage"]["round1"].update({
                i + "0-" + i + "1":
                None,
                i + "2-" + i + "3":
                None
            })
            ALL_MATCHES["group_stage"]["round2"].update({
                i + "0-" + i + "2":
                None,
                i + "1-" + i + "3":
                None
            })
            ALL_MATCHES["group_stage"]["round3"].update({
                i + "0-" + i + "3":
                None,
                i + "1-" + i + "2":
                None
            })

    R_fin = [
        None not in ALL_MATCHES["group_stage"]["round" + str(i)]
        for i in range(1, 4)
    ]
    K_fin = False
    K_pre = False

    while True:
        command = input("\n>>> ")
        try:
            if command == "L":
                print(PLAYER_NAMES)
                print(ALL_MATCHES)

            elif command[0] == "R":  # 小组赛
                if not (len(command) == 2 and command[1] in '123'):
                    continue
                rounds = int(command[1]) - 1
                if R_fin[rounds]:
                    choice = input(
                        "R{} is done now, do you want to run again? You will lose all saved data. [Y/N]".
                        format(command[1]))
                    if choice != "Y":
                        continue
                multitask = MultiTask("F", ALL_MATCHES, "group_stage",
                                      "round" + command[1])
                multitask.run()
                R_fin[rounds] = True

            elif command == "S":  # 淘汰赛前出线
                # 小组赛后统分
                tot_score = {
                    ch: [[0] * 6 for i in range(4)]
                    for ch in "ABCDEFGH"
                }
                all_group_stage = {
                    **ALL_MATCHES["group_stage"]["round1"],
                    **ALL_MATCHES["group_stage"]["round2"],
                    **ALL_MATCHES["group_stage"]["round3"]
                }
                for plrs, score in all_group_stage.items():
                    if score == [0, 0]:
                        continue
                    plrs = plrs.split('-')
                    for i in range(2):
                        d_score = [
                            1,
                            score[i] > score[1 - i],
                            score[i] < score[1 - i],
                            score[i] == score[1 - i],
                            score[i],
                            score[1 - i],
                        ]
                        for j in range(6):
                            tot_score[plrs[i][0]][int(
                                plrs[i][1])][j] += d_score[j]

            elif command == "K8":  # 16进8
                if K_pre or not R_fin == [1, 1, 1]:
                    print("!")
                    continue
                ranking = {i: [None for j in range(4)] for i in "ABCDEFGH"}
                named_score = [[[
                    i + str(j),
                    (tot_score[i][j][1] * 3 + tot_score[i][j][3] * 1),
                    tot_score[i][j][4]
                ] for j in range(4)] for i in "ABCDEFGH"]
                for lst in named_score:
                    lst.sort(key=lambda x: -x[2])
                    lst.sort(key=lambda x: -x[1])
                for i in range(4):
                    a_lst = [0, 2, 4, 6]
                    b_lst = [1, 3, 5, 7]
                    ALL_MATCHES["final_stage"]["8th_final"].update({
                        named_score[a_lst[i]][0][0] + "-" + named_score[b_lst[i]][1][0]:
                        None,
                        named_score[a_lst[i]][1][0] + "-" + named_score[b_lst[i]][0][0]:
                        None
                    })

                multitask = MultiTask("F", ALL_MATCHES, "final_stage",
                                      "8th_final")
                multitask.run(1)

            elif command == "K4":  # 8进4
                fighters = []
                for plrs, score in ALL_MATCHES["final_stage"][
                        "8th_final"].items():
                    plrs = plrs.split('-')
                    if score[0] > score[1]:
                        fighters.append(plrs[0])
                    else:
                        fighters.append(plrs[1])
                    if len(fighters) == 2:
                        ALL_MATCHES["final_stage"]["quarter_final"][
                            fighters[0] + "-" + fighters[1]] = None
                        fighters = []
                multitask = MultiTask("F", ALL_MATCHES, "final_stage",
                                      "quarter_final")
                multitask.run(1)
                winners = []
                for plrs, score in ALL_MATCHES["final_stage"][
                        "quarter_final"].items():
                    plrs = plrs.split('-')
                    if score[0] > score[1]:
                        winners.append(plrs[0])
                    else:
                        winners.append(plrs[1])
                print("Winners:", winners)
            elif command == "K2":  # 4 to 2
                fighters = []
                for plrs, score in ALL_MATCHES["final_stage"][
                        "quarter_final"].items():
                    plrs = plrs.split('-')
                    if score[0] > score[1]:
                        fighters.append(plrs[0])
                    else:
                        fighters.append(plrs[1])
                    if len(fighters) == 2:
                        ALL_MATCHES["final_stage"]["semi_final"][
                            fighters[0] + "-" + fighters[1]] = None
                        fighters = []
                multitask = MultiTask("F", ALL_MATCHES, "final_stage",
                                      "semi_final")
                multitask.run(1)
                winners = []
                for plrs, score in ALL_MATCHES["final_stage"][
                        "semi_final"].items():
                    plrs = plrs.split('-')
                    if score[0] > score[1]:
                        winners.append(plrs[0])
                    else:
                        winners.append(plrs[1])
                print("Winners:", winners)
            elif command == "3-4 FINAL":  # 3 vs 4
                fighters = []
                for plrs, score in ALL_MATCHES["final_stage"][
                        "semi_final"].items():
                    plrs = plrs.split('-')
                    if score[0] < score[1]:
                        fighters.append(plrs[0])
                    else:
                        fighters.append(plrs[1])
                    if len(fighters) == 2:
                        ALL_MATCHES["final_stage"]["3_4_final"][
                            fighters[0] + "-" + fighters[1]] = None
                        fighters = []
                multitask = MultiTask("F", ALL_MATCHES, "final_stage",
                                      "3_4_final")
                multitask.run(1)
                winners = []
                for plrs, score in ALL_MATCHES["final_stage"][
                        "3_4_final"].items():
                    plrs = plrs.split('-')
                    if score[0] > score[1]:
                        winners.append(plrs[0])
                    else:
                        winners.append(plrs[1])
                print("Winner:", winners)
            elif command == "FINAL":  # final champion
                fighters = []
                for plrs, score in ALL_MATCHES["final_stage"][
                        "semi_final"].items():
                    plrs = plrs.split('-')
                    if score[0] > score[1]:
                        fighters.append(plrs[0])
                    else:
                        fighters.append(plrs[1])
                    if len(fighters) == 2:
                        ALL_MATCHES["final_stage"]["final"][fighters[0] + "-" +
                                                            fighters[1]] = None
                        fighters = []
                multitask = MultiTask("F", ALL_MATCHES, "final_stage", "final")
                multitask.run(1)
                winners = []
                for plrs, score in ALL_MATCHES["final_stage"]["final"].items():
                    plrs = plrs.split('-')
                    if score[0] > score[1]:
                        winners.append(plrs[0])
                    else:
                        winners.append(plrs[1])
                print("Winner:", winners)
            else:  # 调试用
                print(repr(eval(command)))
        except:
            traceback.print_exc()
            raise
