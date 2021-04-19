#!/usr/bin/env python3
from consts import Consts
from math import pi
from cell import Cell

import random
import math


class Player():
	def __init__(self, id, arg=None	):
		self.id = id
		self.arg=arg
	# escape master
	# 疑问:如何解决两个小球相撞的问题
	# problem 1：参数函数 平方后？
	# problem 2: 突然变大
	def strategy(self, allcells):
		# -------------------------------------------------------------------------
		# 计算几何
		emp=0.0000001 #防止除0错误
		def get_theta(a, b):  # 两个向量的夹角函数
			return math.acos(cros(a, b) / (ab(a) * ab(b)+emp))
		
		def get_cosin(a,b):
		    return cros(a,b)/(ab(a) *ab(b))

		def ab(l):  # 求出一个向量的长度
			s = 0
			for i in l:
				s += i ** 2
			return s ** (1 / 2)

		def sgn(l):
			if (l > 0):
				return 1
			else:
				return -1

		def dec(si, bi):  # 向量减法
			s = [0 for i in range(0, len(si))]
			for i in range(0, len(si)):
				s[i] = si[i] - bi[i]
			return s

		def cros(si, bi):  # 内积
			s = 0
			for i in range(0, len(si)):
				s += si[i] * bi[i]
			return s

		def scal(si, bi):  # 外积 由于坐标系变化，需要修正
			s = 0
			s = si[0] * bi[1] - si[1] * bi[0]
			return -s

		def r_arg(l):  # 调整角度直到范围到[0,2*pi]
			s = l
			while (s < 0): s += 2 * pi
			while (s >= 2 * pi): s -= 2 * pi
			return s

		def get_arg(l):  # 已知一个向量，返回其坐标下的角度
			dx, dy = l[0], l[1]
			s = math.acos(dy / (ab(l)+emp))
			if (dx < 0): s = -s
			return r_arg(s)  # 将s调整到正确的范围

		# ---------------------------------------------------------------------
		# 游戏机制相关
		def eject(st,theta):#模拟喷射 解决不连续
			fx = math.sin(theta)
			fy = math.cos(theta)
			st.veloc[0] -= Consts["DELTA_VELOC"] * fx * Consts["EJECT_MASS_RATIO"]
			st.veloc[1] -= Consts["DELTA_VELOC"] * fy * Consts["EJECT_MASS_RATIO"]
			st.radius *= (1 - Consts["EJECT_MASS_RATIO"]) ** 0.5
			return None

		def cross_scr(v):#如何考虑穿过屏幕？这里借鉴了助教的代码
			WX=Consts["WORLD_X"]
			WY=Consts["WORLD_Y"]
			lst=[v[0]-WX,v[0],v[0]+WX]
			min1=abs(lst[0])
			i_min=0
			for i in range(3):
				if abs(lst[i])<min1:
					i_min=i
					min1=abs(lst[i])
			v0=lst[i_min]
			lst=[v[1]-WY,v[1],v[1]+WY]
			min1=abs(lst[0])
			i_min=0
			for i in range(3):
				if abs(lst[i])<min1:
					i_min=i
					min1=abs(lst[i])
			v1=lst[i_min]
			return [v0,v1]

		def check_escape(now, sp):  # 是否需要逃跑的列表
			if (now.radius > sp.radius):
				return False
			elif (now.radius == sp.radius and ab(now.veloc) < ab(sp.veloc)):
				return False
			return True

		def get_loss(now,sp,max_score,len_elst,v_min=0.6): #吃完球会变成原来的多少 max_score剪枝
			n=0
			sp1 = Cell(now.id, [now.pos[0], now.pos[1]], [now.veloc[0], now.veloc[1]], now.radius)
			sp2 = Cell(now.id, [sp.pos[0], sp.pos[1]], [sp.veloc[0], sp.veloc[1]], sp.radius) #同样模拟喷球
			st=60
			while True:
				st-=1
				lsp=Cell(now.id,cross_scr(dec(now.pos,sp.pos)),dec(now.veloc,sp.veloc),sp1.radius+sp2.radius)
				theta = get_theta([-i for i in lsp.pos], lsp.veloc)
				theta_r = get_arg([-i for i in lsp.pos])
				theta_v = get_arg(lsp.veloc)
				if(st<0 ):
					sp1.radius=0
					break
				if(sp1.radius<sp2.radius):
					sp1.radius=0
					break
				if(sp1.radius+sp2.radius+210-(60-st)+1<max_score):
					sp1.radius=0
					break

				if(sp1.collide(sp2)):
					break
				if math.sin(theta) * ab(sp.pos) < sp1.radius+sp2.radius-0.2: # 如果可以打的到
					if (abs(cros(lsp.veloc, lsp.pos)) / ab(sp1.pos)) < v_min * 0.5*max(0,(len_elst-10)/50): 
																		rs=get_arg(lsp.pos)  # 返回速度矢量的反方向角度
					else:  rs=None  # 不用动
				elif(ab(lsp.veloc)<0.3):
					rs= get_arg(lsp.pos)
				elif (-cros(lsp.veloc, lsp.pos) / ab(lsp.pos)) < v_min:  # 速度在位矢方向上的分量小于要求速度

					theta = get_theta([-i for i in lsp.pos], lsp.veloc)
					atan = math.atan((math.sin(theta) * ab(lsp.veloc)) / (v_min - (math.cos(theta) * ab(lsp.veloc))))
					rs=r_arg(math.pi - atan + theta_r)  # 考虑返回一个角度，在（-v）和(r)之间
				else:
					sgn1=scal(lsp.veloc, lsp.pos)
					sp11 = Cell(sp1.id, [sp1.pos[0], sp1.pos[1]], [sp1.veloc[0], sp1.veloc[1]], sp1.radius)#防止左右喷射
					sp11.move(Consts["FRAME_DELTA"])
					sp22 = Cell(sp2.id, [sp2.pos[0], sp2.pos[1]], [sp2.veloc[0], sp2.veloc[1]], sp2.radius)
					sp22.move(Consts["FRAME_DELTA"])
					eject(sp11,theta_v + math.pi * 0.5 * sgn(scal(lsp.veloc, lsp.pos)))
					sgn2=scal(dec(sp11.veloc,sp22.veloc),cross_scr(dec(sp11.pos,sp22.pos))) #模拟喷射后的过程
					if(sgn1*sgn2<0): rs=None
					else: rs=theta_v + math.pi * 0.5 * sgn(scal(lsp.veloc, lsp.pos))
				sp1.move(Consts["FRAME_DELTA"])
				sp2.move(Consts["FRAME_DELTA"])
				if(rs!=None):eject(sp1,rs)
			return (sp1.radius,60-st)


		def find_escape(now, wlst, min_t):
			s = None
			for i in wlst:
				sp1 = Cell(now.id, [now.pos[0], now.pos[1]], [now.veloc[0], now.veloc[1]], now.radius)
				sp2 = Cell(now.id, [i.pos[0], i.pos[1]], [i.veloc[0], i.veloc[1]], i.radius)
				if (sp1.distance_from(sp2) - sp1.radius - sp2.radius > ab(dec(now.veloc, i.veloc)) * min_t[0] * Consts[
					"FRAME_DELTA"]):
					continue
				for st in range(0, min(50, min_t[0])): #模拟
					sp1.move(Consts["FRAME_DELTA"])
					sp2.move(Consts["FRAME_DELTA"])
					if (sp1.collide(sp2)):
						# print(i.id," Danger!")
						if (st > min_t[0]):
							break
						else:
							min_t[0] = st
							s = i
			return s

		def arg_escape(now, sp):  # 找到逃跑的角度
			i = sp
			ars=Cell(now.id,cross_scr(dec(now.pos,i.pos)),dec(now.veloc,i.veloc),now.radius)
			args = get_arg(ars.veloc) + sgn(scal(ars.pos, ars.veloc)) * pi / 2  # 找到一个合适的垂直喷射角度
			args = r_arg(args)
			sgn1=sgn(scal(ars.veloc, ars.pos))
			sp1 = Cell(now.id, [now.pos[0], now.pos[1]], [now.veloc[0], now.veloc[1]], now.radius)
			sp2 = Cell(now.id, [i.pos[0], i.pos[1]], [i.veloc[0], i.veloc[1]], i.radius)
			sp1.move(Consts["FRAME_DELTA"])
			sp2.move(Consts["FRAME_DELTA"])
			eject(sp1,args)
			ars2=Cell(now.id,cross_scr(dec(sp1.pos,sp2.pos)),dec(sp1.veloc,sp2.veloc),now.radius)
			sgn2=sgn(scal(ars2.pos, ars2.veloc))
			if(sgn1*sgn2<0):
				args=r_arg(get_arg(ars.pos)+pi)
			return args

		def check_attack(now, sp):  # 对比是否放入考虑吃的列表,不能太大也不能太小,不能太远
			if (sp.radius <= 1 * now.radius and sp.radius > 0.3 * now.radius and sp.radius>0.5 and now.distance_from(sp) < 3000):
				return True
			else:
				return False

		def find_attack2(now, elst, min_t):  # 战术2：Aggressive ball 主动寻求收益的去进攻
			pass

		def find_attack3(now, elst, min_t):# 战术3：参数函数
			flag = False
			scorelist = [0 for i in range(len(elst))]
			aim= None
			max_score=1
			for i, item in enumerate(elst):
				sp = Cell(now.id, cross_scr(dec(now.pos, item.pos)), dec(now.veloc, item.veloc), now.radius + item.radius-0.2)
				cosin = get_cosin([-i for i in sp.pos], sp.veloc)
				theta = get_theta([-i for i in sp.pos], sp.veloc)
				if(self.arg['world'].timer[self.id]>3):
				#if True:
					rsl=get_loss(now,item,max_score,len(elst)) #rs为喷射之后的半径
					rs,rt=rsl[0],rsl[1]
					
					sf=True #判断在rt内是否会突然变大
					sl=True #判断在rt内是否会被吃掉
					if((now.radius**2)-(rs**2)<=(item.radius**2) and sf and sl):
						scorelist[i]=rs+item.radius+210-rt
				else:
					if math.sin(theta) * ab(sp.pos) < now.radius+item.radius-0.2:
						scorelist[i] = sp.radius
					else:
						scorelist[i]=score(item.radius/now.radius,ab(now.pos),cosin,sp.veloc)
				if(scorelist[i]>max_score):
					aim=item
					max_score=scorelist[i]
			if(aim!=None):print("id:",item.id,"max_score:",max_score)
			return aim

		def find_args(now, allcells):  # 战术3：梯度发射法 设计一个合适的引力函数
			pass

		def score(dr,dis,cosin,v):#加权的函数，用于判断相撞的概率以及
			return cosin*(0.2-0.1*ab(v))+(120*(dis**(-4/3)))*(math.exp(3*dr)-1) #dr也要和dis相关!!!

		def check_ok(now, i):  # 判断能否碰撞+返回碰撞时间
			sp1 = Cell(now.id, [now.pos[0], now.pos[1]], [now.veloc[0], now.veloc[1]], now.radius)
			sp2 = Cell(now.id, [i.pos[0], i.pos[1]], [i.veloc[0], i.veloc[1]], i.radius)
			rmin = [sp1.distance_from(sp2),0]
			for st in range(0, 40):
				sp1.move(Consts["FRAME_DELTA"])
				sp2.move(Consts["FRAME_DELTA"])
				if (sp1.collide(sp2)):  # 如果能够碰撞，那么返回True+碰撞时间
					return True, st
				else:
					if rmin[0] > sp1.distance_from(sp2):  # 如果不能碰撞，判断什么时候距离最近，最近距离为多少
						rmin = [sp1.distance_from(sp2), i]
			return False, rmin

		def arg_attack(now, sp,len_elst):  # 选定目标找到最小的发射方式
			veloc_min = 0.6
			ip = check_ok(now, sp)
			bt = Cell(now.id, cross_scr(dec(now.pos, sp.pos)), dec(now.veloc, sp.veloc), now.radius + sp.radius)  # 换系
			theta_r = get_arg([-i for i in bt.pos])
			theta_v = get_arg(bt.veloc)
			if ip[0]:  # 如果可以打的到
				print("Fine")
				try:
					if (abs(cros(bt.veloc, bt.pos)) / ab(now.pos)) < veloc_min * 0.5*max(0,(len_elst-10)/50):  # 速度在位矢方向上的分量小于要求速度
						print("Speeding up")
						return get_arg(bt.pos)  # 返回速度矢量的反方向角度
					else:
						print("Stay")
						return None  # 不用动
				except:  # ab(now.pos)==0
					pass
			elif(ab(bt.veloc)<0.3):
				print("Speeding up")
				return get_arg(bt.pos)
			else:
				if (-cros(bt.veloc, bt.pos) / ab(bt.pos)) < veloc_min:  # 速度在位矢方向上的分量小于要求速度
					theta = get_theta([-i for i in bt.pos], bt.veloc)
					atan = math.atan((math.sin(theta) * ab(bt.veloc)) / (veloc_min - (math.cos(theta) * ab(bt.veloc))))
					print(bt.pos, bt.veloc, theta_r)
					print("theta:", theta, "\natan:", atan)
					print("Speeding up")
					return r_arg(math.pi - atan + theta_r)  # 考虑返回一个角度，在（-v）和(r)之间
				else:
					print("Changing angle")
					sgn1=scal(bt.veloc, bt.pos)
					sp1 = Cell(now.id, [now.pos[0], now.pos[1]], [now.veloc[0], now.veloc[1]], now.radius)#防止左右喷射
					sp1.move(Consts["FRAME_DELTA"])
					sp2 = Cell(now.id, [sp.pos[0], sp.pos[1]], [sp.veloc[0], sp.veloc[1]], sp.radius)
					sp2.move(Consts["FRAME_DELTA"])
					eject(sp1,theta_v + math.pi * 0.5 * sgn(scal(bt.veloc, bt.pos)))
					sgn2=scal(dec(sp1.veloc,sp2.veloc),cross_scr(dec(sp1.pos,sp2.pos))) #模拟喷射后的过程
					#if(check_ok(sp1,sp2)):
					#	return theta_v + math.pi * 0.5 * sgn(scal(bt.veloc, bt.pos))  # 返回r和v的叉乘
					if(sgn1*sgn2<0): #有突变
						return None
					else: return theta_v + math.pi * 0.5 * sgn(scal(bt.veloc, bt.pos))

		#---------------------------------------------------------------------
		#主程序
		now=allcells[self.id] #now是我们的参数
		sp=allcells[self.id^1] #sp是对手的参数
		m_now=now.radius**2
		m_sp=sp.radius**2
		m_l=0
		min_t=[51,31]
		args=None
		elst=[] #构建一个可以吃的列表，想办法找到一个合适的
		wlst=[] #构建一个需要逃跑的列表，找个最需要跑的
		for i in allcells:
			if(i.id==self.id): continue 
			if(i.id==self.id^1):
				if(check_escape(now,i)):wlst.append(i)
				continue 
			m_l+=i.radius**2
			if(i.dead):continue 
			if(check_attack(now,i)): elst.append(i) #考虑一下可以吃的
			if(check_escape(now,i)): wlst.append(i) #考虑一下要跑的
		
		if(len(elst)>0):
			elst.sort(key=lambda x:-x.radius)

		#已经必胜—————————————————————————
		if(m_now>m_sp+m_l):
			print("you Win!")
			return None

		#需要跑就果断跑————————————————————
		aim=find_escape(now,wlst,min_t)	
		if(aim!=None):
			args=arg_escape(now,aim)

		# 不愿打，但也不怕打————————————————
		if(aim==None):
			aim=find_attack3(now,elst,min_t)
			if aim!=None: 
				args=arg_attack(now,aim,len(elst))
				if(args!=None): #防止喷完之后逃跑
					noww=Cell(now.id,[now.pos[0],now.pos[1]],[now.veloc[0],now.veloc[1]],now.radius)
					noww.move(Consts["FRAME_DELTA"])
					eject(noww,args)
					sb=find_escape(noww,wlst,min_t)
					if(sb!=None):
						args=None
			else: args=None 

		# 找一个合适的角度去发育—————————————
		return args

