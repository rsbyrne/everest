###############################################################################
''''''
###############################################################################


from everest.ptolemaic.essence import Essence as _Essence


class Armature(metaclass=_Essence):
    '''
    An `Armature` is the ptolemaic system's equivalent
    of a generic Python collection, like `tuple` or `dict`.
    '''


class Element(Armature):

    basis: _Essence


class Brace(Armature):
    ...


class Map(Armature):
    ...


###############################################################################
###############################################################################