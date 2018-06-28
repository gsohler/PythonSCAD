import math

class Point:
	def __init__(self, x = 0.0, y = 0.0):
		self.x = x
		self.y = y
	
	def distance(self, p):
		return math.sqrt((p.x-self.x)*(p.x-self.x)+(p.y-self.y)*(p.y-self.y))

	def length(self):
		return self.distance(Point(float(0), float(0)))

	def __sub__(self, p):
		return Point(self.x-p.x, self.y-p.y)

	def __add__(self, p):
		return Point(self.x+p.x, self.y+p.y)

	def __mul__(self, c):
		return Point(c*self.x, c*self.y)

	def __eq__(self, p):
		return self.x == p.x and self.y == p.y

	def __ne__(self, p):
		return not (self == p)
	
	def towards(self, target, t):
		if t == 0.5:
			return self.halfway(target)
		else:
			return Point((1.0-t)*self.x+t*target.x, (1.0-t)*self.y+t*target.y)
	
	def halfway(self, target):
		return Point((self.x+target.x)/2.0, (self.y+target.y)/2.0)

	def __repr__(self):
		return "Point(%s, %s)" % (self.x, self.y) 	

