###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import itertools as _itertools
import inspect as _inspect
import types as _types
from collections import abc as _collabc

from everest.utilities import pretty as _pretty

from .essence import Essence as _Essence
from .sprite import Sprite as _Sprite
from .system import System as _System
from . import sett as _sett
from .stele import Stele as _Stele_


class _Stele_(_Stele_):

    def __call__(self, arg, /):
        if arg is self:
            arg = Mapp
        return convert(arg)

    def __instancecheck__(self, arg, /):
        return isinstance(arg, Mapp)

    def __subclasscheck__(self, arg, /):
        return issubclass(arg, Mapp)

    @property
    def register(self, /):
        return self.Mapp.register

    def __mro_entries__(self, bases, /):
        return (self.Mapp,)


_Stele_.commence()


class MappError(RuntimeError):
    ...


def convert(arg, /):
    if isinstance(arg, Mapp):
        return arg
    if isinstance(arg, _collabc.Mapping):
        return ArbitraryMapp(arg)
    if isinstance(arg, _collabc.Iterable):
        return SwitchMapp(*arg)
    if isinstance(arg, _collabc.Callable):
        return CallMapp(arg)
    raise TypeError(type(arg))


class Mapp(metaclass=_Essence):

    convert = staticmethod(convert)

    @_abc.abstractmethod
    def __getitem__(self, _, /):
        raise NotImplementedError

    # @_abc.abstractmethod
    # def __call__(self, /, *_, **__):
    #     raise NotImplementedError

    @property
    @_abc.abstractmethod
    def domain(self, /):
        raise NotImplementedError

    @property
    @_abc.abstractmethod
    def codomain(self, /):
        raise NotImplementedError

    def __matmul__(self, arg, /):
        return ComposedMapp(arg, self)

    def __rmatmul__(self, arg, /):
        return ComposedMapp(self, arg)

    def extend(self, arg, /):
        return ChainMapp(arg, self)

    def subtend(self, arg, /):
        raise NotImplementedError


class CallMapp(Mapp, metaclass=_System):

    func: _collabc.Callable

    # @comp
    # def ismethod(self, /):
    #     return isinstance(self.func, _types.MethodType)

    @comp
    def setts(self, /):
        # pms = iter()
        # if self.ismethod:
        #     next(pms)
        return tuple(
            _sett(pm.annotation)
            for pm in _inspect.signature(self.func).parameters.values()
            if pm.kind.value < 2
            )

    @comp
    def arity(self, /):
        return len(self.setts)

    @comp
    def domain(self, /):
        setts = self.setts
        if len(setts) == 1:
            return setts[0]
        return _sett.BraceSett(setts)

    @comp
    def codomain(self, /):
        return _sett(self.func.__annotations__.get('return', None))

    @comp
    def _getitem_(self, /):
        func = self.func
        if self.arity == 1:
            return func
        return lambda x: func(*x)

    def __getitem__(self, arg, /):
        if arg in self.domain:
            return self._getitem_(arg)
        raise MappError(arg)

#     @property
#     def __call__(self, /):
#         return self.func


class SuperMapp(Mapp):

    @_abc.abstractmethod
    def subtend(self, arg, /):
        raise NotImplementedError


@_collabc.Mapping.register
class ArbitraryMapp(SuperMapp, metaclass=_System):

    mapping: _collabc.Mapping

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        return super().__parameterise__(dict(*args, **kwargs))

    with escaped('methname'):
        for methname in (
                '__len__', '__contains__', '__iter__',
                '__getitem__', 'keys', 'items', 'values', 'get',
                ):
            exec('\n'.join((
                f"@property",
                f"def {methname}(self, /):",
                f"    return self.mapping.{methname}",
                )))

    @comp
    def domain(self, /):
        return _sett(tuple(self.mapping))

    @comp
    def codomain(self, /):
        return _sett(tuple(self.mapping.values()))

    def extend(self, arg: _collabc.Mapping, /):
        return self.__ptolemaic_class__({**self.mapping, **arg})

    def subtend(self, arg: _collabc.Mapping, /):
        mapping = {**self.mapping}
        for key in arg:
            mapping[key] = arg[key] @ mapping[key]
        return self.__ptolemaic_class__(mapping)

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        return _pretty.pretty_dict(self.mapping, p, cycle, root=root)


class TypeMapp(ArbitraryMapp):

    @_functools.lru_cache
    def __getitem__(self, arg, /):
        for typ, val in self.mapping.items():
            if issubclass(arg, typ):
                return val
        raise MappError(arg)


class MappOp(SuperMapp):

    ...


class ModifiedMapp(MappOp, metaclass=_System):

    mapp: Mapp

    @field
    def domain(self, /) -> _sett.Sett:
        return self.mapp.domain

    @field
    def codomain(self, /) -> _sett.Sett:
        return self.mapp.codomain

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params.mapp = convert(params.mapp)
        return params

    def __getitem__(self, arg, /):
        out = self.mapp[arg]
        assert out in self.codomain
        return out

    # def __call__(self, /, *args, **kwargs):
    #     out = self.mapp(*args, **kwargs)
    #     assert out in self.codomain
    #     return out


class MappMultiOp(MappOp):

    ...


class MappVariadicOp(MappMultiOp, metaclass=_System):

    args: ARGS

    @classmethod
    def _unpack_args(cls, args, /):
        for arg in args:
            if isinstance(arg, cls):
                yield from arg.args
            else:
                yield convert(arg)

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.args = tuple(cls._unpack_args(params.args))
        return params

    def subtend(self, arg, /):
        return self.__ptolemaic_class__(*(arg @ sub for sub in arg))


class ElasticMapp(MappVariadicOp):

    def extend(self, arg, /):
        return self.__ptolemaic_class__(self, arg)


class ChainMapp(ElasticMapp):

    def __getitem__(self, arg, /):
        for mapp in self.args:
            try:
                return mapp[arg]
            except MappError:
                continue
        raise MappError(arg)

    @comp
    def domain(self, /):
        return _sett.union(arg.domain for arg in self.args)

    @comp
    def codomain(self, /):
        return _sett.union(arg.codomain for arg in self.args)


class SwitchMapp(ElasticMapp):

    @comp
    def typemapp(self, /):
        return TypeMapp(
            (mp.domain.signaltype, mp) for mp in self.args
            )

    @comp
    def domain(self, /):
        return _sett.union(*(mp.domain for mp in self.args))

    @comp
    def codomain(self, /):
        return _sett.union(*(mp.codomain for mp in self.args))

    def __getitem__(self, arg, /):
        return self.typemapp[type(arg)][arg]

    def subtend(self, arg, /):
        if isinstance(arg, SwitchMapp):
            arg = arg.typemapp
        return self.__ptolemaic_class__(*self.typemapp.subtend(arg).values())

    # @property
    # def __call__(self, /):
    #     return self._get_mapp(type(arg))


class ComposedMapp(MappVariadicOp, metaclass=_System):

    @comp
    def domain(self, /):
        return self.args[0].domain

    @comp
    def codomain(self, /):
        return self.args[-1].codomain

    def __getitem__(self, arg, /):
        for mapp in self.args:
            arg = mapp[arg]
        return arg


class StyleMapp(MappMultiOp, metaclass=_System):

    pre: Mapp
    post: Mapp

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.pre, params.post = map(convert, (params.pre, params.post))
        return params

    def __getitem__(self, arg, /):
        arg, style = self.pre[arg]
        return self.post[style][arg]

    def subtend(self, arg, /):
        if not isinstance(arg, StyleMapp):
            raise TypeError(
                "You can only subtend a StyleMapp with another StyleMapp:",
                type(arg),
                )
        pre, argpre = self.pre, arg.pre
        if pre is not argpre:
            if isinstance(pre, SuperMapp):
                pre = pre.subtend(pre)
            else:
                pre = argpre @ pre
        post = self.post.subtend(arg.post)
        return self.__ptolemaic_class__(pre, post)

    @comp
    def domain(self, /):
        return self.pre.domain

    @comp
    def codomain(self, /):
        return self.post.domain


# class Mappette(Mapp, metaclass=_System):

#     __mergenames__ = {'__mapp_styles__': (dict, dict)}

#     @classmethod
#     def __class_init__(cls, /):
#         super().__class_init__()
#         cls.pre = ...
#         cls.post = ...

#     def __getitem__(self, arg, /):
#         arg, style =


_Stele_.complete()


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
