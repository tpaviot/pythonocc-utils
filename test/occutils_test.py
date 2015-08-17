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

from Topology import Topo, WireExplorer
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
    def setUp(self):
        self.topo = Topo(get_test_box_shape())
        assert self.topo

    def test_loop_faces(self):
        i = 0
        for face in self.topo.faces():
            i += 1
            assert(isinstance(face, TopoDS_Face))
        assert(i == 6)

    def test_loop_edges(self):
        i = 0
        for face in self.topo.edges():
            i += 1
            assert(isinstance(face, TopoDS_Edge))
        assert(i == 12)

    def number_of_topological_entities(self):
        assert(self.topo.number_of_faces() == 6)
        assert(self.topo.number_of_edges() == 12)
        assert(self.topo.number_of_vertices() == 8)
        assert(self.topo.number_of_wires() == 6)
        assert(self.topo.number_of_solids() == 1)
        assert(self.topo.number_of_shells() == 1)
        assert(self.topo.number_of_compounds() == 0)
        assert(self.topo.number_of_comp_solids() == 0)

    def test_nested_iteration(self):
        '''check nested looping'''
        for f in self.topo.faces():
            for e in self.topo.edges():
                assert isinstance(f, TopoDS_Face)
                assert isinstance(e, TopoDS_Edge)

    def test_kept_reference(self):
        '''did we keep a reference after looping several time through a list
        of topological entities?'''
        _tmp = []
        _faces = [i for i in self.topo.faces()]
        for f in _faces:
            _tmp.append(0 == f.IsNull())
        for f in _faces:
            _tmp.append(0 == f.IsNull())
        self.assert_(all(_tmp))

    def test_edge_face(self):
        edg = self.topo.edges().next()
        face = self.topo.faces().next()
        faces_from_edge = [i for i in self.topo.faces_from_edge(edg)]
        self.assert_(len(faces_from_edge) == self.topo.number_of_faces_from_edge(edg))
        edges_from_face = [i for i in self.topo.edges_from_face(face)]
        self.assert_(len(edges_from_face) == self.topo.number_of_edges_from_face(face))

    def test_edge_wire(self):
        edg = self.topo.edges().next()
        wire = self.topo.wires().next()
        wires_from_edge = [i for i in self.topo.wires_from_edge(edg)]
        self.assert_(len(wires_from_edge) == self.topo.number_of_wires_from_edge(edg))
        edges_from_wire = [i for i in self.topo.edges_from_wire(wire)]
        self.assert_(len(edges_from_wire) == self.topo.number_of_edges_from_wire(wire))

    def test_vertex_edge(self):
        vert = self.topo.vertices().next()
        edge = self.topo.edges().next()
        verts_from_edge = [i for i in self.topo.vertices_from_edge(edge)]
        self.assert_(len(verts_from_edge) == self.topo.number_of_vertices_from_edge(edge))
        edges_from_vert = [i for i in self.topo.edges_from_vertex(vert)]
        self.assert_(len(edges_from_vert) == self.topo.number_of_edges_from_vertex(vert))

    def test_vertex_face(self):
        vert = self.topo.vertices().next()
        face = self.topo.faces().next()
        faces_from_vertex = [i for i in self.topo.faces_from_vertex(vert)]
        self.assert_(len(faces_from_vertex) == self.topo.number_of_faces_from_vertex(vert))
        verts_from_face = [i for i in self.topo.vertices_from_face(face)]
        self.assert_(len(verts_from_face) == self.topo.number_of_vertices_from_face(face))

    def test_face_solid(self):
        face = self.topo.faces().next()
        solid = self.topo.solids().next()
        faces_from_solid = [i for i in self.topo.faces_from_solids(solid)]
        self.assert_(len(faces_from_solid) == self.topo.number_of_faces_from_solids(solid))
        solids_from_face = [i for i in self.topo.solids_from_face(face)]
        self.assert_(len(solids_from_face) == self.topo.number_of_solids_from_face(face))

    def test_wire_face(self):
        wire = self.topo.wires().next()
        face = self.topo.faces().next()
        faces_from_wire = [i for i in self.topo.faces_from_wire(wire)]
        self.assert_(len(faces_from_wire) == self.topo.number_of_faces_from_wires(wire))
        wires_from_face = [i for i in self.topo.wires_from_face(face)]
        self.assert_(len(wires_from_face) == self.topo.number_of_wires_from_face(face))

    def test_edges_out_of_scope(self):
        # check pointers going out of scope
        face = self.topo.faces().next()
        _edges = []
        for edg in Topo(face).edges():
            _edges.append(edg)
        for edg in _edges:
            assert not edg.IsNull()

    def test_wires_out_of_scope(self):
        # check pointers going out of scope
        wire = self.topo.wires().next()
        _edges, _vertices = [], []
        for edg in WireExplorer(wire).ordered_edges():
            _edges.append(edg)
        for edg in _edges:
            assert not edg.IsNull()
        for vert in WireExplorer(wire).ordered_vertices():
            _vertices.append(vert)
        for v in _vertices:
            assert not v.IsNull()


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
