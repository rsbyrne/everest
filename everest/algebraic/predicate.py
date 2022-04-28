###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from everest.ptolemaic.sprite import Sprite as _Sprite

from .chora import Chora as _Chora
from .algebraic import Algebraic as _Algebraic


class Predicate(_Chora, _Algebraic, metaclass=_Sprite):

    func: _collabc.Callable

    def __incise__(self, incisor, /, *, caller):
        return caller.__incise_retrieve__(self(incisor))

    @property
    def __call__(self, /):
        return self.func


###############################################################################
###############################################################################
