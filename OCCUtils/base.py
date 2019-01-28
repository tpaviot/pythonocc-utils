##Copyright 2008-2013 Jelle Feringa (jelleferinga@gmail.com)
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
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>

'''
Please note the following;
@readonly
means that the decorated method is a readonly descriptor
@property
means that the decorated method can be set / get using the descriptor
( irony is that just using @property *would*
    result in a readonly descriptor :")

Sometimes a set of methods should be contained in another module or class,
or simply grouped.
For instance the set of methods after:
#===========================================================================
#    Curve.local_properties
#===========================================================================

Can be a module, class or namespace.

'''

import functools

from OCC.Core import TopAbs
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Copy
from OCC.Core.BRepGProp import (brepgprop_VolumeProperties,
                                brepgprop_LinearProperties,
                                brepgprop_SurfaceProperties)
from OCC.Core.BRepCheck import (BRepCheck_Vertex, BRepCheck_Edge, BRepCheck_Wire,
                                BRepCheck_Face, BRepCheck_Shell, BRepCheck_Analyzer)
from OCC.Core.GProp import GProp_GProps
from OCC.Display.SimpleGui import init_display

from OCCUtils.Common import get_boundingbox
from OCCUtils.Construct import (make_vertex, TOLERANCE)
from OCCUtils.types_lut import shape_lut, topo_lut, curve_lut, surface_lut

#===========================================================================
# DISPLAY
#===========================================================================
global display


class singleton(object):
    def __init__(self, cls):
        self.cls = cls
        self.instance_container = []

    def __call__(self, *args, **kwargs):
        if not len(self.instance_container):
            cls = functools.partial(self.cls, *args, **kwargs)
            self.instance_container.append(cls())
        return self.instance_container[0]


@singleton
class Display(object):
    def __init__(self):
        self.display, self.start_display, self.add_menu, self.add_function_to_menu = init_display()

    def __call__(self, *args, **kwargs):
        return self.display.DisplayShape(*args, **kwargs)

#============
# base class
#============



def dumps_class_name(klass):
    """ Improve string output for any oce object.
    By default, __repr__ method returns something like:
    <OCC.Core.TopoDS.TopoDS_Shape; proxy of <Swig Object of type 'TopoDS_Shape *' at 0x02BB0758> >
    This is too much verbose.
    We prefer :
    class<'gp_Pnt'>
    or
    class<'TopoDS_Shape'; Type:Solid; Id:59391729>
    """
    # klass_name = str(klass.__class__).split(".")[3].split("'")[0]
    klass_name = str(klass.__class__).split(".")[-1].split("\'")[0]
    repr_string = "class<'" + klass_name + "'"
# for TopoDS_Shape, we also look for the base type
    if klass_name == "TopoDS_Shape":
        if klass.IsNull():
            repr_string += " : Null>"
            return repr_string
        st = klass.ShapeType()
        types = {TopAbs.TopAbs_VERTEX: "Vertex",
                 TopAbs.TopAbs_SOLID: "Solid",
                 TopAbs.TopAbs_EDGE: "Edge",
                 TopAbs.TopAbs_FACE: "Face",
                 TopAbs.TopAbs_SHELL: "Shell",
                 TopAbs.TopAbs_WIRE: "Wire",
                 TopAbs.TopAbs_COMPOUND: "Compound",
                 TopAbs.TopAbs_COMPSOLID: "Compsolid"}
        repr_string += "; Type:%s" % types[st]
# for each class that has an HashCode method define,
# print the id
    if hasattr(klass, "HashCode"):
        klass_id = hash(klass)
        repr_string += "; id:%s" % klass_id
    if hasattr(klass, "IsNull"):
        if klass.IsNull():
            repr_string += "; Null"
    repr_string += ">"
    return repr_string


class BaseObject(object):
    """base class for all objects"""
    def __init__(self, name=None, tolerance=TOLERANCE):
        self.GlobalProperties = GlobalProperties(self)
        self.name = name
        self._dirty = False
        self.tolerance = tolerance
        self.display_set = False


    @property
    def is_dirty(self):
        '''when an object is dirty, its topology will be
        rebuild when update is called'''
        return self._dirty

    @is_dirty.setter
    def is_dirty(self, _bool):
        self._dirty = bool(_bool)

    @property
    def topo_type(self):
        return topo_lut[self.ShapeType()]

    @property
    def geom_type(self):
        if self.topo_type == 'edge':
            return curve_lut[self.ShapeType()]
        if self.topo_type == 'face':
            return surface_lut[self.adaptor.GetType()]
        else:
            raise ValueError('geom_type works only for edges and faces...')

    def set_display(self, display):
        if hasattr(display, 'DisplayShape'):
            self.display_set = True
            self.display = display
        else:
            raise ValueError('not a display')

    def check(self):
        """
        """
        _check = dict(vertex=BRepCheck_Vertex, edge=BRepCheck_Edge,
                      wire=BRepCheck_Wire, face=BRepCheck_Face,
                      shell=BRepCheck_Shell)
        _check[self.topo_type]
        # TODO: BRepCheck will be able to inform *what* actually is the matter,
        # though implementing this still is a bit of work...
        raise NotImplementedError

    def is_valid(self):
        analyse = BRepCheck_Analyzer(self)
        ok = analyse.IsValid()
        if ok:
            return True
        else:
            return False

    def copy(self):
        """

        :return:
        """
        cp = BRepBuilderAPI_Copy(self)
        cp.Perform(self)
        # get the class, construct a new instance
        # cast the cp.Shape() to its specific TopoDS topology
        _copy = self.__class__(shape_lut(cp.Shape()))
        return _copy

    def distance(self, other):
        '''
        return the minimum distance

         :return: minimum distance,
             minimum distance points on shp1
             minimum distance points on shp2
        '''
        return minimum_distance(self, other)

    def show(self, *args, **kwargs):
        """
        renders the topological entity in the viewer

        :param update: redraw the scene or not
        """
        if not self.display_set:
            Display()(self, *args, **kwargs)
        else:
            self.disp.DisplayShape(*args, **kwargs)

    def build(self):
        if self.name.startswith('Vertex'):
            self = make_vertex(self)

    def __eq__(self, other):
        return self.IsEqual(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return dumps_class_name(self)

    def __str__(self):
        return dumps_class_name(self)


class GlobalProperties(object):
    '''
    global properties for all topologies
    '''
    def __init__(self, instance):
        self.instance = instance

    @property
    def system(self):
        self._system = GProp_GProps()
        # todo, type should be abstracted with TopoDS...
        _topo_type = self.instance.topo_type
        if _topo_type == 'face' or _topo_type == 'shell':
            brepgprop_SurfaceProperties(self.instance, self._system)
        elif _topo_type == 'edge':
            brepgprop_LinearProperties(self.instance, self._system)
        elif _topo_type == 'solid':
            brepgprop_VolumeProperties(self.instance, self._system)
        return self._system

    def centre(self):
        """
        :return: centre of the entity
        """
        return self.system.CentreOfMass()

    def inertia(self):
        '''returns the inertia matrix'''
        return self.system.MatrixOfInertia(), self.system.MomentOfInertia()

    def area(self):
        '''returns the area of the surface'''
        return self.system.Mass()

    def bbox(self):
        '''
        returns the bounding box of the face
        '''
        return get_boundingbox(self.instance)
