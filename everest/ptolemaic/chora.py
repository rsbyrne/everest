###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import deque as _deque, abc as _collabc
import types as _types
import functools as _functools
import itertools as _itertools

from .stele import Stele as _Stele_
from .semaphore import Semaphore as _Semaphore
from . import sett as _sett, mapp as _mapp
from .system import System as _System
from .essence import Essence as _Essence


class _Stele_(_Stele_):

    def __call__(self, arg, /):
        if arg is self:
            arg = Chora
        return convert(arg)

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
    raise TypeError(arg, type(arg))


def _default_incise_retrieve_(obj, arg, /) -> _sett.NULL:
    raise IncisionError(incisor)

def _default_incise_slyce_(obj, incisor, /) -> _sett.NULL:
    if isinstance(incisor, Chora):
        return obj.compose(incisor)
    raise IncisionError(incisor)

def _default_incise_trivial_(obj, incisor, /):
    return obj


class IncisionStyle(metaclass=_Semaphore):

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
            envelope, content = self.params
            try:
                meth = getattr(arg, envelope.methname)
            except AttributeError:
                meth = envelope._value_.__get__(arg)
            return meth(content)


class Chora(_sett.Sett, _mapp.Mapp, metaclass=_System):

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


class SuperChora(Chora, _mapp.SuperMapp):

    def subtend(self, other, /):
        raise NotImplementedError


class ChoraOp(SuperChora, _mapp.SuperMapp):

    ...


class ChoraMultiOp(ChoraOp, _mapp.MappMultiOp):

    ...


class ChoraVariadicOp(ChoraMultiOp, _mapp.MappVariadicOp):

    ...


class ChoraComposition(ChoraVariadicOp, _mapp.MappComposition):

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
        return self.__ptolemaic_class__(chora._incise_slyce_(incisor), *others)

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
            fallback = style._value_.__get__(self)
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

    @comp
    def _contains_(self, /):
        return self._incise_retrieve_.__self__.codomain._contains_

    @comp
    def _includes_(self, /):
        return self._incise_retrieve_.__self__.codomain._includes_


class Chorelle(ChoraOp):

    @property
    @_abc.abstractmethod
    def chora(self, /):
        raise NotImplementedError

    def _incise_handle_(self, incisor, /):
        return self.chora._incise_handle_(incisor)

    def _incise_retrieve_(self, incisor, /):
        return self.chora._incise_retrieve_(incisor)

    def _incise_slyce_(self, incisor, /):
        return self.chora._incise_slyce_(incisor)


class Degenerate(Choret, _sett.Degenerate):

    def _incise_retrieve_int_(self, incisor: int, /):
        if incisor == 0:
            return self.member
        raise IncisionError(incisor)

    def __iter__(self, /):
        yield self.member


class Dimension(Chorelle):

    chora: Chora

    def _incise_retrieve_(self, incisor: ..., /) -> Degenerate:
        chora = self.chora
        return DegenerateDimension(chora, chora._incise_retrieve_(incisor))

    def _incise_slyce_(self, incisor, /):
        return self.__ptolemaic_class__(super()._incise_slyce_(incisor))


class DegenerateDimension(Dimension):

    value: ...

    def _incise_handle_(self, incisor, /):
        raise IncisorError(incisor)


class MultiChora(Choret):

    dimensions: ARGS
    labels: KW = ()

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.dimensions = tuple(
            arg if isinstance(arg, Dimension) else Dimension(arg)
            for arg in params.dimensions
            )
        return params

    @comp
    def depth(self, /):
        return len(self.dimensions)

    @comp
    def active(self, /):
        return tuple(
            not isinstance(cho, DegenerateDimension)
            for cho in self.dimensions
            )

    @comp
    def activedimensions(self, /):
        return tuple(_itertools.compress(self.dimensions, self.active))

    @comp
    def activedepth(self, /):
        return len(self.activedimensions)

    def _generic_multiincise(self, meth, incisor, /):
        dims = tuple(meth(incisor))
        if all(isinstance(dim, DegenerateDimension) for dim in dims):
            return IncisionStyle.RETRIEVE(tuple(dim.value for dim in dims))
        return IncisionStyle.SLYCE(dims)

    @comp
    def _mapping_multiincise(self, /):
        return _functools.partial(
            self._generic_multiincise, self._yield_mapping_multiincise
            )

    @comp
    def _sequence_multiincise(self, /):
        return _functools.partial(
            self._generic_multiincise, self._yield_sequence_multiincise
            )

    @comp
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
            if isinstance(dim, DegenerateDimension):
                yield dim
            else:
                yield dim[incisor]
                break
        else:
            assert False
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
                        if not isinstance(dim, DegenerateDimension):
                            count += 1
                        yield dim
                    continue
                while True:
                    dim = next(dimit)
                    if isinstance(dim, DegenerateDimension):
                        yield dim
                        continue
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
        return self.__ptolemaic_class__(*incisor, labels=self.labels)


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

#     @comp
#     def domain(self, /):
#         return self.mapp.pre.domain

#     @comp
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
#     def __parameterise__(cls, /, *args, **kwargs):
#         params = super().__parameterise__(*args, **kwargs)
#         params.handler = _mapp(params.handler)
#         params.mapper = _mapp(params.mapper)
#         return params

#     @comp
#     def domain(self, /):
#         return self.handler.domain

#     @comp
#     def codomain(self, /):
#         return self.mapper.codomain

#     @comp
#     def get_signaltype(self, /):
#         return self.codomain.get_signaltype

#     @comp
#     def _contains_(self, /):
#         return self.codomain._contains_

#     @comp
#     def _includes_(self, /):
#         return self.codomain._contains_
