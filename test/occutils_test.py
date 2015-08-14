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

from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.TopoDS import TopoDS_Face, TopoDS_Edge

from Topology import Topo
from edge import Edge


def get_test_box_shape():
    return BRepPrimAPI_MakeBox(10, 20, 30).Shape()


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
        my_Edge = Edge(edge_0)
        assert not my_Edge.IsNull()
        assert my_Edge.tolerance == 1e-06


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestTopo))
    test_suite.addTest(unittest.makeSuite(TestEdge))
    return test_suite

if __name__ == "__main__":
    unittest.main()
