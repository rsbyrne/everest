###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc, deque as _deque

from everest import ur as _ur

from .essence import Essence as _Essence
from . import sett as _sett, mapp as _mapp
from .enumm import Enumm as _Enumm
from .stele import Stele as _Stele_
from .system import System as _System


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


class IncisionStyle(metaclass=_Enumm):

    RETRIEVE: 'The procedure to return a single element.'
    SLYCE: 'The procedure to return a subset of elements.'
    TRIVIAL: 'The procedure for trivial incisors like `...`.'
    NULL: 'The special procedure for incisor `None`.'


@_mapp.register
@_sett.register
class Chora(metaclass=_Essence):

    ...
#     @property
#     def domain(self, /):
#         return s

#     @property
#     def codomain(self, /):
#         return self


class Choret(Chora, metaclass=_System):

    __mergenames__ = dict(__incision_styles__=list)
    __incision_styles__ = IncisionStyle

    @classmethod
    def _incision_gather_methnames(cls, /):
        channels = {'_incise_handle_': _deque()}
        styles = cls.__incision_styles__
        channels.update(
            (f'_incise_{style.name.lower()}_', _deque())
            for style in styles
            )
        for name in dir(cls):
            for prefix, deq in channels.items():
                if name.startswith(prefix):
                    if name not in deq:
                        deq.append(name)
                continue
        return (
            channels.pop('_incise_handle_'),
            {style: deq for style, deq in zip(styles, channels.values())},
            )

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls._inchandlers, cls._incmeths = \
            cls._incision_gather_methnames()

    @comp
    def mapp(self, /):
        return _mapp.StyleMapp(
            _mapp((getattr(self, nm) for nm in self._inchandlers)),
            _mapp({
                style: _mapp((getattr(self, nm) for nm in names))
                for style, names in self._incmeths.items()
                }),
            )

    def __getitem__(self, arg, /):
        return self.mapp[arg]

#     def subtend(self, arg, /):
        


_Stele_.complete()


###############################################################################
###############################################################################


#     @classmethod
#     def _gather_methods(cls, /):
#         channels = {'_incise_handle_': {}}
#         styles = cls.__incision_styles__
#         channels.update(
#             (f'_incise_{style.name.lower()}_', {})
#             for style in styles
#             )
#         for base in reversed(cls.__mro__):
#             for name, meth in base.__dict__.items():
#                 for prefix, dct in channels.items():
#                     if name.startswith(prefix):
#                         dct[name] = meth
#                     continue
#         return (
#             _mapp(channels.pop('_incise_handle_').values()),
#             _mapp({
#                 style: _mapp(meths)
#                 for style, meths in zip(styles, channels.values())
#                 }),
#             )


# class IncisionStyle(metaclass=_Enumm):

#     RETRIEVE: 'The procedure to return a single element.' \
#         = '__incise_retrieve__'
#     SLYCE: 'The procedure to return a subset of elements.' \
#         = '__incise_slyce__'
#     TRIVIAL: 'The procedure for trivial incisors like `...`.' \
#         = '__incise_trivial__'
#     NULL: 'The special procedure for incisor `None`.' \
#         = '__incise_null__'

#     def __call__(self, other, /):
#         return getattr(other, self._value_)


# def convert(arg, /):
#     if isinstance(arg, Chora):
#         return arg
#     if isinstance(arg, _mapp):
#         return Chora(arg.codomain, )
#     raise TypeError(type(arg))


# @_sett.register
# @_mapp.register
# class Chora(metaclass=_System):

#     sett: _sett.Sett
#     mapp: _mapp.Mapp

#     @classmethod
#     def parameterise(cls, /, *args, **kwargs):
#         params = super().parameterise(*args, **kwargs)
#         params.sett = _sett.convert(params.sett)
#         params.mapp = _mapp.convert(params.mapp)
#         return params

#     def __getitem__(self, arg, /):
#         out = self.mapp[arg]
#         if out in self.sett:
#             return out
#         raise IncisionError(arg)

#     def __contains__(self, arg, /):
#         return arg in self.sett

#     def __includes__(self, arg, /):
#         return self.sett.__includes__(arg)


# @Chora.register
# class Choric(metaclass=_System):

#     @comp
#     def chora(self, /) -> Chora:
#         raise NotImplementedError

#     def __getitem__(self, arg, /):
#         return self.chora[arg]

#     def __contains__(self, arg, /):
#         return arg in self.chora

#     def __includes__(self, arg, /):
#         return self.chora.__includes__(arg)


# class Chora(_sett.Sett, _mapp.Mapp):

#     convert = staticmethod(convert)

#     @_abc.abstractmethod
#     def __incise_pre__(self, arg, /) -> tuple[IncisionStyle, object]:
#         if isinstance(arg, slice):
#             args = arg.start, arg.stop, arg.step
#             if all(subarg is None for subarg in args):
#                 return IncisionStyle.TRIVIAL, arg
#             return IncisionStyle.SLYCE, arg
#         if arg is NotImplemented:
#             return IncisionStyle.NULL, arg
#         if arg is None:
#             return IncisionStyle.TRIVIAL, arg
#         return IncisionStyle.RETRIEVE, arg

#     @_abc.abstractmethod
#     def __incise_retrieve__(self, arg, /):
#         raise NotImplementedError

#     @_abc.abstractmethod
#     def __incise_slyce__(self, arg, /):
#         raise NotImplementedError

#     def __incise_trivial__(self, arg, /):
#         return self

#     def __incise_null__(self, arg, /):
#         return _sett.NULL

#     def __incise__(self, arg, /):
#         style, arg = self.__incise_pre__(arg)
#         return style(self)(arg)

#     def __getitem__(self, arg, /):
#         return self.__incise__(arg)

#     @property
#     def domain(self, /):
#         return self.__incise_retrieve__.__annotations__.get('return', object)

#     @property
#     def codomain(self, /):
#         return self


# class QuickChora(Chora, metaclass=_System):

#     retrievemapp: _mapp.Mapp
#     slycemapp: _mapp.Mapp

#     @property
#     def __incise_retrieve__(self, /):
#         return self.retrievemapp.__getitem__

#     @property
#     def __incise_slyce__(self, /):
#         return self.slycemapp.__getitem__


# class ChoraOp(Chora, _mapp.MappOp):

#     ...


# class ChoraMultiOp(ChoraOp, _mapp.MappMultiOp):

#     ...


# class ComposedChora(ChoraMultiOp, _mapp.ComposedMapp):

#     def __incise_retrieve__(self, arg, /):
#         for chora in self.args:
#             arg = chora.__incise_retrieve__(arg)
#         return arg

#     def __incise_slyce__(self, arg, /):
#         for chora in self.args:
#             arg = chora.__incise_slyce__(arg)
#         return arg

#     __getitem__ = Chora.__getitem__



# class Choras(Chora, metaclass=_Enumm):

#     UNIVERSE: None = _sett.Setts.UNIVERSE
#     NULL: None = _sett.Setts.NULL
#     POWER: None = _sett.Setts.POWER

#     def __incise_retrieve__(self, arg: object, /):
#         if arg in self:
#             return arg
#         raise IncisionError(arg)

#     def __incise_slyce__(self, arg: object, /):
#         raise IncisionError(arg)

#     def __sett_contains__(self, arg, /):
#         return self._value_.__sett_contains__(arg)

#     def __sett_includes__(self, arg, /):
#         return self._value_.__sett_includes__(arg)
