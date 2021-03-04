################################################################################

from functools import partial

from . import _utilities
from .derived import Derived as _Derived

from .exceptions import *

class Operation(_Derived):
    __slots__ = ('opkwargs', 'opfn')

    def __init__(self,
            *terms,
            op = None,
            **kwargs,
            ):
        self.opfn = partial(op, **kwargs)
        self.opfn.__name__ = op.__name__
        self.opkwargs = kwargs
        super().__init__(*terms, op = op, **kwargs)

    def evaluate(self):
        return self.opfn(*self._resolve_terms())

    def _titlestr(self):
        return self.opfn.__name__
    def _kwargstr(self):
        kwargs = self.kwargs.copy()
        del kwargs['op']
        if kwargs:
            return _utilities.kwargstr(**kwargs)
        else:
            return ''

################################################################################
