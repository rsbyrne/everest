###############################################################################
''''''
###############################################################################


import itertools as _itertools
import weakref as _weakref
import types as _types

from everest.utilities import reseed as _reseed, pretty as _pretty
from everest.ur import Var as _Var

from everest.ptolemaic.ousia import Ousia as _Ousia


class Protean(_Ousia):

    def __call__(cls, basis: object, /):
        obj = object.__new__(cls.Concrete)
        obj.basis = basis
        obj.__init__()
        obj.freezeattr.toggle(True)
        return obj


@_Var.register
class ProteanBase(metaclass=Protean):

    MERGETUPLES = ('_var_slots__',)
    _var_slots__ = ()
    _req_slots__ = ('basis',)

    reseed = _reseed.GLOBALRAND

    @property
    def varvals(self, /):
        return _types.MappingProxyType({
            key: getattr(self, key) for key in self._var_slots__
            })
        
    def __setattr__(self, name, value, /):
        if name in self._var_slots__:
            self._alt_setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def __delattr__(self, name, /):
        if name in self._var_slots__:
            self._alt_delattr__(name)
        else:
            super().__delattr__(name)

    ### Representations:

    def _var_reprs(self, /):
        for key in self._var_slots__:
            yield f"{key}={getattr(self, key)}"

    def _repr(self, /):
        return repr(self.basis)

    def _repr_pretty_(self, p, cycle):
        root = ':'.join((
            self._ptolemaic_class__.__name__,
            self.basis.hashID,
            str(id(self)),
            ))
        try:
            kwargs = self.varvals
        except ValueError:
            p.text(root + '(Null)')
        _pretty.pretty_kwargs(kwargs, p, cycle, root=root)


###############################################################################
###############################################################################
