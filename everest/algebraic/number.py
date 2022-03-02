###############################################################################
''''''
###############################################################################


import numbers as _numbers

import numpy as _np

from everest.utilities import pretty as _pretty

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite

from .chora import Sampleable as _Sampleable
from .fundament import Fundament as _Fundament


class Number(_Fundament):


    pytyp = _numbers.Number
    comptyp = _numbers.Number
    nptyp = _np.number

    @classmethod
    def __class_init__(cls, /):
        pytyp, nptyp = cls.pytyp, cls.nptyp
        try:
            nptyp(0)
        except TypeError:
            convtyp = pytyp
        else:
            convtyp = nptyp
        cls.register(convtyp)
        cls.convtyp = convtyp
        super().__class_init__()

    @classmethod
    def __class_call__(cls, arg, /):
        return cls.convtyp(arg)


    class Oid(metaclass=_Essence):

        SUBCLASSES = ('Open', 'Limit', 'Closed')

        @classmethod
        def __mroclass_init__(cls, /):
            for attr in ('pytyp', 'nptyp', 'convtyp', 'comptyp'):
                setattr(cls, attr, getattr(cls.owner, attr))
            super().__mroclass_init__()

        # def __incise_retrieve__(self, incisor, /):
        #     return self._ptolemaic_class__.owner.convtyp(incisor)

        class Space(metaclass=_Essence):

            class __choret__(_Sampleable):

                def retrieve_iscomparable(self, incisor: 'owner.comptyp', /):
                    return self._ptolemaic_class__.owner.convtyp(incisor)

                def bounds_slyce_open(self,
                        incisor: ('owner.comptyp', type(None)), /
                        ):
                    return self.bound.Open(incisor.lower)

                def bounds_slyce_limit(self,
                        incisor: (type(None), 'owner.comptyp'), /
                        ):
                    return self.bound.Limit(incisor.upper)

                def bounds_slyce_closed(self,
                        incisor: ('owner.comptyp', 'owner.comptyp'), /
                        ):
                    lower, upper = incisor.lower, incisor.upper
                    if upper <= lower:
                        return self.bound._ptolemaic_class__.owner.Empty
                    return self.bound.Closed(lower, upper)


###############################################################################
###############################################################################
