###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.ptolemaic import thing as _thing


class BoollLike(_thing.ThingLike):
    ...


class BoollElement(_thing.ThingElement, BoollLike):
    ...


class BoollGeneric(_thing.ThingGeneric, BoollElement):
    ...


class BoollVar(_thing.ThingVar, BoollElement):

    _default = False

    def toggle(self, /):
        self.value = not self.value


class BoollSpace(_thing.ThingSpace, BoollLike):

    @property
    def __incise_generic__(self, /):
        return BoollGeneric(self.bound)

    @property
    def __incise_variable__(self, /):
        return BoollVar(self.bound)

    def retrieve_contains(self, incisor: bool, /):
        return incisor


class Booll(BoollLike, _thing.Thing):

    @classmethod
    def __class_get_incision_manager__(cls, /):
        return BoollSpace(cls)

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, bool)


###############################################################################
###############################################################################
