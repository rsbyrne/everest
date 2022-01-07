import abc as _abc
from collections import abc as _collabc

from everest.ptolemaic.chora import Chora as _Chora, ChoraBase as _ChoraBase
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.eidos import Eidos as _Eidos
from everest.ptolemaic.chora import ElementType


class PredicateBase(metaclass=_Essence):

    @_abc.abstractmethod
    def __call__(self, arg, /) -> bool:
        raise NotImplementedError

    @property
    def __incise_retrieve__(self, /) -> bool:
        return self

    def __contains__(self, arg, /):
        return isinstance(arg, bool)


class PredicateChora(metaclass=_Chora):

    def retrieve_object(self, incisor: object, /):
        return incisor


@PredicateChora
class Predicate(PredicateBase, metaclass=_Eidos):

    __call__: _collabc.Callable


@_ChoraBase
class Sett(metaclass=_Eidos):

    __contains__: Predicate


mysett = Sett(Predicate(lambda x: x > 10))
assert mysett[...] is mysett
assert 1 not in mysett and 11 in mysett
assert mysett.iselement(mysett[ElementType.GENERIC])