#! /usr/bin/python
#! /home/gigl/anaconda3/bin/python

# TODO editor syntax highlighting
# TODO mirror
#  ang_converrt, slice
# TODO publish
# TODO GTK3
# TODO DOCU
# TODO model loswerden ?


import math
import argparse
import sys
import signal
import numpy as np

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
from model import *
import pymesh

from OpenGL.GL import *

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
					

	def renderVertices(self):
		self.raw_lines = []
		self.raw_triangles = []
		self.raw_triangles_normal=[]

		self.renderLines(self.model.items)
		for path in self.model.pathes:
			self.renderLines(path)
	
		
		self.lines = [];

		self.call_lists = [];
		for ind in range(len(self.raw_triangles)): # Anzahl der layer
			data_tri = self.raw_triangles[ind]
			data_normal = self.raw_triangles_normal[ind]
			data_lines = self.raw_lines[ind]
			listind = glGenLists(1)
			glNewList(listind, GL_COMPILE)
			glBegin(GL_TRIANGLES)
			for i in range(len(data_tri)/3):
				glColor3f(0.8,0.8,0)
				glNormal3f(data_normal[3*i+0], data_normal[3*i+1], data_normal[3*i+2])
				glVertex3f(data_tri[3*i+0], data_tri[3*i+1], data_tri[3*i+2])
			glEnd()

			glBegin(GL_LINES)
			for i in range(len(data_lines)/3):
				glVertex3f(data_lines[3*i+0], data_lines[3*i+1], data_lines[3*i+2])
			glEnd()
			
			glEndList()
	
			self.call_lists.append(listind)
	
		self.layer_num = len(self.call_lists)
		self.start_layer=0
		self.end_layer = self.layer_num-1



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
	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	
	# rotate axes to match reprap style
	glRotated(-90, 1,0,0)

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


	for i in range(viewer.end_layer-viewer.start_layer+1):
#		viewer.lines[viewer.start_layer+i].draw(GL_LINES)
		glColor3f(0,1,0)
		glCallList(viewer.call_lists[viewer.start_layer+i])
	
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

	viewer.renderVertices()

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
def dump():
	obj=meshstack[-1]
	print("Vertices")
	print(obj.vertices)
	print("Faces")
	print(obj.faces)

global square
def square(s=1):
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

global circle	
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

global polygon
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
def bezier(src,n):
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


global cube	
def cube(dim=[1,1,1]):
	cube=pymesh.generate_box_mesh([0,0,0],dim)
	meshstack.append(cube)

global sphere
def sphere(r=1,center=[0,0,0],n=2):
	meshstack.append(pymesh.generate_icosphere(r,center,refinement_order=n))

global cylinder
def cylinder(h=1,r=1,r1=None,r2=None,n=16):
	if r1 is None:
		r1=r
	if r2 is None:
		r2=r
	meshstack.append(pymesh.generate_cylinder([0,0,0],[0,0,h],r1,r2,num_segements=n))

global tube
def tube(h=1,ro=1,ri=0.5,r1o=None,r2o=None,r1i=None,r2i=None,n=16):
	if r1o is None:
		r1o=ro
	if r2o is None:
		r2o=ro
	if r1i is None:
		r1i=ri
	if r2i is None:
		r2i=ri
	meshstack.append(pymesh.generate_tube([0,0,0],[0,0,h],r1o,r2o,r1i,r2i,num_segments=n))

global tetrahedron
def tetrahedron(r=1):
	meshstack.append(pymesh.generate_regular_tetrahedron(r))

global dodecahedron
def dodecahedron(r=1):
	dod=pymesh.generate_dodecahedron(r,[0,0,0])
	meshstack.append(dod)

####
def extrude_finish(obj,layers,conns,vertices,endcap=1):
	nf=len(obj.faces)
	nv=len(obj.vertices)
	nd=len(obj.faces[0]) # points per face

	# Interior faces of base polygons assembled by tri/quads are also built
	faces = np.empty([2*nf*endcap+conns*nd*nf*(5-nd),nd],dtype=int)
#	for j in range(len(faces)):
#		for i in range(nd):
#			faces[j][i]=-1

	if endcap == 1:
		for i in range(nf):
			for j in range(nd):
				faces[i][j]=obj.faces[i][nd-j-1] # Bottom Face
				faces[nf+i][j]=obj.faces[i][j]+conns*nv # Top Face

	if nd == 3:

		# Side walls
		for x in range(conns):
			for i in range(nf):
				for j in range(nd):
					faces[2*nf*endcap+2*(nd*(x*nf+i)+j)+0,0]=obj.faces[i][j]+x*nv
					faces[2*nf*endcap+2*(nd*(x*nf+i)+j)+0,1]=obj.faces[i][(j+1)%nd]+x*nv
					faces[2*nf*endcap+2*(nd*(x*nf+i)+j)+0,2]=obj.faces[i][(j+1)%nd]+((x+1)%layers)*nv

					faces[2*nf*endcap+2*(nd*(x*nf+i)+j)+1,0]=obj.faces[i][j]+x*nv
					faces[2*nf*endcap+2*(nd*(x*nf+i)+j)+1,1]=obj.faces[i][(j+1)%nd]+((x+1)%layers)*nv
					faces[2*nf*endcap+2*(nd*(x*nf+i)+j)+1,2]=obj.faces[i][j]+((x+1)%layers)*nv

	if nd == 4:

		# Side walls
		for x in range(conns):
			for i in range(nf):
				for j in range(nd):
					faces[2*nf*endcap+nd*(x*nf+i)+j,0]=obj.faces[i][j]+x*nv
					faces[2*nf*endcap+nd*(x*nf+i)+j,1]=obj.faces[i][(j+1)%nd]+x*nv
					faces[2*nf*endcap+nd*(x*nf+i)+j,2]=obj.faces[i][(j+1)%nd]+((x+1)%layers)*nv
					faces[2*nf*endcap+nd*(x*nf+i)+j,3]=obj.faces[i][j]+((x+1)%layers)*nv

	meshstack.append(pymesh.form_mesh(vertices,faces))


global linear_extrude
def linear_extrude(height=1):
	if len(meshstack) == 0:
		message("No Object to extrude")
		return
	obj=meshstack.pop()
	nv=len(obj.vertices)
	layers=2
	conns=layers-1

	# Generate Points
	vertices = np.empty([layers*nv,3],dtype=float)
	for j in range(layers):
		for i in range(nv):
			vertices[j*nv+i][0]=obj.vertices[i][0]
			vertices[j*nv+i][1]=obj.vertices[i][1]
			vertices[j*nv+i][2]=height*j/(layers-1)

	extrude_finish(obj,layers,conns,vertices,1)

global rotate_extrude
def rotate_extrude(n=16,a1=0,a2=360,elevation=0,func=None):

	layers=n+1
	conns=n
	closed=1

	if func == None:
		if len(meshstack) == 0:
			message("No Object to extrude")
			return
		obj=meshstack.pop()
		nv=len(obj.vertices)
		vertices = np.empty([layers*nv,3],dtype=float)
	else:
		vertices=None


	if a2-a1 == 360 and elevation == 0 and func is None:
		closed=0
		layers = layers-1
	a1=a1*math.pi/180
	a2=a2*math.pi/180
	

	# Generate Points
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
			else:
				if nv != len(obj.vertices):
					message("Vertices of object must be constant!")
	
		for i in range(nv):
			vertices[j*nv+i][0]=obj.vertices[i][0]*math.cos(a2-(a2-a1)*j/conns)
			vertices[j*nv+i][1]=obj.vertices[i][0]*math.sin(a2-(a2-a1)*j/conns)
			vertices[j*nv+i][2]=obj.vertices[i][1]+elevation*j/conns
	extrude_finish(obj,layers,conns,vertices,closed)

####

global translate
def translate(off):

	if len(meshstack) == 0:
		message("No Object to translate")
		return

	obj=meshstack.pop()
	dim=len(obj.vertices[0])
	if dim == 3:	
		xs=off[0]
		if type(xs) is not list:
			xs=[xs]

		ys=off[1]
		if type(ys) is not list:
			ys=[ys]

		zs=off[2]
		if type(zs) is not list:
			zs=[zs]

		for z in zs:
			for y in ys:
				for x in xs:

					vertices = np.empty([len(obj.vertices),dim],dtype=float)
					for i in range(len(obj.vertices)):
						vertices[i][0]=obj.vertices[i][0]+x
						vertices[i][1]=obj.vertices[i][1]+y
						vertices[i][2]=obj.vertices[i][2]+z
					meshstack.append(pymesh.form_mesh(vertices,obj.faces))
		union(len(xs)*len(ys)*len(zs))
	elif dim == 2:
		vertices = np.empty([len(obj.vertices),dim],dtype=float)
		for i in range(len(obj.vertices)):
			vertices[i][0]=obj.vertices[i][0]+off[0]
			vertices[i][1]=obj.vertices[i][1]+off[1]
		meshstack.append(pymesh.form_mesh(vertices,obj.faces))
	else:
		message("Dimension %d not supported"%(dim))

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
def rotate(rot):
	if len(meshstack) == 0:
		message("No Object to rotate")
		return
	obj=meshstack.pop()
	dim=len(obj.vertices[0])
	if dim == 3:
		rotmat = None
		if rot[0] != 0:
			xc=math.cos(rot[0]*math.pi/180)
			xs=math.sin(rot[0]*math.pi/180)
			rotmat = [[1,0,0],[0,xc,-xs],[0,xs,xc]]
	
		if rot[1] != 0:
			yc=math.cos(rot[1]*math.pi/180)
			ys=math.sin(rot[1]*math.pi/180)
			rotmaty = [[yc,0,ys],[0,1,0],[-ys,0,yc]]
			if rotmat is None:
				rotmat=rotmaty
			else:
				rotmat = np.matmul(rotmat,rotmaty)

		if rot[2] != 0:
			zc=math.cos(rot[2]*math.pi/180)
			zs=math.sin(rot[2]*math.pi/180)
			rotmatz = [[zc,-zs,0],[zs,zc,0],[0,0,1]] 
			if rotmat is None:
				rotmat=rotmatz
			else:
				rotmat = np.matmul(rotmat,rotmatz)

		if rotmat is None:
			return
		vertices = np.empty([len(obj.vertices),dim],dtype=float)
		for i in range(len(obj.vertices)):
			vertices[i]=np.matmul(obj.vertices[i],rotmat)
		meshstack.append(pymesh.form_mesh(vertices,obj.faces))
	elif dim == 2:
		zc=math.cos(rot*math.pi/180)
		zs=math.sin(rot*math.pi/180)
		rotmat = [[zc,-zs],[zs,zc]] 
		vertices = np.empty([len(obj.vertices),dim],dtype=float)
		for i in range(len(obj.vertices)):
			vertices[i]=np.matmul(obj.vertices[i],rotmat)
		meshstack.append(pymesh.form_mesh(vertices,obj.faces))
	else:
		message("Dimension %d not supported"%(dim))


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
	meshstack.append(pymesh.boolean(obj1,obj2,"difference"))

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
		obj1 =pymesh.boolean(obj1,obj2,"union")
	meshstack.append(obj1)

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
		obj1 =pymesh.boolean(obj1,obj2,"intersection")
	meshstack.append(obj1)


####################################
# Top
####################################

def render(window):
	global meshstack
	model.items = []
	meshstack = []

	try:
		buffer = tv.get_buffer()
		script = buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
		exec(script)
	except Exception:
		message("Error in Script")
		traceback.print_exc()
		viewer.renderVertices()
		return

	if len(meshstack) == 0:
		message( "Error: No Objects generated")
		viewer.renderVertices()
		return

	if(len(meshstack) > 1):
		union(len(meshstack))

	mesh=meshstack.pop()
	if len(mesh.vertices[0]) == 2:
		meshstack.append(mesh)
		linear_extrude(1)
		mesh=meshstack[0]
	meshstack.append(mesh)


	if len(mesh.vertices[0]) != 3:
		message( "Not a a 3D Object")
		viewer.renderVertices()
		return

	ptmin = [ mesh.vertices[0][0],mesh.vertices[0][1], mesh.vertices[0][2] ]
	ptmax = [ mesh.vertices[0][0],mesh.vertices[0][1], mesh.vertices[0][2] ]
	for pt in mesh.vertices:
		if pt[0] > ptmax[0]:
			ptmax[0] = pt[0]
		if pt[0] < ptmin[0]:
			ptmin[0] = pt[0]
		if pt[1] > ptmax[1]:
			ptmax[1] = pt[1]
		if pt[1] < ptmin[1]:
			ptmin[1] = pt[1]
		if pt[2] > ptmax[2]:
			ptmax[2] = pt[2]
		if pt[2] < ptmin[2]:
			ptmin[2] = pt[2]
	print("Dimension %g:%g:%g\n",ptmax[0]-ptmin[0],ptmax[1]-ptmin[1],ptmax[2]-ptmin[2])
	v = mesh.vertices;
	mesh.add_attribute("face_normal")
	norms=mesh.get_face_attribute("face_normal")
	for i in range(len(mesh.faces)):
		face=mesh.faces[i]
		n = norms[i]
		n = Model.Point(n[0],n[1],n[2])
		for i in range(len(face)-2):
			tri = Model.Triangle(
				model.Point(v[face[0]][0],v[face[0]][1],v[face[0]][2]),
				model.Point(v[face[i+1]][0],v[face[i+1]][1],v[face[i+1]][2]),
				model.Point(v[face[i+2]][0],v[face[i+2]][1],v[face[i+2]][2]),
				n)
			model.items.append(tri)
	viewer.renderVertices()
	


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

model = Model()

if args.file.endswith(".svg"):
	model.loadSvg(args.file,args.scale)
if args.file.endswith(".plt"):
	model.loadPlt(args.file,args.scale)
if args.file.endswith(".gcode"):
	model.loadGcode(args.file)
if args.file.endswith(".ngc"):
	model.loadNgc(args.file)
if args.file.endswith(".stl"):
	model.loadStl(args.file,1.0,1.0,1.0)
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
viewer.setModel(model)



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
