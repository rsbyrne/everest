###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc

from . import sett as _sett, mapp as _mapp
from .enumm import Enumm as _Enumm
from .stele import Stele as _Stele
from .system import System as _System


class _SteleType_(metaclass=_Stele):

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
            with self.mutable:
                for enumm in choras.enumerators:
                    setattr(self, enumm.name, enumm)

    def __instancecheck__(self, arg, /):
        return isinstance(arg, Chora)

    def __subclasscheck__(self, arg, /):
        return issubclass(arg, Chora)


_SteleType_.commence()


class IncisionError(_mapp.MappError):

    ...


def convert(arg, /):
    if isinstance(arg, Chora):
        return arg
    raise TypeError(type(arg))


class IncisionStyle(metaclass=_Enumm):

    RETRIEVE: 'The procedure to return a single element.' \
        = '__incise_retrieve__'
    SLYCE: 'The procedure to return a subset of elements.' \
        = '__incise_slyce__'
    TRIVIAL: 'The procedure for trivial incisors like `...`.' \
        = '__incise_trivial__'
    NULL: 'The special procedure for incisor `None`.' \
        = '__incise_null__'

    def __call__(self, other, /):
        return getattr(other, self._value_)


class Chora(_sett.Sett, _mapp.Mapp):

    convert = staticmethod(convert)

    @_abc.abstractmethod
    def __incise_pre__(self, arg, /) -> tuple[IncisionStyle, object]:
        if isinstance(arg, slice):
            args = arg.start, arg.stop, arg.step
            if all(subarg is None for subarg in args):
                return IncisionStyle.TRIVIAL, arg
            return IncisionStyle.SLYCE, arg
        if arg is NotImplemented:
            return IncisionStyle.NULL, arg
        if arg is None:
            return IncisionStyle.TRIVIAL, arg
        return IncisionStyle.RETRIEVE, arg

    @_abc.abstractmethod
    def __incise_retrieve__(self, arg, /):
        raise NotImplementedError

    @_abc.abstractmethod
    def __incise_slyce__(self, arg, /):
        raise NotImplementedError

    def __incise_trivial__(self, arg, /):
        return self

    def __incise_null__(self, arg, /):
        return Choras.NULL

    def __incise__(self, arg, /):
        style, arg = self.__incise_pre__(arg)
        return style(self)(arg)

    def __getitem__(self, arg, /):
        return self.__incise__(arg)

    @property
    def domain(self, /):
        return self.__incise_retrieve__.__annotations__.get('return', object)

    @property
    def codomain(self, /):
        return self


class Choras(Chora, metaclass=_Enumm):

    UNIVERSE: None = _sett.Setts.UNIVERSE
    NULL: None = _sett.Setts.NULL
    POWER: None = _sett.Setts.POWER

    def __incise_retrieve__(self, arg: object, /):
        if arg in self:
            return arg
        raise IncisionError(arg)

    def __incise_slyce__(self, arg: object, /):
        raise IncisionError(arg)

    def __sett_contains__(self, arg, /):
        return self._value_.__sett_contains__(arg)

    def __sett_includes__(self, arg, /):
        return self._value_.__sett_includes__(arg)


class QuickChora(Chora, metaclass=_System):

    retrievemapp: _mapp.Mapp
    slycemapp: _mapp.Mapp

    @property
    def __incise_retrieve__(self, /):
        return self.retrievemapp.__getitem__

    @property
    def __incise_slyce__(self, /):
        return self.slycemapp.__getitem__


class ChoraOp(Chora, _mapp.MappOp):

    ...


class ChoraMultiOp(ChoraOp, _mapp.MappMultiOp):

    ...


class ComposedChora(ChoraMultiOp, _mapp.ComposedMapp):

    def __incise_retrieve__(self, arg, /):
        for chora in self.args:
            arg = chora.__incise_retrieve__(arg)
        return arg

    def __incise_slyce__(self, arg, /):
        for chora in self.args:
            arg = chora.__incise_slyce__(arg)
        return arg

    __getitem__ = Chora.__getitem__


_SteleType_.complete()


###############################################################################
###############################################################################
