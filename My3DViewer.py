#!/usr/bin/python3

import os
import sys
import math

import glm

# https://learnopengl.com/Getting-started/Shaders 
# http://www.songho.ca/opengl/gl_vbo.html#example2

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np

VERTEX_SHADER = """
    #version 330
    //uniforms
    uniform mat4 matrixModelView;
    uniform mat4 matrixNormal;
    uniform mat4 matrixModelViewProjection;
    // vertex attribs (input)
    attribute vec3 vertexPosition;
    attribute vec3 vertexNormal;
    attribute vec3 vertexColor;
    attribute vec2 vertexTexCoord;
    // varyings (output)
    varying vec3 esVertex, esNormal;
    varying vec3 color;
    void main()
    {
        esVertex = vec3(matrixModelView * vec4(vertexPosition, 1.0));
        esNormal = vec3(matrixNormal * vec4(vertexNormal, 1.0));
        color = vertexColor;
//	color = vec3(1,0,1)* esNormal; // TODO
        gl_Position = matrixModelViewProjection * vec4(vertexPosition, 1.0);
    }"""

FRAGMENT_SHADER = """
    #version 330
    // uniforms
    uniform vec4 lightPosition;             // should be in the eye space
    uniform vec4 lightAmbient;              // light ambient color
    uniform vec4 lightDiffuse;              // light diffuse color
    uniform vec4 lightSpecular;             // light specular color

    // varyings
    varying vec3 esVertex, esNormal;
    varying vec3 color;

    void main()
    {
        vec3 normal = normalize(esNormal);
        vec3 light;
        if(lightPosition.w == 0.0)
        {
            light = normalize(lightPosition.xyz);
        }
        else
        {
            light = normalize(lightPosition.xyz - esVertex);
        }
        vec3 view = normalize(-esVertex);
        vec3 halfv = normalize(light + view);

        vec3 fragColor = lightAmbient.rgb * color;                  // begin with ambient
        float dotNL = max(dot(normal, light), 0.0);
       fragColor += lightDiffuse.rgb * color * dotNL;              // add diffuse
       float dotNH = max(dot(normal, halfv), 0.0);
       fragColor += pow(dotNH, 128.0) * lightSpecular.rgb * color; // add specular
        
       // set frag color
        gl_FragColor = vec4(fragColor, 1.0);  // keep opaque=1
    }
    """


class My3DViewer(Gtk.GLArea):

    def createShader(self):
        vs = shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
        fs = shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        self.shader = shaders.compileProgram(vs, fs)

    def updateModel(self,vertices,normals, colors, indices):

        self.vboId = glGenBuffers(1) # TODO am falschen Platz ?
        self.iboId = glGenBuffers(1)

        self.vsize = 4*len(vertices) #  falschen Platz
        self.nsize = 4*len(normals)
        self.csize = 4*len(colors)

        npvertices = np.array(vertices, dtype=np.float32)
        npnormals = np.array(normals, dtype=np.float32)
        npcolors = np.array(colors, dtype=np.float32)
        npindices = np.array(indices, dtype=np.int32)

        self.vertex_array_object = glGenVertexArrays(1)
        glBindVertexArray( self.vertex_array_object )




        glBindBuffer(GL_ARRAY_BUFFER, self.vboId)
        glBufferData(GL_ARRAY_BUFFER, self.vsize+self.nsize+self.csize, None, GL_STATIC_DRAW)
        glBufferSubData(GL_ARRAY_BUFFER, 0, self.vsize, npvertices)
        glBufferSubData(GL_ARRAY_BUFFER, self.vsize, self.nsize, npnormals)
        glBufferSubData(GL_ARRAY_BUFFER, self.vsize+self.nsize, self.csize, npnormals)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.iboId)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(npindices)*4, npindices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        # Describe the position data layout in the buffer


        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # Unbind the VAO first (Important)
        glBindVertexArray( 0 )

        # Unbind other stuff
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def updateTransform(self,phi,theta):

        new=True

        glUseProgram(self.shader)

        mymat = glm.mat4(1.0)
        mymat = glm.rotate(mymat,glm.radians(phi),glm.vec3(0,1,0))
        mymat = glm.rotate(mymat,glm.radians(theta),glm.vec3(1,0,0))
        mymat = glm.translate(mymat,glm.vec3(self.PX,self.PY,-self.zoom))

        if new == True:
            self.matrixView = mymat
            self.matrixModel = glm.mat4(1.0)
            self.matrixModelView = self.matrixView * self.matrixModel
            self.matrixNormal = self.matrixModelView
            glm.column(self.matrixNormal,3, glm.vec4(0,0,0,1))
            self.matrixModelViewProjection = self.matrixProjection * self.matrixModelView

        else:
            self.matrixModelView = mymat
            self.matrixNormal = self.matrixModelView
            self.matrixModelViewProjection = glm.mat4(1.0)
            self.matrixModelViewProjection = glm.rotate(self.matrixModelViewProjection,glm.radians(phi),glm.vec3(0,1,0))
            self.matrixModelViewProjection = glm.rotate(self.matrixModelViewProjection,glm.radians(theta),glm.vec3(0,0,1))


        glUniformMatrix4fv(self.uniformMatrixModelView,1,False,glm.value_ptr(self.matrixModelView))
        glUniformMatrix4fv(self.uniformMatrixModelViewProjection,1,False,glm.value_ptr(self.matrixModelViewProjection))
        glUniformMatrix4fv(self.uniformMatrixNormal,1,False,glm.value_ptr(self.matrixNormal))

    def initGLSL(self):
        self.createShader()
        glUseProgram(self.shader)

        self.uniformMatrixModelView = glGetUniformLocation(self.shader, "matrixModelView")
        self.uniformMatrixModelViewProjection = glGetUniformLocation(self.shader, "matrixModelViewProjection")
        self.uniformMatrixNormal  = glGetUniformLocation(self.shader, "matrixNormal");
        self.uniformLightPosition = glGetUniformLocation(self.shader, "lightPosition");
        self.uniformLightAmbient  = glGetUniformLocation(self.shader, "lightAmbient");
        self.uniformLightDiffuse  = glGetUniformLocation(self.shader, "lightDiffuse");
        self.uniformLightSpecular = glGetUniformLocation(self.shader, "lightSpecular");

        self.attribVertexPosition = glGetAttribLocation(self.shader, "vertexPosition")
        self.attribVertexNormal   = glGetAttribLocation(self.shader, "vertexNormal")
        self.attribVertexColor    = glGetAttribLocation(self.shader, "vertexColor")
        self.attribVertexTexCoord = glGetAttribLocation(self.shader, "vertexTexCoord")


        # set uniform values
        lightPosition = [0.0, 0.0, 1.0, 0.0];
        lightAmbient  = [0.3, 0.3, 0.3, 1.0];
        lightDiffuse  = [0.7, 0.7, 0.7, 1.0];
        lightSpecular = [1.0, 1.0, 1.0, 1.0];
        glUniform4fv(self.uniformLightPosition, 1, lightPosition); 
        glUniform4fv(self.uniformLightAmbient, 1, lightAmbient);
        glUniform4fv(self.uniformLightDiffuse, 1, lightDiffuse);
        glUniform4fv(self.uniformLightSpecular, 1, lightSpecular);




    def on_configure_event(self, widget):
        print('realize event')

        widget.make_current()
        # widget.attach_buffers()
        context = widget.get_context()

        print('configure errors')
        print(widget.get_error())


        self.initGLSL()



        print('errors')
        print(widget.get_error())


        self.updateModel(self.vertices,self.normals, self.colors, self.indices)

        self.toPerspective()
#        self.toOrtho()


        return True


    def on_draw(self, widget, *args):
#        print('render event')
#        print(widget.get_error())
        #Create the VBO

        widget.attach_buffers()

        self.updateTransform(self.RX,self.RZ)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBindVertexArray( self.vertex_array_object )

        glUseProgram(self.shader)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboId)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.iboId)

        glEnableVertexAttribArray(self.attribVertex)
        glEnableVertexAttribArray(self.attribNormal)
        glEnableVertexAttribArray(self.attribColor)

        glVertexAttribPointer(self.attribVertex, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))
        glVertexAttribPointer(self.attribNormal, 3, GL_FLOAT, False, 0, ctypes.c_void_p(self.vsize))
        glVertexAttribPointer(self.attribColor, 3, GL_FLOAT, False, 0, ctypes.c_void_p(self.vsize+self.nsize))


# Set Color        

        glDrawElements(GL_TRIANGLES,len(self.indices),GL_UNSIGNED_INT,ctypes.c_void_p(0)) 

        glDisableVertexAttribArray(self.attribVertex)
        glDisableVertexAttribArray(self.attribNormal)
        glDisableVertexAttribArray(self.attribColor)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glUseProgram(0)

        glBindVertexArray( 0 )

        glFlush()

        glBindVertexArray( 0)
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
        self.queue_draw()


    def pan_drag_end(self, x, y, button, modifiers):
        self.panDragStartPX = None
        self.panDragStartPY = None
        self.panDragStartX = None
        self.panDragStartY = None


    def buttonpress(self,widget, event):
        x= widget.get_allocation()
        rect = widget.get_allocation()
        event.y = rect.height - event.y
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
        rect = widget.get_allocation()
        event.y = rect.height - event.y
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
        print("scrollevent")
        if event.direction.value_name == "GDK_SCROLL_DOWN":
                self.zoom = self.zoom / 1.5
        if event.direction.value_name == "GDK_SCROLL_UP":
                self.zoom = self.zoom * 1.5
        print(self.PX, self.PY,self.RX,self.RZ, self.zoom)
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

    def toOrtho(self):

        win= self.get_allocation()
        N = -1.0
        F = 1.0

        # set viewport to be the entire window
        glViewport(0, 0, win.width, win.height)

        # construct ortho projection matrix
        self.matrixProjection = glm.mat4(1.0)
        self.matrixProjection[0][0]  =  2 / win.width
        self.matrixProjection[1][1]  =  2 / win.height
        self.matrixProjection[2][2] = -2 / (F - N)
        self.matrixProjection[3][2] = -(F + N) / (F - N) # TODO dies richtig rum ?

        # set orthographic viewing frustum
#        glMatrixMode(GL_PROJECTION)
#        glLoadMatrixf(glm.value_ptr(self.matrixProjection))
        #glLoadIdentity()
        #glOrtho(0, win.width, 0, win.height, -1, 1)

        # switch to modelview matrix in order to set scene
#        glMatrixMode(GL_MODELVIEW) TODO activate
#        glLoadIdentity() TODO activate

    def toPerspective(self): 
        print("to perspective")
        win= self.get_allocation()
        N = 0.1
        F = 100.0
        DEG2RAD = 3.141592 / 180
        FOV_Y = 60.0 * DEG2RAD

        # set viewport to be the entire window
        glViewport(0, 0, win.width, win.height)

        # construct perspective projection matrix
        aspectRatio = (float)(win.width) / win.height
        tangent = math.tan(FOV_Y / 2.0);     # tangent of half fovY
        h = N * tangent;                  # half height of near plane
        w = h * aspectRatio;              # half width of near plane
        self.matrixProjection = glm.mat4(1.0)
#        self.matrixProjection[0][0]  =  N / w
#        self.matrixProjection[1][1]  =  N / h
#        self.matrixProjection[2][2] = -(F + N) / (F - N)
#        self.matrixProjection[2][3] = -1 # TODO richtig rum ?
#        self.matrixProjection[3][2] = -(2 * F * N) / (F - N)
#        self.matrixProjection[3][3] =  0
#
        # set perspective viewing frustum
#        glMatrixMode(GL_PROJECTION) TODO dies bringt fehler
#        glLoadMatrixf(glm.value_ptr(self.matrixProjection)) # TODO dies geht nicht
        #@@ equivalent fixed pipeline
        #glLoadIdentity()
        #gluPerspective(60.0f, (float)(screenWidth)/screenHeight, 0.1f, 100.0f); # FOV, AspectRatio, NearClip, FarClip

        # switch to modelview matrix in order to set scene
#        glMatrixMode(GL_MODELVIEW) TODO dies bringt fehler
#        glLoadIdentity() # TODO dies bringt fehler


    def initGL(self): # TODO is not called
        glShadeModel(GL_SMOOTH)
        glPixelStorei(GL_UNPACK_ALIGNMENT,4)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_CULL_FACE)

        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)

        glClearColor(0, 0, 0, 0)                   # background color
        glClearStencil(0)                          # clear stencil buffer
        glClearDepth(1.0)                         # 0 is near, 1 is far
        glDepthFunc(GL_LEQUAL)
        self.initLights()

    def __init__(self):
        Gtk.GLArea.__init__(self)
#        self.canvas = Gtk.GLArea()
        self.set_required_version(3, 3)
        self.test_features()

        self.attribVertex=0
        self.attribNormal=1
        self.attribColor=2

# For mouse control
        self.button_pressed = 0
        self.eventx = 0
        self.eventy = 0
        self.modifiers = 0

        # Rotation and pan parameters
        self.RX = -74.2
        self.RZ = 29.2
        self.PX = -0.68
        self.PY = -1.38
        self.zoom = 0.0058

        self.connect('realize', self.on_configure_event)
        self.connect('render', self.on_draw)
        self.connect('button-press-event',self.buttonpress)
        self.connect('button-release-event',self.buttonrelease)
        self.connect('motion-notify-event',self.pointermotion)
        self.connect('scroll-event',self.scrollevent)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.SCROLL_MASK)


        self.set_double_buffered(False)
        self.set_size_request(500, 500)
#        self.initGL()

    def setModel(self,vertices,normals,colors,indices): # TODO besser
        self.vertices=vertices
        self.normals=normals
        self.colors=colors
        self.indices=indices
        pass

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


        for n, f in enumerate(self.faces):
            glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

            glBegin(GL_POLYGON)
            glColor3f(0.8,0.8,0)
            glNormal3fv(self.normals[n])
            for i in f:
                glVertex3fv(self.vertices[i])
            glEnd()


    def test_features(self):
        print('Testing features')
        print('glGenVertexArrays Available %s' % bool(glGenVertexArrays))
        print('Alpha Available %s' % bool(self.get_has_alpha()))
        print('Depth buffer Available %s' % bool(self.get_has_depth_buffer()))


