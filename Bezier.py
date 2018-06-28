
from Point import *

class Bezier:
	def __init__(self, v):
		self.n = len(v)
		self.vp = v
		self.isConvex = False
		self.diam = 0
		self.deg = len(v) - 1
		self.cp = v
		self.tmin = float(0)
		self.tmax = float(1)
	
	def getPoint(self, t):
		curr = [0]*self.deg
		# get initial
		for i in range(self.deg):
			curr[i] = self.cp[i].towards(self.cp[i+1], t)
		for i in range(self.deg-1):
			for j in range(self.deg-1-i):
				curr[j] = curr[j].towards(curr[j+1], t)
		return curr[0]

	def getCurve(self,f):
		curve = []
		td = 0.1
		told=0
		ptold = self.getPoint(told)
		curve.append(ptold)

		while told < 1:
			while True:
				tnew = told+td
				if tnew > 1:
					tnew=1
				ptnew = self.getPoint(tnew)
				if ptnew.distance(ptold) < f:
					curve.append(ptnew)
					td = td / 0.75
					told = tnew
					ptold = ptnew
					break
				else:
					td = td * 0.75

		return curve

def demo():
	vp = [Point(0.0, 0.0), Point(0.2, 1.0), Point(1.0, 1.0), Point(1.0, 0.2), Point(2.0, 0.2), Point(2.0, 1.0)]
	
	bc = Bezier(vp)
	pts = bc.getCurve(0.5)
	print(pts)
        

