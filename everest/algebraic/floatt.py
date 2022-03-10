###############################################################################
''''''
###############################################################################


import numbers as _numbers

import numpy as _np

from everest.utilities import (
    RestrictedNamespace as _RestrictedNamespace,
    pretty as _pretty,
    )

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite

from .eidos import Eidos as _Eidos
from .chora import (
    Choric as _Choric,
    Sampleable as _Sampleable,
    TrivialException as _TrivialException,
    )
from .thing import Thing as _Thing
from .number import Number as _Number


def _build_oids(Floatt, ns, /):


    class Open(_Choric, metaclass=_Eidos):

        lower: Floatt

        @classmethod
        def parameterise(cls, /, *args, **kwargs):
            bound = super().parameterise(*args, **kwargs)
            bound.arguments.update({
                key: cls.owner.pytyp(val)
                for key, val in bound.arguments.items()
                })
            return bound

        class __choret__(_Sampleable):

            def retrieve_float(self, incisor: 'owner.comptyp', /):
                if incisor >= 0:
                    return self.bound.lower + incisor
                raise IndexError

            def bounds_slyce_open(self,
                    incisor: ('owner.comptyp', type(None)), /
                    ):
                lower = incisor.lower
                if lower == 0:
                    raise _TrivialException
                elif lower < 0:
                    raise IndexError
                return self.bound._ptolemaic_class__(
                    lower + self.bound.lower,
                    )

            def bounds_slyce_limit(self,
                    incisor: (type(None), 'owner.comptyp'), /
                    ):
                lower = self.bound.lower
                upper = incisor.upper
                if upper <= 0:
                    raise IndexError
                if upper <= lower:
                    return self.bound._ptolemaic_class__.owner.Empty
                return self.bound.Closed(lower, upper)

            def bounds_slyce_closed(self,
                    incisor: ('owner.comptyp', 'owner.comptyp'), /
                    ):
                lower, upper = incisor.lower, incisor.upper
                if upper <= lower:
                    return self.bound._ptolemaic_class__.owner.Empty
                if upper == 0:
                    raise _TrivialException
                if upper < 0:
                    raise IndexError
                oldlower = self.bound.lower
                lower = oldlower + lower
                upper = oldlower + upper
                return self.bound._ptolemaic_class__.Closed(lower, upper)

        def __contains__(self, arg, /):
            if not super().__contains__(arg):
                return False
            return arg >= self.lower

        def __includes__(self, arg, /):
            raise NotImplementedError

        def _repr_pretty_(self, p, cycle, root=None):
            if root is None:
                root = self._ptolemaic_class__.trueowner.__name__
            if cycle:
                p.text(root + '{...}')
                return
            p.text(root)
            p.text('[')
            _pretty.pretty(self.lower, p, cycle)
            p.text('::')
            # _pretty.pretty(self.step, p, cycle)
            p.text(']')


    class Limit(_Choric, metaclass=_Eidos):

        upper: Floatt

        @classmethod
        def parameterise(cls, /, *args, **kwargs):
            bound = super().parameterise(*args, **kwargs)
            bound.arguments.update({
                key: cls.owner.pytyp(val)
                for key, val in bound.arguments.items()
                })
            return bound

        class __choret__(_Sampleable):

            def retrieve_float(self, incisor: 'owner.comptyp', /):
                if incisor < 0:
                    return self.bound.upper + incisor
                raise IndexError

            def bounds_slyce_open(self,
                    incisor: ('owner.comptyp', type(None)), /
                    ):
                lower, upper = incisor.lower, self.bound.upper
                if lower >= 0:
                    raise IndexError
                lower = upper + lower
                return self.bound._ptolemaic_class__.Closed(lower, upper)

            def bounds_slyce_limit(self,
                    incisor: (type(None), 'owner.comptyp'), /
                    ):
                upper = incisor.upper
                if upper >= 0.:
                    raise IndexError
                return self.bound._ptolemaic_class__(self.bound.upper + upper)

            def bounds_slyce_closed(self,
                    incisor: ('owner.comptyp', 'owner.comptyp'), /
                    ):
                lower, upper = incisor.lower, incisor.upper
                if upper >= 0:
                    raise IndexError
                upper = self.bound.upper + upper
                if upper <= lower:
                    return self.bound._ptolemaic_class__.owner.Empty
                return self.bound.Closed(lower, upper)

        def __contains__(self, arg, /):
            if not super().__contains__(arg):
                return False
            return arg < self.upper

        def __includes__(self, arg, /):
            raise NotImplementedError

        def _repr_pretty_(self, p, cycle, root=None):
            if root is None:
                root = self._ptolemaic_class__.trueowner.__name__
            if cycle:
                p.text(root + '{...}')
                return
            p.text(root)
            p.text('[')
            p.text('::')
            _pretty.pretty(self.upper, p, cycle)
            p.text(']')


    class Closed(_Choric, metaclass=_Eidos):

        lower: Floatt
        upper: Floatt

        @classmethod
        def parameterise(cls, /, *args, **kwargs):
            bound = super().parameterise(*args, **kwargs)
            bound.arguments.update({
                key: cls.owner.pytyp(val)
                for key, val in bound.arguments.items()
                })
            return bound

        class __choret__(_Sampleable):

            def retrieve_float(self, incisor: 'owner.comptyp', /):
                if incisor == 0:
                    return self.bound.lower
                if incisor < 0:
                    out = self.bound.upper + incisor
                    if out < self.bound.lower:
                        raise ValueError
                    return out
                out = self.bound.lower + incisor
                if out >= self.bound.upper:
                    raise ValueError
                return out

            def bounds_slyce_open(self,
                    incisor: ('owner.comptyp', type(None)), /
                    ):
                ilower = incisor.lower
                lower, upper = self.bound.lower, self.bound.upper
                if ilower == 0:
                    raise _TrivialException
                if ilower < 0:
                    lower = upper + ilower
                else:
                    lower = lower + ilower
                if upper <= lower:
                    return self.bound._ptolemaic_class__.owner.Empty
                return self.bound._ptolemaic_class__(lower, upper)

            def bounds_slyce_limit(self,
                    incisor: (type(None), 'owner.comptyp'), /
                    ):
                iupper = incisor.upper
                lower, upper = self.bound.lower, self.bound.upper
                if iupper == 0:
                    return self.bound._ptolemaic_class__.owner.Empty
                if iupper < 0:
                    upper = upper + iupper
                else:
                    upper = lower + iupper
                if upper <= lower:
                    return self.bound._ptolemaic_class__.owner.Empty
                return self.bound._ptolemaic_class__(lower, upper)

            def bounds_slyce_closed(self,
                    incisor: ('owner.comptyp', 'owner.comptyp'), /
                    ):
                ilower, iupper = incisor.lower, incisor.upper
                olower, oupper = self.bound.lower, self.bound.upper
                if iupper == 0:
                    return self.bound._ptolemaic_class__.owner.Empty
                if iupper < 0:
                    upper = oupper + iupper
                else:
                    upper = olower + iupper
                if ilower < 0:
                    lower = oupper + ilower
                else:
                    lower = olower + ilower
                if upper <= lower:
                    return self.bound._ptolemaic_class__.owner.Empty
                if (lower, upper) == (olower, oupper):
                    raise _TrivialException
                return self.bound._ptolemaic_class__(lower, upper)

        def _repr_pretty_(self, p, cycle, root=None):
            if root is None:
                root = self._ptolemaic_class__.trueowner.__name__
            if cycle:
                p.text(root + '{...}')
                return
            p.text(root)
            p.text('[')
            _pretty.pretty(self.lower, p, cycle)
            p.text(':')
            _pretty.pretty(self.upper, p, cycle)
            p.text(':')
            # _pretty.pretty(self.step, p, cycle)
            p.text(']')


    ns.update(locals())


class Floatt(_Number, _Thing):


    pytyp = float
    comptyp = _numbers.Real
    nptyp = _np.floating


    class Oid(metaclass=_Essence):

        # class Var(metaclass=_Essence):
        #     _default = 0.

        @classmethod
        def __mroclass_init__(cls, /):
            if cls.overclass is None:
                owner = cls.owner
                ns = _RestrictedNamespace(badvals={owner,})
                _build_oids(owner, ns)
                cls.incorporate_namespace(ns)
            super().__mroclass_init__()


for _num in (16, 32, 64, 128):
    _new = type(
        f"Floatt{_num}",
        (Floatt,),
        dict(nptyp=getattr(_np, f"float{_num}")),
        )
    exec(f"{_new.__name__}=_new")


###############################################################################
###############################################################################
