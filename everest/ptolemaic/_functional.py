###############################################################################
''''''
###############################################################################


import abc as _abc

from .compound import Compound as _Compound
from .ousia import Tuuple as _Tuuple


class Functional(_Compound):
    ...


class FunctionalBase(metaclass=Functional):

    @_abc.abstractmethod
    def __call__(self, /):
        raise NotImplementedError


class Tuupleator(FunctionalBase):

    __req_slots__ = ('_call_meth',)

    n: (int, None) = None

    def __init__(self, /):
        n = self.n
        if n is None:
            _call_meth = self._none_call
        else:
            argstrn = ', '.join(f"arg{i}" for i in range(n))
            exec('\n'.join((
                f"",
                f"def call_meth(self, {argstrn}, /):",
                f"    return _Tuuple(({argstrn}))",
                )))
            _call_meth = eval('call_meth').__get__(self)
        self._call_meth = _call_meth

    def _none_call(self, /, *args):
        return _Tuuple(args)

    @property
    def __call__(self, /):
        return self._call_meth


###############################################################################
###############################################################################
