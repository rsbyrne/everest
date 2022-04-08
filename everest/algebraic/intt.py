###############################################################################
''''''
###############################################################################


import numbers as _numbers
import itertools as _itertools
import types as _types

import numpy as _np

from everest.utilities import (
    pretty as _pretty,
    caching as _caching,
    )
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    )

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite

from .chora import (
    Choric as _Choric,
    Sampleable as _Sampleable,
    TrivialException as _TrivialException,
    )
from .thing import Thing as _Thing
from .number import Number as _Number
from .index import Index as _Index


def _nth(iterable, n):
    try:
        return next(_itertools.islice(iterable, n, None))
    except StopIteration:
        raise IndexError(n)


class Intt(_Number, _Thing):


    pytyp = int
    comptyp = _numbers.Integral
    nptyp = _np.integer


    class Oid(metaclass=_Essence):

        @_Index.register
        class LowerBound(_Choric, metaclass=_Sprite):

            lower: int
            step: int = 1

            @classmethod
            def parameterise(cls, /, *args, **kwargs):
                bound = super().parameterise(*args, **kwargs)
                bound.arguments.update({
                    key: cls.owner.pytyp(val)
                    for key, val in bound.arguments.items()
                    })
                if bound.arguments['step'] < 1:
                    raise ValueError
                return bound

            class __choret__(_Sampleable):

                def retrieve_int(self, incisor: 'owner.comptyp', /):
                    if incisor >= 0:
                        return _nth(self.bound, incisor)
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
                        self.bound.step,
                        )

                def bounds_slyce_limit(self,
                        incisor: (type(None), 'owner.comptyp'), /
                        ):
                    lower = self.bound.lower
                    upper = incisor.upper
                    if upper == 0:
                        return self.bound._ptolemaic_class__.owner.Empty
                    elif upper < 0:
                        raise IndexError
                    return self.bound.DoubleBound(
                        lower, lower + upper, self.bound.step
                        )

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
                    return self.bound.DoubleBound(
                        lower, upper, self.bound.step
                        )

                def sample_slyce_int(self, incisor: 'owner.comptyp', /):
                    bound = self.bound
                    return bound._ptolemaic_class__(
                        bound.lower, bound.step * incisor
                        )

            def __incise_iter__(self, /):
                return _itertools.count(self.lower, self.step)

            def __incise_contains__(self, arg, /):
                if not super().__contains__(arg):
                    return False
                if arg < self.lower:
                    return False
                return not (arg - self.lower) % self.step

            def __incise_includes__(self, arg, /):
                raise NotImplementedError

            @property
            @_caching.soft_cache()
            def arrayquery(self, /):
                return slice(self.lower, None, self.step)

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
                _pretty.pretty(self.step, p, cycle)
                p.text(']')


        class UpperBound(_Choric, metaclass=_Sprite):

            upper: int

            @classmethod
            def parameterise(cls, /, *args, **kwargs):
                bound = super().parameterise(*args, **kwargs)
                bound.arguments.update({
                    key: cls.owner.pytyp(val)
                    for key, val in bound.arguments.items()
                    })
                return bound

            class __choret__(_Sampleable):

                def retrieve_int(self, incisor: 'owner.comptyp', /):
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
                    return self.bound.DoubleBound(lower, upper)

                def bounds_slyce_limit(self,
                        incisor: (type(None), 'owner.comptyp'), /
                        ):
                    upper = incisor.upper
                    if upper >= 0:
                        raise IndexError
                    return self.bound._ptolemaic_class__(
                        self.bound.upper + upper
                        )

                def bounds_slyce_closed(self,
                        incisor: ('owner.comptyp', 'owner.comptyp'), /
                        ):
                    lower, upper = incisor.lower, incisor.upper
                    if upper >= 0:
                        raise IndexError
                    upper = self.bound.upper + upper
                    if upper <= lower:
                        return self.bound._ptolemaic_class__.owner.Empty
                    return self.bound.DoubleBound(lower, upper)

            def __incise_contains__(self, arg, /):
                if not super().__contains__(arg):
                    return False
                return arg < self.upper

            def __incise_includes__(self, arg, /):
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


        @_Index.register
        class DoubleBound(_Choric, metaclass=_Sprite):

            lower: int
            upper: int
            # step: Intt[1:] = 1
            step: int = 1

            _req_slots__ = ('_rangeobj',)

            @classmethod
            def parameterise(cls, /, *args, **kwargs):
                bound = super().parameterise(*args, **kwargs)
                bound.arguments.update({
                    key: cls.owner.pytyp(val)
                    for key, val in bound.arguments.items()
                    })
                return bound

            def __init__(self, /):
                super().__init__()
                self._rangeobj = range(self.lower, self.upper, self.step)

            @property
            def pytyp(self, /):
                return self.owner.pytyp

            @property
            def nptyp(self, /):
                return self.owner.nptyp

            class __choret__(_Sampleable):

                def retrieve_int(self, incisor: 'owner.comptyp', /):
                    return self.bound._rangeobj[incisor]

                def bounds_handle_any(self,
                        incisor: (
                            (type(None), 'owner.comptyp'),
                            (type(None), 'owner.comptyp')
                            ),
                        /, *, caller
                        ):
                    oldr = self.bound._rangeobj
                    newr = oldr[slice(*incisor)]
                    if len(newr) == 0:
                        return _IncisionProtocol.SLYCE(caller)(
                            self.bound._ptolemaic_class__.owner.Empty
                            )
                    olds = oldr.start, oldr.stop, oldr.step
                    news = newr.start, newr.stop, newr.step
                    if news == olds:
                        return _IncisionProtocol.TRIVIAL(caller)()
                    return _IncisionProtocol.SLYCE(caller)(
                        self.bound._ptolemaic_class__(*news)
                        )

                def sample_slyce_int(self, incisor: 'owner.comptyp', /):
                    bound = self.bound
                    return bound._ptolemaic_class__(
                        bound.lower, bound.upper, bound.step * incisor
                        )

            @_caching.soft_cache()
            def asdict(self, /):
                return _types.MappingProxyType(dict(zip(
                    self, range(len(self))
                    )))

            @property
            def __incise_contains__(self, /):
                return self._rangeobj.__contains__

            def __incise_includes__(self, arg, /):
                raise NotImplementedError

            def __incise_length__(self, /):
                return len(self._rangeobj)

            def __incise_iter__(self, /):
                return iter(self._rangeobj)

            @property
            @_caching.soft_cache()
            def arrayquery(self, /):
                return slice(self.lower, self.upper, self.step)

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
                _pretty.pretty(self.step, p, cycle)
                p.text(']')

            def __array__(self, dtype=None):
                return _np.array(self, dtype=self.nptyp).__array__(dtype)


        class Brace(metaclass=_Essence):

            class Oid(metaclass=_Essence):

                class Form(metaclass=_Essence):

                    class Symmetric(metaclass=_Essence):

                        @property
                        def arrayquery(self, /):
                            return tuple(
                                chora.arrayquery for chora in self.choras
                                )

                    class Asymmetric(metaclass=_Essence):

                        MYATTRIBUTE = 1

                        @property
                        def arrayquery(self, /):
                            return tuple(
                                chora.arrayquery for chora in self.choras
                                )


for _num in (8, 16, 32, 64):
    _new = type(
        f"Intt{_num}",
        (Intt,),
        dict(nptyp=getattr(_np, f"int{_num}")),
        )
    exec(f"{_new.__name__}=_new")


###############################################################################
###############################################################################


# from everest.utilities import (
#     RestrictedNamespace as _RestrictedNamespace,
#     pretty as _pretty,
#     caching as _caching,
#     )

        # @classmethod
        # def __mroclass_init__(cls, /):
        #     if cls.overclass is None:
        #         owner = cls.owner
        #         ns = _RestrictedNamespace(badvals={owner,})
        #         _build_oids(owner, ns)
        #         cls.incorporate_namespace(ns)
        #     super().__mroclass_init__()
