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

        SUBCLASSES = ('UpperBound', 'LowerBound', 'DoubleBound')

        @classmethod
        def __mroclass_init__(cls, /):
            for attr in ('pytyp', 'nptyp', 'convtyp', 'comptyp'):
                setattr(cls, attr, getattr(cls.owner, attr))
            cls.dtype = cls.convtyp
            super().__mroclass_init__()


        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            cls.UnBound = cls.Space


        class Brace(metaclass=_Essence):


            class Oid(metaclass=_Essence):

                @classmethod
                def __mroclass_init__(cls, /):  # vvv UGLY!
                    try:
                        for attr in ('pytyp', 'nptyp', 'convtyp', 'comptyp'):
                            setattr(cls, attr, getattr(cls.owner, attr))
                        cls.dtype = cls.convtyp
                    except AttributeError:
                        pass
                    super().__mroclass_init__()


        class Space(metaclass=_Essence):


            class __choret__(_Sampleable):

                def retrieve_iscomparable(self, incisor: 'owner.comptyp', /):
                    return self._ptolemaic_class__.owner.convtyp(incisor)

                def bounds_slyce_lower(self,
                        incisor: ('owner.comptyp', type(None)), /
                        ):
                    return self.bound.LowerBound(incisor.lower)

                def bounds_slyce_upper(self,
                        incisor: (type(None), 'owner.comptyp'), /
                        ):
                    return self.bound.UpperBound(incisor.upper)

                def bounds_slyce_double(self,
                        incisor: ('owner.comptyp', 'owner.comptyp'), /
                        ):
                    lower, upper = incisor.lower, incisor.upper
                    if upper <= lower:
                        return self.bound._ptolemaic_class__.owner.Empty
                    return self.bound.DoubleBound(lower, upper)

        # class Brace(metaclass=_Essence):


###############################################################################
###############################################################################
