###############################################################################
''''''
###############################################################################


from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite


class Armature(metaclass=_Essence):
    '''
    An `Armature` is the ptolemaic system's equivalent
    of a generic Python collection, like `tuple` or `dict`.
    '''


class Element(Armature):

    basis: _Essence


class Brace(Armature):
    ...


# class BraceShape(metaclass=_Sprite):

#     n


class Mapp(Armature):
    ...


###############################################################################
###############################################################################