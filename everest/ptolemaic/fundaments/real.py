###############################################################################
''''''
###############################################################################


from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite

from everest.ptolemaic.fundaments.fundament import Fundament as _Fundament


class Real(_Fundament):


    # Necessary to straighten out inheritance:
    class Slyce(metaclass=_Essence):
        ...


    class Space(metaclass=_Essence):

        class __choret__(metaclass=_Essence):

            def bounds_slyce_open(self,
                    incisor: ('owner.MemberType', type(None)), /
                    ):
                return self.bound.MemberType.Open(incisor.lower)

            def bounds_slyce_limit(self,
                    incisor: (type(None), 'owner.MemberType'), /
                    ):
                return self.bound.MemberType.Limit(incisor.upper)

            def bounds_slyce_closed(self,
                    incisor: ('owner.MemberType', 'owner.MemberType'), /
                    ):
                lower, upper = incisor.lower, incisor.upper
                if upper <= lower:
                    return self.bound.MemberType.Null
                return self.bound.MemberType.Closed(lower, upper)


    class Brace(metaclass=_Sprite):

        content: tuple = ()

        for name in ('__getitem__', '__len__', '__iter__', '__contains__'):
            exec('\n'.join((
                f'@property',
                f'def {name}(self, /):',
                f'    return self.content.{name}',
                )))
        del name

        __class_incise_retrieve__ = \
            classmethod(_Sprite.BaseTyp.__class_call__.__func__)



###############################################################################
###############################################################################
