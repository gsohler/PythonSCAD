#!/usr/bin/python3

import os
import sys
import math

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
        color = vertexColor;
        gl_Position = matrixModelModel * matrixModelView * matrixModelProjection * vec4(vertexPosition, 1.0);
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

    def updateModel(self,vertices,normals, colors, indices):


        self.vsize = 4*len(vertices) #  falschen Platz
        self.nsize = 4*len(normals)
        self.csize = 4*len(colors)

        npvertices = np.array(vertices, dtype=np.float32)
        npnormals = np.array(normals, dtype=np.float32)
        npcolors = np.array(colors, dtype=np.float32)
        npindices = np.array(indices, dtype=np.int32)

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

        matrixModelModel = glm.mat4(1.0) # Modell wird nicht gedreht
        glUniformMatrix4fv(self.uniformMatrixModelModel,1,False,glm.value_ptr(matrixModelModel))


        matrixModelView = glm.mat4(1.0) # Camera wird gedreht und entfernt
        matrixModelView = glm.translate(matrixModelView,glm.vec3(self.PX,self.PY,-self.zoom))
        matrixModelView = glm.rotate(matrixModelView,glm.radians(phi),glm.vec3(0,1,0))
        matrixModelView = glm.rotate(matrixModelView,glm.radians(theta),glm.vec3(1,0,0))

        glUniformMatrix4fv(self.uniformMatrixModelView,1,False,glm.value_ptr(matrixModelView))

        matrixModelProjection = glm.mat4(1.0) # Keine Projektion
        glUniformMatrix4fv(self.uniformMatrixModelViewProjection,1,False,glm.value_ptr(matrixModelProjection))

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


        self.vertex_array_object = glGenVertexArrays(1)
        self.vboId = glGenBuffers(1) 
        self.iboId = glGenBuffers(1)

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


        glVertexAttribPointer(self.attribVertex, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))
        glVertexAttribPointer(self.attribNormal, 3, GL_FLOAT, False, 0, ctypes.c_void_p(self.vsize))
        glVertexAttribPointer(self.attribColor, 3, GL_FLOAT, False, 0, ctypes.c_void_p(self.vsize+self.nsize))

        glEnableVertexAttribArray(self.attribVertex)
        glEnableVertexAttribArray(self.attribNormal)
        glEnableVertexAttribArray(self.attribColor)


        glDrawElements(GL_TRIANGLES,len(self.indices),GL_UNSIGNED_INT,ctypes.c_void_p(0)) 

        glDisableVertexAttribArray(self.attribVertex)
        glDisableVertexAttribArray(self.attribNormal)
        glDisableVertexAttribArray(self.attribColor)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glUseProgram(0)

        glBindVertexArray( 0 )

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

        self.PX=-0.56
        self.PY=-0.14
        self.RX=-54
        self.RZ=-61
        self.zoom=0.0011

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
        print("renderVertices called")
        pts = [] 
        self.indices = []
        polygons=result.toPolygons()

       	for polygon in polygons:
            n = polygon.plane.normal
            indices = []
            for v in polygon.vertices:
                pt = [v.pos.x, v.pos.y, v.pos.z, v.normal.x, v.normal.y, v.normal.z, 0.8, 0.8, 0.8 ]
                if not pt in pts:
                    pts.append(pt)
                index = pts.index(pt)
                indices.append(index)
            for i in range(len(indices)-2): # TODO delaunay here
                self.indices.append(indices[0])
                self.indices.append(indices[i+1])
                self.indices.append(indices[i+2])

        self.vertices = []
        self.normals = []
        self.colors = []
        for pt in pts:
            self.vertices.append(pt[0])
            self.vertices.append(pt[1])
            self.vertices.append(pt[2])
            self.normals.append(pt[3]) # TODO dies ist 0
            self.normals.append(pt[4])
            self.normals.append(pt[5])
            self.colors.append(pt[6])
            self.colors.append(pt[7])
            self.colors.append(pt[8])

        print(self.vertices)
        print(self.normals)
        print(self.colors)
        print(self.indices)
        self.updateModel(self.vertices,self.normals, self.colors, self.indices)


    def test_features(self):
        print('Testing features')
        print('glGenVertexArrays Available %s' % bool(glGenVertexArrays))
        print('Alpha Available %s' % bool(self.get_has_alpha()))
        print('Depth buffer Available %s' % bool(self.get_has_depth_buffer()))


