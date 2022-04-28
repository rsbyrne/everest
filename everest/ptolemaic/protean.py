###############################################################################
''''''
###############################################################################


import types as _types

from everest.ur import Var as _Var
from everest.exceptions import (
    FrozenAttributesException as _FrozenAttributesException
    )

from .ousia import Ousia as _Ousia
from .sprite import Sprite as _Sprite


class Protean(_Ousia):

    ...


@_Var.register
class ProteanBase(metaclass=Protean):

    BasisType = type(None)

    MERGETUPLES = ('_req_slots__', '_var_slots__',)
    _req_slots__ = ('basis',)
    _var_slots__ = ()

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.varnames = set(cls._var_slots__)

    @classmethod
    def instantiate(cls, varvals, basis=None, /):
        if not isinstance(basis, cls.BasisType):
            raise TypeError(type(basis))
        obj = cls.Concrete()
        obj.basis = basis
        obj.update(varvals)
        cls.__init__(obj)
        return obj

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        varvals = {}
        for key in set(kwargs) & cls.varnames:
            varvals[key] = kwargs.pop(key)
        basis = cls.BasisType(*args, **kwargs)
        return super().__class_call__(varvals, basis)

    def update(self, arg: dict = None, /, **kwargs):
        if arg is None:
            arg = kwargs
        elif kwargs:
            raise ValueError("Cannot update from both arg and kwargs.")
        elif isinstance(arg, tuple):
            for name, arg in zip(self._var_slots__, args):
                object.__setattr__(self, key, val)
            return
        varnames = self.varnames
        if (bad := set(arg).difference(varnames)):
            raise _FrozenAttributesException(bad)
        for key, val in arg.items():
            object.__setattr__(self, key, val)

    def __getattr__(self, name, /):
        try:
            return super().__getattr__(name)
        except AttributeError as exc:
            if name in self._var_slots__:
                return None
            raise

    def __setattr__(self, name, val, /):
        if name in self._var_slots__:
            object.__setattr__(self, name, val)
        else:
            super().__setattr__(name, val)

    def __delattr__(self, name, /):
        if name in self._var_slots__:
            object.__delattr__(self, name)
        else:
            super().__setattr__(name, val)

    @property
    def vardict(self, /):
        return _types.MappingProxyType({
            key: getattr(self, key) for key in self._var_slots__
            })

    @property
    def varvals(self, /):
        return tuple(getattr(self, name) for name in self._var_slots__)

    @property
    def epitaph(self, /):
        ptolcls = self._ptolemaic_class__
        return ptolcls.taphonomy.custom_epitaph(
            '$a.instantiate($b,$c)',
            a=ptolcls, b=self.varvals, c=self.basis,
            )

    def _var_repr(self, /):
        dct = self.vardict
        return ', '.join(map(': '.join, zip(dct, map(str, dct.values()))))

    @property
    def varrepr(self, /):
        return self._var_repr()

    def __str__(self, /):
        return super().__str__() + f"{{{self.varrepr}}}"


###############################################################################
###############################################################################