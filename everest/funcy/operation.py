################################################################################
from functools import partial

from .derived import Derived
from .group import Group
from .utilities import kwargstr

class Operation(Derived):
    __slots__ = ('opkwargs', 'opfn')

    def __init__(self,
            *terms,
            op = None,
            **kwargs,
            ):
        terms = (self._process_term(t) for t in terms)
        self.opfn = partial(op, **kwargs)
        self.opfn.__name__ = op.__name__
        self.opkwargs = kwargs
        super().__init__(*terms, op = op, **kwargs)
    @staticmethod
    def _process_term(term):
        if type(term) is tuple:
            return Group(*term)
        else:
            return term

    def evaluate(self):
        return self.opfn(*self._resolve_terms())

    def _titlestr(self):
        return self.opfn.__name__
    def _kwargstr(self):
        kwargs = self.kwargs.copy()
        del kwargs['op']
        if kwargs:
            return utilities.kwargstr(**kwargs)
        else:
            return ''

#         if type(op) is tuple:
#             sops, op = op[:-1], op[-1]
#             for sop in sops:
#                 terms = Operation(*terms, op = sop)
#                 if not type(terms) is tuple:
#                     terms = terms,
################################################################################
