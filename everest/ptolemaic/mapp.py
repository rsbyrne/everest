###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import inspect as _inspect
from collections import abc as _collabc

from .essence import Essence as _Essence
from .sprite import ModuleMate as _ModuleMate
from .armature import Armature as _Armature
from . import sett as _sett


class MappError(RuntimeError):
    ...


def convert(arg, /):
    if isinstance(arg, Mapp):
        return arg
    if isinstance(arg, _collabc.Iterable):
        return SwitchMapp(*arg)
    if isinstance(arg, _collabc.Callable):
        return DefMapp(arg)
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

    @property
    def signaltype(self, /):
        return self.domain.signaltype

    def __matmul__(self, arg, /):
        if isinstance(arg, Mapp):
            return ComposedMapp(arg, self)
        raise TypeError(type(arg))

    def __rmatmul__(self, arg, /):
        return NotImplemented


class DefMapp(Mapp, metaclass=_Armature):

    func: _Armature.Field.POS[_collabc.Callable]

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        func = params.func
        parameters = tuple(_inspect.signature(func).parameters.values())
        if not all(pm.kind.value == 0 for pm in parameters):
            message = (
                "Functions being converted to Mapps "
                "must have only positional arguments."
                )
            raise cls.paramexc(func, message=message)
        return params

    @_Armature.prop
    def domain(self, /):
        setts = tuple(
            _sett(pm.annotation)
            for pm in _inspect.signature(self.func).parameters.values()
            )
        if len(setts) == 1:
            return setts[0]
        return _sett.Brace(setts)

    @_Armature.prop
    def codomain(self, /):
        return _sett(self.func.__annotations__.get('return', None))

    @_Armature.prop
    def __getitem__(self, /):
        func = self.func
        if len(_inspect.signature(func).parameters) == 1:
            getitem = func
        else:
            getitem = lambda x: func(*x)
        return getitem


class MappOp(Mapp):
    ...


class ModifiedMapp(MappOp, metaclass=_Armature):

    mapp: _Armature.Field.POS[Mapp]
    domain: _Armature.Field[_sett.Sett] = None
    codomain: _Armature.Field[_sett.Sett] = None

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        mapp = params.mapp
        for methname in ('domain', 'codomain'):
            if getattr(params, methname) is None:
                setattr(params, methname, getattr(mapp, methname))
        return params

    def __getitem__(self, arg, /):
        if arg not in self.domain:
            raise MappError
        out = self.mapp[arg]
        assert out in self.codomain
        return out


class MappMultiOp(MappOp, metaclass=_Armature):

    mapps: _Armature.Field.ARGS

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        params.mapps = tuple(map(convert, params.mapps))
        return params


class SwitchMapp(MappMultiOp):

    @_Armature.prop
    def domain(self, /):
        return _sett.union(*(mp.domain for mp in self.mapps))

    @_Armature.prop
    def codomain(self, /):
        return _sett.union(*(mp.codomain for mp in self.mapps))

    def __getitem__(self, arg, /):
        for mapp in self.mapps:
            if arg in mapp.domain:
                return mapp[arg]
        raise MappError(arg)


class BraceSwitchMapp(SwitchMapp):

    @_Armature.prop
    def domain(self, /):
        return _sett.union(*(mp.domain for mp in self.mapps))

    def __getitem__(self, arg, /):
        return self.get_mapp(tuple(map(type, arg)))[arg]


class ComposedMapp(MappMultiOp):

    mapps: _Armature.Field.ARGS

    @_Armature.prop
    def domain(self, /):
        return self.mapps[0].domain

    @_Armature.prop
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
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        params.mapps = cls._unpack_args(params.mapps)
        return params

    def __getitem__(self, arg, /):
        for mapp in self.mapps:
            arg = mapp[arg]
        return arg


class _MappModuleMate_(_ModuleMate):

    def __call__(self, arg, /):
        if arg is self:
            arg = Mapp
        return convert(arg)

    def __instancecheck__(self, arg, /):
        return isinstance(arg, Mapp)

    def __subclasscheck__(self, arg, /):
        return issubclass(arg, Mapp)


_MappModuleMate_(__name__)


###############################################################################
###############################################################################


# class SwitchMapp(MappMultiOp):

#     @classmethod
#     def instantiate(cls, params, /):
#         if cls is SwitchMapp:
#             isbrace = tuple(
#                 isinstance(mp.domain, _sett.Brace)
#                 for mp in params.mapps
#                 )
#             if any(isbrace):
#                 if all(isbrace):
#                     return BraceSwitchMapp.instantiate(params)
#                 raise TypeError(
#                     "Cannot mix bracelike and non-bracelike mapps "
#                     "in a single SwitchMapp."
#                     )
#         return super().instantiate(params)

#     @_Armature.prop
#     def domain(self, /):
#         return _sett.union(*(mp.domain for mp in self.mapps))

#     @_Armature.prop
#     def codomain(self, /):
#         return _sett.union(*(mp.codomain for mp in self.mapps))

#     @_Armature.prop
#     def get_mapp(self, /):
#         checkmapps = tuple(
#             (mapp.signaltype, mapp) for mapp in self.mapps
#             )
#         @_functools.lru_cache
#         def _func_(arg: type, /):
#             for typ, mapp in checkmapps:
#                 if issubclass(arg, typ):
#                     return mapp
#             raise MappError(arg)
#         return _func_

#     def __getitem__(self, arg, /):
#         return self.get_mapp(type(arg))[arg]


# class BraceSwitchMapp(SwitchMapp):

#     @_Armature.prop
#     def domain(self, /):
#         return _sett.union(*(mp.domain for mp in self.mapps))

#     def __getitem__(self, arg, /):
#         return self.get_mapp(tuple(map(type, arg)))[arg]
