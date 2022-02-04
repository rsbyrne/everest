###############################################################################
''''''
###############################################################################


from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.eidos import Eidos as _Eidos
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Sampleable as _Sampleable,
    TrivialException as _TrivialException,
    )

from everest.ptolemaic.fundaments.thing import Thing as _Thing
from everest.ptolemaic.fundaments.real import Real as _Real


class Floatt(_Real, _Thing):


    @classmethod
    def __class_init__(cls, /):
        _ = cls.register(float)
        super().__class_init__()


    class Var(metaclass=_Essence):
        _default = 0.


with Floatt.mutable:


    class FloattOpen(_Chora, Floatt.Slyce, metaclass=_Eidos):

        lower: Floatt

        class __choret__(_Sampleable):

            def retrieve_float(self, incisor: float, /):
                if incisor >= 0:
                    return self.bound.lower + incisor
                raise IndexError

            def bounds_slyce_open(self, incisor: (float, type(None)), /):
                lower = incisor.lower
                if lower == 0:
                    raise _TrivialException
                elif lower < 0:
                    raise IndexError
                return self.bound._ptolemaic_class__(
                    lower + self.bound.lower,
                    )

            def bounds_slyce_limit(self, incisor: (type(None), float), /):
                lower = self.bound.lower
                upper = incisor.upper
                if upper <= 0:
                    raise IndexError
                if upper <= lower:
                    return FloattNull
                return FloattClosed(lower, upper)

            def bounds_slyce_closed(self, incisor: (float, float), /):
                lower, upper = incisor.lower, incisor.upper
                if upper <= lower:
                    return FloattNull
                if upper == 0:
                    raise _TrivialException
                if upper < 0:
                    raise IndexError
                oldlower = self.bound.lower
                lower = oldlower + lower
                upper = oldlower + upper
                return FloattClosed(lower, upper)

        def __contains__(self, arg, /):
            if not super().__contains__(arg):
                return False
            return arg >= self.lower

        def __includes__(self, arg, /):
            raise NotImplementedError


    Floatt.Open = FloattOpen


    class FloattLimit(_Chora, Floatt.Slyce, metaclass=_Eidos):

        upper: Floatt

        class __choret__(_Sampleable):

            def retrieve_float(self, incisor: float, /):
                if incisor < 0:
                    return self.bound.upper + incisor
                raise IndexError

            def bounds_slyce_open(self, incisor: (float, type(None)), /):
                lower, upper = incisor.lower, self.bound.upper
                if lower >= 0:
                    raise IndexError
                lower = upper + lower
                return FloattClosed(lower, upper)

            def bounds_slyce_limit(self, incisor: (type(None), float), /):
                upper = incisor.upper
                if upper >= 0.:
                    raise IndexError
                return self.bound._ptolemaic_class__(self.bound.upper + upper)

            def bounds_slyce_closed(self, incisor: (float, float), /):
                lower, upper = incisor.lower, incisor.upper
                if upper >= 0:
                    raise IndexError
                upper = self.bound.upper + upper
                if upper <= lower:
                    return FloattNull
                return FloattClosed(lower, upper)

        def __contains__(self, arg, /):
            if not super().__contains__(arg):
                return False
            return arg < self.upper

        def __includes__(self, arg, /):
            raise NotImplementedError


    Floatt.Limit = FloattLimit


    class FloattClosed(_Chora, Floatt.Slyce, metaclass=_Eidos):

        lower: Floatt
        upper: Floatt

        class __choret__(_Sampleable):

            def retrieve_float(self, incisor: float, /):
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

            def bounds_slyce_open(self, incisor: (float, type(None)), /):
                ilower = incisor.lower
                lower, upper = self.bound.lower, self.bound.upper
                if ilower == 0:
                    raise _TrivialException
                if ilower < 0:
                    lower = upper + ilower
                else:
                    lower = lower + ilower
                if upper <= lower:
                    return FloatNull
                return self.bound._ptolemaic_class__(lower, upper)

            def bounds_slyce_limit(self, incisor: (type(None), float), /):
                iupper = incisor.upper
                lower, upper = self.bound.lower, self.bound.upper
                if iupper == 0:
                    return FloattNull
                if iupper < 0:
                    upper = upper + iupper
                else:
                    upper = lower + iupper
                if upper <= lower:
                    return FloatNull
                return self.bound._ptolemaic_class__(lower, upper)

            def bounds_slyce_closed(self, incisor: (float, float), /):
                ilower, iupper = incisor.lower, incisor.upper
                olower, oupper = self.bound.lower, self.bound.upper
                if iupper == 0:
                    return FloattNull
                if iupper < 0:
                    upper = oupper + iupper
                else:
                    upper = olower + iupper
                if ilower < 0:
                    lower = oupper + ilower
                else:
                    lower = olower + ilower
                if upper <= lower:
                    return FloattNull
                if (lower, upper) == (olower, oupper):
                    raise _TrivialException
                return self.bounds._ptolemaic_class__(lower, upper)


    Floatt.Closed = FloattClosed


###############################################################################
###############################################################################
