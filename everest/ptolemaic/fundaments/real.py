###############################################################################
''''''
###############################################################################


from everest.utilities import pretty as _pretty

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite

from everest.ptolemaic.fundaments.fundament import Fundament as _Fundament


class Real(_Fundament):

    class Oid(metaclass=_Essence):

        SUBCLASSES = ('Open', 'Limit', 'Closed')

        class Space(metaclass=_Essence):

            class __choret__(metaclass=_Essence):

                def bounds_slyce_open(self,
                        incisor: ('owner.owner', type(None)), /
                        ):
                    return self.bound.Open(incisor.lower)

                def bounds_slyce_limit(self,
                        incisor: (type(None), 'owner.owner'), /
                        ):
                    return self.bound.Limit(incisor.upper)

                def bounds_slyce_closed(self,
                        incisor: ('owner.owner', 'owner.owner'), /
                        ):
                    lower, upper = incisor.lower, incisor.upper
                    if upper <= lower:
                        return self.bound._ptolemaic_class__.owner.Empty
                    return self.bound.Closed(lower, upper)


###############################################################################
###############################################################################
