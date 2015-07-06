#!/usr/bin/env python

##Copyright 2009-2053 Thomas Paviot (tpaviot@gmail.com)
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
from OCC.TopoDS import TopoDS_Face

from Topology import Topo


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

    def test_get_numbers_of_members(self):
        b = get_test_box_shape()
        t = Topo(b)
        assert(t.number_of_faces() == 6)
        assert(t.number_of_edges() == 12)
        assert(t.number_of_vertices() == 8)


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestTopo))
    return test_suite

if __name__ == "__main__":
    unittest.main()
