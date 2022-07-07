###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import itertools as _itertools
import inspect as _inspect
from collections import abc as _collabc

from everest.utilities import pretty as _pretty

from .essence import Essence as _Essence
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

    @property
    def register(self, /):
        return self.Mapp.register


_SteleType_.commence()


class MappError(RuntimeError):
    ...


def convert(arg, /):
    if isinstance(arg, Mapp):
        return arg
    if isinstance(arg, _collabc.Mapping):
        return ArbitraryMapp(arg)
    if isinstance(arg, _collabc.Iterable):
        return SwitchMapp(arg)
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
        raise NotImplementedError

    def subtend(self, arg, /):
        raise NotImplementedError


class CallMapp(Mapp, metaclass=_System):

    func: _collabc.Callable

    @comp
    def setts(self, /):
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
        if len(_inspect.signature(func).parameters) == 1:
            return func
        return lambda x: func(*x)

    def __getitem__(self, arg, /):
        return self._getitem_(arg)

#     @property
#     def __call__(self, /):
#         return self.func


class SuperMapp(Mapp):

    @_abc.abstractmethod
    def subtend(self, arg, /):
        raise NotImplementedError


@_collabc.Mapping.register
class ArbitraryMapp(Mapp, metaclass=_System):

    mapping: _collabc.Mapping

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


class SwitchMapp(Mapp, metaclass=_System):

    mapps: ARGS

    @comp
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

    @comp
    def domain(self, /):
        return _sett.union(*(mp.domain for mp in self.mapps))

    @comp
    def codomain(self, /):
        return _sett.union(*(mp.codomain for mp in self.mapps))

    def __getitem__(self, arg, /):
        return self._get_mapp(type(arg))[arg]

    # @property
    # def __call__(self, /):
    #     return self._get_mapp(type(arg))


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

    # def __call__(self, /, *args, **kwargs):
    #     out = self.mapp(*args, **kwargs)
    #     assert out in self.codomain
    #     return out


class MappMultiOp(MappOp, metaclass=_System):

    args: ARGS

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.args = tuple(map(cls.convert, params.args))
        return params


class ComposedMapp(MappMultiOp):

    @comp
    def domain(self, /):
        return self.args[0].domain

    @comp
    def codomain(self, /):
        return self.args[-1].codomain

    @classmethod
    def _unpack_args(cls, args, /):
        for arg in args:
            if isinstance(arg, cls):
                yield from arg.args
            else:
                yield arg

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.args = tuple(cls._unpack_args(params.args))
        return params

    def __getitem__(self, arg, /):
        for mapp in self.args:
            arg = mapp[arg]
        return arg


class StyleMapp(Mapp, metaclass=_System):

    pre: Mapp
    post: Mapp

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        convert = cls.convert
        params.pre = convert(params.pre)
        params.post = convert(params.post)
        # params.posts.update(
        #     (key, convert(val)) for key, val in params.posts.items()
        #     )
        return params

    def __getitem__(self, arg, /):
        arg, style = self.pre[arg]
        return self.post[style][arg]

    def subtend(self, arg, /):
        return self.__ptolemaic_class__(self.pre, self.post.subtend(arg))

    @comp
    def domain(self, /):
        return self.pre.domain

    @comp
    def codomain(self, /):
        return self.post.domain
        # return _sett.BraceSett(post.codomain for post in self.posts.values())


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
