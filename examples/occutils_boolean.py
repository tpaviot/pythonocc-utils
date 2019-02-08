from OCC.Core.gp import gp_Pln
from OCC.Core.gp import gp_Pnt, gp_Vec
from OCC.Display.SimpleGui import init_display

import sys
from pathlib import Path
p = Path().resolve()
sys.path.insert(0,str(p.parent))

from OCCUtils import Topo
from OCCUtils.Construct import make_box, make_face
from OCCUtils.Construct import vec_to_dir
from OCCUtils.boolean import common_volume


def test_common_volume():
    display, start_display, add_menu, add_function_to_menu = init_display()

    box = make_box(100, 100, 100)

    p, v = gp_Pnt(50, 50, 50), gp_Vec(0, 0, -1)
    pln = gp_Pln(p, vec_to_dir(v))
    fc = make_face(pln, -1000, 1000, -1000, 1000)  # limited, not infinite plane

    display.DisplayShape(fc, transparency=0.5)
    common_shape = common_volume([box, fc])

    solids = Topo(common_shape).solids()
    display.DisplayShape(next(solids), transparency=0.5)
    display.DisplayColoredShape(next(solids), "BLACK")

    display.FitAll()
    start_display()


if __name__ == "__main__":
    test_common_volume()
