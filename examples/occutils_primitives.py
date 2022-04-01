#!/usr/bin/env python

##Copyright 2009-2015 Jelle Ferina (jelleferinga@gmail.com)
##
##This file is part of pythonOCC.
##
##pythonOCC is free software: you can redistribute it and/or modify
##it under the terms of the GNU Lesser General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##pythonOCC is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU Lesser General Public License for more details.
##
##You should have received a copy of the GNU Lesser General Public License
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

import sys
from itertools import chain

from OCC.Display.SimpleGui import init_display

#sys.path.append('..')
from OCCUtils.Common import points_to_bspline, GpropsFromShape, get_boundingbox
from OCCUtils.Construct import gp_Pnt, gp_Vec, gp_Dir, gp_Ax1, make_edge, make_n_sided, make_plane, make_circle, rotate, make_n_sections, make_wire, \
                        make_oriented_box, boolean_cut, translate_topods_from_vector, make_solid, compound, sew_shapes

from OCCUtils.Topology import dumpTopology, shapeTypeString, Topo

display, start_display, add_menu, add_function_to_menu, _ = init_display()
from OCC import STEPControl as _STEPControl
import os


def circle():

    pt = gp_Pnt(0.,0.,0.)
    radius = 20.0    
    c1 = make_circle(pt, radius)
    p1 = make_plane()

    display.DisplayShape(p1)
    display.DisplayShape(c1, update=True)
    print("TOPOLOGY of circle:")
    dumpTopology(c1)
    print(shapeTypeString(c1))
    print("TOPOLOGY of plane:")
    dumpTopology(p1)
    print(shapeTypeString(p1))
    direct = gp_Dir(1,0,0)
    axe = gp_Ax1(pt, direct)
    c2 = rotate(c1, axe, 20.0, copy=True)
    
    w1 = make_wire([c2])
    dumpTopology(c2)
    f1 = make_n_sided([c2], [])

    display.DisplayShape(f1, update=True)

    #dumpTopology(w1)

    g = GpropsFromShape(f1).surface()
    #print(g.Mass(), g.CentreOfMass())
    box = get_boundingbox(f1)
    #print(box)
    corner = gp_Vec(box[0], box[1], box[2])
    v1 = gp_Vec(box[3]-box[0],0.,0.)
    v2 = gp_Vec(0.,box[4]-box[1],0.)
    v3 = gp_Vec(0.,0.,box[5]-box[2])
    
    b1 = make_oriented_box(corner, v1,v2,v3)
    display.DisplayShape(b1, update=True)

    b2 = rotate(b1, axe, 20.0, copy=True)

    result = boolean_cut(b2, b1)
    v4 = gp_Vec(0.,0.,25.)
    result = translate_topods_from_vector( result, v4)

    tp = Topo(None)
    faces = tp.faces_from_solids(result)
    l = tp.number_of_faces_from_solids(result)
    lst = list(faces)
    print("L",len(lst))
    
    m = compound(lst[0:4])

    #dumpTopology(m)
    #for f in lst:
    #    m.append(f)
    # sewing 5 leads to a shell, which is closed, sewing 10 leads to a compound (how to separate a compound into two shells?)
    sewed, _ = sew_shapes(lst[0:10])
    
    shells = list(tp.shells_from_compound(sewed))

    print(len(shells))

    #dumpTopology(sewed)
    s1 = make_solid(shells[0])
    print(s1)


    display.DisplayShape(s1, update=True)

    #dumpTopology(b1)

if __name__ == '__main__':
    circle()
    start_display()
