###############################################################################
''''''
###############################################################################


from everest.utilities.protocol import Protocol as _Protocol

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite


class ArmatureProtocol(_Protocol):

    BRACE = ('__armature_brace__', True)
    GENERIC = ('__armature_generic__', True)
    VARIABLE = ('__armature_variable__', True)

    @classmethod
    def defer(cls, obj, /):
        return getattr(obj, '__incision_manager__')


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