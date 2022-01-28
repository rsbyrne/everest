###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.utilities import caching as _caching
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    )

from everest.ptolemaic import thing as _thing
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Sampleable as _Sampleable,
    Degenerate as _Degenerate,
    TrivialException as _TrivialException,
    )
from everest.ptolemaic.schema import Schema as _Schema
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic import tuuple as _tuuple


def _nth(iterable, n):
    try:
        return next(_itertools.islice(iterable, n, None))
    except StopIteration:
        raise IndexError(n)


_OPINT = (type(None), float)


class FloattLike(_thing.ThingLike):
    ...


FloattLike.register(float)


class FloattGen(FloattLike, _thing.ThingGen,):
    ...


class FloattVar(FloattLike, _thing.ThingVar):
    _default = 0


class FloattSpace(_thing.ThingSpace):

    MemberType = FloattLike

    __incise_generic__ = property(FloattGen)
    __incise_variable__ = property(FloattVar)

    @property
    def __armature_brace__(self, /):
        return Coord

#     @property
#     def __incise_degenerate__(self, /):
#         return FloattDegenerate


# class FloattDegenerate(FloattSpace, _Degenerate):
#     ...


class _Floatt_(_Chora, FloattSpace, metaclass=_Sprite):

    class __incision_manager__(_Sampleable):

        def retrieve_contains(self, incisor: float, /):
            return incisor

        def bounds_slyce_open(self, incisor: (float, type(None))):
            return FloattOpen(incisor.lower)

        def bounds_slyce_limit(self, incisor: (type(None), float)):
            return FloattLimit(incisor.upper)

        def bounds_slyce_closed(self, incisor: (float, float)):
            lower, upper = incisor.lower, incisor.upper
            if upper <= lower:
                return FloattNull
            return FloattClosed(lower, upper)

    @property
    def __incise_trivial__(self, /):
        return Floatt


@FloattSpace.register
class FloattMeta(_thing.ThingMeta):

    @property
    def __armature_brace__(self, /):
        return Coord


class Floatt(_thing.Thing, metaclass=FloattMeta):

    __class_incision_manager__ = _Floatt_()


class _FloattNull_(FloattSpace, _thing._ThingNull_):

    ...


class FloattNull(Floatt):

    __class_incision_manager__ = _FloattNull_()


class FloattOpen(_Chora, FloattSpace, metaclass=_Schema):

    lower: Floatt

    class __incision_manager__(_Sampleable):

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


class FloattLimit(_Chora, FloattSpace, metaclass=_Schema):

    upper: Floatt

    class __incision_manager__(_Sampleable):

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


class FloattClosed(_Chora, FloattSpace, metaclass=_Schema):

    lower: Floatt
    upper: Floatt

    class __incision_manager__(_Sampleable):

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


class CoordLike(_tuuple.TuupleLike):
    ...


class CoordGen(CoordLike, _tuuple.TuupleGen):
    ...


class CoordVar(CoordLike, _tuuple.TuupleVar):
    ...


class CoordSpace(_tuuple.TuupleSpace):

    contentspace = Floatt

    __incise_generic__ = property(CoordGen)
    __incise_variable__ = property(CoordVar)

    @property
    def SymForm(self, /):
        return SymPlane

    @property
    def AsymForm(self, /):
        return AsymPlane

    @property
    def __incise_retrieve__(self, /):
        return Coord


class SymPlane(CoordSpace, _tuuple.SymBrace):
    ...


class AsymPlane(CoordSpace, _tuuple.AsymBrace):
    ...


class Plane(CoordSpace, _tuuple.Brace):

    chora: _Chora = Floatt


@CoordSpace.register
class CoordMeta(_Sprite, _tuuple.TuupleMeta):

    ...


class Coord(_tuuple.Tuuple, metaclass=CoordMeta):

    __class_incision_manager__ = Plane()

    content: tuple

    @property
    def __getitem__(self, /):
        return self.content.__getitem__

    @property
    def __len__(self, /):
        return self.content.__len__

    @property
    def __contains__(self, /):
        return self.content.__contains__

    @property
    def __iter__(self, /):
        return self.content.__iter__


###############################################################################
###############################################################################
