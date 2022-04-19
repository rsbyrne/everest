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


    MROCLASSES = ('UpperBound', 'LowerBound', 'DoubleBound')

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
        cls.UnBound = cls.Space

    @classmethod
    def __class_call__(cls, arg, /):
        return cls.convtyp(arg)


    class Oid(metaclass=_Essence):

        @classmethod
        def __class_init__(cls, /):
            if (owner := cls.owner) is not None:
                for attr in ('pytyp', 'nptyp', 'convtyp', 'comptyp'):
                    setattr(cls, attr, getattr(owner, attr))
                cls.dtype = cls.convtyp
                cls.outer = owner
            super().__class_init__()


    class UpperBound(metaclass=_Essence):

        OVERCLASSES = ('Oid',)


    class LowerBound(metaclass=_Essence):

        OVERCLASSES = ('Oid',)


    class DoubleBound(metaclass=_Essence):

        OVERCLASSES = ('Oid',)


    class Space(metaclass=_Essence):

        class __choret__(_Sampleable):

            def retrieve_iscomparable(self, incisor: 'owner.comptyp', /):
                return self.bound.convtyp(incisor)

            def bounds_slyce_lower(self,
                    incisor: ('owner.comptyp', type(None)), /
                    ):
                return self.boundowner.LowerBound(incisor.lower)

            def bounds_slyce_upper(self,
                    incisor: (type(None), 'owner.comptyp'), /
                    ):
                return self.boundowner.UpperBound(incisor.upper)

            def bounds_slyce_double(self,
                    incisor: ('owner.comptyp', 'owner.comptyp'), /
                    ):
                lower, upper = incisor.lower, incisor.upper
                if upper <= lower:
                    return self.bound.Empty
                return self.boundowner.DoubleBound(lower, upper)


#         class Brace(metaclass=_Essence):


#             class Oid(metaclass=_Essence):

#                 @classmethod
#                 def __mroclass_init__(cls, /):  # vvv UGLY!
#                     try:
#                         for attr in ('pytyp', 'nptyp', 'convtyp', 'comptyp'):
#                             setattr(cls, attr, getattr(cls.owner, attr))
#                         cls.dtype = cls.convtyp
#                     except AttributeError:
#                         pass
#                     super().__mroclass_init__()


###############################################################################
###############################################################################
