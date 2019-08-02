#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

from My3DViewer import *

def keypressevent(window, event):
    print("keypress")
#    global modifiers
    keyval = event.keyval
    print(keyval)

    if keyval == Gdk.KEY_F1:
        print("F1 presed")
#        save_script(window)
#        message( "Script saved")
    if keyval == Gdk.KEY_F5:
        print("F5 presed")
#        render(window)
    if keyval == Gdk.KEY_F6:
        print("F6 presed")
#        export_stl(window)
    if keyval == 65505 or keyval == 65506: # TODO
        print("Shift presed")
#        modifiers=1

def keyreleaseevent(window, event):
    pass
#    global modifiers
#   keyname = Gtk.gdk.keyval_name(event.keyval)
#    keyname=""
#    if keyname == "Shift_L" or keyname == "Shift_R":
#        modifiers=0

# vertex position array
vertices  = [
     .5, .5, .5,  -.5, .5, .5,  -.5,-.5, .5,  .5,-.5, .5, # v0,v1,v2,v3 (ront)
     .5, .5, .5,   .5,-.5, .5,   .5,-.5,-.5,  .5, .5,-.5, # v0,v3,v4,v5 (right)
     .5, .5, .5,   .5, .5,-.5,  -.5, .5,-.5, -.5, .5, .5, # v0,v5,v6,v1 (top)
    -.5, .5, .5,  -.5, .5,-.5,  -.5,-.5,-.5, -.5,-.5, .5, # v1,v6,v7,v2 (let)
    -.5,-.5,-.5,   .5,-.5,-.5,   .5,-.5, .5, -.5,-.5, .5, # v7,v4,v3,v2 (bottom)
     .5,-.5,-.5,  -.5,-.5,-.5,  -.5, .5,-.5,  .5, .5,-.5  # v4,v7,v6,v5 (back)
    ]

normals = [
     0, 0, 1,   0, 0, 1,   0, 0, 1,   0, 0, 1,  # v0,v1,v2,v3 (front)
     1, 0, 0,   1, 0, 0,   1, 0, 0,   1, 0, 0,  # v0,v3,v4,v5 (right)
     0, 1, 0,   0, 1, 0,   0, 1, 0,   0, 1, 0,  # v0,v5,v6,v1 (top)
    -1, 0, 0,  -1, 0, 0,  -1, 0, 0,  -1, 0, 0,  # v1,v6,v7,v2 (left)
     0,-1, 0,   0,-1, 0,   0,-1, 0,   0,-1, 0,  # v7,v4,v3,v2 (bottom)
     0, 0,-1,   0, 0,-1,   0, 0,-1,   0, 0,-1   # v4,v7,v6,v5 (back)
        ]

# colour array
colors=[
     1, 1, 1,   1, 1, 0,   1, 0, 0,   1, 0, 1,  # v0,v1,v2,v3 (front)
     1, 1, 1,   1, 0, 1,   0, 0, 1,   0, 1, 1,  # v0,v3,v4,v5 (right)
     1, 1, 1,   0, 1, 1,   0, 1, 0,   1, 1, 0,  # v0,v5,v6,v1 (top)
     1, 1, 0,   0, 1, 0,   0, 0, 0,   1, 0, 0,  # v1,v6,v7,v2 (left)
     0, 0, 0,   0, 0, 1,   1, 0, 1,   1, 0, 0,  # v7,v4,v3,v2 (bottom)
     0, 0, 1,   0, 0, 0,   0, 1, 0,   0, 1, 1   # v4,v7,v6,v5 (back)
        ]


indices = [
     0, 1, 2,   2, 3, 0,    # v0-v1-v2, v2-v3-v0 (front)
     4, 5, 6,   6, 7, 4,    # v0-v3-v4, v4-v5-v0 (right)
     8, 9,10,  10,11, 8,    # v0-v5-v6, v6-v1-v0 (top)
    12,13,14,  14,15,12,    # v1-v6-v7, v7-v2-v1 (left)
    16,17,18,  18,19,16,    # v7-v4-v3, v3-v2-v7 (bottom)
    20,21,22,  22,23,20     # v4-v7-v6, v6-v5-v4 (back)
        ]


viewer3d = My3DViewer()
viewer3d.setModel(vertices,normals,colors,indices)

text = Gtk.Button("eee",name="text")

text.set_size_request(100, 500)

hbox = Gtk.HBox(False,2)
hbox.add(text)
hbox.add(viewer3d)
hbox.set_size_request(600, 500)

window = Gtk.Window()
window.connect('delete_event', Gtk.main_quit)
window.connect('destroy', lambda quit: Gtk.main_quit())
window.connect('key-press-event',keypressevent)
window.connect('key-release-event',keyreleaseevent)

window.add(hbox)
window.show_all()

Gtk.main()
