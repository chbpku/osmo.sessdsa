from consts import Consts
import math


class Player():

    def __init__(self, id, arg=None):
        self.id = id
        self.radius = 15
        self.pos = [0, 0]
        self.veloc = [0, 0]
        self.oppo = int(1 - id)  # 对手的id
        self.counter = 0  # 静止计数器
        self.adjacentRange = 7  # 邻近范围
        self.jet = 0  # 喷射计数器
        self.orientation = 0  # 喷射方向
        self.radius = 15
        self.pos = [0, 0]
        self.veloc = [0, 0]
        self.target = None

    def strategy(self, allcells):
        relaCells = list(self.relaInfo(allcells))
        self.adjacentRange = self.adjacentRangeCal()
        adjacent = list(self.adjacentInfo(relaCells))
        dangerCell = self.safeCheck(adjacent)
        return self.ejectJudge(dangerCell, adjacent, relaCells)

    class Cell():
        # 补一个Cell类

        def __init__(self, id=None, pos=[0, 0], veloc=[0, 0], radius=5):
            # ID to judge Player or free particle
            self.id = id
            # Variables to hold current position
            self.pos = pos
            # Variables to hold current velocity
            self.veloc = veloc
            # Variables to hold size
            self.radius = radius

    def relaInfo(self, originCells):
        # 修正为自己不动，在最中间, 返回其他星体的参数(以自己为新的坐标原点)
        relaCells = []
        self.radius = originCells[self.id].radius
        self.pos = originCells[self.id].pos
        self.veloc = originCells[self.id].veloc
        for cell in originCells:
            if not cell.dead:
                rpx = cell.pos[0] - self.pos[0]
                rpy = cell.pos[1] - self.pos[1]
                rvx = cell.veloc[0] - self.veloc[0]
                rvy = cell.veloc[1] - self.veloc[1]
                if rpx > Consts["WORLD_X"] / 2:
                    rpx -= Consts["WORLD_X"]
                if rpx < -Consts["WORLD_X"] / 2:
                    rpx += Consts["WORLD_X"]
                if rpy > Consts["WORLD_Y"] / 2:
                    rpy -= Consts["WORLD_Y"]
                if rpy < -Consts["WORLD_Y"] / 2:
                    rpy += Consts["WORLD_Y"]
                tmp = self.Cell(cell.id, [rpx, rpy], [rvx, rvy], cell.radius)
                relaCells.append(tmp)
        return relaCells

    def adjacentRangeCal(self):
        # 根据不同的半径考虑不同的邻近范围
        if self.radius < 25:
            return 15 + self.radius * 7
        elif self.radius < 35:
            return 40 + self.radius * 7
        else:
            return 80 + self.radius * 7

    def adjacentInfo(self, cells):
        # 侦测周边星体 (半径adjacentRange以内)，返回一个列表
        adjacent = []
        for cell in cells:
            largerange = self.adjacentRange * 1.5
            if abs(cell.pos[0]) + abs(cell.pos[1]) < largerange:

                if (cell.pos[0] ** 2 + cell.pos[1] ** 2) ** 0.5 < self.adjacentRange:

                    if cell.radius > 3 + cells[self.id].radius * 0.1:
                        adjacent.append(cell)
        return adjacent

    def ejectJudge(self, dangerCell, adjacent, allcells):
        # 判断喷射
        if list(dangerCell) == []:
            # safe
            if self.jet > 0:
                self.jet -= 1
                if self.jet == 0:
                    self.counter = self.idleJudge(adjacent)
                return self.orientation
            if self.counter > 0:
                self.counter = self.counter - 1
                return None
            self.chase(adjacent, allcells)
            return self.orientation
        else:
            # dangerous
            self.escape(dangerCell)
            self.counter = 0
            return self.orientation

    def safeCheck(self, adjacent):
        # 返回一个列表，为不能喷射的指向，没有危险返回None
        dangerCell = []
        for cell in adjacent:
            if cell.radius > self.radius * 0.98 and not cell.id == self.id:
                distance = (cell.pos[0] ** 2 + cell.pos[1] ** 2) ** 0.5
                speed_1 = cell.veloc[0] ** 2 + cell.veloc[1] ** 2
                if distance < self.radius * 2 + cell.radius * 2 + speed_1 * 50:
                    if self.isDanger(cell, distance):
                        dangerCell.append(cell)
                        print("danger")
        return dangerCell

    def isDanger(self, target, distance):
        # 判断是否危险
        cos = -(target.pos[0] * target.veloc[0] + target.pos[1] * target.veloc[1]) / (
                distance * (target.veloc[0] ** 2 + target.veloc[1] ** 2) ** 0.5)
        if cos < 0:
            return False
        if cos > 1:
            return False
        if ((1 - cos ** 2) ** 0.5) * distance * 0.98 < target.radius + self.radius + 1:
            return True
        return False

    def escape(self, dangerCell):
        # 给出self.orientation,self.jet
        extremeDanger = []
        midDanger = []

        for bigger in dangerCell:
            distance = (bigger.pos[0] ** 2 + bigger.pos[1] ** 2) ** 0.5
            speed_1 = bigger.veloc[0] ** 2 + bigger.veloc[1] ** 2
            cos = -(bigger.pos[0] * bigger.veloc[0] + bigger.pos[1] * bigger.veloc[1]) / (
                    distance * ((speed_1) ** 0.5))

            if bigger.id == self.oppo:
                if distance < self.radius * 1.4 + bigger.radius * 1.6 + speed_1 * 50 * ((1 - cos ** 2) ** 0.6):
                    ang = math.atan2(bigger.pos[0], bigger.pos[1])
                    if bigger.pos[0] * bigger.veloc[1] - bigger.pos[1] * bigger.veloc[0] < 0:
                        ang += 0.1
                    else:
                        ang -= 0.1
                    if ang < 0:
                        ang += 2 * math.pi
                    extremeDanger.append(ang)
                    self.orientation = ang
                    self.jet = 2
                    pass
                else:
                    ang = math.atan2(bigger.pos[0], bigger.pos[1])
                    if bigger.pos[0] * bigger.veloc[1] - bigger.pos[1] * bigger.veloc[0] < 0:
                        ang += min(0.8, (distance - 40) * (0.8 * math.pi) / 40)
                    else:
                        ang -= min(0.8, (distance - 40) * (0.8 * math.pi) / 40)
                    if ang < 0:
                        ang += 2 * math.pi
                midDanger.append(ang)
            if distance < self.radius * 1.2 + bigger.radius * 1.2 + speed_1 * 50 * ((1 - cos ** 2) ** 0.5):
                ang = math.atan2(bigger.pos[0], bigger.pos[1])
                if ang < 0:
                    ang += 2 * math.pi
                extremeDanger.append(ang)
                print("speed = ", speed_1)
                print("extremeDanger")
            else:
                ang = math.atan2(bigger.pos[0], bigger.pos[1])
                if bigger.pos[0] * bigger.veloc[1] - bigger.pos[1] * bigger.veloc[0] < 0:
                    ang += 1
                else:
                    ang -= 1
                if ang < 0:
                    ang += 2 * math.pi
                print("speed = ", speed_1)
                midDanger.append(ang)
        if len(extremeDanger) == 0:
            self.jet = 1
            self.orientation = midDanger[0]
        else:
            if len(extremeDanger) == 1:
                self.jet = 2
                self.orientation = extremeDanger[0]
            else:
                self.jet = 1
                self.orientation = (extremeDanger[0] + extremeDanger[1]) / 2
                if abs(extremeDanger[0] - extremeDanger[1]) > 1.5707:
                    self.orientation += math.pi
                    if self.orientation >= 2 * math.pi:
                        self.orientation -= 2 * math.pi

    def idleJudge(self, adjacent):
        found = False
        if self.target == None:
            return 0
        for cell in adjacent:
            if cell.id == self.target.id:
                Target = cell
                found = True
                break
        if not found:
            return 0
        if Target.radius > self.radius:
            # 自己因为喷射比对方小，停止喷射
            self.jet = 0
            return 0
        '''
        distance = (Target.pos[0] ** 2 + Target.pos[1] ** 2) ** 0.5
        cos = -(Target.pos[0] * Target.veloc[0] + Target.pos[1] * Target.veloc[1]) / (
                distance * (Target.veloc[0] ** 2 + Target.veloc[1] ** 2) ** 0.5)
        minDistance = ((1 - cos ** 2) ** 0.5) * distance
        if minDistance * 1.05 < Target.radius + self.radius - 1:
        '''
        if self.ontrack(Target):
            # 在轨道上
            t = self.timeforcollision(Target)
            # 计算碰撞前需要的帧数
            if t == None:
                return 0
            print(t / self.norm(Target.pos))
            if t / self.norm(Target.pos) < 0.5:
                return t
            else:
                # 需要修正轨道（代码要重写）
                if self.angleofvector2(Target.pos, Target.veloc) < math.pi / 12:
                    if self.norm(Target.veloc) < 10:  # 可调
                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（ Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.2  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(- Target.pos[0], - Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 3

                elif self.angleofvector2(Target.pos, Target.veloc) < math.pi / 12 * 2 and self.angleofvector2(
                        Target.pos, Target.veloc) >= math.pi / 12:
                    if self.norm(Target.veloc) < 10:  # 可调

                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（ Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.5  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(- Target.pos[0], - Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 3

                elif self.angleofvector2(Target.pos, Target.veloc) < math.pi / 4 and self.angleofvector2(Target.pos,
                                                                                                         Target.veloc) >= math.pi / 12 * 2:
                    if self.norm(Target.veloc) < 10:  # 可调

                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（ Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.8  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(- Target.pos[0], - Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 3

                elif self.angleofvector2(Target.pos, Target.veloc) < math.pi / 3 and self.angleofvector2(
                        Target.pos, Target.veloc) >= math.pi / 4:
                    if self.norm(Target.veloc) < 10:  # 可调

                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（ Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.8  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(- Target.pos[0], - Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 4

                elif self.angleofvector2(Target.pos, Target.veloc) < math.pi / 12 * 5 and self.angleofvector2(
                        Target.pos, Target.veloc) >= math.pi / 3:
                    if self.norm(Target.veloc) < 10:  # 可调

                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（ Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.6  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(- Target.pos[0], - Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 4

                elif self.angleofvector2(Target.pos, Target.veloc) < math.pi / 12 * 6 and self.angleofvector2(
                        Target.pos, Target.veloc) >= math.pi / 12 * 5:
                    if self.norm(Target.veloc) < 10:  # 可调

                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（ Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.3  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(- Target.pos[0], - Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        self.jet = 4

                elif self.angleofvector2(Target.pos, Target.veloc) > math.pi / 12 * 6 and self.angleofvector2(
                        Target.pos, Target.veloc) <= math.pi / 12 * 7:
                    if self.norm(Target.veloc) < 10:  # 可调
                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.4  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-Target.pos[0], -Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 4

                elif self.angleofvector2(Target.pos, Target.veloc) > math.pi / 12 * 7 and self.angleofvector2(
                        Target.pos, Target.veloc) <= math.pi / 12 * 8:
                    if self.norm(Target.veloc) < 10:  # 可调
                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.6  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-Target.pos[0], -Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 4

                elif self.angleofvector2(Target.pos, Target.veloc) > math.pi / 12 * 8 and self.angleofvector2(
                        Target.pos, Target.veloc) <= math.pi / 12 * 9:
                    if self.norm(Target.veloc) < 0.5:  # 可调
                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.3  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-Target.pos[0], -Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 4

                elif self.angleofvector2(Target.pos, Target.veloc) > math.pi / 12 * 9 and self.angleofvector2(
                        Target.pos, Target.veloc) <= math.pi / 12 * 10:
                    if self.norm(Target.veloc) < 10:  # 可调
                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.3  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-Target.pos[0], -Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 4



                elif self.angleofvector2(Target.pos, Target.veloc) > math.pi / 12 * 10 and self.angleofvector2(
                        Target.pos, Target.veloc) <= math.pi / 12 * 11:
                    if self.norm(Target.veloc) < 10:  # 可调
                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.2  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-Target.pos[0], -Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 3


                else:
                    if self.norm(Target.veloc) < 10:  # 可调
                        self.Target = Target
                        angle1 = self.angleofvector2(Target.pos, Target.veloc)  # 位置矢量与速度矢量夹角（Target自身）
                        angle2 = math.atan2(self.norm(Target.pos), self.radius + Target.radius) * 0.1  # 由经验得出的偏向角
                        anglerealpos = math.atan2(Target.pos[0], Target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(Target.veloc[0], Target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-Target.pos[0], -Target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 4

        return 0

    def chase(self, adjacent, allcells):
        possible = []
        bigger = []
        smaller = []
        for cell in adjacent:
            if cell.radius > self.radius and cell != allcells[1 - self.id]:
                bigger.append(cell)
            if (self.radius * 0.4 < cell.radius < self.radius * 0.95 and cell != allcells[
                1 - self.id]) or (cell.radius < self.radius * 0.75 and cell == allcells[1 - self.id]):
                smaller.append(cell)
        if smaller == []:  # 没有更小的球
            self.jet = 0
            self.target = None
            self.orientation = None
        else:
            # 选出小球中的较大球
            smaller.sort(key=lambda x: x.radius ** 1.5 / (self.norm(x.pos) + 3 - self.radius), reverse=True)
            for cell in smaller:
                target = cell
                if self.angleofvector2(target.pos, target.veloc) < math.pi / 12:
                    if self.norm(target.veloc) < 1.2:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.2  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 5

                    else:
                        continue

                elif self.angleofvector2(target.pos, target.veloc) < math.pi / 12 * 2 and self.angleofvector2(
                        target.pos, target.veloc) >= math.pi / 12:
                    if self.norm(target.veloc) < 1:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.5  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 6

                    else:
                        continue

                elif self.angleofvector2(target.pos, target.veloc) < math.pi / 4 and self.angleofvector2(target.pos,
                                                                                                         target.veloc) >= math.pi / 12 * 2:
                    if self.norm(target.veloc) < 0.8:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.8  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 7

                    else:
                        continue

                elif self.angleofvector2(target.pos, target.veloc) < math.pi / 3 and self.angleofvector2(
                        target.pos, target.veloc) >= math.pi / 4:
                    if self.norm(target.veloc) < 0.7:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.8  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 7

                    else:
                        continue

                elif self.angleofvector2(target.pos, target.veloc) < math.pi / 12 * 5 and self.angleofvector2(
                        target.pos, target.veloc) >= math.pi / 3:
                    if self.norm(target.veloc) < 0.7:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.6  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 7

                    else:
                        continue

                elif self.angleofvector2(target.pos, target.veloc) < math.pi / 12 * 6 and self.angleofvector2(
                        target.pos, target.veloc) >= math.pi / 12 * 5:
                    if self.norm(target.veloc) < 0.6:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.3  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        if ((angleveloc > anglepos and not (
                                angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)) or (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and not (
                                angleveloc < math.pi / 2 and anglepos > math.pi * 3 / 2)) or (
                                      angleveloc > math.pi * 3 / 2 and anglepos < math.pi / 2)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 7

                    else:
                        continue


                elif self.angleofvector2(target.pos, target.veloc) > math.pi / 12 * 6 and self.angleofvector2(
                        target.pos, target.veloc) <= math.pi / 12 * 7:
                    if self.norm(target.veloc) < 0.6:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.4  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 7

                    else:
                        continue

                elif self.angleofvector2(target.pos, target.veloc) > math.pi / 12 * 7 and self.angleofvector2(
                        target.pos, target.veloc) <= math.pi / 12 * 8:
                    if self.norm(target.veloc) < 0.6:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.6  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 7

                    else:
                        continue

                elif self.angleofvector2(target.pos, target.veloc) > math.pi / 12 * 8 and self.angleofvector2(
                        target.pos, target.veloc) <= math.pi / 12 * 9:
                    if self.norm(target.veloc) < 0.5:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.3  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 7

                    else:
                        continue

                elif self.angleofvector2(target.pos, target.veloc) > math.pi / 12 * 9 and self.angleofvector2(
                        target.pos, target.veloc) <= math.pi / 12 * 10:
                    if self.norm(target.veloc) < 0.5:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.3  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 7

                    else:
                        continue


                elif self.angleofvector2(target.pos, target.veloc) > math.pi / 12 * 10 and self.angleofvector2(
                        target.pos, target.veloc) <= math.pi / 12 * 11:
                    if self.norm(target.veloc) < 0.4:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.2  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 7

                    else:
                        continue


                else:
                    if self.norm(target.veloc) < 0.5:  # 可调
                        possible.append(target)  # 加入可追列表
                        self.target = target
                        angle1 = self.angleofvector2(target.pos, target.veloc)  # 位置矢量与速度矢量夹角（target自身）
                        angle2 = math.atan2(self.norm(target.pos), self.radius + target.radius) * 0.1  # 由经验得出的偏向角
                        anglerealpos = math.atan2(target.pos[0], target.pos[1])  # 相对自身的位置矢量
                        if anglerealpos < 0:
                            anglerealpos += 2 * math.pi
                        angleveloc = math.atan2(target.veloc[0], target.veloc[1])
                        if angleveloc < 0:
                            angleveloc += 2 * math.pi
                        anglepos = math.atan2(-target.pos[0], -target.pos[1])
                        if anglepos < 0:
                            anglepos += 2 * math.pi

                        # 判断偏向角是距离位矢+angle还是-angle
                        # 角度处理与第一种情况略有不同
                        if ((angleveloc > anglepos and angleveloc < anglepos + math.pi) or (
                                angleveloc < math.pi and anglepos > math.pi and anglepos > angleveloc + math.pi)):
                            theta = anglerealpos - angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        elif ((angleveloc < anglepos and anglepos < angleveloc + math.pi) or (
                                angleveloc > math.pi and anglepos < math.pi and angleveloc > anglepos + math.pi)):
                            theta = anglerealpos + angle2 + math.pi
                            if theta > 2 * math.pi:
                                theta -= 2 * math.pi
                        self.orientation = theta
                        # 接下来计算喷射个数

                        self.jet = 7

                    else:
                        continue

            if possible == []:  # 没有可追的
                '''
                这里我不知道是直接返回idle还是做一个范围扩大
                '''
                self.orientation = None
                self.jet = 0
                self.target = None

        '''

        possible = []
        for cell in adjacent:
            if not (cell.radius > self.radius * 0.98 and not cell.id == self.id):
                Dist = self.dist(cell)
                if Dist < 0.5:
                    continue
                if cell.radius - Dist * 0.07 > self.radius * 0.3:
                    Speed = self.speed(cell)
                    cos = -(cell.pos[0] * cell.veloc[0] + cell.pos[1] * cell.veloc[1]) / (Dist * Speed)
                    if Speed * cos - Speed * ((1 - cos**2)**0.5) > - 0.5:
                        possible.append(cell)
        if possible == []:
            self.jet = 0
            self.orientation = None
            self.target = None
        else:
            direction = [possible[0].pos[0] + possible[0].veloc[0] * self.dist(possible[0]) * 3,possible[0].pos[1] + possible[0].veloc[1] * self.dist(possible[0]) * 3]
            ang = math.atan2(-direction[0], -direction[1])
            if ang < 0:
                ang += 2 * math.pi
            self.jet = int(self.dist(possible[0]) ** 0.5)
            self.orientation = ang
            self.target = possible[0].id
        '''

    def norm(self, vector):
        # 向量取模
        return (vector[0] ** 2 + vector[1] ** 2) ** 0.5

    def angleofvector(self, vector1, vector2):
        '''
        angle between veector1 and vector2
        '''
        a = vector1
        b = vector2
        # 夹角太小返回0
        if math.sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2)) < 1e-6:
            return 0
        det = a[0] * b[1] - a[1] * b[0]
        # 余弦定理求夹角
        anglecos = (a[0] * b[0] + a[1] * b[1]) / math.sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2))
        angle = math.acos(anglecos)
        return angle

    def angleofvector2(self, vector1, vector2):
        '''
        angle between veector1 and vector2
        '''
        a = vector1
        b = vector2
        # 夹角太小返回0
        if math.sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2)) < 1e-6:
            return 0
        det = a[0] * b[1] - a[1] * b[0]
        # 余弦定理求夹角
        anglecos = (-a[0] * b[0] - a[1] * b[1]) / math.sqrt((a[0] ** 2 + a[1] ** 2) * (b[0] ** 2 + b[1] ** 2))
        angle = math.acos(anglecos)
        return angle

    def timeforcollision(self, other):
        '''

        time for collision between other cell and self
        '''
        pos = other.pos
        veloc = other.veloc
        angle = self.angleofvector(pos, veloc)
        if angle <= math.pi / 2:
            return None
        else:
            angle = math.pi - angle
        r = self.radius + other.radius
        traveldistance = math.cos(angle) * self.norm(pos) - (
                -(math.sin(angle) ** 2) * self.norm(pos) ** 2 + r ** 2) ** 0.5
        time = traveldistance / self.norm(veloc)
        return time / 3

    def ontrack(self, other):
        # 余弦定理算速度与位置连线夹角
        ang = self.angleofvector2(other.pos, other.veloc)
        if ang >= math.pi / 2:
            return False
        else:
            if self.radius + other.radius >= self.norm(other.pos) * math.sin(ang):
                return True
            else:
                return False
