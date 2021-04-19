from consts import Consts
import numpy as np

# from DDPG_keras import agent
# from stable_baselines import A2C, DDPG

# 思路：
# 1. 保留最近的NUMCONC (number of concern) 个cell的数据组 (dx,dy,vx,vy,radius) 。如果allcells不足NUMCONC个，用radius=0的cell补全. 特殊照顾一下对手比较好.
# 2. 将一切信息转换为相对参考系的信息，每个cell离player的距离是循环边界条件下最近的距离
# 3. 现在的NUMCONC*5数组作为输入。输出是theta or None。为了良好的数学结构，或许可以把输出设置成一个复数r*\exp(i\theta) ，r<r0为None，r>r0发射。
# 4. 训练神经网络，预期使用增强拓扑的神经网络。在训练的不同阶段应该设置不同的情景难度和适应度。适应度暂定为 sum (win/lose)+(weight)*(killed cells)+(weight)*(duration)
# 5. 最初阶段对手不主动操作。训练目标是多吃cell。后期阶段自身变异，对局。训练首要目标是吃掉对方

# USING = 'DDPG'
NUMCONC = 25


class Player():
    def __init__(self, id, arg=None):
        self.id = id
        # if USING=='DDPG':
        #     self.model = DDPG.load('DDPG_baselines')
        # elif USING=='A2C':
        #     self.model = A2C.load("A2C_baselines")
        # agent.load_weights('OsmoEnv.hdf5')

    def strategy(self, allcells):
        # x,y = agent.forward(self.inputdata(allcells))
        # x, y = self.model.predict(self.inputdata(allcells))[0]
        # pesudomomentum = np.abs(self.myself(allcells).veloc[0]+1j*self.myself(allcells).veloc[1])*self.myself(allcells).radius
        # if pesudomomentum >= 4.:
        #     z = None
        # else:
        #     z = trained_response(self.inputdata(allcells))
        z = trained_response(self.inputdata(allcells))
        return np.pi / 2 - np.angle(z) if abs(z) >= 1 else None

    def myself(self, cells):
        return cells.pop(0)

    def inputdata(self, cells):
        mycell = cells.pop(0)
        opcell = cells.pop(0)
        if self.id:
            mycell, opcell = opcell, mycell

        # relative displacement and velocity and radius
        def info(cell):
            x = cell.pos[0] - mycell.pos[0]
            y = cell.pos[1] - mycell.pos[1]
            dx = min(x, x + Consts['WORLD_X'], x - Consts['WORLD_X'], key=abs)
            dy = min(y, y + Consts['WORLD_Y'], y - Consts['WORLD_Y'], key=abs)
            return [np.array([dx, dy]) / mycell.radius,
                    np.array([cell.veloc[0] - mycell.veloc[0], cell.veloc[1] - mycell.veloc[1]]) / mycell.radius,
                    cell.radius / mycell.radius]

        # cells of concern = nearest cells and opponent
        cells.sort(key=mycell.distance_from)
        if len(cells) < NUMCONC - 1:
            data = [info(c) for c in cells]
            while len(data) < NUMCONC - 1:
                theta = 2 * np.pi * np.random.random()
                data.append([Consts['WORLD_X'] / 15 * np.cos(theta),
                             Consts['WORLD_X'] / 15 * np.sin(theta), 0., 0., 0.])
        else:
            data = [info(c) for c in cells[:NUMCONC - 1]]
        data.append(info(opcell))
        return data

    # def trained_response(self, data):
    #     def pref(r):
    #         return r if r < 0.96 else 2*(1/(1+np.exp(r-1))-1)

    #     def weight(dx, dy, vx, vy, r):
    #         d = np.sqrt(dx**2+dy**2)-r-1
    #         if d<=0:
    #             d=10**(-5)
    #         w = 0.002*d**(-0.35) if d>2 else 100
    #         nx, ny = dx/d, dy/d
    #         vn = -vx*nx-vy*ny
    #         # wv = 1/(1+np.exp(-vn/0.005+1))
    #         wv=np.exp(4*vn) if vn>0 else 1/(1+np.exp(-1.5*vn))
    #         print(wv)
    #         return w*wv*nx, w*wv*ny

    #     def finalweight(info):
    #         nx, ny = weight(info[0], info[1], info[2], info[3], info[4])
    #         p = pref(info[-1])
    #         return p*(nx+1j*ny)

    #     z = sum(sorted(map(finalweight,data),key=abs,reverse=True)[:2])
    #     # double contribution from opponent
    #     z+=finalweight(data[-1])
    #     return z


def trained_response(data):
    # ingore cells smaller than the size of my ejection
    radius_low_crit = 1.5 * np.sqrt(1 / (1 - Consts['EJECT_MASS_RATIO']) - 1)
    opponent = data.pop()
    data = [info for info in data if info[2] > radius_low_crit]
    data.append(opponent)

    bigcells = [info for info in data if info[2] > 0.93]
    smallcells = [info for info in data if not info[2] > 0.93]

    if len(bigcells) != 0:
        info = max(bigcells, key=lambda info: emergency_index(info) * info[2] ** 0.3)
        index = emergency_index(info) * info[2] ** 0.3
        # print('dodge: ',index)
        if index > 0.08:
            return dodge(info)
    if len(smallcells) != 0:
        # checkmate
        if any(smallcells) is data[-1] and data[-1][2] < 0.8 and emergency_index(data[-1]) > 0.00004:
            print('Checkmate!')
            chase(data[-1])
        info = max(smallcells, key=lambda info: emergency_index(info) * info[2] ** 3)
        index = value_index(info) * info[2] ** 3
        # print('chase: ',index)
        if index > 0.0004:
            return chase(info)


    return 0

    # pm = +1 if nearest[2]>=0.9 else -1
    # z = 1*nearest[0]+1j*nearest[1]
    # if nearest[2]>radius_low_crit:
    #     return -pm*z/abs(z)
    # else:
    #     return 0


# def distance(info):
#     return np.sqrt(info[0]**2+info[1]**2)-info[4]-1

def emergency_index(info):  # consider time, distance
    time = np.inner(info[0], info[1]) / (np.inner(info[1], info[1]) + 1e-12)  # <0:approaching, >0:leaving
    dist = np.linalg.norm(info[0] - time * info[1])
    dist -= (info[2] + 1)
    time_index = 0 if time > 0 else 1 - np.tanh(-time / 50)
    dist_index = 1 / (np.exp(dist / 1.5))
    # print(time,time_index)
    return time_index * dist_index


def value_index(info):
    time = np.inner(info[0], info[1]) / (np.inner(info[1], info[1]) + 1e-12)  # <0:approaching, >0:leaving
    dist = np.linalg.norm(info[0] - time * info[1])
    dist -= (info[2] + 1)
    time_index =  0 if time < 0 else 1 - np.tanh(-time / 50)
    dist_index = 2 / (1 + np.exp(dist / 5.))
    return time_index * dist_index


def chase(info):
    # dv = Consts['DELTA_VELOC']*Consts['EJECT_MASS_RATIO']/(1.5*Consts['DEFAULT_RADIUS'])
    A = np.tan(np.angle(info[0][0] + 1j * info[0][1]))  # A and D are two parameters to calculate x, y
    D = (info[1][0] - A * info[1][1]) / (Consts["DELTA_VELOC"] * Consts["EJECT_MASS_RATIO"])
    if A ** 2 - D ** 2 + 1 >= 0:
        y = (-A * D + np.sqrt(A ** 2 - D ** 2 + 1)) / (A ** 2 + 1)
        x = -info[0][0] / abs(info[0][0]) * np.sqrt(1 - y ** 2)
        z = x + 1j * y
    else:
        if np.inner(info[0], info[1]) > 0:
            z = info[1][0] + 1j * (info[1][1])
            z = -z / abs(z)
        else:
            z = info[1][0] + 1j * info[1][1]
            z = z / abs(z)
    return z


def dodge(info):
    # dv = Consts['DELTA_VELOC']*Consts['EJECT_MASS_RATIO']/(1.5*Consts['DEFAULT_RADIUS'])
    z = info[0][0] + 1j * info[0][1]
    z = z / abs(z)
    return z