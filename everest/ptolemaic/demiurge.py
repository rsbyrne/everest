###############################################################################
''''''
###############################################################################


from .essence import Essence as _Essence
from .tekton import Tekton as _Tekton


class Demiurge(_Tekton):
    ...


class DemiurgeBase(metaclass=Idealiser):

    MROCLASSES = ('Ideal',)

    class Demiurge(metaclass=_Essence):
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
