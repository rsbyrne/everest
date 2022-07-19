###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import deque as _deque

from .stele import Stele as _Stele_
from .semaphore import Semaphore as _Semaphore
from . import sett as _sett, mapp as _mapp
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


def convert(arg, /):
    if isinstance(arg, Chora):
        return arg
    raise TypeError(arg, type(arg))


class IncisionStyle(metaclass=_Semaphore):

    RETRIEVE: 'The procedure to return a single element.'
    SLYCE: 'The procedure to return a subset of elements.'
    TRIVIAL: 'The procedure for trivial incisors like `...`.'
    NULL: 'The special procedure for incisor `None`.'


class IncisionError(_mapp.MappError):

    ...


class Chora(_sett.Sett, _mapp.Mapp, metaclass=_System):

    @property
    @_abc.abstractmethod
    def mapp(self, /) -> _mapp.Mapp:
        raise NotImplementedError

    def __getitem__(self, arg, /):
        return self.mapp[arg]

    @comp
    def domain(self, /):
        return self.mapp.pre.domain

    @comp
    def codomain(self, /):
        return self.mapp.post[IncisionStyle.RETRIEVE].codomain

    def __compose__(self, other, /):
        return ChoraComposition(self, other)

    def __rcompose__(self, other, /):
        return ChoraComposition(other, self)

    with escaped('methname'):
        for methname in (
                'get_signaltype', '_contains_', '_includes_'
                ):
            exec('\n'.join((
                f"@property",
                f"def {methname}(self, /):",
                f"    return self.codomain.{methname}",
                )))


class Choret(Chora):

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

    def _incise_handle_ellipsis_(self, incisor: type(Ellipsis), /):
        return IncisionStyle.TRIVIAL(incisor)

    def _incise_handle_none_(self, incisor: type(None), /):
        return IncisionStyle.NULL(incisor)

    def _incise_handle_chora_(self, incisor: Chora, /):
        return IncisionStyle.SLYCE(incisor)

    def _incise_slyce_chora_(self, incisor: Chora, /):
        return incisor >> self

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls._inchandlers, cls._incmeths = \
            cls._incision_gather_methnames()

    @organ
    def mapp(self, /):
        return _mapp.StyleMapp.__class_alt_call__(
            _mapp((getattr(self, nm) for nm in self._inchandlers)),
            _mapp({
                style: _mapp((getattr(self, nm) for nm in names))
                for style, names in self._incmeths.items()
                }),
            )


class ChoraComposition(Chora):

    choras: ARGS

    @comp
    def mapp(self, /):
        mapps = (chora.mapp for chora in self.choras)
        mapp = next(mapps)
        for nextmapp in mapps:
            mapp = mapp.subtend(nextmapp)
        return mapp


_Stele_.complete()


###############################################################################
###############################################################################


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



