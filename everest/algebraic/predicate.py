###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionHandler as _IncisionHandler,
    )

from everest.ptolemaic.sprite import Sprite as _Sprite

from .chora import (
    Chora as _Chora
    )
from .fundament import Fundament as _Fundament


class Predicate(_Fundament, _Chora, _IncisionHandler, metaclass=_Sprite):

    func: _collabc.Callable

    def __incise__(self, incisor, /, *, caller):
        return _IncisionProtocol.RETRIEVE(caller)(self(incisor))

    @property
    def __call__(self, /):
        return self.func


###############################################################################
###############################################################################
