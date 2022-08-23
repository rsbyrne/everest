###############################################################################
''''''
###############################################################################


from .classbody import MROClassHelper as _MROClassHelper
from .tekton import Tekton as _Tekton
from .system import System as _System


class DemiclassHelper(_MROClassHelper):

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.body.awaiting_mroclass_names.append('._DemiBase_')


class Demiurge(_Tekton):

    @classmethod
    def _yield_bodymeths(meta, body, /):
        yield from super()._yield_bodymeths(body)
        yield 'demiclass', property(DemiclassHelper)


class _DemiurgeBase_(metaclass=Demiurge):


    @classmethod
    def demiconvert(cls, arg, /):
        if isinstance(arg, cls):
            return arg
        for kls in cls.__mro__:
            try:
                meth = kls.__dict__['_demiconvert_']
            except KeyError:
                continue
            out = meth.__func__(cls, arg)
            if out is not NotImplemented:
                return out
        raise ValueError(arg)

    @classmethod
    def _demiconvert_(cls, arg, /):
        return NotImplemented

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        Base = cls._DemiBase_
        assert Base.__corpus__ is cls, (cls, Base, Base.__corpus__)
        cls.register(Base)
        if cls is not __class__:
            for kls in Base.__bases__:
                if issubclass(kls, __class__._DemiBase_):
                    # i.e. the demiurge should be a subclass
                    # of all of its base's bases' demiurges.
                    kls.demiurge.register(cls)
        Base.demiurge = cls


    class _DemiBase_(mroclass, metaclass=_System):

        ...


###############################################################################
###############################################################################
