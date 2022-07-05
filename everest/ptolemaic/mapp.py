###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import itertools as _itertools
import inspect as _inspect
from collections import abc as _collabc

from .essence import Essence as _Essence
from .content import ModuleMate as _ModuleMate
from .sprite import Sprite as _Sprite
from .system import System as _System
from . import sett as _sett
from .stele import Stele as _Stele


class _SteleType_(metaclass=_Stele):

    def __call__(self, arg, /):
        if arg is self:
            arg = Mapp
        return convert(arg)

    def __instancecheck__(self, arg, /):
        return isinstance(arg, Mapp)

    def __subclasscheck__(self, arg, /):
        return issubclass(arg, Mapp)


_SteleType_.commence()


class MappError(RuntimeError):
    ...


def convert(arg, /):
    if isinstance(arg, Mapp):
        return arg
    if isinstance(arg, _collabc.Iterable):
        return SwitchMapp(arg)
    if isinstance(arg, _collabc.Callable):
        return CallMapp(arg)
    raise TypeError(type(arg))


class Mapp(metaclass=_Essence):

    @_abc.abstractmethod
    def __getitem__(self, _, /):
        raise NotImplementedError

    @property
    @_abc.abstractmethod
    def domain(self, /):
        raise NotImplementedError

    @property
    @_abc.abstractmethod
    def codomain(self, /):
        raise NotImplementedError

    def __matmul__(self, arg, /):
        if isinstance(arg, Mapp):
            return ComposedMapp(arg, self)
        raise TypeError(type(arg))

    def __rmatmul__(self, arg, /):
        if isinstance(arg, Mapp):
            return ComposedMapp(self, arg)
        raise TypeError(type(arg))


class CallMapp(Mapp, metaclass=_Sprite):

    func: _collabc.Callable

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        func = params.func
        parameters = tuple(_inspect.signature(func).parameters.values())
        if not all(pm.kind.value == 0 for pm in parameters):
            raise ValueError(func, (
                "Functions being converted to Mapps "
                "must have only positional arguments."
                ))
        return params

    @property
    def domain(self, /):
        setts = tuple(
            _sett(pm.annotation)
            for pm in _inspect.signature(self.func).parameters.values()
            )
        if len(setts) == 1:
            return setts[0]
        return _sett.Brace(setts)

    @property
    def codomain(self, /):
        return _sett(self.func.__annotations__.get('return', None))

    @property
    def __getitem__(self, /):
        func = self.func
        if len(_inspect.signature(func).parameters) == 1:
            getitem = func
        else:
            getitem = lambda x: func(*x)
        return getitem


class SwitchMapp(Mapp, metaclass=_Sprite):

    mapps: _collabc.Iterable

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.mapps = tuple(map(convert, params.mapps))
        return params

    @property
    def domain(self, /):
        return _sett.union(*(mp.domain for mp in self.mapps))

    @property
    def codomain(self, /):
        return _sett.union(*(mp.codomain for mp in self.mapps))

    def __getitem__(self, arg, /):
        for mapp in self.mapps:
            if arg in mapp.domain:
                return mapp[arg]
        raise MappError(arg)


class SwitchMapp(Mapp, metaclass=_System):

    mapps: ARGS

    @prop
    def _get_mapp(self, /):
        checkmapps = tuple(
            (mapp.domain.signaltype, mapp) for mapp in self.mapps
            )
        @_functools.lru_cache
        def func(typ: type, /):
            for checktyp, mapp in checkmapps:
                if issubclass(typ, checktyp):
                    return mapp
            raise MappError(typ)
        return func

    @prop
    def domain(self, /):
        return _sett.union(*(mp.domain for mp in self.mapps))

    @prop
    def codomain(self, /):
        return _sett.union(*(mp.codomain for mp in self.mapps))

    def __getitem__(self, arg, /):
        return self._get_mapp(type(arg))[arg]


# class BraceSwitchMapp(SwitchMapp):

#     @classmethod
#     def __parameterise__(cls, /, *args, **kwargs):
#         params = super().__parameterise__(*args, **kwargs)
#         mapps = params.mapps
#         domains = tuple(mapp.domain for mapp in mapps)
#         if not all(map(_sett.Brace.__instancecheck__, domains)):
#             raise cls.paramexc(
#                 mapps, "All mapps in a BraceSwitchMapp must be of Brace type."
#                 )
#         if len(set(domain.breadth for domain in domains)) != 1:
#             raise cls.paramexc(mapps, (
#                 "All mapps in a BraceSwitchMapp must have domains "
#                 "of the same shape."
#                 ))
#         return params

#     @_Armature.prop
#     def get_mapp(self, /):
#         checkmapps = tuple(
#             (tuple(sett.signaltype for sett in mapp.domain.setts), mapp)
#             for mapp in self.mapps
#             )
#         @_functools.lru_cache
#         def _func_(*typs):
#             for checktyps, mapp in checkmapps:
#                 if all(_itertools.starmap(issubclass, zip(typs, checktyps))):
#                     return mapp
#             raise MappError(typs)
#         return _func_

#     def __getitem__(self, arg, /):
#         return self.get_mapp(*map(type, arg))[arg]


#     @_Armature.prop
#     def get_mapp(self, /):
#         checkmapps = tuple(
#             (mapp.domain.signaltype, mapp) for mapp in self.mapps
#             )
#         @_functools.lru_cache
#         def func(typ: type, /):
#             for checktyp, mapp in checkmapps:
#                 if issubclass(typ, checktyp):
#                     return mapp
#             raise MappError(typ)
#         return func

#     def __getitem__(self, arg, /):
#         return self.get_mapp(type(arg))[arg]


class MappOp(Mapp):

    ...


class ModifiedMapp(MappOp, metaclass=_Sprite):

    mapp: Mapp
    domain: _sett.Sett = None
    codomain: _sett.Sett = None

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        mapp = params.mapp = convert(params.mapp)
        for methname in ('domain', 'codomain'):
            obj = getattr(params, methname)
            if obj is None:
                setattr(params, methname, getattr(mapp, methname))
            else:
                setattr(params, methname, _sett(obj))
        return params

    def __getitem__(self, arg, /):
        out = self.mapp[arg]
        assert out in self.codomain
        return out


class MappMultiOp(MappOp, metaclass=_Sprite):

    mapps: _collabc.Iterable

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.mapps = tuple(map(convert, params.mapps))
        return params


class ComposedMapp(MappMultiOp):

    mapps: _collabc.Iterable

    @property
    def domain(self, /):
        return self.mapps[0].domain

    @property
    def codomain(self, /):
        return self.mapps[-1].codomain

    @classmethod
    def _unpack_args(cls, args, /):
        for arg in args:
            if isinstance(arg, cls):
                yield from arg.mapps
            elif isinstance(arg, Mapp):
                yield arg
            else:
                raise RuntimeError(arg)

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.mapps = tuple(cls._unpack_args(params.mapps))
        return params

    def __getitem__(self, arg, /):
        for mapp in self.mapps:
            arg = mapp[arg]
        return arg


_SteleType_.complete()


###############################################################################
###############################################################################


# class BraceSwitchMapp(SwitchMapp):

#     @classmethod
#     def __parameterise__(cls, /, *args, **kwargs):
#         params = super().__parameterise__(*args, **kwargs)
#         mapps = params.mapps
#         domains = tuple(mapp.domain for mapp in mapps)
#         if not all(map(_sett.Brace.__instancecheck__, domains)):
#             raise cls.paramexc(
#                 mapps, "All mapps in a BraceSwitchMapp must be of Brace type."
#                 )
#         if len(set(domain.breadth for domain in domains)) != 1:
#             raise cls.paramexc(mapps, (
#                 "All mapps in a BraceSwitchMapp must have domains "
#                 "of the same shape."
#                 ))
#         return params

#     @_Armature.prop
#     def get_mapp(self, /):
#         checkmapps = tuple(
#             (tuple(sett.signaltype for sett in mapp.domain.setts), mapp)
#             for mapp in self.mapps
#             )
#         @_functools.lru_cache
#         def _func_(*typs):
#             for checktyps, mapp in checkmapps:
#                 if all(_itertools.starmap(issubclass, zip(typs, checktyps))):
#                     return mapp
#             raise MappError(typs)
#         return _func_

#     def __getitem__(self, arg, /):
#         return self.get_mapp(*map(type, arg))[arg]
