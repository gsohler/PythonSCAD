#!/usr/bin/env python

# https://pypi.python.org/packages/source/p/pyclipper/pyclipper-0.9.3b0.tar.gz
# boolean, offsetting

# hg clone https://code.google.com/p/poly2tri.python/
# triangulation

import math
import xml.etree.ElementTree as ET
import re
import sys
import struct
# import pyclipper
# import ezdxf
from Bezier import *

class Model:

	epsilon = 0.001
	class Point:
		def __init__(self, x = 0.0 ,y = 0.0 ,z = 0.0 ):
			self.x=x
			self.y=y
			self.z=z

	
		def distance(self, p):
			return math.sqrt((p.x-self.x)*(p.x-self.x)+(p.y-self.y)*(p.y-self.y)+(p.z-self.z)*(p.z-self.z))

		def length(self):
			return self.distance(Model.Point(float(0), float(0),float(0)))

		def __sub__(self, p):
			return Model.Point(self.x-p.x, self.y-p.y,self.z-p.z)

		def __add__(self, p):
			return Model.Point(self.x+p.x, self.y+p.y,self.z+p.z)

		def __mul__(self, c):
			return Model.Point(c*self.x, c*self.y,c*self.z)

		def __eq__(self, p):
			return math.fabs(self.x - p.x) < Model.epsilon and math.fabs(self.y - p.y) < Model.epsilon and math.fabs(self.z - p.z) < Model.epsilon

		def __ne__(self, p):
			return not (self == p)
	
		def cross(self, p):
			return Model.Point(
				self.y * p.z - self.z * p.y ,
				self.z * p.x - self.x * p.z ,
				self.x * p.y - self.y * p.x
			)
		def inner(self, p):
			return self.x * p.x + self.y * p.y + self.z * p.z
	
		def unit(self):
			l=self.length()
			if math.fabs(l) > Model.epsilon:
				return self * (1.0/l)
			else:
				return Model.Point(1,0,0)
	
		def towards(self, target, t):
			if t == 0.5:
				return self.halfway(target)
			else:
				return Model.Point((1.0-t)*self.x+t*target.x, (1.0-t)*self.y+t*target.y,(1.0-t)*self.z)
	
		def halfway(self, target):
			return Model.Point((self.x+target.x)/2.0, (self.y+target.y)/2.0,(self.z+target.z)/2.0)

		def __repr__(self):
			return "Point(%s, %s, %s)" % (self.x, self.y,self.z)
		def __hash__(self):
			return hash(str(self))


	class Item:
		def execute(self,min):
			print("execute not implemented")
	
		def position(self,min):
			print("position not implemented")
	
	class Line(Item):
		def __init__(self,start,end):
			self.start=start
			self.end=end
		def reversed(self):
			return Model.Line(self.end,self.start)

	class Triangle(Item):
		def __init__(self,p1,p2,p3,n):
			self.p1=p1
			self.p2=p2
			self.p3=p3
			self.n=n
	
	class Circle(Item):
		def __init__(self,center,radius):
			self.center=Model.Point(center.x,center.y,0)
			self.start=Model.Point(center.x,center.y,0)
			self.end=Model.Point(center.x,center.y,0)
			self.radius=radius
			self.start.x = self.start.x - radius
			self.start.y = self.start.y - radius
			self.end.x = self.end.x + radius
			self.end.y = self.end.y + radius

	class Arc(Item):
		def __init__(self,center,radius,start,end,ccw):
			self.ccw = ccw
			self.center=center
			self.radius=radius
			self.start=start
			self.end=end
		def reversed(self):
			return Model.Arc(self.center,self.radius,self.end,self.start, not self.ccw)


	def __init__(self):
		self.items = []
		self.pathes = []

	def linsystem(self,v1,v2,v3,pt):
		det=v1.x*(v2.y*v3.z-v3.y*v2.z)-v1.y*(v2.x*v3.z-v3.x*v2.z)+v1.z*(v2.x*v3.y-v3.x*v2.y);
		ad11=v2.y*v3.z-v3.y*v2.z;
		ad12=v3.x*v2.z-v2.x*v3.z;
		ad13=v2.x*v3.y-v3.x*v2.y;
		ad21=v3.y*v1.z-v1.y*v3.z;
		ad22=v1.x*v3.z-v3.x*v1.z;
		ad23=v3.x*v1.y-v1.x*v3.y;
		ad31=v1.y*v2.z-v2.y*v1.z;
		ad32=v2.x*v1.z-v1.x*v2.z;
		ad33=v1.x*v2.y-v2.x*v1.y;
		if math.fabs(det) < 1e-9:
			return None
		l1=(ad11*pt.x+ad12*pt.y+ad13*pt.z)/det;
		l2=(ad21*pt.x+ad22*pt.y+ad23*pt.z)/det;
		l3=(ad31*pt.x+ad32*pt.y+ad33*pt.z)/det;
		
		result=self.Point(l1,l2,l3);
#		xcheck=v1*result.x + v2*result.y + v3*result.z - pt
#		err=xcheck.length()
#		print(err)
		return result


	def offset(self,slice,offset):
		pco = pyclipper.PyclipperOffset()
		for poly in slice:
			path_clipper = []
			for item in poly:
				path_clipper.append([item.start.x*1000, item.start.y*1000])
		
			try:
				pco.AddPath(path_clipper, pyclipper.JT_SQUARE, pyclipper.ET_CLOSEDPOLYGON)
			except pyclipper.ClipperException:
				pass
		paths = pco.Execute(offset*1000);
		slice = []
		for path in paths:
			poly= []
			ptold = None
			for pt in path:
				pt1 = Model.Point(pt[0]*0.001,pt[1]*0.001,0)
				if ptold is not None:
					poly.append(Model.Line(ptold,pt1))
				ptold = pt1
			poly.append(Model.Line(poly[-1].end,poly[0].start))
			slice.append(poly)
		return slice

	def layer_notrect(self,xmin,xmax,ymin,ymax,slice):

		pc = pyclipper.Pyclipper()

		rect = ( (xmin*1000, ymin*1000), (xmin*1000, ymax*1000), (xmax*1000, ymax*1000), (xmax*1000, ymin*1000))
		try:
			pc.AddPath(rect, pyclipper.PT_SUBJECT, True)
		except pyclipper.ClipperException:
			pass

		for poly in slice:
			path_clipper = []
			for item in poly:
				path_clipper.append([item.start.x*1000, item.start.y*1000])
		
			try:
				pc.AddPath(path_clipper, pyclipper.PT_CLIP, True)
			except pyclipper.ClipperException:
				pass

		paths = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

		slice = []
		for path in paths:
			poly= []
			ptold = None
			for pt in path:
				pt1 = Model.Point(pt[0]*0.001,pt[1]*0.001,0)
				if ptold is not None:
					poly.append(Model.Line(ptold,pt1))
				ptold = pt1
			poly.append(Model.Line(poly[-1].end,poly[0].start))
			slice.append(poly)
		return slice

	def path_intersect_poly(self,start,end,slice):

		pc = pyclipper.Pyclipper()

		path = ( (start.x*1000, start.y*1000), (end.x*1000, end.y*1000))
		try:
			pc.AddPath(path, pyclipper.PT_SUBJECT, False)
		except pyclipper.ClipperException:
			pass


		for poly in slice:
			path_clipper = []
			for item in poly:
				path_clipper.append([item.start.x*1000, item.start.y*1000])
		
			try:
				pc.AddPath(path_clipper, pyclipper.PT_CLIP, True)
			except pyclipper.ClipperException:
				pass

		res = pc.Execute2(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
		if len(res.Childs) > 0:
			return True
		return False


	def layer_or(self,slice1, slice2):

		pc = pyclipper.Pyclipper()
		if len(slice1) == 0:
			return slice2

		if len(slice2) == 0:
			return slice1

		for poly in slice1:
			path_clipper = []
			for item in poly:
				path_clipper.append([item.start.x*1000, item.start.y*1000])
			try:
				pc.AddPath(path_clipper, pyclipper.PT_CLIP, True)
			except pyclipper.ClipperException:
				pass

		for poly in slice2:
			path_clipper = []
			for item in poly:
				path_clipper.append([item.start.x*1000, item.start.y*1000])
			try:
				pc.AddPath(path_clipper, pyclipper.PT_SUBJECT, True)
			except pyclipper.ClipperException:
				pass

		paths = pc.Execute(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

		slice = []
		for path in paths:
			poly= []
			ptold = None
			for pt in path:
				pt1 = Model.Point(pt[0]*0.001,pt[1]*0.001,0)
				if ptold is not None:
					poly.append(Model.Line(ptold,pt1))
				ptold = pt1
			poly.append(Model.Line(poly[-1].end,poly[0].start))
			slice.append(poly)
		return slice

	def layer_not(self,slice1, slice2):

		pc = pyclipper.Pyclipper()
		if len(slice1) == 0:
			return slice2

		if len(slice2) == 0:
			return slice1

		for poly in slice2:
			path_clipper = []
			for item in poly:
				path_clipper.append([item.start.x*1000, item.start.y*1000])
			try:
				pc.AddPath(path_clipper, pyclipper.PT_CLIP, True)
			except pyclipper.ClipperException:
				pass

		for poly in slice1:
			path_clipper = []
			for item in poly:
				path_clipper.append([item.start.x*1000, item.start.y*1000])
			try:
				pc.AddPath(path_clipper, pyclipper.PT_SUBJECT, True)
			except pyclipper.ClipperException:
				pass
	
		paths = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

		slice = []
		for path in paths:
			poly= []
			ptold = None
			for pt in path:
				pt1 = Model.Point(pt[0]*0.001,pt[1]*0.001,0)
				if ptold is not None:
					poly.append(Model.Line(ptold,pt1))
				ptold = pt1
			poly.append(Model.Line(poly[-1].end,poly[0].start))
			slice.append(poly)
		return slice


############################################################################
# SVG Load
############################################################################	

	def parse_rect(self,node):
		for keyx in node.attrib.keys():
			key = re.sub('{.*}','',keyx)
			if key == "width": pass
			elif key == "height": pass
			elif key == "fill": pass
			else:
				print(node.tag)
				print(key)
	
	def parse_line(self,node):
		for keyx in node.attrib.keys():
			key = re.sub('{.*}','',keyx)
			d=node.attrib[key]
			if key == "fill": pass
			elif key == "stroke": pass
			elif key == "stroke-width": pass
			elif key == "stroke-miterlimit": pass
			elif key == "x1": x1 = d; pass
			elif key == "y1": y1 = d; pass
			elif key == "x2": x2 = d; pass
			elif key == "y2": y2 = d; pass
			else:
				print(node.tag)
				print(key)

		p1=Model.Point(float(x1)*self.scale,float(y1)*self.scale,0)
		p2=Model.Point(float(x2)*self.scale,float(y2)*self.scale,0)
		return Model.Line(p1,p2)

	def parse_dummy(self,node):
		for keyx in node.attrib.keys():
			key = re.sub('{.*}','',keyx)

	def use_path(self,path):
		result = []
		if len(path) < 2:
#			print("Too few points")
			return result
		ref = path[0]
		path = path[1:]
		for pt in path:
			result.append(Model.Line(ref,pt))
			ref = pt
		if len(result) == 1:
			self.items.append(result[0])
		else:
			self.pathes.append(result)


	def use_svg_path(self,path):
		if self.svg_symbol_name == None:
			self.use_path(path)
		else:
			self.svg_symbol_dict[self.svg_symbol_name].append(path)
			pass	

	def parse_symbol(self,node):
		id=""
		for keyx in node.attrib.keys():
			key = re.sub('{.*}','',keyx)
			d=node.attrib[key]
			if key == "id": id = d ; pass
		self.svg_symbol_name=id
		self.svg_symbol_dict[id]=[]
			
	def parse_use(self,node):
		x=0.0
		y=0.0
		href=""
		for keyx in node.attrib.keys():
			d=node.attrib[keyx]
			key = re.sub('{.*}','',keyx)
			if key == "href": href = d ; pass
			if key == "x": x = float(d)*self.scale ; pass
			if key == "y": y = -float(d)*self.scale ; pass
		href = re.sub('#','',href)
		pathes=self.svg_symbol_dict[href]
		for path in pathes:
			path_offset=[]
			for item in path:
				path_offset.append(Model.Point(item.x+x,item.y+y))
			self.use_path(path_offset) # hier noch offsetten

			
	

	def parse_svg_path(self,node):
		path=[]
		d=""
		for keyx in node.attrib.keys():
			key = re.sub('{.*}','',keyx)
			if key == "export-filename": pass
			elif key == "export-xdpi": pass
			elif key == "export-ydpi": pass
			elif key == "stroke-linejoin": pass
			elif key == "stroke-linecap": pass
			elif key == "stroke-width": pass
			elif key == "stroke": pass
			elif key == "fill": pass
			elif key == "d":
				d=node.attrib[key]
				pass
			elif key == "nodetypes": pass
			elif key == "style": pass
			elif key == "id": pass
			else:
				print("|"+node.tag)
				print(key)
		d = d.replace(","," ")
		i = iter(d.split(" "))
		try:
			while True:
				item = next(i)
				if item == "M":
					if len(path) > 0:
						self.use_svg_path(path)
						path=[]
					x = float(next(i))*self.scale
					y = -float(next(i))*self.scale
					path.append(Model.Point(x,y,0))
				elif item == "C":
					p1 = path[-1]
					x = float(next(i))*self.scale
					y = -float(next(i))*self.scale
					p2=Model.Point(x,y,0)
					x = float(next(i))*self.scale
					y = -float(next(i))*self.scale
					p3=Model.Point(x,y,0)
					x = float(next(i))*self.scale
					y = -float(next(i))*self.scale
					p4=Model.Point(x,y,0)
					bc = Bezier([p1,p2,p3,p4])
					pts=bc.getCurve(0.5/self.scale)
					path += pts[1:]
				elif item == "L":
					x = float(next(i))*self.scale
					y = -float(next(i))*self.scale
					path.append(Model.Point(x,y,0))
				elif item == "Z":
					path.append(path[0])
					pass
				elif item == "":
					pass
				else:
					print("Unknown item")
					print(item)
		except StopIteration:
			pass
	
		if len(path) > 0:
			self.use_svg_path(path)
			path=[]

		

	

	def parse_circle(self,node):
		for keyx in node.attrib.keys():
			key = re.sub('{.*}','',keyx)
			d=node.attrib[key]
			if key == "cx": cx = float(d); pass
			elif key == "cy": cy = float(d); pass
			elif key == "r": r = float(d); pass
			elif key == "fill": pass
			elif key == "stroke-width": pass
			elif key == "stroke-miterlimit": pass
			elif key == "stroke": pass
			else:
				print(node.tag)
				print(key)
		circs = []
		circs.append(Model.Circle(Model.Point(self.scale*cx,self.scale*cy,0),self.scale*r))
		return circs

	def parse_ellipse(self,node):
		for keyx in node.attrib.keys():
			key = re.sub('{.*}','',keyx)
			d=node.attrib[key]
			if key == "cx": cx = float(d) ; pass
			elif key == "cy": cy = float(d); pass
			elif key == "rx": rx = float(d); pass
			elif key == "ry": ry = float(d); pass
			elif key == "fill": pass
			elif key == "stroke-width": pass
			elif key == "stroke-miterlimit": pass
			elif key == "stroke": pass
			else:
				print(node.tag)
				print(key)

	def parse_text(self,node):
		for keyx in node.attrib.keys():
			key = re.sub('{.*}','',keyx)
			if key == "x": pass
			elif key == "y": pass
			elif key == "font-size": pass
			elif key == "text-anchor": pass
			elif key == "fill": pass
			else:
				print(node.tag)
				print(key)


	def parse_tree(self,node):
		for child in node:
			tag = re.sub('{.*}','',child.tag)
			if tag == "path":
				self.parse_svg_path(child)
			elif tag == "rect":
				self.parse_rect(child)
			elif tag == "line":
				items = self.parse_line(child)
				self.items.append(items)
			elif tag == "stop":
				self.parse_dummy(child)
			elif tag == "linearGradient":
				self.parse_dummy(child)
			elif tag == "circle":
				circs = self.parse_circle(child)
				self.pathes.append(circs)
			elif tag == "ellipse":
				self.parse_ellipse(child)
			elif tag == "text":
				self.parse_text(child)
			elif tag == "defs":
				pass
			elif tag == "namedview":
				pass
			elif tag == "metadata":
				pass
			elif tag == "RDF":
				pass
			elif tag == "Work":
				pass
			elif tag == "about":
				pass
			elif tag == "format":
				pass
			elif tag == "type":
				pass
			elif tag == "title":
				pass
			elif tag == "desc":
				pass
			elif tag == "svg":
				pass
			elif tag == "symbol":
				self.parse_symbol(child)
			elif tag == "use":
				self.parse_use(child)
			elif tag == "g":
				pass
			else:
				print("Unknown!")
				print(tag)
				print(child)
				print(child.text)
				print(child.attrib)
			self.parse_tree(child)

	def loadSvg(self,svgfile,scale):
		self.svg_symbol_name=None
		self.svg_symbol_dict={}
		self.scale=scale
		tree = ET.parse(svgfile)
		root = tree.getroot()
		self.parse_tree(root)


############################################################################
# STL Load
############################################################################

	def loadStl(self,filename,scalex,scaley,scalez):
	
		with open(filename,'rb') as f:
			b = f.read(1)
			if b == b's': # Read Ascii STL
				f.seek(0)
				pts = []
				norm = None
				for line in f:
					token = line.strip().split()
					if len(token) == 4 and token[0] == b'vertex':
						pts.append(Model.Point(float(token[1])*scalex,float(token[2])*scaley,float(token[3])*scalez))
						pass
					elif len(token) == 5 and token[0] == b'facet':
						norm = Model.Point(float(token[2])*scalex,float(token[3])*scaley,float(token[4])*scalez)
						# collect everything
						pass
					elif len(token) == 1 and token[0] == b'endloop':
						pass
					elif len(token) == 1 and token[0] == b'endfacet':
						if len(pts) == 3:
							t = Model.Triangle(pts[0],pts[1],pts[2],norm)
							self.items.append(t)
						pts = []
						pass
					elif len(token) == 2 and token[0] == b'outer':
						pass
					elif len(token) == 2 and token[0] == b'solid':
						pass
					elif len(token) == 2 and token[0] == b'endsolid':
						pass
					elif len(token) == 1 and token[0] == b'endsolid':
						pass
					else:
						print("unknown line %s"%(line))
				return
			else:	# Read Binary STL
				f.seek(80)
	
				b = f.read(4)
				triangles = struct.unpack('<I', b)[0]
				for i in range(triangles):
					b = f.read(4*3*4)
					coords = struct.unpack('<ffffffffffff',b)
					b = f.read(2)	
		
					n = Model.Point(coords[0]*scalex,coords[1]*scaley,coords[2]*scalez)
					p1 = Model.Point(coords[3]*scalex,coords[4]*scaley,coords[5]*scalez)
					p2 = Model.Point(coords[6]*scalex,coords[7]*scaley,coords[8]*scalez)
					p3 = Model.Point(coords[9]*scalex,coords[10]*scaley,coords[11]*scalez)
					#Recalculate n
					v1=p2-p1
					v2=p3-p1
					n=v1.cross(v2).unit()
					
					t = Model.Triangle(p1,p2,p3,n)
					self.items.append(t)

############################################################################
# STL Save
############################################################################

	def exportStl(self,filename):
	
		with open(filename,'wb') as f:
			f.write(struct.pack("<IIIIIIIIIIIIIIIIIIII", 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))
			f.write(struct.pack("<I", len(self.items)))
			for item in self.items:
				if isinstance(item,Model.Triangle):
					n = item.n
					p1 = item.p1
					p2 = item.p2
					p3 = item.p3
					data = struct.pack('<ffffffffffff',n.x,n.y,n.z,p1.x,p1.y,p1.z,p2.x,p2.y,p2.z,p3.x,p3.y,p3.z)
					f.write(data)
					f.write(struct.pack('<bb',0,0))

	def exportStlAscii(self,filename):
	
		with open(filename,'w') as f:
			f.write("solid gcode_tools\r\n")
			for item in self.items:
				if isinstance(item,Model.Triangle):
					n = item.n
					p1 = item.p1
					p2 = item.p2
					p3 = item.p3
					f.write(" facet normal %f %f %f\r\n"%(n.x,n.y,n.z))
					f.write("  outer loop\r\n")
					f.write("   vertex %f %f %f\r\n"%(p1.x,p1.y,p1.z))
					f.write("   vertex %f %f %f\r\n"%(p2.x,p2.y,p2.z))
					f.write("   vertex %f %f %f\r\n"%(p3.x,p3.y,p3.z))
					f.write("  endloop\r\n")
					f.write(" endfacet\r\n")
			f.write("endsolid gcode_tools\r\n")


############################################################################
# NGC load
############################################################################
	def loadNgc(self,path):
		self.pos = self.Point(0,0,0)
		self.layernum = 0

		with open(path, 'r') as f:
			# init line counter
			self.lineNb = 0
			# for all lines
			for line in f:
				# inc line counter
				self.lineNb += 1
				# parse a line
				self.loadNgcLine(line.rstrip())

	def loadNgcLine(self,line):
		if line == "":
			return
		token = line.split(' ')
		x=int(token[1])
		y=int(token[2])
		if token[0] == "0":
			self.pos = self.Point(x,y,0)
			pass
		elif token[0] == "1":
			newpos = self.Point(x,y,0)
			line = self.Line(self.pos,newpos)
		
			self.items.append(line)
			self.pos = self.Point(x,y,0)
			pass
		else:
			print("Unknown Command %s"%(line))

############################################################################
# GCode load
############################################################################
	def loadGcode(self,path):
		self.pos = self.Point(0,0,0)
		self.layernum = 0

		with open(path, 'r') as f:
			# init line counter
			self.lineNb = 0
			# for all lines
			for line in f:
				# inc line counter
				self.lineNb += 1
				# parse a line
				self.loadGcodeLine(line.rstrip())

	def loadGcodeLine(self,line):
		if line == "":
			return
		if line.startswith("(Layer"):
			self.layernum = self.layernum + 1
		if line[0] == "(":
			return
		line = line.split(';',1)
		line = line[0]
		token = line.split(' ')
		cmd = token[0]
		if len(token) > 1:
			dic = {}
			for arg in token[1:]:
				if arg != "":
					letter = arg[0]
					coord = arg[1:]
					dic[letter] = float(coord)

		if cmd == "G0" or cmd == "G1":
			newpos = self.Point(self.pos.x,self.pos.y,self.pos.z)
			for axis in dic.keys():
				if axis == "X":
					newpos.x = dic[axis]
				elif axis == "Y":
					newpos.y = dic[axis]
				elif axis == "Z":
					newpos.z = dic[axis]
				elif axis == "F":
					pass
				else:
					print("Unknown axis %s"%(axis))
			line = self.Line(self.pos,newpos)
			line.layernum = self.layernum
			if cmd == "G1":
				self.items.append(line)
			self.pos = self.Point(newpos.x,newpos.y,newpos.z)
			pass
		elif cmd == "G3" or cmd == "G2":
			newpos = self.Point(self.pos.x,self.pos.y,self.pos.z)
			i=0.0
			j=0.0
			k=0.0
			for axis in dic.keys():
				if axis == "X":
					newpos.x = dic[axis]
				elif axis == "Y":
					newpos.y = dic[axis]
				elif axis == "Z":
					newpos.z = dic[axis]
				elif axis == "I":
					i=dic[axis]
				elif axis == "J":
					j=dic[axis]
				elif axis == "K":
					k=dic[axis]
				elif axis == "F":
					pass
				else:
					print("Unknown axis '%s'"%(axis))
			center = self.Point(self.pos.x+i,self.pos.y+j,self.pos.z+k)
			d1 = self.Point(self.pos.x - center.x, self.pos.y - center.y,0)
			d2 = self.Point(newpos.x - center.x, newpos.y - center.y,0)
			ang1=math.atan2( d1.y,d1.x)
			ang2=math.atan2( d2.y,d2.x)
			radius = math.hypot(d1.x,d1.y)
			radius2 = math.hypot(d2.x,d2.y)
			if math.fabs(radius - radius2) > Model.epsilon:
				print(line)
				print("Only Circle arcs allowed so far %.2f %.2f"%(radius,radius2))
			if cmd == "G2": # ang1 -> ang1 CW
				ccw = False	
				while ang1 < ang2:
					ang1 = ang1 + 2*math.pi
			if cmd == "G3": # ang1 -> ang2 CCW
				ccw = True
				while ang2 < ang1:
					ang2 = ang2 + 2*math.pi
			arc = self.Arc(center,radius,self.pos,newpos,ccw)
			self.items.append(arc)
			self.pos = self.Point(newpos.x,newpos.y,newpos.z)
			pass
		elif cmd == "M2":# End of Prg
			pass
		elif cmd == "G4": # Dwell
			pass
		elif cmd == "G28": # Home
			pass
		elif cmd == "T0":
			pass
		elif cmd == "G21":
			pass
		elif cmd == "G90":
			pass
		elif cmd == "M25":
			pass
		elif cmd == "M104":
			pass
		elif cmd == "M109":
			pass
		elif cmd == "M104": # Laser on
			pass
		elif cmd == "M106": # Laser on
			pass
		elif cmd == "M107": # Laser off
			pass
		elif cmd == "G92": # move origin
			pass
		elif cmd == "M400": #  finish moves
			pass
		elif cmd == "M82": 
			pass
		else:
			print("Unknown Command %s"%(line))


############################################################################
# GCode Save
############################################################################

	def calc_bbox_path(self,path,min,max):
		for item in path:
			if min is None:
				min = Model.Point(item.start.x,item.start.y,0)
				max = Model.Point(item.start.x,item.start.y,0)
	
			if item.start.x < min.x:
				min.x = item.start.x
			if item.start.y < min.y:
				min.y = item.start.y
			if item.start.x > max.x:
				max.x = item.start.x
			if item.start.y > max.y:
				max.y = item.start.y
			if item.end.x < min.x:
				min.x = item.end.x
			if item.end.y < min.y:
				min.y = item.end.y
			if item.end.x > max.x:
				max.x = item.end.x
			if item.end.y > max.y:
				max.y = item.end.y
		return (min,max)

	def calc_area(self,path):
		sum=0
		for item in path:
			sum = sum + (item.end.x - item.start.x)*(item.end.y + item.start.y)
		return sum/2

	def reverse_path(self,path):
		newpath = []
		for item in path:
			itemnew = Model.Line(item.end,item.start)
			newpath.insert(0,itemnew)
		return newpath
		


	def chainItems(self,items):
		pathes = []
		path = []
		refpt = None
		while len(items) > 0:
			match = False
			if refpt is not None:
				for item in items:
					if item.start.distance(refpt) < Model.epsilon:
						refpt = item.end
						items.remove(item)
						path.append(item)
						match = True
						break
				if match == True:
					continue
				for item in items:
					if item.end.distance(refpt) < Model.epsilon:
						refpt = item.start
						items.remove(item)
						item = item.reversed()
						path.append(item)
						match = True
						break
				if match == True:
					continue
	
			# Neuen path anfangen
			if len(path) > 0:
				pathes.append(path)
			path = []
			path.append(items[0])		
			refpt = items[0].end
			items = items[1:]

		if len(path) > 0:
			pathes.append(path)
		return pathes
	
## ExportGcode

	def exportGcodeLayer(self,callbacks,pathes,travelspeed,workspeed, xyoffset):
		for path in pathes:

			item = path[0]
			if isinstance(item,Model.Line):
				print("G0 X%.2f Y%.2f F%.2f"%(item.start.x-xyoffset.x,item.start.y-xyoffset.y,travelspeed))
			elif isinstance(item,Model.Circle):
				print("G0 X%.2f Y%.2f F%.2f"%(item.center.x-xyoffset.x-item.radius,item.center.y-xyoffset.y,travelspeed))
			elif isinstance(item, Model.Arc):
				print("G0 X%.2f Y%.2f F%.2f"%(item.start.x-xyoffset.x,item.start.y-xyoffset.y,travelspeed))
			else:
				print("Type %s not supported"%item)

			callbacks.enable()
			for item in path:
				if isinstance(item, Model.Line):
					print("G1 X%.2f Y%.2f F%.2f"%(item.end.x-xyoffset.x,item.end.y-xyoffset.y,workspeed))
				elif isinstance(item, Model.Circle):
					print("G3 X%.2f Y%.2f I%.2f J%.2f F%.2f"%(item.center.x-xyoffset.x+item.radius,item.center.y-xyoffset.y,item.radius,0,workspeed))
					print("G3 X%.2f Y%.2f I%.2f J%.2f F%.2f"%(item.center.x-xyoffset.x-item.radius,item.center.y-xyoffset.y,-item.radius,0,workspeed))
				elif isinstance(item, Model.Arc):
					command="G3"
					if item.ccw == False:
						command="G2"
					print("%s X%.2f Y%.2f I%.2f J%.2f F%.2f"%(command, item.end.x-xyoffset.x,item.end.y-xyoffset.y,item.center.x-item.start.x,item.center.y-item.start.y,workspeed))

				else:
					print("Type %s not supported"%item)
			callbacks.disable()

	def exportGcode(self,items,pathes,travelspeed,workspeed, depth,delta,off,zoff):
		cl=self.exportGcodeMill(depth, delta, zoff, workspeed)
		self.exportGcodeMain(cl,items,pathes,travelspeed,workspeed, off)	

	def exportGcode(self,cl,items,pathes,travelspeed,workspeed, off):


		# pathes are combined sequences already, items ain't
	
		# Chain elements against each other
		# pathes = [[item,item,item,item],[item,item]]
		# items = [item,item,item]

		#inputs: items
		# output: pathes
		pathes += self.chainItems(items)
		#determine min/max
		min = None
		max = None
		for path in pathes:
			(min_sub,max_sub) = self.calc_bbox_path(path,None,None)
			(min,max) = self.calc_bbox_path(path,min,max)

		if max is None:
			print("No data available")
			return	
		print("( Overall Size: %.2f/%.2f )"%((max.x-min.x),(max.y-min.y)))
	
		# Then offset all pathes
		for path in pathes:
			if path[0].start == path[-1].end:
				area=self.calc_area(path)
				if area < 0:
					path1 = []
					for p in path:
						path1.append(p.reversed())
					path = list(reversed(path1))
				# offset all of them
				#path=offset(path,off) TODO activate

		cl.worker(pathes,travelspeed,workspeed,min,self.exportGcodeLayer)

	class exportGcodeMill:
		def __init__(self,depth, delta, zoff, workspeed):
			self.depth = depth
			self.delta = delta
			self.zoff = zoff
			self.workspeed = workspeed;

		def enable(self):
			print("G1 Z%.2f F%.2f"%(self.z+self.zoff,self.workspeed))

		def disable(self):
			print("G1 Z0")

		def worker(self,pathes,travelspeed,workspeed, xyoffset,layerfunc):
			print("T0 ; first device")
			print("G21 ;metric values")
			print("G90 ;absolute positioning")
			print("G28 X0 Y0  ;move X/Y to min endstops")
			print("G28 Z0     ;move Z to min endstops")
			print("G0 Z0 F%.2f"%(travelspeed))
			self.z=0
			while self.z < self.depth:
				self.z+= self.delta
				layerfunc(self,pathes,travelspeed,workspeed, xyoffset)
			print("G0 X0 Y0 F%.2f"%(travelspeed))
			print("M2")

	class exportGcodeLaser:
		def __init__(self):
			pass

		def enable(self):
			print("G4 P500") # To sync planne
			print("M104 S200")

		def disable(self):
			print("G4 P500") # To sync planne
			print("M104 S0")

		def worker(self,pathes,travelspeed,workspeed, xyoffset,layerfunc):
			print("T0 ; first device")
			print("G21 ;metric values")
			print("G90 ;absolute positioning")
			print("G28 X0 Y0  ;move X/Y to min endstops")
			print("G28 Z0     ;move Z to min endstops")
			print("G0 Z0 F%.2f"%(travelspeed))
			layerfunc(self,pathes,travelspeed,workspeed, xyoffset)
			print("G0 X0 Y0 F%.2f"%(travelspeed))
			print("M2")

############################################################################
# Plt load
############################################################################
	def loadPlt(self,path,scale):
		self.scale = scale
		self.pos = self.Point(0,0,0)
		self.pltpath = None

		with open(path, 'r') as f:
			# init line counter
			self.lineNb = 0
			# for all lines
			for line in f:
				# inc line counter
				self.lineNb += 1
				# parse a line
				token = line.rstrip().split(';',1)
				for tok in token:
					if tok != "":
						self.loadPltToken(tok)
		if self.pltpath != None:
			self.use_path(self.pltpath)
			self.pltpath = None

	def loadPltToken(self,token):
		if token.startswith("PU"): # Pen Up
			coords = token[2:].split(" ")
			if self.pltpath != None:
				self.use_path(self.pltpath)
				self.pltpath = None
			self.pos = Model.Point(float(coords[0])*self.scale,float(coords[1])*self.scale,0)
				
		elif token.startswith("PD"): #Pen Down
			coords = token[2:].split(" ")
			if self.pltpath == None:
				self.pltpath = [self.pos]
			
			self.pos = Model.Point(float(coords[0])*self.scale,float(coords[1])*self.scale,0)
			self.pltpath.append(self.pos)
			pass
		elif token.startswith("IN"): # Init
			pass
		elif token.startswith("WU"):
			pass
		elif token.startswith("VS"):
			pass
		elif token.startswith("PW"): # Pen Width
			pass
		elif token.startswith("SP"): # Select Pen
			pass
		else:
			print("(%s)"%(token))

############################################################################
# DXF load
############################################################################
	def loadDxf(self,path,scale):
		dwg = ezdxf.readfile(path)
		modelspace = dwg.modelspace()
		for e in modelspace:
			if e.dxftype() == 'LINE':
				p1 = Model.Point(e.dxf.start[0],e.dxf.start[1])
				p2 = Model.Point(e.dxf.end[0],e.dxf.end[1])
				self.items.append(Model.Line(p1,p2))
			elif e.dxftype() == 'ARC':
				c=Model.Point(e.dxf.center[0],e.dxf.center[1])
				r=e.dxf.radius
				# from sa to ea CCW!!!
				sa=3.1415926*e.dxf.start_angle/180.0
				ea=3.1415926*e.dxf.end_angle/180.0
				sx=c.x+r*math.cos(sa)
				sy=c.y+r*math.sin(sa)
				ex=c.x+r*math.cos(ea)
				ey=c.y+r*math.sin(ea)
		
				arc = Model.Arc(c,r,Model.Point(sx,sy),Model.Point(ex,ey),True)
					
				self.items.append(arc)
			else:
				print(e.dxftype())


