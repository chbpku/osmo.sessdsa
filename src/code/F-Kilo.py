from consts import Consts
from math import *

#####################################################
class Player():
    def __init__(self, id, arg=None):
        self.id = id

    def strategy(self, allcells):

        def d_theta(other, allcells):            # 判断该目标球的友好度，由相对速度 与 速度、位移夹角差共同决定
            dx = allcells[self.id].pos[0] - other.pos[0]
            dy = allcells[self.id].pos[1] - other.pos[1]
            if abs(dx) > Consts["WORLD_X"] / 2:
                if dx > 0:
                    dx -= Consts["WORLD_X"]
                else:
                    dx += Consts["WORLD_X"]
            if abs(dy) > Consts["WORLD_Y"] / 2:
                if dy > 0:
                    dy -= Consts["WORLD_Y"]
                else:
                    dy += Consts["WORLD_Y"]       # 考虑边界情况
            if dy == 0:
                dy = 0.00001                      # 防止分母为0
            if dy > 0:
                theta = atan(dx / dy)
            else:
                theta = pi + atan(dx / dy)
            if theta < 0:
                theta += 2 * pi

            r_vx = other.veloc[0] - allcells[self.id].veloc[0]
            r_vy = other.veloc[1] - allcells[self.id].veloc[1]
            r_v = (r_vx ** 2 + r_vy ** 2) ** 0.5
            if r_vy == 0:
                r_vy = 0.00001                    # 防止分母为0
            if r_vy > 0:
                theta_v = atan(r_vx / r_vy)
            else:
                theta_v = pi + atan(r_vx / r_vy)
            if theta_v < 0:
                theta_v += 2 * pi

            temp1 = abs(theta_v - theta)
            if temp1 > pi:                        #由于0和2*pi对应同一角度，我们需要防止它对夹角的计算产生干扰
                real = 2 * pi - temp1             #此处，包括下文中所有类似的处理，都是为了得到真正的夹角差
            else:                                 
                real = temp1

            return real > 2 * pi / 3 and r_v > 2

        def value(aim, allcells):                 # 吃掉目标球所需改变的速度，仅仅是估算
            get = distance_theta(aim, allcells)   # 由于distance_theta函数要多次调用，我们先存储它的值来减少时间复杂度
            get1 = veloc_theta(aim, allcells)     # 下文中类似的操作 都是由于该原因
            theta_p = get[1]
            theta_v = get1[1]

            temp1 = abs(theta_v - theta_p)
            if temp1 > pi:
                d_theta = 2 * pi - temp1
            else:
                d_theta = temp1

            temp2 = (aim.radius + allcells[self.id].radius) / get[0]
            if temp2 > 1:
                dream = pi / 2
            else:
                dream = asin(temp2)

            if d_theta - dream > 0:
                if d_theta - dream <= pi / 3:
                    re = 500 * sin((d_theta - dream) / 2) * get1[0] * 2
                else:
                    re = 500 * get1[0]              # 这里对速度差的分段处理，主要是为了让这个函数值域尽可能小
                if re < 2:                          # 不再接近0附近发散或过大
                    return 2                        # 有关系数的确定来自于实战的模拟与经验
                else:
                    return re
            else:
                return 2

        def distance_theta(other, allcells):         # 得出目标球与自身的距离，相对角度
            dx = allcells[self.id].pos[0] - other.pos[0]
            dy = allcells[self.id].pos[1] - other.pos[1]
            if abs(dx) > Consts["WORLD_X"] / 2:
                if dx > 0:
                    dx -= Consts["WORLD_X"]
                else:
                    dx += Consts["WORLD_X"]
            if abs(dy) > Consts["WORLD_Y"] / 2:
                if dy > 0:
                    dy -= Consts["WORLD_Y"]
                else:
                    dy += Consts["WORLD_Y"]
            if dy == 0:
                dy = 0.00001
            if dy > 0:
                theta = atan(dx / dy)
            else:
                theta = pi + atan(dx / dy)
            if theta < 0:
                theta += 2 * pi
            return (abs(dx) ** 2 + abs(dy) ** 2) ** 0.5, theta

        def veloc_theta(other, allcells):          # 得出目标球与自身的相对速度，以及相对速度角
            r_vx = other.veloc[0] - allcells[self.id].veloc[0]
            r_vy = other.veloc[1] - allcells[self.id].veloc[1]
            r_v = (r_vx ** 2 + r_vy ** 2) ** 0.5
            if r_vy == 0:
                r_vy = 0.00001
            if r_vy > 0:
                theta_v = atan(r_vx / r_vy)
            else:
                theta_v = pi + atan(r_vx / r_vy)
            if theta_v < 0:
                theta_v += 2 * pi
            return r_v, theta_v

        def trap(aim, allcells):                    # 判断自己与目标球连线之间是否有更大的球干扰
            get = distance_theta(aim, allcells)
            theta = get[1]
            juli = get[0]
            for i in allcells:
                if i.radius <= allcells[self.id].radius:
                    continue
                else:
                    get1 = distance_theta(i, allcells)
                    if get1[0] < juli:
                        temp2 = (i.radius + allcells[self.id].radius) / get1[0]
                        if temp2 > 1:
                            dream = pi / 2
                        else:
                            dream = asin(temp2)

                        temp1 = abs(theta - get1[1])
                        if temp1 > pi:
                            real = 2 * pi - temp1      #首先得到自己与目标球的方向角 和 自己与大球的方向角的差值
                        else:                          #将此值和 自己与大球相切时的arcsin角度比较，
                            real = temp1               #若此值小，则说明有危险
                        if real < dream:               #这里的arcsin判断是否碰撞在下文会经常用到
                            return False
            return True

        def choice(allcells):                          # 当自己半径较小时（小于20）时目标球的选择函数
            max = 0
            choice = None
            if allcells[self.id].radius < 20:           #自己半径小于20则采用此函数
                for i in allcells:
                    juli = distance_theta(i, allcells)[0]
                    if i == self:
                        continue
                    elif juli > 200:                  #只考虑200范围之内的小球
                        continue
                    else:
                        delta = allcells[self.id].radius ** 2 - i.radius ** 2
                        temp = value(i, allcells) * 0.2 * Consts["EJECT_MASS_RATIO"] * allcells[self.id].radius ** 2
                        if delta > temp:
                            if i.radius ** 2 > temp:             
                                if trap(i, allcells):      #以上一系列if判断都是为了确保目标球 ‘值得’我们去吃
                                    rate = i.radius ** 2 / juli ** 2   
                                    if rate > max:         #这里的比率rate经过多次实战以及调整得到，尤其是它的幂次
                                        max = rate
                                        choice = i

            if max < 0.0022:                               #这里的参数经过多次实战经验得到，太小说明不值得去吃球
                if anotherchoice(allcells) != None:
                    choice = anotherchoice(allcells)
                else:
                    choice = None
            return choice

        def anotherchoice(allcells):                      # 当自己半径较大时（大于20）目标球的选择函数
            if allcells[self.id].radius > 40:
                const = 1000                              # 半径小于40  吃球半径在450左右
            else:
                const = 450                               #半径大于40时 吃球的选择半径基本上为全图
            max = 0
            choice = None                                 
            for i in allcells:
                juli = distance_theta(i, allcells)[0]      
                temp = juli - allcells[self.id].radius - i.radius
                if i == allcells[1] or i == allcells[0]:
                    continue
                elif temp > const:
                    continue
                else:
                    delta = allcells[self.id].radius ** 2 - i.radius ** 2
                    if i.radius > 13:
                        if allcells[self.id].radius - i.radius <= 26:    # 目标球与自己差值在26以上不予考虑
                            temp = value(i, allcells) * 0.2 * Consts["EJECT_MASS_RATIO"] * allcells[self.id].radius ** 2
                            if delta > temp:                             # 上面的temp为了确定追球损失，具体得出过程主要为经验
                                if i.radius ** 2 > temp:
                                    if not d_theta(i, allcells):
                                        if trap(i, allcells):
                                            rate = i.radius ** 2 / juli   # 这里的rate与之前半径很小的rate已经不同
                                            if rate > max:
                                                max = rate
                                                choice = i

            if max < 1.1:               # 参数同样来自大量实战与不断修改
                choice = None
            return choice

        def judge(theta, allcells):     # 判断沿当前方向走会不会死亡
            if theta == None:
                new_vx = allcells[self.id].veloc[0]
                new_vy = allcells[self.id].veloc[1]
            else:
                new_vx = allcells[self.id].veloc[0] - Consts["DELTA_VELOC"] * sin(theta) * Consts["EJECT_MASS_RATIO"]
                new_vy = allcells[self.id].veloc[1] - Consts["DELTA_VELOC"] * cos(theta) * Consts["EJECT_MASS_RATIO"]
            for i in allcells:
                get = distance_theta(i, allcells)
                if get[0] > 2 * i.radius + 2 * allcells[self.id].radius + (new_vx ** 2 + new_vy ** 2) ** 0.5 * 20:
                    continue
                else:
                    if i.radius > allcells[self.id].radius:
                        r_vx = i.veloc[0] - new_vx
                        r_vy = i.veloc[1] - new_vy
                        if r_vy == 0:
                            r_vy = 0.0001
                        if r_vy > 0:
                            theta_v = atan(r_vx / r_vy)
                        else:
                            theta_v = pi + atan(r_vx / r_vy)
                        if theta_v < 0:
                            theta_v = 2 * pi + theta_v

                        temp1 = abs(theta_v - get[1])
                        if temp1 > pi:
                            real = 2 * pi - temp1
                        else:
                            real = temp1
                        temp = (i.radius + allcells[self.id].radius) / get[0]
                        if temp > 1:
                            a = pi / 2
                        else:
                            a = asin(temp)

                        if (real - pi / 20) <= a:
                            if catch(i, allcells) >= pi:
                                return False, catch1(i, allcells) - pi
                            else:
                                return False, catch1(i, allcells) + pi
            return True, 1

        def catch(aim, allcells):             # 吃掉目标小球，确定喷射角度
            get = distance_theta(aim, allcells)
            a = get[1]
            a_n = a + pi / 2
            if a_n >= 2 * pi:
                a_n -= 2 * pi
            theta_v = veloc_theta(aim, allcells)[1]

            temp1 = abs(theta_v - a_n)
            if temp1 > pi:
                d_theta = 2 * pi - temp1
            else:
                d_theta = temp1
            xxx = veloc_theta(aim, allcells)[0] * cos(temp1)

            temp2 = abs(theta_v - a)
            if temp2 > pi:
                d_theta = 2 * pi - temp2
            else:
                d_theta = temp2                                 #这里的吃球函数具体实现过程比较繁琐，但其数学过程很简单
            yyy = -veloc_theta(aim, allcells)[0] * cos(temp2)   #考虑目标球与自己的位移方向夹角，
                                                                #并且计算相对速度在与位移方向平行、垂直的分量
            if xxx >= 0:                                        #根据相对位移与相对速度的两个分量得出喷射方向
                new_theta = a_n + pi                            #具体参数来自于实战积累
                if new_theta > 2 * pi:
                    new_theta -= 2 * pi
                d_theta = atan((get[0] + yyy * 150) / (xxx * 200))
                end = new_theta + d_theta
                if end > 2 * pi:
                    end -= 2 * pi
            else:
                xxx = -xxx
                new_theta = a_n
                d_theta = atan((get[0] + yyy * 150) / xxx / 200)
                end = new_theta - d_theta
                if end < 0:
                    end += 2 * pi
            return end

        def catch1(aim, allcells):                   # 这个函数用于逃跑，我们将catch1的反方向定义为逃跑方向
            a = distance_theta(aim, allcells)[1]     # 它基本与catch相同，之所以要重写一遍是因为中间个别参数不同
            a_n = a + pi / 2
            if a_n >= 2 * pi:
                a_n -= 2 * pi
            theta_v = veloc_theta(aim, allcells)[1]
            xxx = veloc_theta(aim, allcells)[0] * cos(theta_v - a_n)
            if xxx >= 0:
                new_theta = a_n + pi
                if new_theta > 2 * pi:
                    new_theta -= 2 * pi

                d_theta = atan(distance_theta(aim, allcells)[0] / xxx / 30)
                end = new_theta + d_theta
                if end > 2 * pi:
                    end -= 2 * pi
            else:
                xxx = -xxx
                new_theta = a_n
                d_theta = atan(distance_theta(aim, allcells)[0] / xxx / 30)
                end = new_theta - d_theta
                if end < 0:
                    end += 2 * pi
            return end

        ###########################################################
        if choice(allcells) == None:            # 以下为具体执行代码，根据之前的定义的各类函数return喷射方向
            if judge(None, allcells)[0]:
                return None
            else:
                return judge(None, allcells)[1]
        else:
            i = choice(allcells)
            theta_v = veloc_theta(i, allcells)[1]
            get = distance_theta(i, allcells)
            temp = (i.radius + allcells[self.id].radius) / get[0]
            if temp > 1:
                a = pi / 2
            else:
                a = asin(temp)
            temp1 = abs(theta_v - get[1])         # 主要根据choice函数的返回值确定目标球是否为None
            if temp1 > pi:                        # 在每次决定追球或者原地不动之前
                real = 2 * pi - temp1             # 都调用一次judge函数，判断是否有被吃的危险
            else:
                real = temp1
            if temp1 < a and get[0] / veloc_theta(i, allcells)[0] / 3 < 90:
                if judge(None, allcells)[0]:
                    return None
                else:
                    return judge(None, allcells)[1]
            else:
                theta_pos = catch(i, allcells)
                if judge(theta_pos, allcells)[0]:
                    return theta_pos
                else:
                    return judge(theta_pos, allcells)[1]
