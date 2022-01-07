###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import itertools as _itertools

from everest.utilities import (
    caching as _caching,
    reseed as _reseed,
    )
from everest.incision import (
    Degenerate as _Degenerate,
    IncisionHandler as _IncisionHandler,
    IncisionProtocol as _IncisionProtocol,
    )

from everest.ptolemaic.chora import Chora as _Chora
from everest.ptolemaic.eidos import Eidos as _Eidos
from everest.ptolemaic.ousia import Monument as _Monument
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.protean import Protean as _Protean


class Armature(metaclass=_Essence):
    '''
    An `Armature` is the ptolemaic system's equivalent
    of a generic Python collection, like `tuple` or `dict`.
    '''


class Brace(Armature):
    ...


class Mapp(Armature):
    ...


class Element(Armature):

    ...


class GenericElement(Element, metaclass=_Eidos):

    FIELDS = (
        _inspect.Parameter('basis', 0),
        _inspect.Parameter('identity', 3, default=None),
        )

    reseed = _reseed.GLOBALRAND

    @classmethod
    def parameterise(cls, cache, *args, **kwargs):
        bound = super().parameterise(cache, *args, **kwargs)
        if (argu := bound.arguments)['identity'] is None:
            argu['identity'] = cls.reseed.rdigits(12)
        return bound


class VariableElement(Element, metaclass=_Protean):

    _req_slots__ = ('_value',)
    _var_slots__ = ('value',)

    @property
    def value(self, /):
        try:
            return self._value
        except AttributeError as exc:
            raise ValueError from exc

    @value.setter
    def value(self, val, /):
        if val in self.basis:
            self._alt_setattr__('_value', val)
        else:
            raise ValueError(val)

    @value.deleter
    def value(self, /):
        self._alt_delattr__('_value')


class Degenerator(_Monument, _IncisionHandler):

    __slots__ = ()

    def __incise_retrieve__(self, index, /):
        return _Degenerate(index)


DEGENERATOR = Degenerator()


class MultiChora(_Chora, Armature):
    '''
    A `MultiChora` is a collection of choras which are indexed collectively
    in a similar manner to a Numpy 'fancy slice' or Pandas `MultiIndex`.
    '''

    __slots__ = ()

    @property
    @_abc.abstractmethod
    def choras(self, /):
        raise NotImplementedError

    @property
    def depth(self, /):
        return len(self.choras)

    @property
    @_caching.soft_cache()
    def active(self, /):
        return tuple(not isinstance(cho, _Degenerate) for cho in self.choras)

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
                        if not isinstance(chora, _Degenerate):
                            count += 1
                        yield chora
                    continue
                while True:
                    chora = next(chorait)
                    if isinstance(chora, _Degenerate):
                        yield chora
                        continue
                    yield chora.__incise__(incisor, caller=DEGENERATOR)
                    break
        except StopIteration:
#             raise ValueError("Too many incisors in tuple incision.")
            pass
        yield from chorait


class MultiBrace(Brace, MultiChora, metaclass=_Eidos):

    FIELDS = (_inspect.Parameter('choraargs', 2),)

    @property
    def choras(self, /):
        return self.choraargs

    def handle_tuple(self, incisor: tuple, /, *, caller):
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        choras = tuple(self.yield_tuple_multiincise(*incisor))
        if all(isinstance(cho, _Degenerate) for cho in choras):
            incisor = self.retrieve_tuple(tuple(cho.value for cho in choras))
            return _IncisionProtocol.RETRIEVE(caller)(incisor)
        return _IncisionProtocol.SLYCE(caller)(self.slyce_tuple(choras))

    def retrieve_tuple(self, incisor: tuple, /):
        return incisor

    def slyce_tuple(self, incisor: tuple, /):
        return self._ptolemaic_class__(*incisor)


class MultiMapp(Mapp, MultiChora, metaclass=_Eidos):

    FIELDS = (_inspect.Parameter('chorakws', 4),)

    @property
    def choras(self, /):
        return tuple(self.chorakws.values())

    def handle_tuple(self, incisor: tuple, /, *, caller):
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        choras = tuple(self.yield_tuple_multiincise(*incisor))
        if all(isinstance(cho, Degenerate) for cho in choras):
            incisor = self.retrieve_dict(dict(zip(
                self.chorakws,
                (cho.value for cho in choras),
                )))
            return _IncisionProtocol.RETRIEVE(caller)(incisor)
        incisor = dict(zip(self.chorakws, choras))
        return _IncisionProtocol.SLYCE(caller)(self.slyce_dict(incisor))

    def yield_dict_multiincise(self, /, **incisors):
        chorakws = self.chorakws
        for name, incisor in incisors.items():
            chora = chorakws[name]
            yield name, chora.__incise__(incisor, caller=Degenerator(chora))

    def handle_dict(self, incisor: dict, /, *, caller):
        choras = self.chorakws | dict(self.yield_dict_multiincise(**incisor))
        if all(isinstance(chora, Degenerate) for chora in choras.values()):
            incisor = self.retrieve_dict({
                key: val.value for key, val in choras.items()
                })
            return _IncisionProtocol.RETRIEVE(caller)(incisor)
        return _IncisionProtocol.SLYCE(caller)(self.slyce_dict(choras))

    def retrieve_dict(self, incisor: dict, /):
        return _types.MappingProxyType(incisor)

    def slyce_dict(self, incisor: dict, /):
        return self._ptolemaic_class__(**incisor)


###############################################################################
###############################################################################