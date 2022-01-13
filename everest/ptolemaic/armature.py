###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import itertools as _itertools

from everest.utilities import (
    caching as _caching,
    reseed as _reseed,
    FrozenMap as _FrozenMap,
    )
from everest.incision import (
    Incisable as _Incisable,
    IncisionHandler as _IncisionHandler,
    IncisionProtocol as _IncisionProtocol,
    )

from everest.ptolemaic.chora import Chora as _Chora, Sliceable as _Sliceable
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.protean import Protean as _Protean


class Armature(metaclass=_Essence):
    '''
    An `Armature` is the ptolemaic system's equivalent
    of a generic Python collection, like `tuple` or `dict`.
    '''


class Brace(Armature):
    ...


class Map(Armature):
    ...


class Degenerate(_Incisable, metaclass=_Sprite):

    value: object

    def __incise__(self, incisor, /, *, caller):
        return _IncisionProtocol.FAIL(caller)(
            incisor,
            "Cannot further incise an already degenerate incisable."
            )


class Degenerator(metaclass=_Bythos):

    @classmethod
    def __class_incise_retrieve__(cls, incisor, /):
        return Degenerate(incisor)


class MultiChora(Armature, _Incisable):
    '''
    A `MultiChora` is a collection of choras which are indexed collectively
    in a similar manner to a Numpy 'fancy slice' or Pandas `MultiIndex`.
    '''

    @property
    @_abc.abstractmethod
    def choras(self, /):
        raise NotImplementedError

    class Choret(_Sliceable):

        BOUNDREQS = ('choras',)

        @property
        def choras(self, /):
            return self.bound.choras

        @property
        def __call__(self, /):
            return self.bound._ptolemaic_class__

        @property
        def depth(self, /):
            return len(self.choras)

        @property
        @_caching.soft_cache()
        def active(self, /):
            return tuple(
                not isinstance(cho, Degenerate) for cho in self.choras
                )

        @property
        @_caching.soft_cache()
        def activechoras(self, /):
            return tuple(_itertools.compress(self.choras, self.active))

        @property
        def activedepth(self, /):
            return len(self.activechoras)

        def yield_tuple_multiincise(self, /, *incisors):
            ninc, ncho = len(incisors), self.activedepth
            nell = incisors.count(...)
            if nell:
                ninc -= nell
                if ninc % nell:
                    raise ValueError("Cannot resolve incision ellipses.")
                ellreps = (ncho - ninc) // nell
            chorait = iter(self.choras)
            try:
                for incisor in incisors:
                    if incisor is ...:
                        count = 0
                        while count < ellreps:
                            chora = next(chorait)
                            if not isinstance(chora, Degenerate):
                                count += 1
                            yield chora
                        continue
                    while True:
                        chora = next(chorait)
                        if isinstance(chora, Degenerate):
                            yield chora
                            continue
                        yield chora.__incise__(incisor, caller=Degenerator)
                        break
            except StopIteration:
    #             raise ValueError("Too many incisors in tuple incision.")
                pass
            yield from chorait


class MultiBrace(Brace, MultiChora, metaclass=_Sprite):

    choraargs: tuple

    @property
    def choras(self, /):
        return self.choraargs

    class Choret:

        def handle_tuple(self, incisor: tuple, /, *, caller):
            '''Captures the special behaviour implied by `self[a,b,...]`'''
            choras = tuple(self.yield_tuple_multiincise(*incisor))
            if all(isinstance(cho, Degenerate) for cho in choras):
                incisor = tuple(cho.value for cho in choras)
                return _IncisionProtocol.RETRIEVE(caller)(incisor)
            return _IncisionProtocol.SLYCE(caller)(self(choras))

    @classmethod
    def __new__(cls, arg=None, /, *args):
        if args:
            return super().__new__(cls, (arg, *args))
        return super().__new__(cls, tuple(arg))


class MultiMap(Map, MultiChora, metaclass=_Sprite):

    chorakws: _FrozenMap = _FrozenMap()

    @property
    def choras(self, /):
        return tuple(self.chorakws.values())

    class Choret:

        BOUNDREQS = ('chorakws',)

        @property
        def chorakws(self, /):
            return self.bound.chorakws

        def handle_tuple(self, incisor: tuple, /, *, caller):
            '''Captures the special behaviour implied by `self[a,b,...]`'''
            choras = tuple(self.yield_tuple_multiincise(*incisor))
            if all(isinstance(cho, Degenerate) for cho in choras):
                incisor = _FrozenMap(zip(
                    self.chorakws,
                    (cho.value for cho in choras),
                    ))
                return _IncisionProtocol.RETRIEVE(caller)(incisor)
            incisor = _FrozenMap(zip(self.chorakws, choras))
            return _IncisionProtocol.SLYCE(caller)(self(incisor))

        def yield_dict_multiincise(self, /, **incisors):
            chorakws = self.chorakws
            for name, incisor in incisors.items():
                chora = chorakws[name]
                yield name, chora.__incise__(
                    incisor, caller=Degenerator(chora)
                    )

        def handle_dict(self, incisor: dict, /, *, caller):
            choras = (
                self.chorakws
                | dict(self.yield_dict_multiincise(**incisor))
                )
            if all(
                    isinstance(chora, Degenerate)
                    for chora in choras.values()
                    ):
                incisor = _FrozenMap({
                    key: val.value for key, val in choras.items()
                    })
                return _IncisionProtocol.RETRIEVE(caller)(incisor)
            return _IncisionProtocol.SLYCE(caller)(self(choras))

    @classmethod
    def __new__(cls, dct=None, /, **kwargs):
        if dct is not None:
            if kwargs:
                raise ValueError("Cannot input both arg and kwargs.")
            kwargs = dict(dct)
        return super().__new__(cls, _FrozenMap(kwargs))


###############################################################################
###############################################################################