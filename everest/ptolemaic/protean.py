###############################################################################
''''''
###############################################################################


import itertools as _itertools
import weakref as _weakref
import types as _types

from everest.utilities import pretty as _pretty
from everest.ur import Var as _Var

from everest.ptolemaic.ousia import Ousia as _Ousia


class Protean(_Ousia):

    ...


@_Var.register
class ProteanBase(metaclass=Protean):

    _req_slots__ = ('basis',)

    @classmethod
    def __class_call__(cls, basis: object, /):
        obj = object.__new__(cls.Concrete)
        obj.basis = basis
        obj.__init__()
        obj.freezeattr.toggle(True)
        return obj
       
    ### Representations:

    def _content_repr(self, /):
        return repr(self.basis)

    def _repr_pretty_base(self, p, cycle, /):
        _pretty.pretty_tuple((self.basis,), p, cycle, root=self.rootrepr)

    def _repr_pretty_(self, p, cycle):
        self._repr_pretty_base(p, cycle)
        if self._var_slots__:
            try:
                kwargs = self.varvals
            except ValueError:
                p.text(root + '(Null)')
            else:
                _pretty.pretty_kwargs(kwargs, p, cycle)


###############################################################################
###############################################################################
