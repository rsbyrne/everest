###############################################################################
''''''
###############################################################################


# from everest.utilities import caching as _caching
# from everest.incision import (
#     IncisionProtocol as _IncisionProtocol,
#     IncisionHandler as _IncisionHandler,
#     )

from everest.ptolemaic import thing as _thing
from everest.ptolemaic.chora import (
    Sliceable as _Sliceable,
    )
# from everest.ptolemaic.schema import Schema as _Schema


_OPFLOAT = (type(None), float)


class FloattLike(_thing.ThingLike):
    ...


class FloattElement(_thing.ThingElement, FloattLike):
    ...


class FloattGeneric(_thing.ThingGeneric, FloattElement):
    ...


class FloattVar(_thing.ThingVar, FloattElement):

    _default = 0.


class FloattSpace(_Sliceable, _thing.ThingSpace, FloattLike):

    @property
    def __incise_generic__(self, /):
        return FloattGeneric(self.bound)

    @property
    def __incise_variable__(self, /):
        return FloattVar(self.bound)

    def retrieve_contains(self, incisor: float, /):
        return incisor

#     def slice_slyce_open(self, incisor: (int, type(None), _OPINT), /):
#         start, stop, step = incisor.start, incisor.stop, incisor.step
#         return FloattCount(start, step)

#     def slice_slyce_closed(self, incisor: (_OPINT, int, _OPINT), /):
#         start, stop, step = incisor.start, incisor.stop, incisor.step
#         return FloattRange(start, stop, step)


class Floatt(FloattLike, _thing.Thing):

    @classmethod
    def __class_get_incision_manager__(cls, /):
        return FloattSpace(cls)

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, float)


###############################################################################
###############################################################################
