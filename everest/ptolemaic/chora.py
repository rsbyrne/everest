###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import deque as _deque, abc as _collabc
import types as _types
import functools as _functools
import itertools as _itertools

from ..ptolemaic.stele import Stele as _Stele_
from ..ptolemaic.enumm import Enumm as _Enumm
from ..ptolemaic.semaphore import Semaphore as _Semaphore
from ..ptolemaic.system import System as _System
from ..ptolemaic.essence import Essence as _Essence
from ..ptolemaic.ousia import Ousia as _Ousia

from . import sett as _sett, mapp as _mapp


class _Stele_(_Stele_):

    def __call__(self, arg, /):
        if arg is self:
            arg = Chora
        return convert(arg)

    def __initialise__(self, /):
        super().__initialise__()
        try:
            choras = self.Choras
        except AttributeError:
            pass
        else:
            with self.__mutable__:
                for enumm in choras:
                    setattr(self, enumm.name, enumm)

    def __instancecheck__(self, arg, /):
        return isinstance(arg, Chora)

    def __subclasscheck__(self, arg, /):
        return issubclass(arg, Chora)

    def __mro_entries__(self, bases, /):
        return (self.Chora,)


_Stele_.commence()


class IncisionError(_mapp.MappError):

    ...


class IncisorError(_mapp.MappError):

    ...


def convert(arg, /):
    if isinstance(arg, Chora):
        return arg
    # if not isinstance(arg, type):
    #     if hasattr(arg, '__chora_convert__'):
    #         return arg.__chora_convert__()
    raise TypeError(arg, type(arg))


def _default_incise_retrieve_(obj, arg, /) -> _sett.NULL:
    raise IncisionError(incisor)

def _default_incise_slyce_(obj, incisor, /) -> _sett.NULL:
    if isinstance(incisor, Chora):
        return obj.compose(incisor)
    raise IncisionError(incisor)

def _default_incise_trivial_(obj, incisor, /):
    return obj


class IncisionStyle(_Semaphore):

    RETRIEVE: 'The procedure to return a single element.' \
        = _default_incise_retrieve_
    SLYCE: 'The procedure to return a subset of elements.' \
        = _default_incise_slyce_
    TRIVIAL: 'The procedure for trivial incisors like `...`.' \
        = _default_incise_trivial_
    # NULL: 'The special procedure for incisor `None`.'

    __slots__ = ('methname',)

    def __init__(self, /):
        super().__init__()
        self.methname = f"_incise_{self.name.lower()}_"

    class Dispatch(metaclass=_Essence):

        def __call__(self, arg, /):
            envelope, content = self.__params__
            try:
                meth = getattr(arg, envelope.methname)
            except AttributeError:
                meth = envelope.value.__get__(arg)
            return meth(content)


class Chora(_sett.Sett, _mapp.Mapp, metaclass=_Ousia):

    __mergenames__ = dict(__incision_styles__=list)
    __incision_styles__ = IncisionStyle

    def _incise_handle_(self, incisor, /) -> IncisionStyle.Dispatch:
        raise IncisorError(incisor)

    def _incise_retrieve_(self, incisor, /):
        raise IncisionError(incisor)

    def _incise_slyce_(self, incisor, /):
        raise IncisionError(incisor)

    def _incise_trivial_(self, incisor, /):
        return self

    def __getitem__(self, arg, /):
        return self._incise_handle_(arg)(self)

    def union(self, other, /):
        raise NotImplementedError

    def intersection(self, other, /):
        raise NotImplementedError

    def invert(self, /):
        raise NotImplementedError

    def extend(self, other, /):
        raise NotImplementedError

    def compose(self, other, /):
        return ChoraComposition(other, self)

    @property
    def domain(self, /):
        return _sett.UNIVERSE

    @property
    def codomain(self, /):
        return self


class Choras(Chora, metaclass=_Enumm):

    UNIVERSE: "A chora over the universal sett." = _sett.UNIVERSE
    NULL: "A chora over the null sett." = _sett.NULL
    POWER: "The power chora, containing all choras." = _sett(Chora)

    def get_signaltype(self, /):
        return self.value.get_signaltype()

    def _contains_(self, arg, /):
        return True

    def _includes_(self, arg, /):
        return True


class SuperChora(Chora, _mapp.SuperMapp):

    def subtend(self, other, /):
        raise NotImplementedError


class ChoraOp(SuperChora, _mapp.SuperMapp):

    ...


class ChoraMultiOp(ChoraOp, _mapp.MappMultiOp):

    ...


class ChoraEnnaryOp(ChoraMultiOp, _mapp.MappEnnaryOp):

    ...


class ChoraComposition(ChoraEnnaryOp, _mapp.MappComposition):

    def _incise_handle_(self, incisor, /) -> IncisionStyle.Dispatch:
        for chora in self.args:
            try:
                return chora._incise_handle_(incisor)
            except IncisorError:
                continue
        raise IncisorError(incisor)

    def _incise_retrieve_(self, incisor, /):
        for chora in self.args:
            incisor = chora._incise_retrieve_(incisor)
        return incisor

    def _incise_slyce_(self, incisor, /):
        chora, *others = self.args
        return self._abstract_class_(chora._incise_slyce_(incisor), *others)

    def _incise_trivial_(self, incisor, /):
        return self


class Choret(Chora):

    @classmethod
    def _yield_slots(cls, /):
        yield from super()._yield_slots()
        yield '_incise_handle_', _types.MethodType
        for style in cls.__incision_styles__:
            yield style.methname, _types.MethodType

    @classmethod
    def _incision_gather_methnames(cls, /):
        channels = {'_incise_handle_': _deque()}
        styles = cls.__incision_styles__
        channels.update((style.methname, _deque()) for style in styles)
        for name in dir(cls):
            for prefix, deq in channels.items():
                if name.startswith(prefix) and name != prefix:
                    if name not in deq:
                        deq.append(name)
                continue
        return (
            channels.pop('_incise_handle_'),
            {style: deq for style, deq in zip(styles, channels.values())},
            )

    def __init__(self, /):
        super().__init__()
        self._add_incision_methods()

    def _add_incision_methods(self, /):
        self._incise_handle_ = _mapp(
            (getattr(self, nm) for nm in self._inchandlers)
            ).__getitem__
        for style, names in self._incmeths.items():
            fallback = style.value.__get__(self)
            mapp = _mapp((*(getattr(self, nm) for nm in names), fallback))
            setattr(self, style.methname, mapp.__getitem__)

    def _incise_handle_ellipsis_(self, incisor: type(Ellipsis), /):
        return IncisionStyle.TRIVIAL(incisor)

    # def _incise_handle_none_(self, incisor: type(None), /):
    #     return IncisionStyle.NULL(incisor)

    def _incise_handle_chora_(self, incisor: Chora, /):
        return IncisionStyle.SLYCE(incisor)

    def _incise_slyce_chora_(self, incisor: Chora, /):
        return self @ incisor

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls._inchandlers, cls._incmeths = \
            cls._incision_gather_methnames()

#     @property
#     def _contains_(self, /):
#         print('foo')
#         return self._incise_retrieve_.__self__.codomain._contains_

#     @property
#     def _includes_(self, /):
#         return self._incise_retrieve_.__self__.codomain._includes_


class Chorelle(ChoraOp):

    @property
    def chora(self, /):
        return Choras.NULL

    def _incise_handle_(self, incisor, /):
        return self.chora._incise_handle_(incisor)

    def _incise_retrieve_(self, incisor, /):
        return self.chora._incise_retrieve_(incisor)

    def _incise_slyce_(self, incisor, /):
        return self.chora._incise_slyce_(incisor)

    @property
    def _contains_(self, /):
        return self.chora._contains_

    @property
    def _includes_(self, /):
        return self.chora._includes_


class Dimension(Chorelle, metaclass=_System):

    chora: Chora

    def _incise_retrieve_(self, incisor: ..., /):
        return _sett.Degenerate(self.chora._incise_retrieve_(incisor))

    def _contains_(self, other, /):
        if isinstance(other, _sett.Degenerate):
            return self.chora._contains_(other.value)
        return False

    def _includes_(self, other, /):
        if isinstance(other, self._abstract_class_):
            return self.chora._includes_(other)
        return False

    @prop
    def isdegenerate(self, /):
        return isinstance(self.chora, _sett.Degenerate)


class MultiChora(Choret, ChoraEnnaryOp):

    labels: KW = ()

    @prop
    def dimensions(self, /):
        return tuple(map(Dimension, self.args))

    @prop
    def depth(self, /):
        return len(self.dimensions)

    @prop
    def active(self, /):
        return tuple(
            not isinstance(cho, _sett.Degenerate)
            for cho in self.args
            )

    @prop
    def activedimensions(self, /):
        return tuple(_itertools.compress(self.dimensions, self.active))

    @prop
    def activedepth(self, /):
        return len(self.activedimensions)

    def _generic_multiincise(self, meth, incisor, /):
        choras = tuple(meth(incisor))
        if all(isinstance(chora, _sett.Degenerate) for chora in choras):
            return IncisionStyle.RETRIEVE(tuple(
                chora.value for chora in choras
                ))
        return IncisionStyle.SLYCE(choras)

    @prop
    def _mapping_multiincise(self, /):
        return _functools.partial(
            self._generic_multiincise, self._yield_mapping_multiincise
            )

    @prop
    def _sequence_multiincise(self, /):
        return _functools.partial(
            self._generic_multiincise, self._yield_sequence_multiincise
            )

    @prop
    def _single_multiincise(self, /):
        return _functools.partial(
            self._generic_multiincise, self._yield_single_multiincise
            )

    def _yield_mapping_multiincise(self, incisors: _collabc.Mapping, /):
        for key, dim in zip(self.labels, self.dimensions):
            try:
                incisor = incisors[key]
            except KeyError:
                yield dim
            else:
                yield dim[incisor]

    def _yield_single_multiincise(self, incisor: ..., /):
        dimit = iter(self.dimensions)
        while True:
            dim = next(dimit)
            if dim.isdegenerate:
                yield dim.chora
            else:
                yield dim[incisor]
                break
        else:
            raise IncisionError(incisor)
        yield from dimit

    def _yield_sequence_multiincise(self, incisors: _collabc.Sequence, /):
        ncho = self.activedepth
        ninc = len(incisors)
        nell = incisors.count(...)
        if nell:
            ninc -= nell
            if ninc % nell:
                raise ValueError("Cannot resolve incision ellipses.")
            ellreps = (ncho - ninc) // nell
        dimit = iter(self.dimensions)
        try:
            for incisor in incisors:
                if incisor is ...:
                    count = 0
                    while count < ellreps:
                        dim = next(dimit)
                        if not dim.isdegenerate:
                            count += 1
                        yield dim
                else:
                    while True:
                        dim = next(dimit)
                        if dim.isdegenerate:
                            yield dim.chora
                        else:
                            yield dim[incisor]
                            break
        except StopIteration:
            raise ValueError("Too many incisors in tuple incision.")
        yield from dimit

    def _incise_handle_mapping_(self, incisor: _collabc.Mapping, /):
        if not incisor:
            return IncisionStyle.TRIVIAL(incisor)
        elif self.activedepth == 1:
            return self._single_multiincise(incisor)
        return self._mapping_multiincise(incisor)

    def _incise_handle_sequence_(self, incisor: _collabc.Sequence, /):
        if not incisor:
            return IncisionStyle.TRIVIAL(incisor)
        elif self.activedepth == 1:
            return self._single_multiincise(incisor)
        return self._sequence_multiincise(incisor)

    def _incise_handle_single_(self, incisor: ..., /):
        return self._single_multiincise(incisor)

    def _incise_retrieve_tuple_(self, incisor: tuple, /):
        return incisor

    def _incise_slyce_tuple_(self, incisor: tuple, /):
        return self._abstract_class_(*incisor, labels=self.labels)

    def _contains_(self, arg, /):
        choras = self.args
        if len(arg) != len(choras):
            return False
        elif isinstance(arg, _collabc.Mapping):
            for key, chora in zip(self.labels, choras):
                if key in arg:
                    if not chora._contains_(arg[key]):
                        return False
        else:
            for val, chora in zip(arg, choras):
                print(chora)
                if not chora._contains_(val):
                    return False
        return True

    def _includes_(self, arg, /):
        choras = self.args
        if len(arg) != len(choras):
            return False
        elif isinstance(arg, _collabc.Mapping):
            for key, chora in zip(self.labels, choras):
                if key in arg:
                    if not chora._includes_(arg[key]):
                        return False
        else:
            for val, chora in zip(arg, choras):
                if not chora._includes_(val):
                    return False
        return True


_Stele_.complete()


###############################################################################
###############################################################################


# class MappChora(Chora):

#     @property
#     @_abc.abstractmethod
#     def mapp(self, /) -> _mapp.Mapp:
#         raise NotImplementedError

#     def __getitem__(self, arg, /):
#         return self.mapp[arg]

#     @prop
#     def domain(self, /):
#         return self.mapp.pre.domain

#     @prop
#     def codomain(self, /):
#         return self.mapp.post.codomain

#     with escaped('methname'):
#         for methname in (
#                 'get_signaltype', '_contains_', '_includes_'
#                 ):
#             exec('\n'.join((
#                 f"@property",
#                 f"def {methname}(self, /):",
#                 f"    return self.codomain.{methname}",
#                 )))


# class Chora(_sett.Sett, _mapp.Mapp):

#     @_abc.abstractmethod
#     def __handle_incisor__(self, incisor: ..., /) -> IncisionStyle.Dispatch:
#         raise NotImplementedError

#     @_abc.abstractmethod
#     def __incise__(self, incisor: IncisionStyle.Dispatch, /) -> ...:
#         raise NotImplementedError

#     def __getitem__(self, incisor, /):
#         return self.__incise__(self.__handle_incisor__(incisor))


# class MappChora(Chora, metaclass=_System):

#     handler: _mapp.Mapp
#     mapper: _mapp.Mapp

#     @classmethod
#     def _parameterise_(cls, /, *args, **kwargs):
#         params = super()._parameterise_(*args, **kwargs)
#         params.handler = _mapp(params.handler)
#         params.mapper = _mapp(params.mapper)
#         return params

#     @prop
#     def domain(self, /):
#         return self.handler.domain

#     @prop
#     def codomain(self, /):
#         return self.mapper.codomain

#     @prop
#     def get_signaltype(self, /):
#         return self.codomain.get_signaltype

#     @prop
#     def _contains_(self, /):
#         return self.codomain._contains_

#     @prop
#     def _includes_(self, /):
#         return self.codomain._contains_
