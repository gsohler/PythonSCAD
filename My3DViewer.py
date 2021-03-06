#!/usr/bin/python3

import os
import sys
import math
import struct

import glm

# https://learnopengl.com/Getting-started/Shaders 
# http://www.songho.ca/opengl/gl_vbo.html#example2
# https://learnopengl.com/code_viewer.php?code=advanced/cubemaps-exercise1

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np

from csg.geom import Vertex, Vector

experiment=False # TODO loswerden
# Local Space
# -> Model Matrix, wie ist das Ding gedreht im Raum
# World Space
# -> View Matrix, zur Camera hin drehen
# View Space
# -> Projection Matrix # Orthogonal oder Pespectivisch
# Clip Space
# Screen Space

VERTEX_SHADER = """
    #version 330
    //uniforms
    uniform mat4 matrixModelModel; // Model Matrix
    uniform mat4 matrixModelView; // View Matrix
    uniform mat4 matrixModelProjection; //Projection Matrix
    // vertex attribs (input)
    attribute vec3 vertexPosition;
    attribute vec3 vertexNormal;
    attribute vec3 vertexColor;
    // varyings (output)
    varying vec3 color;
    void main()
    {
        gl_Position = matrixModelProjection * matrixModelView * matrixModelModel * vec4(vertexPosition, 1.0);
        vec4 wnormal  =  matrixModelView * matrixModelModel * vec4(vertexNormal, 0.0);
        vec4 sight = vec4(0, 0, 1.0, 0.0);
        float fdot = dot(sight, wnormal);
        color = vertexColor * (fdot*0.6+0.4);
    }"""

FRAGMENT_SHADER = """
    #version 330
    // uniforms
    uniform vec4 lightPosition;             // should be in the eye space
    uniform vec4 lightAmbient;              // light ambient color
    uniform vec4 lightDiffuse;              // light diffuse color
    uniform vec4 lightSpecular;             // light specular color

    // varyings
//    varying vec3 esVertex, esNormal;
    varying vec3 color;

    void main()
    {
//        vec3 normal = normalize(esNormal);
//        vec3 light;
//        if(lightPosition.w == 0.0)
//        {
//            light = normalize(lightPosition.xyz);
//        }
//        else
//        {
//            light = normalize(lightPosition.xyz - esVertex);
//        }
//        vec3 view = normalize(-esVertex);
//        vec3 halfv = normalize(light + view);

//        vec3 fragColor = lightAmbient.rgb * color;                  // begin with ambient
//        float dotNL = max(dot(normal, light), 0.0);
//       fragColor += lightDiffuse.rgb * color * dotNL;              // add diffuse
//       float dotNH = max(dot(normal, halfv), 0.0);
//       fragColor += pow(dotNH, 128.0) * lightSpecular.rgb * color; // add specular
        
       // set frag color
       // gl_FragColor = vec4(fragColor, 1.0);  // keep opaque=1
       gl_FragColor = vec4(color, 1.0);  // keep opaque=1

    }
    """


class My3DViewer(Gtk.GLArea):

    def createShader(self):
        vs = shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
        fs = shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        self.shader = shaders.compileProgram(vs, fs)

    def copyDataToBuffers(self):
        print("copy")

        if experiment == True:
            self.pts=self.vertices
            self.indices = self.xindices

        npobj = np.arange(len(self.pts)*9,dtype=np.float32)
        for i in range(len(self.pts)):
            for j in range(9):
                npobj[i*9+j] = self.pts[i][j]
        npindices = np.array(self.indices, dtype=np.int32)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)


        # Get the position of the 'position' in parameter of our shader and bind it.

        glEnableVertexAttribArray(self.attribVertexPosition)
        glEnableVertexAttribArray(self.attribVertexNormal)
        glEnableVertexAttribArray(self.attribVertexColor)



        glVertexAttribPointer(self.attribVertexPosition, 3, GL_FLOAT, GL_FALSE, 4*9*1, ctypes.c_void_p(4*0))
        glVertexAttribPointer(self.attribVertexNormal,   3, GL_FLOAT, GL_FALSE, 4*9*1, ctypes.c_void_p(4*3))
        glVertexAttribPointer(self.attribVertexColor,    3, GL_FLOAT, GL_FALSE, 4*9*1, ctypes.c_void_p(4*6))

        glBufferData(GL_ARRAY_BUFFER,4*len(npobj),npobj,GL_DYNAMIC_DRAW)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4*len(npindices), npindices, GL_DYNAMIC_DRAW) 




#        glBindBuffer(GL_ARRAY_BUFFER, 0)
#        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)


    def updateTransform(self,phi,theta):

        glUseProgram(self.shader)

        self.matrixModelModel = glm.mat4(1.0) # Modell wird nicht gedreht
        glUniformMatrix4fv(self.uniformMatrixModelModel,1,GL_FALSE,glm.value_ptr(self.matrixModelModel))

        self.matrixModelView = glm.mat4(1.0)
        self.matrixModelView = glm.translate(self.matrixModelView,glm.vec3(self.PX,self.PY,-self.zoom))
        self.matrixModelView = glm.rotate(self.matrixModelView,-glm.radians(phi),glm.vec3(1,0,0))
        self.matrixModelView = glm.rotate(self.matrixModelView,glm.radians(theta),glm.vec3(0,1,0))
        glUniformMatrix4fv(self.uniformMatrixModelView,1,GL_FALSE,glm.value_ptr(self.matrixModelView))

        self.matrixModelProjection=glm.perspective(glm.radians(45),self.screen.width/self.screen.height, 0.1, 100.0) 
        glUniformMatrix4fv(self.uniformMatrixModelViewProjection,1,GL_FALSE,glm.value_ptr(self.matrixModelProjection))

    def initGLSL(self):
        self.createShader()
        glUseProgram(self.shader)

        self.uniformMatrixModelView = glGetUniformLocation(self.shader, "matrixModelView")
        self.uniformMatrixModelViewProjection = glGetUniformLocation(self.shader, "matrixModelProjection")
        self.uniformMatrixModelModel  = glGetUniformLocation(self.shader, "matrixModelModel");
        self.uniformLightPosition = glGetUniformLocation(self.shader, "lightPosition");
        self.uniformLightAmbient  = glGetUniformLocation(self.shader, "lightAmbient");
        self.uniformLightDiffuse  = glGetUniformLocation(self.shader, "lightDiffuse");
        self.uniformLightSpecular = glGetUniformLocation(self.shader, "lightSpecular");

        self.attribVertexPosition = glGetAttribLocation(self.shader, "vertexPosition")
        self.attribVertexNormal   = glGetAttribLocation(self.shader, "vertexNormal")
        self.attribVertexColor    = glGetAttribLocation(self.shader, "vertexColor")


        # set uniform values
        lightPosition = np.array([0.0, 0.0, 1.0, 0.0],dtype=np.float32);
        lightAmbient  = np.array([0.3, 0.3, 0.3, 1.0],dtype=np.float32);
        lightDiffuse  = np.array([0.7, 0.7, 0.7, 1.0],dtype=np.float32);
        lightSpecular = np.array([1.0, 1.0, 1.0, 1.0],dtype=np.float32);
        glUniform4fv(self.uniformLightPosition, 1, lightPosition); 
        glUniform4fv(self.uniformLightAmbient, 1, lightAmbient);
        glUniform4fv(self.uniformLightDiffuse, 1, lightDiffuse);
        glUniform4fv(self.uniformLightSpecular, 1, lightSpecular);

    def on_configure_event(self, widget):
        print('realize event')

        widget.make_current()
        # widget.attach_buffers()
        context = widget.get_context()

        self.initGL()
        self.initGLSL()

        # Generate empty buffer
        self.vbo = glGenBuffers(1) 
        self.ibo = glGenBuffers(1)

        # Generate empty vertex Array Object
        self.vao = glGenVertexArrays(1)
        glBindVertexArray( self.vao )

        # Set as current vertex array

        self.pts = [] 
        self.resetVertices()
#        self.pts = self.vertices
#        self.indices = self.xindices
#        self.draw_inst=[[0,3]] # TODO

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)


        self.copyDataToBuffers() # TODO einfacher

        self.matrixModelView = None

        self.queue_draw()



        return True



    def on_draw(self, widget, ctx):
        print('draw event')
        self.screen=widget.get_allocation()

        if self.matrixModelView is None:
            self.updateTransform(self.RX,self.RZ)

#        glUseProgram(self.shader)


        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if experiment == True:
            glDrawElements(GL_TRIANGLES,3,GL_UNSIGNED_INT,ctypes.c_void_p(0)) 
        print(self.indices)
        if self.draw_inst is not None:
            for inst in self.draw_inst:
                print(inst)
                glDrawElements(GL_TRIANGLES,inst[0]+inst[1],GL_UNSIGNED_INT,ctypes.c_void_p(inst[0])) 

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        glFlush()


        return True

    def rotate_drag_start(self, x, y, button, modifiers):
        self.rotateDragStartRX = self.RX
        self.rotateDragStartRZ = self.RZ
        self.rotateDragStartX = x
        self.rotateDragStartY = y


    def rotate_drag_do(self, x, y, dx, dy, buttons, modifiers):
        # deltas
        deltaX = x - self.rotateDragStartX
        deltaY = y - self.rotateDragStartY
        # rotate!
        self.RZ = self.rotateDragStartRZ + deltaX/5.0 # mouse X bound to model Z
        self.RX = self.rotateDragStartRX + deltaY/5.0 # mouse Y bound to model X
        self.updateTransform(self.RX,self.RZ)
        self.queue_draw()


    def rotate_drag_end(self, x, y, button, modifiers):
        self.rotateDragStartRX = None
        self.rotateDragStartRZ = None
        self.rotateDragStartX = None
        self.rotateDragStartY = None


    def pan_drag_start(self, x, y, button, modifiers):
        self.panDragStartPX = self.PX
        self.panDragStartPY = self.PY
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
        self.updateTransform(self.RX,self.RZ) 
        self.queue_draw()


    def pan_drag_end(self, x, y, button, modifiers):
        self.panDragStartPX = None
        self.panDragStartPY = None
        self.panDragStartX = None
        self.panDragStartY = None


    def buttonpress(self,widget, event):
        event.y = self.screen.height - event.y
        self.eventx = event.x
        self.eventy = event.y
        self.button_pressed = event.button

        if self.modifiers == 0:
            if event.button == 1:
                self.rotate_drag_start(event.x, event.y, event.button, self.modifiers)

            if event.button == 3:
                self.pan_drag_start(event.x, event.y, event.button, self.modifiers)
    def buttonrelease(self,widget, event):
        if event.button == 1:
                self.rotate_drag_end(event.x, event.y, event.button, self.modifiers)

        if event.button == 3:
                self.pan_drag_end(event.x, event.y, event.button, self.modifiers)
        self.button_pressed = 0


    def pointermotion(self, widget, event):
        if self.button_pressed == 0:
                return
        event.y = self.screen.height - event.y
        dx = event.x - self.eventx
        dy = event.y - self.eventy
        if self.modifiers == 0:
                if self.button_pressed == 1:
                        self.rotate_drag_do(event.x, event.y, dx, dy, self.button_pressed, self.modifiers)

                if self.button_pressed == 3:
                        self.pan_drag_do(event.x, event.y, dx, dy, self.button_pressed, self.modifiers)

        if self.modifiers == 1:
                dy = int(dy)

                if self.button_pressed == 1 or self.button_pressed == 2:
                        self.start_layer = self.start_layer + dy
                        if self.start_layer < 0:
                                self.start_layer = 0
                        if self.start_layer > self.end_layer:
                                self.start_layer = self.end_layer
                if self.button_pressed == 3 or self.button_pressed == 2:
                        self.end_layer = self.end_layer + dy
                        if self.end_layer >= self.layer_num:
                                self.end_layer = self.layer_num-1
                        if self.end_layer < self.start_layer:
                                self.end_layer = self.start_layer
        return True
    
    def scrollevent(self, widget, event):
        if event.direction.value_name == "GDK_SCROLL_DOWN":
                self.zoom = self.zoom * 1.5
        if event.direction.value_name == "GDK_SCROLL_UP":
                self.zoom = self.zoom / 1.5
        self.updateTransform(self.RX,self.RZ)
        self.queue_draw()
    


    def initLights(self):
        # set up light colors (ambient, diffuse, specular)
        lightKa = [0.3, 0.3, 0.3, 1.0]  # ambient light
        lightKd = [0.7, 0.7, 0.7, 1.0]  # diffuse light
        lightKs = [1.0, 1.0, 1.0, 1.0]           # specular light
        glLightfv(GL_LIGHT0, GL_AMBIENT, lightKa)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightKd)
        glLightfv(GL_LIGHT0, GL_SPECULAR, lightKs)

        # position the light
        lightPos = [0, 0, 1, 0] # directional light
        glLightfv(GL_LIGHT0, GL_POSITION, lightPos)

        glEnable(GL_LIGHT0)       

    def setCamera(self,posX, posY, posZ, targetX, targetY, targetZ):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(posX, posY, posZ, targetX, targetY, targetZ, 0, 1, 0); # eye(x,y,z), focal(x,y,z), up(x,y,z)

    def initGL(self):
        glEnable(GL_DEPTH_TEST)
#        glPixelStorei(GL_UNPACK_ALIGNMENT,4)
        glEnable(GL_CULL_FACE)
        glClearColor(0, 0, 0, 0)                   # background color
        glClearStencil(0)                          # clear stencil buffer
        glClearDepth(1.0)
        glDepthFunc(GL_LEQUAL)
        return

    def __init__(self):
        Gtk.GLArea.__init__(self)
        if experiment == False:
            glBegin(GL_LINES); # TODO dies weg
        self.set_required_version(3, 3)
        self.vertices = [
                                [-0.6, -0.6, 0.0,1.0, 1.0, 1.0,1,0,0],
                                [ 0.6, -0.6, 0.0,1.0, 1.0, 1.0,0,1,0],
                                [ 0.0,  0.6, 0.0,1.0, 1.0, 1.0,0,0,1]
                             ]

        self.xindices = [0,1,2]



# For mouse control
        self.button_pressed = 0
        self.eventx = 0
        self.eventy = 0
        self.modifiers = 0

        # Rotation and pan parameters

        self.PX=0
        self.PY=0
        self.RX=0
        self.RZ=0
        self.zoom=5.0

        self.connect('realize', self.on_configure_event)
        self.connect('render', self.on_draw)
        self.connect('button-press-event',self.buttonpress)
        self.connect('button-release-event',self.buttonrelease)
        self.connect('motion-notify-event',self.pointermotion)
        self.connect('scroll-event',self.scrollevent)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.SCROLL_MASK)



        self.set_double_buffered(GL_FALSE)
        self.set_size_request(500, 500)
        self.draw_inst = None


    def resetVertices(self):
        self.draw_inst = []
        self.indices = []
        self.pts = []  # TODO activate

    def addVertices(self,result): 
        print("keys are")
        polygons=None
        for key,value  in result.items():
            print(key)
            polygons = value
            print(polygons)

        startind=len(self.indices)
       	for polygon in polygons:
            n = polygon.plane.normal
            indices = []
            for v in polygon.vertices:
                pt = [v.pos.x, v.pos.y, v.pos.z, n.x, n.y, n.z, 0.8, 0.8, 0.1 ]
                if not pt in self.pts:
                    self.pts.append(pt)
                index = self.pts.index(pt)
                indices.append(index)
            for i in range(len(indices)-2): # TODO delaunay here
                self.indices.append(indices[0])
                self.indices.append(indices[i+1])
                self.indices.append(indices[i+2])

        inst=[startind,len(self.indices)-startind]
        return inst

    def scheduleVertices(self,inst):
        self.draw_inst.append(inst)

