###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools

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

    __req_slots__ = ('_domain', '_codomain')

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        getanno = self.__getitem__.__annotations__
        self._domain = _Sett(getanno.get('arg', None))
        self._codomain = _Sett(getanno.get('return', None))

    @property
    def __getitem__(self, /):
        return self.func

    @property
    def domain(self, /):
        return self._domain

    @property
    def codomain(self, /):
        return self._codomain


class MappOp(Mapp):
    ...


class MappMultiOp(_Compound.BaseTyp, MappOp):

    __req_slots__ = ('_domain', '_codomain')

    mapps: _Field.ARGS

    @property
    def domain(self, /):
        return self._domain

    @property
    def codomain(self, /):
        return self._codomain


class SwitchMapp(MappMultiOp):

    __req_slots__ = ('get_mapper',)

    def __init__(self, /):
        super().__init__()
        mapps = self.mapps
        checkmapps = ((mapp.domain.__contains_like__, mapp) for mapp in mapps)
        @_functools.lru_cache()
        def get_mapper(arg: type, /):
            for check, mapp in checkmapps:
                if check(arg):
                    return mapp
            raise MappError(arg)
        self.get_mapper = get_mapper
        self._domain = _SettUnion(*(mp.domain for mp in mapps))
        self._codomain = _SettUnion(*(mp.codomain for mp in mapps))

    def __getitem__(self, arg, /):
        return self.get_mapper(type(arg))[arg]


# class SwitchMapp(_Compound.BaseTyp, Mapp):

#     __req_slots__ = ('_domain', '_codomain')

#     mapps: _Field.ARGS

#     def __init__(self, /, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self._domain = _SettUnion(*(mp.domain for mp in self.mapps))
#         self._codomain = _SettUnion(*(mp.codomain for mp in self.mapps))

#     def __getitem__(self, arg, /):
#         for mapp in self.mapps:
#             if arg in mapp.domain:
#                 return mapp[arg]
#         raise MappError(arg)


class ComposedMapp(MappMultiOp):

    __req_slots__ = ('_domain', '_codomain')

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

    def __init__(self, /):
        super().__init__()
        mapps = self.mapps
        self._domain = mapps[0].domain
        self._codomain = mapps[-1].codomain

    def __getitem__(self, arg, /):
        for mapp in self.mapps:
            arg = mapp[arg]
        return arg


###############################################################################
###############################################################################
