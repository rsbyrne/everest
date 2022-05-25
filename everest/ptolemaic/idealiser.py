###############################################################################
''''''
###############################################################################


from .essence import Essence as _Essence
from .tekton import Tekton as _Tekton


class Idealiser(_Tekton):
    ...


class IdealiserBase(metaclass=Idealiser):

    MROCLASSES = ('Ideal',)

    class Ideal(metaclass=_Essence):
        ...

    @classmethod
    def construct(cls, params, /):
        epitaph = cls.construct_epitaph(params)
        return type(
            epitaph.hashID,
            (cls.Ideal,),
            dict(params=params, _epitaph=epitaph, **params._asdict()),
            )


###############################################################################
###############################################################################
