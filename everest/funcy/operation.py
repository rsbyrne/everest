################################################################################

from functools import partial

from .derived import Derived as _Derived
from .utilities import kwargstr

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
            return kwargstr(**kwargs)
        else:
            return ''

#         if type(op) is tuple:
#             sops, op = op[:-1], op[-1]
#             for sop in sops:
#                 terms = Operation(*terms, op = sop)
#                 if not type(terms) is tuple:
#                     terms = terms,
################################################################################
