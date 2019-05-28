from math import *

from consts import Consts

class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    __iadd__ = __add__

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    # 类似于数乘
    def __mul__(self, r):
        return Vector(self.x * r, self.y * r)

    __rmul__ = __mul__

    def __eq__(self, other):
        if abs(self.x - other.x) < 1e-6 and abs(self.y - other.y) < 1e-6:
            return True
        else:
            return False

    def __lt__(self, other):
        return self.norm() < other.norm()

    def norm(self):
        try:
            return sqrt(self.x ** 2 + self.y ** 2)
        except:
            return 

    # 计算从other向量到本向量的角
    # 角沿逆时针方向增大
    def thetafrom(self, other):
        if self == LOVE or other == LOVE:
            return 0
        cos_ = (self.x * other.x + self.y * other.y) / (self.norm() * other.norm())
        sgn = (self.x * other.y - self.y * self.x) >= 0
        theta = acos(cos_) if sgn else 2 * pi - acos(cos_)
        return theta

    def theta(self):
        return self.thetafrom(Y_AXIS)

    # 返回该向量的法向量
    # 方向由参考向量ref决定，两者在该向量的同侧
    def _n(self, ref):
        vn = Vector(self.y, -self.x)
        sgn = (self.x * ref.y - self.y * ref.x) >= 0
        return sgn * vn / norm(vn)


LOVE = Vector(0, 0)
X_AXIS, Y_AXIS = Vector(1, 0), Vector(0, 1)
MIU = Vector(0, 1000)  # FIXME

class ReferToMe:
    def __init__(self, other, me):
        self.id = other.id

        self.dm = other.area() - me.area()

        self.safe_dist = other.radius + me.radius + 5

        dx = other.pos[0] - me.pos[0]
        dy = other.pos[1] - me.pos[1]
        dx = min(dx, dx - copysign(Consts["WORLD_X"], dy), key=abs)
        dy = min(dy, dy - copysign(Consts["WORLD_Y"], dy), key=abs)
        self.dr = Vector(dx, dy)

        dvx = other.veloc[0] - me.veloc[0]
        dvy = other.veloc[1] - me.veloc[1]
        self.dv = Vector(dvx, dvy)

        self.gravitation = self._attr() * self.dr

        self.relation = self._willcollide()

    # 计算吸引力的系数
    def _attr(self):
        G = 0.01  # FIXME
        fm = -self.dm * exp(copysign(sqrt(abs(self.dm)),self.dm))
        fr = self.dr.norm() ** (-3)
        fv = 1  # FIXME
        return G * fm * fr * fv

    def _willcollide(self):
        dr_future = self.dr
        for i in range(10):
            dr_future += self.dv
            if dr_future.norm() < self.safe_dist:
                if self.dm >= 0:
                    return {"state": "danger", "level": 10 - i}
                else:
                    return {"state": "chance", "level": 10 - i}
        return {"state": "nothing", "level": 0}

    def isattr(self):
        return self._attr() > 0

    def flee_dir(self):
        return self.dv._n(-self.dr).theta()

    def catch_dir(self):
        return self.dr.theta()


class Player():
    def __init__(self, id, arg=None):
        self.id = id

    # 整体策略是通过计算其他星体对玩家星体引力的合力决定喷气方向
    def strategy(self, allcells):

        # TODO solve the index
        def normal_move():
            sum_f = sum([cell_r.gravitation for cell_r in refer_me], LOVE)
            if sum_f > MIU:
                return {"indx": 5, "theta": sum_f.theta()}
            else:
                return {"indx": 7, "theta": None}

        def catch():
            try:
                chess = chance.pop()
                return {
                    "indx": 2 * chess.relation["level"],
                    "theta": chess.catch_dir()
                }
            except:
                return {"indx": 0, "theta": None}

        def flee():
            try:
                cats = danger.pop()
                return {
                    "indx": 2 * cat.relation["level"],
                    "theta": cat.flee_dir()
                    }
            except:
                return {"indx": 0, "theta": None}

        self.me = allcells[self.id]
        # 计算各个星体相对玩家的数据
        refer_me = [
            ReferToMe(cell, self.me) for cell in allcells
            if cell is not self.me
        ]
        danger = [
            cell_r for cell_r in refer_me
            if cell_r.relation["state"] == "danger"
        ].sort(key=lambda x: x.relation["level"])
        chance = [
            cell_r for cell_r in refer_me
            if cell_r.relation["state"] == "chance"
        ].sort(key=lambda x: x.relation["level"])

        theta = max(flee(), catch(), normal_move(), key=lambda x: x["indx"])
        return theta["theta"]
