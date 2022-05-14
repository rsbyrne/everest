###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools

from everest.utilities.caching import attr_property as _attr_property

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.atlantean import Funcc as _Funcc
from everest.ptolemaic.compound import Compound as _Compound
from everest.ptolemaic.field import Field as _Field

from .sett import Sett as _Sett, SettUnion as _SettUnion


class MappError(RuntimeError):
    ...


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

    @classmethod
    def __class_call__(cls, arg, /):
        if cls is not Mapp:
            raise NotImplementedError
        return DefMapp(arg)

    def __matmul__(self, arg, /):
        if isinstance(arg, Mapp):
            return ComposedMapp(arg, self)
        raise TypeError(type(arg))

    def __rmatmul__(self, arg, /):
        return NotImplemented


class DefMapp(_Funcc, Mapp):

    @property
    def __getitem__(self, /):
        return self.func

    @_attr_property
    def domain(self, /):
        return _Sett(self.__getitem__.__annotations__.get('arg', None))

    @_attr_property
    def codomain(self, /):
        return _Sett(self.__getitem__.__annotations__.get('return', None))


class MappOp(Mapp):

    @property
    def domain(self, /):
        return self._domain

    @property
    def codomain(self, /):
        return self._codomain


class ModifiedMapp(_Compound.Base):

    mapp: _Field.POS[Mapp]
    domain: Field[_Sett] = None
    codomain: Field[_Sett] = None

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


class MappMultiOp(_Compound.BaseTyp, MappOp):

    mapps: _Field.ARGS


class SwitchMapp(MappMultiOp):

    @_attr_property
    def get_mapper(self, /):
        mapps = self.mapps
        checkmapps = ((mapp.domain.__contains_like__, mapp) for mapp in mapps)
        @_functools.lru_cache()
        def _get_mapper(arg: type, /):
            for check, mapp in checkmapps:
                if check(arg):
                    return mapp
            raise MappError(arg)
        return _get_mapper

    def __getitem__(self, arg, /):
        return self.get_mapper(type(arg))[arg]

    @_attr_property
    def domain(self, /):
        return _SettUnion(*(mp.domain for mp in self.mapps))

    @_attr_property
    def codomain(self, /):
        return _SettUnion(*(mp.codomain for mp in self.mapps))


class ComposedMapp(MappMultiOp):

    mapps: _Field.ARGS

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
    def parameterise(cls, /, *args):
        return super().parameterise(*cls._unpack_args(args))

    def __getitem__(self, arg, /):
        for mapp in self.mapps:
            arg = mapp[arg]
        return arg

    @_attr_property
    def domain(self, /):
        return mapps[0].domain

    @_attr_property
    def codomain(self, /):
        return mapps[-1].codomain


###############################################################################
###############################################################################
