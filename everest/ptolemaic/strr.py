###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.ptolemaic import thing as _thing


class StrrLike(_thing.ThingLike):
    ...


class StrrElement(_thing.ThingElement, StrrLike):
    ...


class StrrGeneric(_thing.ThingGeneric, StrrElement):
    ...


class StrrVar(_thing.ThingVar, StrrElement):
    _default = ''


class StrrSpace(_thing.ThingSpace, StrrLike):

    @property
    def __incise_generic__(self, /):
        return StrrGeneric(self.bound)

    @property
    def __incise_variable__(self, /):
        return StrrVar(self.bound)

    def retrieve_contains(self, incisor: str, /):
        return incisor


class Strr(StrrLike, _thing.Thing):

    @classmethod
    def __class_get_incision_manager__(cls, /):
        return StrrSpace(cls)

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, str)


###############################################################################
###############################################################################
