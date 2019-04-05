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

import sys, copy
import numpy as np
from itertools import chain

from OCC.Display.SimpleGui import init_display

#sys.path.append('..')
from OCCUtils.Common import points_to_bspline, GpropsFromShape, get_boundingbox
from OCCUtils.Construct import gp_Pnt, gp_Vec, gp_Dir, gp_Ax1, make_edge_from_vert, make_edge, make_n_sided, make_ruled, \
                        make_plane, make_circle, rotate, make_n_sections, make_wire, make_constrained_surface_from_edges, \
                        make_oriented_box, boolean_cut, boolean_fuse, translate_topods_from_vector, make_solid, compound, sew_shapes, \
                        flip_edge, point_from_vertex
from OCCUtils.Topology import dumpTopology, shapeTypeString, Topo, getFirstLevel

from OCC import IFSelect as _IFSelect
from OCC.BRep import BRep_Tool

from OCC.TopoDS import (topods, TopoDS_Wire, TopoDS_Vertex, TopoDS_Edge,
                        TopoDS_Face, TopoDS_Shell, TopoDS_Solid,
                        TopoDS_Compound, TopoDS_CompSolid, topods_Edge,
                        topods_Vertex, TopoDS_Iterator)

display, start_display, add_menu, add_function_to_menu, add_key_function = init_display()

from OCC.Display.qtDisplay import qtViewer3d
from OCC.Display.backend import get_qt_modules
QtCore, QtGui, QtWidgets, QtOpenGL = get_qt_modules()

#globals
solids = []
solid_i = 0
faces = []
faces_i = 0
viewShapes = []
currentShape = None
selectedShapes = []
fillShapes = []
#selected_i = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 37, 38, 39, 40, 41, 0]
#selected_i = [19, 93, 91, 112, 111, 113, 114, 115, 90, 92, 89, 17, 18, 94]
selected_i = []
from OCC import STEPControl as _STEPControl
import os

def write_step(shape, name, **options):
        """
        Exports the shape in .stp format.  It supports the following options:

        precision_mode:
            -1: uncertainty is set to the minimum tolerance of all shapes
            0 (Default): uncertainty is set to the average tolerance of all
            shapes
            1: uncertainty is set the the maximum tolerance of all shapes
            2: uncertainty is set to precision_value

        precision_value (0.0001 Default): for precision_mode 2, uncertainty is
        set to this

        assembly:
            0 (Default): writes without assemblies
            1: writes with assemblies
            2: TopoDS_Compounds are written as assemblies

        schema: defines the version of schema
            1 (Default): AP214CD
            2: AP214DIS
            3: AP203
            4: AP214IS

        surface_curve_mode:
            0: write without pcurves
            1 (Default): write with pcurves

        transfer_mode:
            0 (Default): automatic
            1: transfer to manifold solid brep
            2: transfer to faceted brep (only for planar faces and linear
                edges)
            3: transfer to shell based surface model
            4: transfer to geometric curve set

        units:
            'MM': millimeters
            'INCH': inches

        product: the product creating the file
        """

        # Setup
        c = _STEPControl.STEPControl_Controller()
        c.Init()
        w = _STEPControl.STEPControl_Writer()

        # Parse Options
        if 'precision_mode' in options:
            _Interface_Static_SetIVal('write.precision.mode',
                                      options['precision_mode'])
        if 'precision_value' in options:
            _Interface_Static_SetRVal('write.precision.val',
                                      options['precision_value'])
        if 'assembly' in options:
            _Interface_Static_SetIVal('write.step.assembly',
                                      options['assembly'])
        if 'schema' in options:
            _Interface_Static_SetCVal('write.step.schema',
                                      str(options['schema']))
            w.Model(True)
        if 'product' in options:
            _Interface_Static_SetCVal('write.product.name',
                                      options['product'])
        if 'surface_curve_mode' in options:
            _Interface_Static_SetIVal('write.surfacecurve.mode',
                                      options['surface_curve_mode'])
        if 'units' in options:
            _Interface_Static_SetCVal('write.step.unit', options['units'])
        if 'transfer_mode' in options:
            transfer_modes = [_STEPControl.STEPControl_AsIs,
                              _STEPControl.STEPControl_ManifoldSolidBrep,
                              _STEPControl.STEPControl_FacetedBrep,
                              _STEPControl.STEPControl_ShellBasedSurfaceModel,
                              _STEPControl.STEPControl_GeometricCurveSet]
            transfer_mode = transfer_modes[options['transfer_mode']]
        else:
            transfer_mode = _STEPControl.STEPControl_AsIs

        # Write
        okay = w.Transfer(shape, transfer_mode)
        if okay in [_IFSelect.IFSelect_RetError,
                    _IFSelect.IFSelect_RetFail,
                    _IFSelect.IFSelect_RetStop]:
            print('Error: Could not translate shape to step')
        else:
            w.Write(name)

def read_step(name):
    """
    Imports a step file and returns the shape.
    """
    if os.path.exists(name):
        reader = _STEPControl.STEPControl_Reader()
        status = reader.ReadFile(name)
        okay = reader.TransferRoots()
        shape = reader.OneShape()
        return shape
    else:
        print('Error: Can\'t find', name)

def updateView(onlySelected=False):
    global viewShapes
    global currentShape
    global selectedShapes
    display.EraseAll()
    if not onlySelected:
        for s in viewShapes:
            display.DisplayShape(s, transparency=0.5)
    for s in selectedShapes:
        display.DisplayShape(s, color="BLUE", transparency=0.5)
    display.DisplayShape(currentShape, update=True, color="RED", transparency=0.5)

def showCompound(shp):
    display.DisplayShape(shp, update=True)
    display.DisplayShape(faces[faces_i], update=True)

def selectViaKey(event=None):
    global faces
    global faces_i
    global selectedShapes
    global selected_i
    s = faces[faces_i]
    if s not in selectedShapes:
        selectedShapes.append(s)
        selected_i.append(faces_i)
    else:
        selectedShapes.remove(s)
    updateView()

def showSolids(event=None):
    global solids
    global solid_i
    print(event)    
    for s in solids:
        display.EraseAll()
        display.DisplayShape(s, update=True, transparency=0.5, fit=True)

def nextFace(event=None):
    global faces
    global faces_i    
    global currentShape
    faces_i += 1
    faces_i = faces_i % len(faces)
    currentShape = faces[faces_i]
    updateView()

def preFace(event=None):
    global faces
    global faces_i
    global currentShape
    faces_i -= 1
    faces_i = faces_i % len(faces)
    currentShape = faces[faces_i]
    updateView()

def selectViaMouse(event=None):
    global faces
    global faces_i
    global selectedShapes
    selShape = display.GetSelectedShapes()
    if selShape is None:
        print("nothing selected")
        return
    else:
        faces_i = faces.index(selShape[0])
        selShape = selShape[0]
    if selShape in selectedShapes:
        selectedShapes.remove(selShape)
        selected_i.remove(faces_i)
    else:
        selectedShapes.append(selShape)
        selected_i.append(faces_i)
    updateView()

def perform_plate():
    global selectedShapes
    global selected_i
    print("all seleced i:", selected_i)
    sewed, sew = sew_shapes(selectedShapes)
    dumpTopology(sewed, max_level=2)
    fe = []
    for n in range(sew.NbFreeEdges()):
        fe.append(sew.FreeEdge(n+1))
    print(fe)
    #shells = getFirstLevel(sewed)
    eraseAll()
    for f in fe:
        display.DisplayShape(f)
    display.DisplayShape(f, update=True)

def save_selected():
    global selectedShapes
    global selected_i
    print("all seleced i:", selected_i)
    sewed, sew = sew_shapes(selectedShapes)
    shells = list(tp.shells_from_compound(sewed))
    print("finally: ",len(shells))
    solids = []
    
    for s in shells:
        solids.append(make_solid(s))
    
    dumpTopology(solids[0], max_level=2)
    name = "/home/isabel/Mittelplatte03.stp"
    print("try to write step:")
    write_step(solids[0], name)
    

def perform_pipe():
    global selectedShapes
    global selected_i
    print("all seleced i:", selected_i)
    sewed, sew = sew_shapes(selectedShapes)
    dumpTopology(sewed, max_level=1)
        
    faces = getFirstLevel(sewed)
    fe = []
    for n in range(sew.NbFreeEdges()):
        fe.append(sew.FreeEdge(n+1))
    print(fe)
    #shells = getFirstLevel(sewed)
    eraseAll()
    for f in fe:
        display.DisplayShape(f)
    display.DisplayShape(f, update=True)
    # now find the small loops:
    we = {}
    tp = Topo(fe[0])
    for edge in fe:
        #dumpTopology(edge)
        we.update({edge:set([hash(x) for x in tp.vertices_from_edge(edge)]) })
    loops = [] #([e1, e2, ...]set([v1, v2 ..])), ([][])...
    for edge in we.keys():
        done = False
        for l in loops:            
            if we[edge].intersection(l[1]):
                l[0].append(edge)
                l[1] = we[edge].union(l[1])
                done= True
        if not done:
            #print(edge, list(we[edge]))
            loops.append([[edge], we[edge]])
    # finally go through single edges:
    singleEdges = []
    
    for l in copy.copy(loops):
        if len(l[0])==1:
            loops.remove(l)
            singleEdges.append(l[0])
    for edge in singleEdges:
        for l in loops:
            if we[edge].intersection(l[1]):
                l[0].append(edge)
                l[1] = we[edge].union(l[1])
    print(loops)
    fixes = []
    for l in loops:
        fixes.append(make_n_sided(l[0], []))
        display.DisplayShape(fixes[-1], update=True)

    selectedShapes.extend(fixes)
    sewed, sew = sew_shapes(selectedShapes)
    dumpTopology(sewed, max_level=1)
    shells = list(tp.shells_from_compound(sewed))
    print("finally: ",len(shells))
    solids = []
    for s in shells:
        solids.append(make_solid(s))
    
    name = "/home/isabel/plate.stp"
    print("try to write step:")
    write_step(solids[0], name)
    
    #f1 = make_n_sided(fe[0:3], [])
    #f2 = make_n_sided(fe[3:6], [])#
    eraseAll()
    display.DisplayShape(solids[0], update=True)
    #display.DisplayShape(f2, update=True)
    #f3 = make_n_sided(fe, [])
    #f4 = make_n_sided(fe[2:4], [])

def displaySelected():
    global selectedShapes
    updateView(onlySelected=True)
    
def closeLoop():
    global fillShapes
    selShape = display.GetSelectedShapes()
    selShape = [topods_Edge(x) for x in selShape]

    tp = Topo(selShape[0])
    vertices = []
    vertices_raw = []
    for f in selShape:
        vertices.extend([hash(x) for x in tp.vertices_from_edge(f)])
        vertices_raw.extend(list(tp.vertices_from_edge(f)))
    # find single vertices:
    singleVertices = []
    for f in vertices:
        if vertices.count(f) == 1:
            singleVertices.append(f)
    singleVertices = [x for x in vertices_raw if hash(x) in singleVertices]
    print(singleVertices)
    if singleVertices:
        brt = BRep_Tool()
        pairings = {}
        #pair the single vertices first:
        for j,v1 in enumerate(singleVertices):
            pnt1 = brt.Pnt(topods_Vertex(v1))
            for i,v2 in enumerate(singleVertices):
                if i == j:
                    continue
                pnt2 = brt.Pnt(topods_Vertex(v2))
                d = np.sqrt(np.power(pnt1.X()-pnt2.X(),2)+
                            np.power(pnt1.Y()-pnt2.Y(),2)+
                            np.power(pnt1.Z()-pnt2.Z(),2))
                try:
                    if d < pairings[j][1]:
                        pairings.update({j:[i, d, v2]})
                except:
                    pairings.update({j:[i, d, v2]})

        print("PAIRS:",pairings)
        edges = []
        done = []
        for i,v in enumerate(singleVertices):
            if i in done:
                continue
            print("from-to", i, pairings[i][0])
            edges.append(make_edge_from_vert([v, pairings[i][2]]))
            done.append(i)
            done.append(pairings[i][0])
            
        print("finally: ",edges)
        selShape.extend(edges)
    # now produce the correct order:
    orderedEdges = [selShape[0]]
    for j,s in enumerate(selShape):
        edge = orderedEdges[-1]
        vertices = [point_from_vertex(x) for x in list(tp.vertices_from_edge(edge))]
        print("o:", vertices)
        endVertex = vertices[-1]
        startVertex = vertices[0]
        for i,q in enumerate(selShape):
            vertices = [point_from_vertex(x) for x in list(tp.vertices_from_edge(q))]
            print("c:", vertices)
            if endVertex in vertices:
                print("in ")
                if startVertex in vertices:
                    continue
                if not endVertex == vertices[0]:
                    u = flip_edge(q)               
                    orderedEdges.append(u)
                else:
                    orderedEdges.append(q)
                print(orderedEdges)
                break
    orderedEdges = orderedEdges[0:-1]
        
    print("all:", orderedEdges)
    for s in orderedEdges:
        display.DisplayShape(s, color="BLACK", update=True)
        dumpTopology(s)
    w = make_wire(orderedEdges)
    try:
        face = make_n_sided(orderedEdges, [])
    #face = make_n_sections(w)
    #face = make_constrained_surface_from_edges(orderedEdges, w)
    except:
        print("retry")
        return
    dumpTopology(face)
    display.DisplayShape(face, update=True)
    fillShapes.append(face)
    selectedShapes.append(face)

def eraseAll(event=None):
    display.EraseAll()

if __name__ == '__main__':
    flag = None #"full"
    if flag == "full":
        fn = "/home/isabel/windev/Fluid/Mittelplatte02.stp"
        sh = read_step(fn)
        tp = Topo(sh)
        print("N", tp.number_of_solids())
        topLevelShapes = getFirstLevel(sh)
        plate = topLevelShapes[-3]
        secondLevel = getFirstLevel(plate)
        left = secondLevel[0]
        dumpTopology(left, max_level=3) # max_level is my invention
        thirdLevel = getFirstLevel(left)
        faces = list(tp.faces_from_solids(left))
        sewed, _ = sew_shapes(faces)
        shells = list(tp.shells_from_compound(sewed))
        print("...",len(shells))
        for s in shells:
            solids.append(make_solid(s))
        plate = solids[2]
        b1 = boolean_fuse(plate, solids[0])
        b2 = boolean_fuse(b1, solids[1])
        pipe = solids[1]
        faces = list(tp.faces_from_solids(plate))
        #write_step(plate, "/home/isabel/plate_orig.stp")
    else:
        
        plate = read_step("/home/isabel/Mittelplatte03.stp")
        tp = Topo(plate)
        faces = list(tp.faces_from_solids(plate))
    
    
    solids.append(plate)
    add_menu("next")
    add_function_to_menu("next", showSolids)
    # add_function_to_menu("next", showFaces)
    add_key_function("6", nextFace)
    add_key_function("5", eraseAll)
    add_key_function("4", preFace)
    add_key_function("8", selectViaKey)
    add_key_function("1", selectViaMouse)
    add_key_function("2", perform_plate)
    add_key_function("0", save_selected)
    add_key_function("9", displaySelected)
    add_key_function("7", closeLoop)
    viewShapes = faces
    for i, v in enumerate(viewShapes):
        selected_i.append(i)
        selectedShapes.append(v)
    print("...",viewShapes)
    showSolids()

    
    start_display()
