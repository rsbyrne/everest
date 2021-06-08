###############################################################################
''''''
###############################################################################

from . import _Datalike, _ur

_Var = _ur.Var


def check_ur(objs, ur):
    return any(isinstance(obj, ur) for obj in objs)


class Functional(_Datalike):


    @classmethod
    def _choose_ur_class(cls, *args, **kwargs) -> _ur.Ur:
        inps = tuple((*args, *kwargs.values()))
        for ur in (cls.Inc, cls.Var, cls.Seq, cls.Dat):
            if check_ur(inps, ur.UrBase):
                return ur
        return cls.Non


    __slots__ = ('terms',)

    def __init__(self, *terms, **kwargs):
        self.terms = terms
        self.register_argskwargs(*terms) # pylint: disable=E1101
        super().__init__(**kwargs)


    class Var:

        @property
        def termsresolved(self):
            return (
                term.value if isinstance(term, _Var) else term
                    for term in self.terms # pylint: disable=E1101
                )


###############################################################################
###############################################################################
