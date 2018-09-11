
import logging
from typing import Iterable

from OCC.Core.BOPAlgo import BOPAlgo_MakerVolume
from OCC.Core.TopTools import TopTools_ListOfShape
from OCC.Core.TopoDS import TopoDS_Shape

log = logging.getLogger("OCCUtils")


def common_volume(shapes):
    # type: (Iterable) -> TopoDS_Shape
    mv = BOPAlgo_MakerVolume()
    ls = TopTools_ListOfShape()
    for i in shapes:
        ls.Append(i)
    mv.SetArguments(ls)
    mv.Perform()

    log.debug("error status: {}".format(mv.ErrorStatus()))

    return mv.Shape()
