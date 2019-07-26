#! /usr/bin/python3

# TODO achsen immer gleich hell
# TODO profile verschieden viele segmente
# TODO rotate_extrude linear_extrude mehr freiheitsgrade
# TODO goal funktion
# TODO rezept, start verschachtelung
# TODO optimizer
# TODO rotate_extrude_extrude anpassen

# TODO editor syntax highlighting
# TODO GTK3
# TODO Sample thingiverse publication
# TODO extrude 2* mit wechselnden shapes
# TODO gears
# TODO cache for speedup
# TODO vertices ueberall korrigieren

import math
import argparse
import sys
import signal
#import numpy as np

import pygtk
pygtk.require('2.0')
import gtk
import pango
import gtk.gtkgl
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import gobject
import os.path
import time
#from model import *

from csg.core import CSG
from csg.geom import Vertex, Vector


from OpenGL.GL import *

listind = -1
####################################
# Viewer
####################################

class Viewer:
	def __init__(self):
		self.RX = 0.0
		self.RZ = 0.0
		self.PX = 0.0
		self.PY = 0.0
		self.zoom = 0.05
		self.start_layer = 0
		self.end_layer = -1

	def setModel(self, model):
		self.model = model


	def renderLines(self,items):

		for item in items:
			if hasattr(item,'layernum'):
				layernum = item.layernum
			else:
				layernum = 0
			while len(self.raw_lines) <= layernum:
				self.raw_lines.append([])

			while len(self.raw_triangles) <= layernum:
				self.raw_triangles.append([])

			while len(self.raw_triangles_normal) <= layernum:
				self.raw_triangles_normal.append([])


			if isinstance(item, Model.Line):
				item.start.x
				item.start.y
				item.start.z
				item.end.x
				item.end.y
				item.end.z
				self.raw_lines[layernum].append(item.start.x)
				self.raw_lines[layernum].append(item.start.y)
				self.raw_lines[layernum].append(item.start.z)
				self.raw_lines[layernum].append(item.end.x)
				self.raw_lines[layernum].append(item.end.y)
				self.raw_lines[layernum].append(item.end.z)
			if isinstance(item, Model.Triangle):
				self.raw_triangles[layernum].append(item.p1.x)
				self.raw_triangles[layernum].append(item.p1.y)
				self.raw_triangles[layernum].append(item.p1.z)
				self.raw_triangles[layernum].append(item.p2.x)
				self.raw_triangles[layernum].append(item.p2.y)
				self.raw_triangles[layernum].append(item.p2.z)
				self.raw_triangles[layernum].append(item.p3.x)
				self.raw_triangles[layernum].append(item.p3.y)
				self.raw_triangles[layernum].append(item.p3.z)
				self.raw_triangles_normal[layernum].append(item.n.x)
				self.raw_triangles_normal[layernum].append(item.n.y)
				self.raw_triangles_normal[layernum].append(item.n.z)
				self.raw_triangles_normal[layernum].append(item.n.x)
				self.raw_triangles_normal[layernum].append(item.n.y)
				self.raw_triangles_normal[layernum].append(item.n.z)
				self.raw_triangles_normal[layernum].append(item.n.x)
				self.raw_triangles_normal[layernum].append(item.n.y)
				self.raw_triangles_normal[layernum].append(item.n.z)
			if isinstance(item, Model.Arc):
				d1 = Model.Point(item.start.x - item.center.x, item.start.y - item.center.y,0)
				d2 = Model.Point(item.end.x - item.center.x, item.end.y - item.center.y,0)
				ang1=math.atan2( d1.y,d1.x)
				ang2=math.atan2( d2.y,d2.x)
				if item.ccw == False:
					x=ang1
					ang1=ang2
					ang2=x
				if ang2 < ang1:
					ang2  = ang2 + 2*3.14159265359


				n = int((ang2-ang1)/0.3)+1
				for i in range(n):
					p1 = ang1+(ang2-ang1)*i/n
					p2 = ang1+(ang2-ang1)*(i+1)/n
					self.raw_lines[layernum].append(item.center.x+item.radius*math.cos(p1))
					self.raw_lines[layernum].append(item.center.y+item.radius*math.sin(p1))
					self.raw_lines[layernum].append(item.center.z)
					self.raw_lines[layernum].append(item.center.x+item.radius*math.cos(p2))
					self.raw_lines[layernum].append(item.center.y+item.radius*math.sin(p2))
					self.raw_lines[layernum].append(item.center.z)
			if isinstance(item, Model.Circle):

				n = 16
				for i in range(n):
					p1 = 2*3.1415*i/n
					p2 = 2*3.1415*(i+1)/n
					self.raw_lines[layernum].append(item.center.x+item.radius*math.cos(p1))
					self.raw_lines[layernum].append(item.center.y+item.radius*math.sin(p1))
					self.raw_lines[layernum].append(item.center.z)
					self.raw_lines[layernum].append(item.center.x+item.radius*math.cos(p2))
					self.raw_lines[layernum].append(item.center.y+item.radius*math.sin(p2))
					self.raw_lines[layernum].append(item.center.z)


	def renderVertices(self,result):
		self.faces = []
		self.normals = []
		self.vertices = []
		self.colors = []
		self.vnormals = []
		polygons=result.toPolygons()

		for polygon in polygons:
			n = polygon.plane.normal
			indices = []
			for v in polygon.vertices:
				pos = [v.pos.x, v.pos.y, v.pos.z]
				if not pos in self.vertices:
					self.vertices.append(pos)
					self.vnormals.append([])
				index = self.vertices.index(pos)
				indices.append(index)
				self.vnormals[index].append(v.normal)
			self.faces.append(indices)
			self.normals.append([n.x, n.y, n.z])
			self.colors.append(polygon.shared)

		# setup vertex-normals
		ns = []
		for vns in self.vnormals:
			n = Vector(0.0, 0.0, 0.0)
			for vn in vns:
				n = n.plus(vn)
			n = n.dividedBy(len(vns))
			ns.append([a for a in n])
		self.vnormals = ns

		global listind
		if listind == -1:
			listind = glGenLists(1)
		glNewList(listind, GL_COMPILE)

		for n, f in enumerate(self.faces):
			glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

			glBegin(GL_POLYGON)
			glColor3f(0.8,0.8,0)
			glNormal3fv(self.normals[n])
			for i in f:
				glVertex3fv(self.vertices[i])
			glEnd()
		glEndList()




	def rotate_drag_start(self, x, y, button, modifiers):
		self.rotateDragStartRX = viewer.RX
		self.rotateDragStartRZ = viewer.RZ
		self.rotateDragStartX = x
		self.rotateDragStartY = y


	def rotate_drag_do(self, x, y, dx, dy, buttons, modifiers):
		# deltas
		deltaX = x - self.rotateDragStartX
		deltaY = y - self.rotateDragStartY
		# rotate!
		self.RZ = self.rotateDragStartRZ + deltaX/5.0 # mouse X bound to model Z
		self.RX = self.rotateDragStartRX + deltaY/5.0 # mouse Y bound to model X


	def rotate_drag_end(self, x, y, button, modifiers):
		self.rotateDragStartRX = None
		self.rotateDragStartRZ = None
		self.rotateDragStartX = None
		self.rotateDragStartY = None


	def pan_drag_start(self, x, y, button, modifiers):
		self.panDragStartPX = viewer.PX
		self.panDragStartPY = viewer.PY
		self.panDragStartX = x
		self.panDragStartY = y


	def pan_drag_do(self, x, y, dx, dy, buttons, modifiers):
		pass
		# deltas
		deltaX = x - self.panDragStartX
		deltaY = y - self.panDragStartY
		# rotate!
		self.PX = self.panDragStartPX + deltaX*0.02
		self.PY = self.panDragStartPY + deltaY*0.02


	def pan_drag_end(self, x, y, button, modifiers):
		self.panDragStartPX = None
		self.panDragStartPY = None
		self.panDragStartX = None
		self.panDragStartY = None

####################################
# Viewer ewvents
####################################


def draw(glarea, event):
	# get GLContext and GLDrawable
	glcontext = glarea.get_gl_context()
	gldrawable = glarea.get_gl_drawable()
	x, y, width, height = glarea.get_allocation()

	# GL calls
	if not gldrawable.gl_begin(glcontext): return


	# Clear buffers
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	# setup projection
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(65, width / float(height), 0.1, 1000)

	# setup camera
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	gluLookAt(0,1.5,2,0,0,0,0,1,0)

	# enable alpha blending
#	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	# rotate axes to match reprap style
	glRotated(-90, 1,0,0)

	glNormal3f(1,0,0)
	glTranslated(viewer.PX,viewer.PY,-0.5)
	# user rotate model
	glRotated(-viewer.RX, 1,0,0)
	glRotated(viewer.RZ, 0,0,1)

	# draw axes
	glBegin(GL_LINES)
	glColor3f(1,0,0)
	glVertex2i(0,0); glVertex2i(1,0)
	glColor3f(0,1,0)
	glVertex2i(0,0); glVertex2i(0,1)
	glColor3f(0,0,1)
	glVertex2i(0,0); glVertex3i(0,0,1)
	glEnd()

	scale = viewer.zoom ;
	glScaled(scale, scale, scale)


	# fit & user zoom model

	glColor3f(1,1,1)

	glLineWidth(1)
	# Draw the model layers
	# lower layers


	global listind
	if listind != -1:
		glCallList(listind)

	# disable depth for HUD
	glDisable(GL_DEPTH_TEST)
	glDepthMask(0)

	#Set your camera up for 2d, draw 2d scene

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity();
	glOrtho(0, width, 0, height, -1, 1)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

	# reenable depth for next model display
	glEnable(GL_DEPTH_TEST)
	glDepthMask(1)


	if gldrawable.is_double_buffered():
		gldrawable.swap_buffers()
	else:
		glFlush()

		gldrawable.gl_end()
	return True

def reshape(glarea, event):
	# get GLContext and GLDrawable
	glcontext = glarea.get_gl_context()
	gldrawable = glarea.get_gl_drawable()

	# GL calls
	if not gldrawable.gl_begin(glcontext): return

	x, y, width, height = glarea.get_allocation()

	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	if width > height:
		w = float(width) / float(height)
		glFrustum(-w, w, -1.0, 1.0, 5.0, 60.0)
	else:
		h = float(height) / float(width)
		glFrustum(-1.0, 1.0, -h, h, 5.0, 60.0)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glTranslatef(0.0, 0.0, -40.0)

	gldrawable.gl_end()

	return True

def keypressevent(window, event):
	global modifiers
	keyname = gtk.gdk.keyval_name(event.keyval)
	if keyname == "F1":
		save_script(window)
		message( "Script saved")
	if keyname == "F5":
		render(window)
	if keyname == "F6":
		export_stl(window)
	if keyname == "Shift_L" or keyname == "Shift_R":
		modifiers=1

def keyreleaseevent(window, event):
	global modifiers
	keyname = gtk.gdk.keyval_name(event.keyval)
	if keyname == "Shift_L" or keyname == "Shift_R":
		modifiers=0

def pointermotion(glarea, event):
	global button_pressed
	global eventx
	global eventy
	global modifiers
	if button_pressed == 0:
		return
	x, y, width, height = glarea.get_allocation()
	event.y = height - event.y
	dx = event.x - eventx
	dy = event.y - eventy
	if modifiers == 0:
		if button_pressed == 1:
			viewer.rotate_drag_do(event.x, event.y, dx, dy, button_pressed, modifiers)

		if button_pressed == 3:
			viewer.pan_drag_do(event.x, event.y, dx, dy, button_pressed, modifiers)

	if modifiers == 1:
		dy = int(dy)

		if button_pressed == 1 or button_pressed == 2:
			viewer.start_layer = viewer.start_layer + dy
			if viewer.start_layer < 0:
				viewer.start_layer = 0
			if viewer.start_layer > viewer.end_layer:
				viewer.start_layer = viewer.end_layer
		if button_pressed == 3 or button_pressed == 2:
			viewer.end_layer = viewer.end_layer + dy
			if viewer.end_layer >= viewer.layer_num:
				viewer.end_layer = viewer.layer_num-1
			if viewer.end_layer < viewer.start_layer:
				viewer.end_layer = viewer.start_layer

def scrollevent(glarea, event):
	if event.direction.value_name == "GDK_SCROLL_DOWN":
		viewer.zoom = viewer.zoom / 1.5
	if event.direction.value_name == "GDK_SCROLL_UP":
		viewer.zoom = viewer.zoom * 1.5

def idle(glarea):
	# Invalidate whole window.
	glarea.window.invalidate_rect(glarea.allocation, False)
	# Update window synchronously (fast).
	glarea.window.process_updates(False)
	return True


def map(glarea, event):
	gobject.idle_add(idle, glarea)
	return True

button_pressed = 0
eventx = 0
eventy = 0
modifiers = 0

def buttonpress(glarea, event):
	global button_pressed
	global eventx
	global eventy
	global modifiers
	x, y, width, height = glarea.get_allocation()
	event.y = height - event.y
	eventx = event.x
	eventy = event.y
	button_pressed = event.button

	if modifiers == 0:
		if event.button == 1:
			viewer.rotate_drag_start(event.x, event.y, event.button, modifiers)

		if event.button == 3:
			viewer.pan_drag_start(event.x, event.y, event.button, modifiers)


def buttonrelease(glarea, event):
	global button_pressed
	global eventx
	global eventy
	global modifiers
	if event.button == 1:
		viewer.rotate_drag_end(event.x, event.y, event.button, modifiers)

	if event.button == 3:
		viewer.pan_drag_end(event.x, event.y, event.button, modifiers)
	button_pressed = 0



def init(glarea):
	# get GLContext and GLDrawable
	glcontext = glarea.get_gl_context()
	gldrawable = glarea.get_gl_drawable()

	# GL calls
	if not gldrawable.gl_begin(glcontext): return

	glClearColor(0, 0, 0, 1)
#	glColor3f(1, 0, 0)
	glEnable(GL_DEPTH_TEST)
	glEnable(GL_CULL_FACE)
	glEnable(GL_NORMALIZE)

	# Uncomment this line for a wireframe view
	#lPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

	# Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
	# but this is not the case on Linux or Mac, so remember to always
	# include it.
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	glEnable(GL_LIGHT1)
	glEnable(GL_COLOR_MATERIAL)

	# Define a simple function to create ctypes arrays of floats:
	def vec(*args):
		return (GLfloat * len(args))(*args)

	glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
	glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
	glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(.5, .5, .5, 1))
	glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
	glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
	glLightfv(GL_LIGHT1, GL_SPECULAR, vec(.5, .5, .5, 1))

	glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.8, 0.8, 0.1, 1))
	glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(0, 0, 0, 0))
	glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 0.3)
	glColorMaterial(GL_FRONT,GL_DIFFUSE)
	glColorMaterial(GL_FRONT,GL_AMBIENT)
#        glColorMaterial(GL_FRONT,GL_SPECULAR)

	glEnable(GL_NORMALIZE)

	gldrawable.gl_end()

#	viewer.renderVertices()

def message(str):
	global win
	parent = None
	md = gtk.MessageDialog(win,
		gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
	    gtk.BUTTONS_OK, str)
	md.run()
	md.destroy()
####################################
# MyTextView
####################################

class MyTextView(gtk.TextView):
	def __init__(self):
		gtk.TextView.__init__(self)
		self.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 24)
		self.connect("expose-event", on_text_view_expose_event)

def on_text_view_expose_event(text_view, event):
	text_buffer = text_view.get_buffer()
	bounds = text_buffer.get_bounds()
	text = text_buffer.get_text(*bounds)
	nlines = text.count("\n") + 1
	layout = pango.Layout(text_view.get_pango_context())
	layout.set_markup("\n".join([str(x + 1) for x in range(nlines)]))
	layout.set_alignment(pango.ALIGN_LEFT)
	width = layout.get_pixel_size()[0]
	text_view.set_border_window_size(gtk.TEXT_WINDOW_LEFT, width + 4)
	y = -text_view.window_to_buffer_coords(gtk.TEXT_WINDOW_LEFT, 2, 0)[1]
	window = text_view.get_window(gtk.TEXT_WINDOW_LEFT)
	window.clear()
	text_view.style.paint_layout(window=window,
		state_type=gtk.STATE_NORMAL,
		use_text=True,
		area=None,
		widget=text_view,
		detail=None,
		x=2,
		y=y,
		layout=layout)


####################################
# Script utility functions
####################################

meshstack = []

global dump
def dump(): # TODO
	obj=meshstack[-1]
	print("Vertices")
	print(obj.vertices)
	print("Faces")
	print(obj.faces)

global dup
def dup(n=1):
	if len(meshstack) == 0:
		message("No Object to dup")
		return
	obj=meshstack.pop()
	for i in range(n+1):
		meshstack.append(obj)



global square
def square(s=1): # TODO
	if type(s) is not list:
		w=s
		l=s
	else:
		w=s[0]
		l=s[1]
	vertices = np.empty([4,2],dtype=float)
	vertices[0]=[0,0]
	vertices[1]=[w,0]
	vertices[2]=[w,l]
	vertices[3]=[0,l]
	nd=3

	if nd == 4:
		faces = np.empty([1,nd],dtype=int)
		faces[0]=[0,1,2,3]
	if nd == 3:
		faces = np.empty([2,nd],dtype=int)
		faces[0]=[0,1,2]
		faces[1]=[0,2,3]

	meshstack.append(pymesh.form_mesh(vertices,faces))

global circle	 # TODO
def circle(r=1,n=10):
	vertices = np.empty([n+1,2],dtype=float)
	faces = np.empty([n,3],dtype=int)
	for i in range(n):
		vertices[i]=[
			r*math.cos(2*math.pi*i/n),
			r*math.sin(2*math.pi*i/n)
		]
		faces[i]=[i,(i+1)%n,n]
	vertices[n]=[0,0]

	meshstack.append(pymesh.form_mesh(vertices,faces))

global polygon # TODO
def polygon(path):
	n = len(path);
	edges = np.array([np.arange(n), np.mod(np.arange(n)+1,n)]).T;
	tri = pymesh.triangle()
	tri.points = path
	tri.segments = edges
	tri.split_boundary = False
	tri.verbosity = 0
	tri.run()
	meshstack.append(tri.mesh)

global bezier
def bezier(src,n): # TODO
	dst=[]
	for i in range(n):
		fact0=1.0*i/(n-1)
		fact1=1.0-fact0
		work=src[:]
		while len(work) > 1:
			tmp=[]
			for j in range(len(work)-1):
				x=work[j][0]*fact1+work[j+1][0]*fact0
				y=work[j][1]*fact1+work[j+1][1]*fact0
				tmp.append([x,y])
			work=tmp
		dst.append(work[0])
	return dst

global bezier_surface_sub
def bezier_surface_sub(pts,x,y): # TODO
	n=len(pts)
	sumx=0
	sumy=0
	sumz=0

	fr=[]
	for row in range(n):
		fr.append(math.pow(1.0-y,n-1-row)*math.pow(y,row)*math.factorial(n)/math.factorial(row+1)/math.factorial(n-row))
	fc=[]
	for col in range(n):
		fc.append(math.pow(1.0-x,n-1-col)*math.pow(x,col)*math.factorial(n)/math.factorial(col+1)/math.factorial(n-col))

	for row in range(n):
		for col in range(n):
			sumx =sumx + pts[row][col][0] * fr[row]*fc[col]
			sumy =sumy + pts[row][col][1] * fr[row]*fc[col]
			sumz =sumz  + pts[row][col][2] * fr[row]*fc[col]


	return([sumx,sumy,sumz])

global bezier_surface
def bezier_surface(pts,n=5,zmin=-1):
	ground=0
	vertices = np.empty([n*n+(n-1)*(n-1)+ground*(4*(n-1)+1),3],dtype=float)
	# grosses grid
	# kleines grid
	# n-1 * 4 sockel
	# sockelmittelpunkt

	faces = np.empty([(n-1)*(n-1)*4+ground*(n-1)*4*3,3],dtype=int)
	# 4fach gridmix
	# (n-1)*4*2 mantel
	# (n-1)*4 fusspunkt

	vertoff=0
	# grosses grid
	for j in range(n):
		for i in range(n):
			vertices[vertoff+j*n+i]=bezier_surface_sub(pts,1.0*i/(n-1),1.0*j/(n-1))
	vertoff = vertoff + n*n

	# kleines grid
	for j in range(n-1):
		for i in range(n-1):
			vertices[vertoff+j*(n-1)+i]=bezier_surface_sub(pts,1.0*(i+0.5)/(n-1),1.0*(j+0.5)/(n-1))
	vertoff=vertoff+(n-1)*(n-1)

	if ground == 1:
		sockeltop=[]
		sockel=[]
		#sockel
		# x+
		for i in range(n-1):
			ind=i
			sockeltop.append(ind)
			sockel.append(vertoff)
			vertices[vertoff]=[vertices[ind][0],vertices[ind][1],zmin]
			vertoff=vertoff+1

		# y+
		for i in range(n-1):
			ind=n-1+i*n
			sockeltop.append(ind)
			sockel.append(vertoff)
			vertices[vertoff]=[vertices[ind][0],vertices[ind][1],zmin]
			vertoff=vertoff+1

		# x-
		for i in range(n-1):
			ind=n*n-1-i
			sockeltop.append(ind)
			sockel.append(vertoff)
			vertices[vertoff]=[vertices[ind][0],vertices[ind][1],zmin]
			vertoff=vertoff+1

		# y-
		for i in range(n-1):
			ind=n*(n-1)-i*n
			sockeltop.append(ind)
			sockel.append(vertoff)
			vertices[vertoff]=[vertices[ind][0],vertices[ind][1],zmin]
			vertoff=vertoff+1

		pt=bezier_surface_sub(pts,0.5,0.5)
		vertices[vertoff]=[pt[0],pt[1],zmin]
		ci=vertoff

	# dreiecke
	faceoffset=0
	for j in range(n-1):
		for i in range(n-1):
			faces[4*(j*(n-1)+i)+0][0]=j*n+i
			faces[4*(j*(n-1)+i)+0][1]=j*n+i+1
			faces[4*(j*(n-1)+i)+0][2]=n*n+j*(n-1)+i
			faces[4*(j*(n-1)+i)+1][0]=j*n+i+1
			faces[4*(j*(n-1)+i)+1][1]=j*n+i+1+n
			faces[4*(j*(n-1)+i)+1][2]=n*n+j*(n-1)+i
			faces[4*(j*(n-1)+i)+2][0]=j*n+i+1+n
			faces[4*(j*(n-1)+i)+2][1]=j*n+i+n
			faces[4*(j*(n-1)+i)+2][2]=n*n+j*(n-1)+i
			faces[4*(j*(n-1)+i)+3][0]=j*n+i+n
			faces[4*(j*(n-1)+i)+3][1]=j*n+i
			faces[4*(j*(n-1)+i)+3][2]=n*n+j*(n-1)+i

	faceoffset=faceoffset+4*(n-1)*(n-1)

	if ground == 1:
		# sockel verzippen
		l=len(sockel)
		for i in range(len(sockel)):
			faces[faceoffset]=[sockel[i],sockel[(i+1)%l],sockeltop[(i+1)%l]]
			faceoffset=faceoffset+1
			faces[faceoffset]=[sockel[i],sockeltop[(i+1)%l],sockeltop[i]]
			faceoffset=faceoffset+1

			faces[faceoffset]=[sockel[(i+1)%l],sockel[i],ci]
			faceoffset=faceoffset+1

	meshstack.append(pymesh.form_mesh(vertices,faces))

global cube
def cube(dim=[1,1,1]):
	half=[dim[0]/2.0,dim[1]/2.0,dim[2]/2.0]
	obj=CSG.cube(center=half,radius=half)
	meshstack.append(obj)

global sphere
def sphere(r=1,center=[0,0,0],n=2):
	obj=CSG.sphere(center=center,radius=r)
	meshstack.append(obj)

global cylinder
def cylinder(h=1,r=1,n=16):
	obj = CSG.cylinder(start=[0,0,0],end=[0,0,h],slices=n,radius=r)
	meshstack.append(obj)

global cone
def cone(h=1,r=1,n=16):
	obj = CSG.cone(start=[0,0,0],end=[0,0,h],slices=n,radius=r)
	meshstack.append(obj)

# TODO
#global tube
#def tube(h=1,ro=1,ri=0.5,r1o=None,r2o=None,r1i=None,r2i=None,n=16):
#	if r1o is None:
#		r1o=ro
#	if r2o is None:
#		r2o=ro
#	if r1i is None:
#		r1i=ri
#	if r2i is None:
#		r2i=ri

#global tetrahedron
#def tetrahedron(r=1):
#	meshstack.append(pymesh.generate_regular_tetrahedron(r))
#
#global dodecahedron
#def dodecahedron(r=1):
#	dod=pymesh.generate_dodecahedron(r,[0,0,0])
#	meshstack.append(dod)
#
#global import_obj
#def import_obj(filename):
#	obj=pymesh.load_mesh(filename)
#	meshstack.append(obj)


####

def triangle_combine(faces):
	# Build edge sea
	edge_sea=[]
	for face in faces:
		n=len(face)
		for i in range(n):
			edge_sea.append([face[i],face[(i+1)%n]])

	# Remove duplicate edges in edge_sea
	n=len(edge_sea)
	edge_sea_new = []
	for i in range(n):
		if edge_sea[i] is None:
			continue
		dup=False
		for j in range(n-i-1):
			if edge_sea[i+j+1] is None:
				continue
			if edge_sea[i][0] == edge_sea[i+j+1][1]:
				if edge_sea[i][1] == edge_sea[i+j+1][0]:
					edge_sea[i+j+1]=None
					dup=True
					break # break inner loop, so outer loop will do a continue
		if dup is False:
			edge_sea_new.append(edge_sea[i])
	edge_sea = edge_sea_new

	# build polygons again

	n=len(edge_sea)
	nd=0
	results = []
	while nd < n:
		ind=edge_sea[0][0]
		result=[ind]
		while True:
			done=False
			for i in range(n):
				if edge_sea[i] is None:
					continue
				if edge_sea[i][0] == ind:
					ind=edge_sea[i][1]
					edge_sea[i]=None
					result.append(ind)
					done=True
					nd=nd+1
			if done == False:
				break
		if result[0] != result[-1]:
			print("Polygon is not closed!")
			return
		result.pop()
		results.append(result)
	return results

def extrude_finish_angle(vertices,faces,faceind,i1,i2,i3):
	pt1=vertices[faces[faceind][i1]]
	pt2=vertices[faces[faceind][i2]]
	pt3=vertices[faces[faceind][i3]]
	d1=[pt2[0]-pt1[0],pt2[1]-pt1[1],pt2[2]-pt1[2]]
	d2=[pt3[0]-pt2[0],pt3[1]-pt2[1],pt3[2]-pt2[2]]
	ang=math.acos((d1[0]*d2[0]+d1[1]*d2[1]+d1[2]*d2[2])/math.sqrt((d1[0]*d1[0]+d1[1]*d1[1]+d1[2]*d1[2])*(d2[0]*d2[0]+d2[1]*d2[1]+d2[2]*d2[2])))

	return 180.0-ang*180.0/3.1415

def extrude_finish_link(vertices,faces,p1x,p2x,faceoff,off):
	n1=len(p1x)
	n2=len(p2x)
	i1=0
	i2=0
	while i1 < n1 and i2 < n2: # TODO hier alg besser!
		faces[faceoff,0]=p1x[(i1+1)%n1]
		faces[faceoff,1]=p2x[(i2+1+off)%n2]
		faces[faceoff,2]=p1x[i1]
#		ang1=extrude_finish_angle(vertices,faces,faceoff,2,0,1)
#		ang2=extrude_finish_angle(vertices,faces,faceoff,1,2,0)
#		print(ang1,ang2)
		faceoff=faceoff+1
		# angle 2:0:1  1:2:0

		faces[faceoff,0]=p2x[(i2+off)%n2]
		faces[faceoff,1]=p1x[i1]
		faces[faceoff,2]=p2x[(i2+off+1)%n2]
#		ang1=extrude_finish_angle(vertices,faces,faceoff,2,0,1)
#		ang2=extrude_finish_angle(vertices,faces,faceoff,1,2,0)
#		print(ang1,ang2)
		faceoff=faceoff+1

		i1=i1+1
		i2=i2+1


def extrude_finish(obj,layers,conns,vertices,profile,endcap=1):
	nf=len(obj.faces)
	nv=len(obj.vertices)
	nd=len(obj.faces[0]) # points per face
	# Calculate number of faces required
	faces_num=0
	if endcap == 1:
		faces_num = faces_num + 2*nf
	for x in range(conns):
		p1 = profile[x]
		p2 = profile[(x+1)%layers]
		for p in p1:
			faces_num = faces_num+len(p)/(nd-2)
		for p in p2:
			faces_num = faces_num+len(p)/(nd-2)

	faceoff=0

	if nd == 3:

		faces = np.empty([faces_num,nd],dtype=int)

		if endcap == 1:
			for i in range(nf):
				for j in range(nd):
					faces[faceoff+i][j]=obj.faces[i][nd-j-1] # Bottom Face
					faces[faceoff+nf+i][j]=obj.faces[i][j]+conns*nv # Top Face
			faceoff=2*nf

		# Side walls
		for x in range(conns):
			p1=profile[x]
			p2=profile[(x+1)%layers]
			for i in range(len(p1)):
				p1x=p1[i]
				p2x=p2[i]

				off=0
				extrude_finish_link(vertices,faces,p1x,p2x,faceoff,off)
				faceoff += len(p1x)+len(p2x)



	if nd == 4:

		faces = np.empty([faces_num,nd],dtype=int)

		if endcap == 1:
			for i in range(nf):
				for j in range(nd):
					faces[faceoff+i][j]=obj.faces[i][nd-j-1] # Bottom Face
					faces[faceoff+nf+i][j]=obj.faces[i][j]+conns*nv # Top Face
			faceoff=2*nf

		# Side walls
		for x in range(conns):
			p1=profile[x]
			p2=profile[(x+1)%layers]
			for i in range(len(p1)):
				p1x=p1[i]
				p2x=p2[i]
				n1=len(p1x)
				n2=len(p2x)
				i1=0
				i2=0
				while i1 < n1 and i2 < n2: # TODO hier alg besser!
					faces[faceoff,0]=p1x[i1]
					faces[faceoff,1]=p1x[(i1+1)%n1]
					faces[faceoff,2]=p2x[(i2+1)%n2]
					faces[faceoff,2]=p2x[i2]
					faceoff=faceoff+1
					i1=i1+1
					i2=i2+1


	meshstack.append(pymesh.form_mesh(vertices,faces))


global linear_extrude
def linear_extrude(height=1,n=2,func=None):
	if func is None:
		if len(meshstack) == 0:
			message("No Object to extrude")
			return
		obj=meshstack.pop()
		nv=len(obj.vertices)
		profile=triangle_combine(obj.faces)
	else:
		vertices = None

	profiles = []
	layers=n
	conns=layers-1

	# Generate Points
	vertices = np.empty([layers*nv,3],dtype=float)
	vertice_off=0
	for j in range(layers):
		if func is not None:
			func(j)
			if len(meshstack) == 0:
				message("No Object to extrude")
				return
			obj=meshstack.pop()
			if vertices is None:
				nv=len(obj.vertices)
				vertices = np.empty([layers*nv,3],dtype=float)
				profile=triangle_combine(obj.faces)
			else:
				if nv != len(obj.vertices):
					message("Vertices of object must be constant!")
		for i in range(nv):
			vertices[vertice_off+i][0]=obj.vertices[i][0]
			vertices[vertice_off+i][1]=obj.vertices[i][1]
			vertices[vertice_off+i][2]=1.0*height*j/(layers-1.0)
		tmp_profile=[]
		for subprof in profile:
			newsubprof=[]
			for ind in subprof:
				newsubprof.append(ind+vertice_off)
			tmp_profile.append(newsubprof)
		profiles.append(tmp_profile)
		vertice_off = vertice_off+nv

	extrude_finish(obj,layers,conns,vertices,profiles,1)

global rotate_extrude
def rotate_extrude(n=16,a1=0,a2=360,elevation=0,func=None):

	layers=n+1
	conns=n
	closed=1

	profiles = []
	if func is None:
		if len(meshstack) == 0:
			message("No Object to extrude")
			return
		obj=meshstack.pop()
		nv=len(obj.vertices)
		vertices = np.empty([layers*nv,3],dtype=float)
		profile=triangle_combine(obj.faces)
	else:
		vertices=None


	if a2-a1 == 360 and elevation == 0 and func is None:
		closed=0
		layers = layers-1
	a1=a1*math.pi/180
	a2=a2*math.pi/180


	# Generate Points
	vertice_off=0
	for j in range(layers):
		if func is not None:
			func(j)
			if len(meshstack) == 0:
				message("No Object to extrude")
				return
			obj=meshstack.pop()
			if vertices is None:
				nv=len(obj.vertices)
				vertices = np.empty([layers*nv,3],dtype=float)
				profile=triangle_combine(obj.faces)
			else:
				if nv != len(obj.vertices):
					message("Vertices of object must be constant!")

		for i in range(nv):
			vertices[vertice_off+i][0]=obj.vertices[i][0]*math.cos(a2-(a2-a1)*j/conns)
			vertices[vertice_off+i][1]=obj.vertices[i][0]*math.sin(a2-(a2-a1)*j/conns)
			vertices[vertice_off+i][2]=obj.vertices[i][1]+elevation*j/conns
		tmp_profile=[]
		for subprof in profile:
			newsubprof=[]
			for ind in subprof:
				newsubprof.append(ind+vertice_off)
			tmp_profile.append(newsubprof)
		profiles.append(tmp_profile)
		vertice_off = vertice_off+nv
	extrude_finish(obj,layers,conns,vertices,profiles,closed)

global ang_convert
def ang_convert(span,steps):
	if len(meshstack) == 0:
		message("No Object to convert")
		return

	obj=meshstack.pop()
	#TODO Sliceing an object is overkill, just add more points
	result=None
	step=1.0*span/steps
	for i in range(steps):
		mask=pymesh.generate_box_mesh([step*i,-100,-100],[step*(i+1),100,100])
		slice=pymesh.boolean(obj,mask,"intersection")

		vertices = np.empty([len(slice.vertices),3],dtype=float)
		for i in range(len(slice.vertices)):
			ang=slice.vertices[i][0]
			r=slice.vertices[i][1]
			vertices[i][0]=-r*math.cos(ang)
			vertices[i][1]=r*math.sin(ang)
			vertices[i][2]=slice.vertices[i][2]
		tmp=pymesh.form_mesh(vertices,slice.faces)
		if result is None:
			result = tmp
		else:
			result =pymesh.boolean(result,tmp,"union")
		meshstack.append(result)


####

global translate
def translate(off):

	if len(meshstack) == 0:
		message("No Object to translate")
		return

	obj=meshstack.pop()
	obj.translate(off)
	meshstack.append(obj)


global scale
def scale(s):
	if len(meshstack) == 0:
		message("No Object to scale")
		return
	obj=meshstack.pop()
	dim=len(obj.vertices[0])
	vertices = np.empty([len(obj.vertices),dim],dtype=float)
	if dim == 3:
		if type(s) is not list:
			s = [s,s,s]

		for i in range(len(obj.vertices)):
			vertices[i][0]=obj.vertices[i][0]*s[0]
			vertices[i][1]=obj.vertices[i][1]*s[1]
			vertices[i][2]=obj.vertices[i][2]*s[2]
		meshstack.append(pymesh.form_mesh(vertices,obj.faces))
	elif dim == 2:
		if type(s) is not list:
			s = [s,s]
		for i in range(len(obj.vertices)):
			vertices[i][0]=obj.vertices[i][0]*s[0]
			vertices[i][1]=obj.vertices[i][1]*s[1]
		meshstack.append(pymesh.form_mesh(vertices,obj.faces))
	else:
		message("Dimension %d not supported"%(dim))

global rotate
def rotate(axis,rot):
	if len(meshstack) == 0:
		message("No Object to rotate")
		return
	obj=meshstack.pop()
	obj.rotate(axis,rot)
	meshstack.append(obj)


global mirror
def mirror(v):
	if len(meshstack) == 0:
		message("No Object to mirror")
		return
	obj=meshstack.pop()
	vertices = np.empty([len(obj.vertices),3],dtype=float)
	faces = np.empty([len(obj.faces),3],dtype=int)
	l=v[0]*v[0]+v[1]*v[1]+v[2]*v[2]
	for i in range(len(obj.vertices)):
		pt=obj.vertices[i]
		# find distance from pt to plane therough [0/0/0],v
		d=pt[0]*v[0]+pt[1]*v[1]+pt[2]*v[2]

		vertices[i][0]=obj.vertices[i][0] -2*d*v[0]/l
		vertices[i][1]=obj.vertices[i][1] -2*d*v[1]/l
		vertices[i][2]=obj.vertices[i][2] -2*d*v[2]/l
	for i in range(len(obj.faces)):
		faces[i][0]=obj.faces[i][0]
		faces[i][1]=obj.faces[i][2]
		faces[i][2]=obj.faces[i][1]
	meshstack.append(pymesh.form_mesh(vertices,faces))


global CutPlaneStraight
def CutPlaneStraight(plpos,pldir,s,sd): # Flaeche mit Gerade  s, s-dir schneiden: punkt
	h =np.dot(pldir,sd)
	if math.fabs(h) < 0.001:
		return None
	q=(np.dot(pldir,plpos)-np.dot(pldir,s))/h
	return s + ( sd * q )

global CutPlanePlane
def CutPlanePlane(p1,n1, p2,n2): # return list(pos, dir)
	n3 = np.cross(n1,n2)
	n3s=np.linalg.norm(n3)
	if math.fabs(n3s) < 0.001:
		return None,None
	n3 = n3/n3s

	nx=np.cross(n1,n3)
	p3=CutPlaneStraight(p2,n2,p1,nx)
	if p3 is None:
		return None
	return p3,n3


global size
def size(s=1.0):
	if len(meshstack) == 0:
		message("No Object to size")
		return
	obj=meshstack.pop()

	obj=pymesh.resolve_self_intersection(obj)

	# gemeinsame flaechen weg, kanten verlaengern
	obj.add_attribute("face_normal")
	norms=obj.get_face_attribute("face_normal")

	vertices = np.empty([len(obj.vertices),3],dtype=float)
	# schauen in welchen triangles p evrwendet wird
	refatpoint=[]
	diratpoint=[]
	for i in range(len(obj.vertices)):
		refatpoint.append([])
		diratpoint.append([])


	for i in range(len(obj.faces)):
		face=obj.faces[i]
		dir=norms[i]
		for j in range(len(face)):
			ind=face[j]
			ref=[s*dir[0]+obj.vertices[ind][0],s*dir[1]+obj.vertices[ind][1],s*dir[2]+obj.vertices[ind][2]]
			diratpoint[ind].append(dir)
			refatpoint[ind].append(ref)

	# jetzt alle pt schneiden

	for i in range(len(obj.vertices)):

		vertices[i]=obj.vertices[i] # fallback

		dirs=diratpoint[i]
		refs = refatpoint[i]

		if len(dirs) == 0:
			continue
		dir1 = dirs.pop()
		ref1 = refs.pop()

		vertices[i] = ref1 # better fallback

		#  2 ebenen schneiden/widerholen
		while True:
			if len(dirs) == 0:
				sp = None
				break
			dir2 = dirs.pop()
			ref2 = refs.pop()

			sp,sd = CutPlanePlane(ref1,dir1,ref2,dir2)
			if sp is not None:
				break
		if sp is None:
			continue

		# ebene mit gerade schneiden
		while True:
			if len(dirs) == 0:
				pt = None
				break
			dir3 = dirs.pop()
			ref3 = refs.pop()
			pt=CutPlaneStraight(ref3,dir3,sp,sd)
			if pt is not None:
				break
		if pt is not None:
			vertices[i]=pt
		else:
			vertices[i]=sp # Kompromiss

	obj=pymesh.resolve_self_intersection(obj)
# pymesh.nerge_meshes
	obj=pymesh.form_mesh(vertices,obj.faces)
	meshstack.append(obj)



global top
def top():
	cube([2000,2000,1000])
	translate([-1000,-1000,0])
	intersection()

global bottom
def bottom():
	cube([2000,2000,1000])
	translate([-1000,-1000,-1000])
	intersection()

global right
def right():
	cube([1000,2000,2000])
	translate([0,-1000,-1000])
	intersection()

global left
def left():
	cube([1000,2000,2000])
	translate([-1000,-1000,-1000])
	intersection()

global front
def front():
	cube([2000,1000,2000])
	translate([-1000,0,-1000])
	intersection()


global back
def back():
	cube([2000,1000,2000])
	translate([-1000,-1000,-1000])
	intersection()

####

global difference
def difference():
	if len(meshstack) < 2:
		message("Too less Objects for Difference")
		return
	obj2=meshstack.pop()
	obj1=meshstack.pop()
	meshstack.append(obj1.inverse().union(obj2).inverse())

global union
def union(n=2):
	if n == 1:
		return
	if len(meshstack) < n:
		message("Too less Objects for Union")
		return
	obj1=meshstack.pop()
	for i in range(n-1):
		obj2=meshstack.pop()
		obj1 =obj1.union(obj2)
	meshstack.append(obj1)

global concat
def concat(n=2):
	if n == 1:
		return
	if len(meshstack) < n:
		message("Too less Objects for Concat")
		return
	objs=[]

	# Calculate number of required vertices and faces
	vertlen=0
	facelen=0
	for i in range(n):
		obj=meshstack.pop()
		vertlen += len(obj.vertices)
		facelen += len(obj.faces)
		objs.append(obj)


	vertices = np.empty([vertlen,3],dtype=float)
	faces = np.empty([facelen,3],dtype=int)

	# Now concatenate all vertices and faces
	vertoff=0
	faceoff=0
	for i in range(n):
		obj=objs[i]
		for j in range(len(obj.vertices)):
			vert=obj.vertices[j]
			vertices[j+vertoff]=vert

		for j in range(len(obj.faces)):
			face=obj.faces[j]
			faces[j+faceoff] = [face[0]+vertoff,face[1]+vertoff,face[2]+vertoff]

		vertoff = vertoff + len(obj.vertices)
		faceoff = faceoff + len(obj.faces)
	obj=pymesh.form_mesh(vertices,faces)
	meshstack.append(obj)


global hull
def hull():
	if len(meshstack) == 0:
		message("No Object to hull")
		return

	obj=meshstack.pop()
	obj=pymesh.convex_hull(obj)
	meshstack.append(obj)

global intersection
def intersection(n=2):
	if n == 1:
		return
	if len(meshstack) < n:
		message("Too less Objects for Intersection")
		return
	obj1=meshstack.pop()
	for i in range(n-1):
		obj2=meshstack.pop()
		obj1 =obj1.intersect(obj2)
	meshstack.append(obj1)


global volume
def volume():
	volume=0
	if len(meshstack) == 0:
		message("No Object to calculate")
		return
	obj=meshstack.pop()
	dim=len(obj.vertices[0])
	if  dim == 2:
		for tri in obj.faces:
			n=len(tri)
			for j in range(n):
				p1=obj.vertices[tri[j]]
				p2=obj.vertices[tri[(j+1)%n]]
				area=p1[0]*p2[1]-p1[1]*p2[0]
				volume=volume+area
	if  dim == 3:
		for tri in obj.faces:
			n=len(tri)
			for j in range(n):
				p1=obj.vertices[tri[j]]
				p2=obj.vertices[tri[(j+1)%n]]
				p3=obj.vertices[tri[(j+2)%n]]
				area	=p1[0]*p2[1]*p3[2]+p1[1]*p2[2]*p3[0]+p1[2]*p2[0]*p3[1]-p1[2]*p2[1]*p3[0]-p1[0]*p2[2]*p3[1]-p1[1]*p2[0]*p3[2]
				volume=volume+area
	return volume/18.0;



####################################
# Top
####################################

def render(window):
	global meshstack
#	model.items = []
	meshstack = []

	try:
		buffer = tv.get_buffer()
		script = buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
		exec(script)
	except Exception:
		message("Error in Script")
		traceback.print_exc()
#		viewer.renderVertices()
		return

	if len(meshstack) == 0:
		message( "Error: No Objects generated")
#		viewer.renderVertices()
		return

	if(len(meshstack) > 1):
		union(len(meshstack))

	mesh=meshstack.pop()
#	if len(mesh) == 0:
#		viewer.renderVertices()
#		return

#	if len(mesh.vertices[0]) == 2:
#		meshstack.append(mesh)
#		linear_extrude(1)
#		mesh=meshstack[0]
#	meshstack.append(mesh)


#	if len(mesh.vertices[0]) != 3:
#		message( "Not a a 3D Object")
#		viewer.renderVertices()
#		return

	olygons=mesh.toPolygons()
	ptmin = [ polygons[0].vertices[0].pos.x,polygons[0].vertices[0].pos.y, polygons[0].vertices[0].pos.z ]
	ptmax = [ polygons[0].vertices[0].pos.x,polygons[0].vertices[0].pos.y, polygons[0].vertices[0].pos.z ]
	for poly in polygons:
		for pt in poly.vertices:
			if pt.pos.x > ptmax[0]:
				ptmax[0] = pt.pos.x
			if pt.pos.x < ptmin[0]:
				ptmin[0] = pt.pos.x

			if pt.pos.y > ptmax[1]:
				ptmax[1] = pt.pos.y
			if pt.pos.y < ptmin[1]:
				ptmin[1] = pt.pos.y

			if pt.pos.z > ptmax[2]:
				ptmax[2] = pt.pos.z
			if pt.pos.z < ptmin[2]:
				ptmin[2] = pt.pos.z

	print("Dimension [%g %g %g]\n"%(ptmax[0]-ptmin[0],ptmax[1]-ptmin[1],ptmax[2]-ptmin[2]))
	viewer.renderVertices(mesh)



def save_script(window):
	buffer = tv.get_buffer()
	script = buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
	outfile = open(args.file, "w")
	if outfile:
		outfile.write(script)
		outfile.close()


def export_stl(window):
	if len(meshstack) == 0:
		message( "Error: No Objects generated")
		viewer.renderVertices()
		return
	mesh = meshstack[0]
	text_filter=gtk.FileFilter()
	text_filter.set_name("Text files")
	text_filter.add_mime_type("text/*")
	all_filter=gtk.FileFilter()
	all_filter.set_name("All files")
	all_filter.add_pattern("*")

	filename=None
	dialog=gtk.FileChooserDialog(title="Select a File", action=gtk.FILE_CHOOSER_ACTION_SAVE,
		buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))

	dialog.add_filter(text_filter)
	dialog.add_filter(all_filter)

	response = dialog.run()

	if response == gtk.RESPONSE_OK:
		filename = dialog.get_filename()
		pymesh.save_mesh(filename, mesh);
		message("File Exported")
	dialog.destroy()

#
# GLX version
#

major, minor = gtk.gdkgl.query_version()

#
# frame buffer configuration
#

# use GLUT-style display mode bitmask
try:
	# try double-buffered
	glconfig = gtk.gdkgl.Config(mode=(gtk.gdkgl.MODE_RGB|
				  gtk.gdkgl.MODE_DOUBLE |
				   gtk.gdkgl.MODE_DEPTH))
except gtk.gdkgl.NoMatches:
	# try single-buffered
	glconfig = gtk.gdkgl.Config(mode=(gtk.gdkgl.MODE_RGB	|
					  gtk.gdkgl.MODE_DEPTH))


parser = argparse.ArgumentParser()
parser.add_argument("file", help="Graphics  File")
parser.add_argument("-s", "--scale", help="Scale(1.0)",default=1.0)
args = parser.parse_args()
signal.signal(signal.SIGINT, signal.SIG_DFL)

# https://gist.github.com/otsaloma/1912166
tv = MyTextView()
tv.set_size_request(300, 600)

#tv.connect("draw", on_text_view_draw)
tvscroll = gtk.ScrolledWindow()
tvscroll.add(tv)

#model = Model()

#if args.file.endswith(".svg"):
#	model.loadSvg(args.file,args.scale)
#if args.file.endswith(".plt"):
#	model.loadPlt(args.file,args.scale)
#if args.file.endswith(".gcode"):
#	model.loadGcode(args.file)
#if args.file.endswith(".ngc"):
#	model.loadNgc(args.file)
#if args.file.endswith(".stl"):
#	model.loadStl(args.file,1.0,1.0,1.0)
if args.file.endswith(".py"):
	textbuffer = tv.get_buffer()
	infile = open(args.file, "r")
	if infile:
		string = infile.read()
		infile.close()
		textbuffer.set_text(string)

#
# top-level gtk.Window
#


viewer = Viewer()
#viewer.setModel(model)



win = gtk.Window()
win.set_title("Model Viewer")

#if sys.platform != 'win32':
#	win.set_resize_mode(gtk.RESIZE_IMMEDIATE)
win.set_reallocate_redraws(True)

win.connect('destroy', gtk.main_quit)


glarea = gtk.gtkgl.DrawingArea(glconfig)
glarea.set_size_request(500, 600)

glarea.connect_after('realize', init)
glarea.connect('configure_event', reshape)
glarea.connect('expose_event', draw)
glarea.connect('map_event', map)
glarea.connect('button-press-event',buttonpress)
glarea.connect('button-release-event',buttonrelease)
glarea.connect('motion-notify-event',pointermotion)
glarea.connect('scroll-event',scrollevent)
glarea.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)
glarea.show()

hbox = gtk.HPaned()
hbox.add(tvscroll)
hbox.add(glarea)

filesave = gtk.MenuItem("Save")
filesave.connect("activate", save_script)

fileexport = gtk.MenuItem("Export STL")
fileexport.connect("activate", export_stl)

fileexit = gtk.MenuItem("Exit")
fileexit.connect("activate", gtk.main_quit)

filemenu = gtk.Menu()
filemenu.append(filesave)
filemenu.append(fileexport)
filemenu.append(fileexit)

filem = gtk.MenuItem("File")
filem.set_submenu(filemenu)

mb = gtk.MenuBar()
mb.append(filem)

vbox = gtk.VBox(False, 2)
vbox.pack_start(mb, False, False, 0)
vbox.add(hbox)

win.add(vbox)
win.connect('key-press-event',keypressevent)
win.connect('key-release-event',keyreleaseevent)

win.show_all()

gtk.main()
# vim: softtabstop=8 noexpandtab

