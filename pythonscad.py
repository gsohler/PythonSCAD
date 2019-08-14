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
import numpy as np
import traceback
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

from csg.core import CSG
from csg.geom import Vertex, Vector, Polygon

from My3DViewer import *

listind = -1
####################################
# Viewer
####################################

def keypressevent(window, event):
    global modifiers
    keyval = event.keyval
#    print(keyval)

    if keyval == Gdk.KEY_F1:
        print("F1 pressed")
        save_script(window)
        message( "Script saved")
    if keyval == Gdk.KEY_F5:
        print("F5 presed")
        render(window)
    if keyval == Gdk.KEY_F6:
        export_stl(window)
    if keyval == 65505 or keyval == 65506: # TODO
#        print("Shift presed")
        modifiers=1
        pass

def keyreleaseevent(window, event):
    global modifiers
    keyval = event.keyval
#   keyname = Gtk.gdk.keyval_name(event.keyval)
#    keyname=""
    if keyval == 65505 or keyval == 65506: # TODO
        modifiers=0


def message(str):
    global win
    parent = None
    md = Gtk.MessageDialog(None,0,Gtk.MessageType.INFO, Gtk.ButtonsType.OK, str)
    md.run()
    md.destroy()

####################################
# MyTextView
####################################

class MyTextView(Gtk.TextView):
    def __init__(self):
        Gtk.TextView.__init__(self)
#        self.set_border_window_size(Gtk.TEXT_WINDOW_LEFT, 24)
#        self.connect("expose-event", on_text_view_expose_event)

def on_text_view_expose_event(text_view, event):
    text_buffer = text_view.get_buffer()
    bounds = text_buffer.get_bounds()
    text = text_buffer.get_text(*bounds)
    nlines = text.count("\n") + 1
    layout = pango.Layout(text_view.get_pango_context())
    layout.set_markup("\n".join([str(x + 1) for x in range(nlines)]))
    layout.set_alignment(pango.ALIGN_LEFT)
    width = layout.get_pixel_size()[0]
    text_view.set_border_window_size(Gtk.TEXT_WINDOW_LEFT, width + 4)
    y = -text_view.window_to_buffer_coords(Gtk.TEXT_WINDOW_LEFT, 2, 0)[1]
    window = text_view.get_window(Gtk.TEXT_WINDOW_LEFT)
    window.clear()
    text_view.style.paint_layout(window=window,
        state_type=Gtk.STATE_NORMAL,
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
    if isinstance(obj, Object2d):
        print("2D Vertices")
        for v in obj.vertices:
            print("%.2f/%.2f, "%(v[0],v[1]),end='')
        print("\n2D Faces")
        for face in obj.faces:
            print(face)
        
    else:
        print("3D Polygons :")
        for poly in obj.polygons:
            print("(",end=' ')
            for v in poly.vertices:
                print("%.2f/%.2f/%.2f, "%(v.pos.x,v.pos.y,v.pos.z),end='')
            print(")")

global dup
def dup(n=1):
    if len(meshstack) == 0:
        message("No Object to dup")
        return
    obj=meshstack[-1]
    for i in range(n):
        meshstack.append(obj.clone())

class Object2d:
    def __init__(self):
        self.vertices=None
        self.faces=None

def form_mesh(vertices, faces):
    polygons=[]
    for face in faces:
        newvertices = []
        for ind in face:
            newvertices.append(Vertex(Vector(vertices[ind][0],vertices[ind][1],vertices[ind][2])))
        polygons.append(Polygon(newvertices))
    return CSG.fromPolygons(polygons)


global square
def square(s=1):
    if type(s) is not list:
        w=s
        l=s
    else:
        w=s[0]
        l=s[1]
    obj=Object2d()
    obj.vertices = np.empty([4,2],dtype=float)
    obj.vertices[0]=[0,0]
    obj.vertices[1]=[w,0]
    obj.vertices[2]=[w,l]
    obj.vertices[3]=[0,l]

    obj.faces = np.empty([2,3],dtype=int)
    obj.faces[0]=[0,1,2]
    obj.faces[1]=[0,2,3]


    meshstack.append(obj)

global circle
def circle(r=1,n=10):
    obj=Object2d()
    obj.vertices = np.empty([n+1,2],dtype=float)
    obj.faces = np.empty([n,3],dtype=int)
    for i in range(n):
        obj.vertices[i]=[
            r*math.cos(2*math.pi*i/n),
            r*math.sin(2*math.pi*i/n)
        ]
        obj.faces[i]=[i,(i+1)%n,n]
    obj.vertices[n]=[0,0]
    meshstack.append(obj)

global polygon
def polygon(path):
    n = len(path);
    obj=Object2d()
    obj.vertices = np.empty([n,2],dtype=float)
    for i in range(len(path)):
        obj.vertices[i][0]=path[i][0]
        obj.vertices[i][1]=path[i][1]
    obj.faces=[range(n)]
    meshstack.append(obj)

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

global bezier_surface_sub
def bezier_surface_sub(pts,x,y):
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
    obj=Object2d()
    ground=0
    obj.vertices = np.empty([n*n+(n-1)*(n-1)+ground*(4*(n-1)+1),3],dtype=float)
    # grosses grid
    # kleines grid
    # n-1 * 4 sockel
    # sockelmittelpunkt

    obj.faces = np.empty([(n-1)*(n-1)*4+ground*(n-1)*4*3,3],dtype=int)
    # 4fach gridmix
    # (n-1)*4*2 mantel
    # (n-1)*4 fusspunkt

    vertoff=0
    # grosses grid
    for j in range(n):
        for i in range(n):
            obj.vertices[vertoff+j*n+i]=bezier_surface_sub(pts,1.0*i/(n-1),1.0*j/(n-1))
    vertoff = vertoff + n*n

    # kleines grid
    for j in range(n-1):
        for i in range(n-1):
            obj.vertices[vertoff+j*(n-1)+i]=bezier_surface_sub(pts,1.0*(i+0.5)/(n-1),1.0*(j+0.5)/(n-1))
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
            obj.vertices[vertoff]=[obj.vertices[ind][0],obj.vertices[ind][1],zmin]
            vertoff=vertoff+1

        # y+
        for i in range(n-1):
            ind=n-1+i*n
            sockeltop.append(ind)
            sockel.append(vertoff)
            obj.vertices[vertoff]=[obj.vertices[ind][0],obj.vertices[ind][1],zmin]
            vertoff=vertoff+1

        # x-
        for i in range(n-1):
            ind=n*n-1-i
            sockeltop.append(ind)
            sockel.append(vertoff)
            obj.vertices[vertoff]=[obj.vertices[ind][0],obj.vertices[ind][1],zmin]
            vertoff=vertoff+1

        # y-
        for i in range(n-1):
            ind=n*(n-1)-i*n
            sockeltop.append(ind)
            sockel.append(vertoff)
            obj.vertices[vertoff]=[obj.vertices[ind][0],obj.vertices[ind][1],zmin]
            vertoff=vertoff+1

        pt=bezier_surface_sub(pts,0.5,0.5)
        obj.vertices[vertoff]=[pt[0],pt[1],zmin]
        ci=vertoff

    # dreiecke
    faceoffset=0
    for j in range(n-1):
        for i in range(n-1):
            obj.faces[4*(j*(n-1)+i)+0][0]=j*n+i
            obj.faces[4*(j*(n-1)+i)+0][1]=j*n+i+1
            obj.faces[4*(j*(n-1)+i)+0][2]=n*n+j*(n-1)+i
            obj.faces[4*(j*(n-1)+i)+1][0]=j*n+i+1
            obj.faces[4*(j*(n-1)+i)+1][1]=j*n+i+1+n
            obj.faces[4*(j*(n-1)+i)+1][2]=n*n+j*(n-1)+i
            obj.faces[4*(j*(n-1)+i)+2][0]=j*n+i+1+n
            obj.faces[4*(j*(n-1)+i)+2][1]=j*n+i+n
            obj.faces[4*(j*(n-1)+i)+2][2]=n*n+j*(n-1)+i
            obj.faces[4*(j*(n-1)+i)+3][0]=j*n+i+n
            obj.faces[4*(j*(n-1)+i)+3][1]=j*n+i
            obj.faces[4*(j*(n-1)+i)+3][2]=n*n+j*(n-1)+i

    faceoffset=faceoffset+4*(n-1)*(n-1)

    if ground == 1:
        # sockel verzippen
        l=len(sockel)
        for i in range(len(sockel)):
            obj.faces[faceoffset]=[sockel[i],sockel[(i+1)%l],sockeltop[(i+1)%l]]
            faceoffset=faceoffset+1
            obj.faces[faceoffset]=[sockel[i],sockeltop[(i+1)%l],sockeltop[i]]
            faceoffset=faceoffset+1

            obj.faces[faceoffset]=[sockel[(i+1)%l],sockel[i],ci]
            faceoffset=faceoffset+1

    meshstack.append(obj)

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

#global import_obj # TODO stl
#def import_obj(filename):
#    obj=CSG.load_mesh(filename)
#    meshstack.append(obj)


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
#        ang1=extrude_finish_angle(vertices,faces,faceoff,2,0,1)
#        ang2=extrude_finish_angle(vertices,faces,faceoff,1,2,0)
#        print(ang1,ang2)
        faceoff=faceoff+1
        # angle 2:0:1  1:2:0

        faces[faceoff,0]=p2x[(i2+off)%n2]
        faces[faceoff,1]=p1x[i1]
        faces[faceoff,2]=p2x[(i2+off+1)%n2]
#        ang1=extrude_finish_angle(vertices,faces,faceoff,2,0,1)
#        ang2=extrude_finish_angle(vertices,faces,faceoff,1,2,0)
#        print(ang1,ang2)
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
            faces_num = faces_num+int(len(p)/(nd-2))
        for p in p2:
            faces_num = faces_num+int(len(p)/(nd-2))

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


    meshstack.append(form_mesh(vertices,faces))


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
        mask=CSG.generate_box_mesh([step*i,-100,-100],[step*(i+1),100,100]) # TODO fix
        slice=CSG.boolean(obj,mask,"intersection") # TODO fix

        vertices = np.empty([len(slice.vertices),3],dtype=float)
        for i in range(len(slice.vertices)):
            ang=slice.vertices[i][0]
            r=slice.vertices[i][1]
            vertices[i][0]=-r*math.cos(ang)
            vertices[i][1]=r*math.sin(ang)
            vertices[i][2]=slice.vertices[i][2]
        tmp=CSG.form_mesh(vertices,slice.faces) # TODO fix
        if result is None:
            result = tmp
        else:
            result =CSG.boolean(result,tmp,"union") # TODO fix
        meshstack.append(result)


####

global translate
def translate(off):

    if len(meshstack) == 0:
        message("No Object to translate")
        return

    obj=meshstack.pop()
    if isinstance(obj,Object2d):
        for vert in obj.vertices:
            vert[0] = vert[0] + off[0]
            vert[1] = vert[1] + off[1]
    else:
        obj.translate(off)
    meshstack.append(obj)


global scale
def scale(s):
    if len(meshstack) == 0:
        message("No Object to scale")
        return
    obj=meshstack.pop()
    if isinstance(obj,Object2d):
        dim=2
    else:
        dim=3
    if dim == 3:
        if type(s) is not list:
            s = [s,s,s]

        for polygon in obj.polygons:
            for vert in polygon.vertices:
                vert.pos.x *= s[0]
                vert.pos.y *= s[1]
                vert.pos.z *= s[2]
        meshstack.append(obj)
    elif dim == 2:
        if type(s) is not list:
            s = [s,s]
        for i in range(len(obj.vertices)):
            vertices[i][0]=obj.vertices[i][0]*s[0]
            vertices[i][1]=obj.vertices[i][1]*s[1]
        meshstack.append(obj)
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
    l=v[0]*v[0]+v[1]*v[1]+v[2]*v[2]
    print(l)
    newpolys=[]
    for poly in obj.polygons:
        vertices=[]
        for pt in poly.vertices:
            # find distance from pt to plane therough [0/0/0],v
            d=pt.pos.x*v[0]+pt.pos.y*v[1]+pt.pos.z*v[2]

            newx = pt.pos.x -2*d*v[0]/l
            newy = pt.pos.y -2*d*v[1]/l
            newz = pt.pos.z -2*d*v[2]/l
            vertices.insert(0,Vertex(Vector(newx,newy,newz)))
        newpolys.append(Polygon(vertices))
    obj.polygons=newpolys

    meshstack.append(obj)


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

    obj=pymesh.resolve_self_intersection(obj) # TODO fix

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

    obj=pymesh.resolve_self_intersection(obj) # TODO fix
# pymesh.nerge_meshes # TODO fix
    obj=pymesh.form_mesh(vertices,obj.faces) # TODO fix
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

global pop
def pop():
    return meshstack.pop()

global push
def push(x):
    meshstack.append(x.clone())

viewer_obj = None
global show
def show(obj):
    global viewer_obj
    viewer_obj=obj

####

global difference
def difference():
    if len(meshstack) < 2:
        message("Too less Objects for Difference")
        return
    obj2=meshstack.pop()
    obj1=meshstack.pop()
    meshstack.append(obj1.subtract(obj2))

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

#global concat
#def concat(n=2):
#    if n == 1:
#        return
#        message("Too less Objects for Concat")
#        return
#    objs=[]
#
#    # Calculate number of required vertices and faces
#    vertlen=0
#    facelen=0
#    for i in range(n):
#        obj=meshstack.pop()
#        vertlen += len(obj.vertices)
#        facelen += len(obj.faces)
#        objs.append(obj)
#
#
#    vertices = np.empty([vertlen,3],dtype=float)
#    faces = np.empty([facelen,3],dtype=int)
#
#    # Now concatenate all vertices and faces
#    vertoff=0
#    faceoff=0
#    for i in range(n):
#        obj=objs[i]
#        for j in range(len(obj.vertices)):
#            vert=obj.vertices[j]
#            vertices[j+vertoff]=vert
#
#        for j in range(len(obj.faces)):
#            face=obj.faces[j]
#            faces[j+faceoff] = [face[0]+vertoff,face[1]+vertoff,face[2]+vertoff]
#
#        vertoff = vertoff + len(obj.vertices)
#        faceoff = faceoff + len(obj.faces)
#    obj=pymesh.form_mesh(vertices,faces) # TODO fix
#    meshstack.append(obj)


#global hull
#def hull():
#    if len(meshstack) == 0:
#        message("No Object to hull")
#        return
#
#    obj=meshstack.pop()
#    obj=pymesh.convex_hull(obj) # TODO fix
#    meshstack.append(obj)

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
                area    =p1[0]*p2[1]*p3[2]+p1[1]*p2[2]*p3[0]+p1[2]*p2[0]*p3[1]-p1[2]*p2[1]*p3[0]-p1[0]*p2[2]*p3[1]-p1[1]*p2[0]*p3[2]
                volume=volume+area
    return volume/18.0;



####################################
# Top
####################################

def get_result(): # TODO verbessern
    global viewer_obj
    if viewer_obj is not None:
        return viewer_obj
    if len(meshstack) > 0:
        if isinstance(meshstack[0],Object2d):
            linear_extrude(1)
        union(len(meshstack))
        return meshstack[0]
    return None





def render(window):
    global meshstack
    meshstack = []
    viewer_obj=None

    try:
        buffer = tv.get_buffer()
        script = buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter(),True)
        exec(script)
    except Exception:
        message("Error in Script")
        traceback.print_exc()
        return

    mesh = get_result()

    if mesh is None:
        message( "Error: No Objects generated")
        return


    polygons=mesh.toPolygons()
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
    viewer3d.renderVertices(mesh)



def save_script(window):
    buffer = tv.get_buffer()
    script = buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter(),True)
    outfile = open(args.file, "w")
    if outfile:
        outfile.write(script)
        outfile.close()

def export_stl_cb(mesh,filename):
    print("Saving STL")

    polygons=mesh.toPolygons()
    trianglelen=0
    for polygon in polygons:
        trianglelen = trianglelen +len( polygon.vertices) -2

    with open(filename,'wb') as f:
        f.write(struct.pack("<IIIIIIIIIIIIIIIIIIII", 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))
        f.write(struct.pack("<I", trianglelen))
        for polygon in polygons:
            n = polygon.plane.normal
            pts = polygon.vertices
            for i in range(len(pts)-2):
                p1 = pts[0] # TODO delauney
                p2 = pts[i+1]
                p3 = pts[i+2]
                data = struct.pack('<ffffffffffff',n.x,n.y,n.z,p1.pos.x,p1.pos.y,p1.pos.z,p2.pos.x,p2.pos.y,p2.pos.z,p3.pos.x,p3.pos.y,p3.pos.z)
                f.write(data)
                f.write(struct.pack('<bb',0,0))

def export_stl(window):
    if len(meshstack) == 0:
        message( "Error: No Objects generated")
        return
    mesh = get_result()
    text_filter=Gtk.FileFilter()
    text_filter.set_name("Text files")
    text_filter.add_mime_type("text/*")
    all_filter=Gtk.FileFilter()
    all_filter.set_name("All files")
    all_filter.add_pattern("*")

    filename=None
    dialog=Gtk.FileChooserDialog(title="Select a File", action=Gtk.FileChooserAction.SAVE,
        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

    dialog.add_filter(text_filter)
    dialog.add_filter(all_filter)

    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        export_stl_cb(mesh,filename)
        message("File Exported")
    dialog.destroy()


parser = argparse.ArgumentParser()
parser.add_argument("file", help="Graphics  File")
parser.add_argument("-s", "--scale", help="Scale(1.0)",default=1.0)
args = parser.parse_args()
signal.signal(signal.SIGINT, signal.SIG_DFL)

separateWindow=True

# https://gist.github.com/otsaloma/1912166
tv = MyTextView()

tvscroll = Gtk.ScrolledWindow()
tvscroll.set_min_content_width(300)
tvscroll.set_size_request(500, 600)
tvscroll.add(tv)

if args.file.endswith(".py"):
    textbuffer = tv.get_buffer()
    infile = open(args.file, "r")
    if infile:
        string = infile.read()
        infile.close()
        textbuffer.set_text(string)

#
# top-level Gtk.Window
#

viewer3d = My3DViewer()
viewer3d.set_size_request(500, 600)

filesave = Gtk.MenuItem("Save")
filesave.connect("activate", save_script)

fileexport = Gtk.MenuItem("Export STL")
fileexport.connect("activate", export_stl)

fileexit = Gtk.MenuItem("Exit")
fileexit.connect("activate", Gtk.main_quit)

filemenu = Gtk.Menu()
filemenu.append(filesave)
filemenu.append(fileexport)
filemenu.append(fileexit)

filem = Gtk.MenuItem("File")
filem.set_submenu(filemenu)

mb = Gtk.MenuBar()
mb.append(filem)

vbox = Gtk.VBox(False, 2)
vbox.pack_start(mb, False, False, 0)
if separateWindow == True:
    vbox.add(tvscroll)
else:
    hbox = Gtk.HPaned()
    hbox.add(tvscroll)
    hbox.add(viewer3d)
    vbox.add(hbox)

# Script Window

win_source = Gtk.Window()
win_source.set_title("PythonSCAD")
win_source.set_reallocate_redraws(True)
win_source.connect('destroy', Gtk.main_quit)

win_source.add(vbox)
win_source.connect('key-press-event',keypressevent)
win_source.connect('key-release-event',keyreleaseevent)

win_source.show_all()

if separateWindow == True:
    # 3D Window
    win_graph = Gtk.Window()
    win_graph.set_title("PythonSCAD - Viewer")
    win_graph.set_reallocate_redraws(True)
    win_graph.connect('destroy', Gtk.main_quit)

    win_graph.add(viewer3d)
    win_graph.connect('key-press-event',keypressevent)
    win_graph.connect('key-release-event',keyreleaseevent)

    win_graph.show_all()
    pos=win_source.get_position()
    win_graph.move(pos.root_x+500,pos.root_y)

Gtk.main()

# vim: softtabstop=8 noexpandtab

