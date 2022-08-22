###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import itertools as _itertools
import inspect as _inspect
import types as _types
from collections import abc as _collabc

from ..utilities import pretty as _pretty

from ..ptolemaic.ousia import Ousia as _Ousia
from ..ptolemaic.sprite import Sprite as _Sprite
from ..ptolemaic.system import System as _System
from ..ptolemaic.stele import Stele as _Stele_

from . import sett as _sett


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
    if arg is Ellipsis:
        return CallMapp(_sett._Any_)
    # if not isinstance(arg, type):
    #     if hasattr(arg, '__mapp_convert__'):
    #         return arg.__mapp_convert__()
    if isinstance(arg, Mapp):
        return arg
    if isinstance(arg, _collabc.Mapping):
        return ArbitraryMapp(arg)
    if isinstance(arg, _collabc.Iterable):
        arg = tuple(arg)
        if len(arg) == 1:
            return convert(arg[0])
        return SwitchMapp(*arg)
    if isinstance(arg, _collabc.Callable):
        if isinstance(arg, _types.MethodType):
            if arg.__name__ == '__getitem__':
                slf = arg.__self__
                if isinstance(slf, Mapp):
                    return slf
        return CallMapp(arg)
    raise TypeError(type(arg))


class Mapp(metaclass=_Ousia):

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

    def compose(self, other, /):
        return MappComposition(other, self)

    def __matmul__(self, arg, /):
        return self.compose(arg)

    def __rmatmul__(self, arg, /):
        return self.__ptolemaic_class__.compose(arg, self)

    def extend(self, arg, /):
        return MappUnion(self, arg)

    def subtend(self, arg, /):
        raise NotImplementedError

    convert = staticmethod(convert)


class RetrieveMapp(Mapp, metaclass=_System):

    codomain: _sett.Sett

    @prop
    def domain(self, /):
        return self.codomain

    def __getitem__(self, arg, /):
        if arg in self.domain:
            return arg
        raise MappError(arg)


class CheckMapp(Mapp, metaclass=_System):

    sett: _sett.Sett

    domain = _sett.UNIVERSE
    codomain = _sett(bool)

    def __getitem__(self, arg, /):
        return arg in self.sett


class CallMapp(Mapp, metaclass=_System):

    func: _collabc.Callable

    @prop
    def setts(self, /):
        return tuple(
            _sett(pm.annotation)
            for pm in _inspect.signature(self.func).parameters.values()
            if pm.kind.value < 2
            )

    @prop
    def arity(self, /):
        return len(self.setts)

    @prop
    def domain(self, /):
        setts = self.setts
        if len(setts) == 1:
            return setts[0]
        return _sett.SettBrace(*setts)

    @prop
    def codomain(self, /):
        return _sett(self.func.__annotations__.get('return', ...))

    @prop
    def _getitem_(self, /):
        func = self.func
        if self.arity == 1:
            return func
        return lambda x: func(*x)

    def __getitem__(self, arg, /):
        return self._getitem_(arg)


class SuperMapp(Mapp):

    @_abc.abstractmethod
    def subtend(self, arg, /):
        raise NotImplementedError


@_collabc.Mapping.register
class ArbitraryMapp(SuperMapp, metaclass=_System):

    mapping: _collabc.Mapping

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        return super()._parameterise_(dict(*args, **kwargs))

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

    def __getitem__(self, arg, /):
        return self.mapping[arg]

    @prop
    def domain(self, /):
        return _sett(tuple(self.mapping))

    @prop
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
    def _parameterise_(cls, /, *args, **kwargs):
        params.mapp = cls.convert(params.mapp)
        return params

    def __getitem__(self, arg, /):
        out = self.mapp[arg]
        assert out in self.codomain
        return out


class MappMultiOp(MappOp):

    ...


class MappEnnaryOp(MappMultiOp, metaclass=_System):

    args: ARGS

    @classmethod
    def _unpack_args(cls, args, /):
        for arg in args:
            if isinstance(arg, cls):
                yield from arg.args
            else:
                yield cls.convert(arg)

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        params.args = tuple(cls._unpack_args(params.args))
        return params

    def subtend(self, arg, /):
        return self.__ptolemaic_class__(*(arg @ sub for sub in arg))


class ElasticMapp(MappEnnaryOp):

    def extend(self, arg, /):
        return self.__ptolemaic_class__(self, arg)


class MappUnion(ElasticMapp):

    def __getitem__(self, arg, /):
        for mapp in self.args:
            try:
                return mapp[arg]
            except MappError:
                continue
        raise MappError(arg)

    @prop
    def domain(self, /):
        return _sett.union(arg.domain for arg in self.args)

    @prop
    def codomain(self, /):
        return _sett.union(arg.codomain for arg in self.args)


class SwitchMapp(ElasticMapp):

    @prop
    def typemapp(self, /):
        return TypeMapp(
            (mp.domain.signaltype, mp) for mp in self.args
            )

    @prop
    def domain(self, /):
        return _sett.union(*(mp.domain for mp in self.args))

    @prop
    def codomain(self, /):
        return _sett.union(*(mp.codomain for mp in self.args))

    def __getitem__(self, arg, /):
        return self.typemapp[type(arg)][arg]

    def subtend(self, arg, /):
        if isinstance(arg, SwitchMapp):
            arg = arg.typemapp
        return self.__ptolemaic_class__(*self.typemapp.subtend(arg).values())


class MappComposition(MappEnnaryOp, metaclass=_System):

    @prop
    def domain(self, /):
        return self.args[0].domain

    @prop
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
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        pre = params.pre = cls.convert(params.pre)
        post = params.post = cls.convert(params.post)
        if not isinstance(pre, ElasticMapp):
            raise ValueError(pre)
        return params

    def __getitem__(self, arg, /):
        arg = self.pre[arg]
        return self.post[arg.envelope][arg.content]

    def subtend(self, arg, /):
        if not isinstance(arg, StyleMapp):
            raise TypeError(
                ("You can only subtend a StyleMapp "
                "with another StyleMapp:"),
                type(arg),
                )
        return self.__ptolemaic_class__(
            self.pre.extend(arg.pre),
            self.post.subtend(arg.post),
            )

    @prop
    def domain(self, /):
        return self.pre.domain

    @prop
    def codomain(self, /):
        return self.post.domain


_Stele_.complete()


###############################################################################
###############################################################################


    # def __get_signature__(self, /) -> _inspect.Signature:
    #     return _inspect.Signature(
    #         (_inspect.Parameter(
    #             'arg', _inspect.Parameter.POSITIONAL_ONLY,
    #             annotation=self.domain,
    #             ),),
    #         return_annotation=self.codomain,
    #         )

    # @_abc.abstractmethod
    # def __call__(self, /, *_, **__):
    #     raise NotImplementedError
