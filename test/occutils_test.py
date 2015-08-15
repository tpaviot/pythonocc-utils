#!/usr/bin/env python

##Copyright 2009-2015 Thomas Paviot (tpaviot@gmail.com)
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

import unittest
import sys

sys.path.append('../OCCUtils')

from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from OCC.TopoDS import TopoDS_Face, TopoDS_Edge

from Topology import Topo
from edge import Edge
from face import Face
from wire import Wire
from vertex import Vertex
from shell import Shell
from solid import Solid


def get_test_box_shape():
    return BRepPrimAPI_MakeBox(10, 20, 30).Shape()


def get_test_sphere_shape():
    return BRepPrimAPI_MakeSphere(10.).Shape()


class TestTopo(unittest.TestCase):
    def test_init(self):
        b = get_test_box_shape()
        t = Topo(b)
        assert(t)

    def test_loop_faces(self):
        b = get_test_box_shape()
        t = Topo(b)
        i = 0
        for face in t.faces():
            i += 1
            assert(isinstance(face, TopoDS_Face))
        assert(i == 6)

    def test_loop_edges(self):
        b = get_test_box_shape()
        t = Topo(b)
        i = 0
        for face in t.edges():
            i += 1
            assert(isinstance(face, TopoDS_Edge))
        assert(i == 12)

    def test_get_numbers_of_members(self):
        b = get_test_box_shape()
        t = Topo(b)
        assert(t.number_of_faces() == 6)
        assert(t.number_of_edges() == 12)
        assert(t.number_of_vertices() == 8)
        assert(t.number_of_wires() == 6)
        assert(t.number_of_solids() == 1)
        assert(t.number_of_shells() == 1)
        assert(t.number_of_compounds() == 0)
        assert(t.number_of_comp_solids() == 0)


class TestEdge(unittest.TestCase):
    def test_creat_edge(self):
        # create a box
        b = get_test_box_shape()
        # take the first edge
        t = Topo(b)
        edge_0 = t.edges().next()  # it's a TopoDS_Edge
        assert not edge_0.IsNull()
        # then create an edge
        my_edge = Edge(edge_0)
        assert not my_edge.IsNull()
        assert my_edge.tolerance == 1e-06
        assert my_edge.type == 'line'
        assert my_edge.length() == 30.


class TestFace(unittest.TestCase):
    def test_creat_face(self):
        # create a box
        my_face = Face(BRepPrimAPI_MakeSphere(1., 1.).Face())
        assert not my_face.IsNull()
        assert my_face.tolerance == 1e-06
        assert not my_face.is_planar()
        assert my_face.is_trimmed()


class TestWire(unittest.TestCase):
    def test_creat_face(self):
        # create a box
        b = get_test_box_shape()
        # take the first edge
        t = Topo(b)
        wire = t.wires().next()
        my_wire = Wire(wire)
        assert not my_wire.IsNull()
        assert my_wire.tolerance == 1e-06


class TestVertex(unittest.TestCase):
    def test_creat_vertex(self):
        my_vertex = Vertex(1., 2., -2.6)
        assert my_vertex.tolerance == 1e-06
        assert my_vertex.x == 1.
        assert my_vertex.y == 2.
        assert my_vertex.z == -2.6


class TestShell(unittest.TestCase):
    def test_creat_shell(self):
        my_shell = Shell(BRepPrimAPI_MakeBox(10, 20, 30).Shell())
        assert my_shell.tolerance == 1e-06


class TestSolid(unittest.TestCase):
    def test_creat_solid(self):
        my_solid = Solid(BRepPrimAPI_MakeBox(10, 20, 30).Solid())
        assert my_solid.tolerance == 1e-06


def suite():
    test_suite = unittest.TestSuite()
    return test_suite

if __name__ == "__main__":
    unittest.main()
