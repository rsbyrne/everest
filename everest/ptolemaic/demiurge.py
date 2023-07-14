###############################################################################
''''''
###############################################################################


import abc as _abc
from types import SimpleNamespace as _Ns

from .classbody import MROClassHelper as _MROClassHelper
from .wisp import Partial as _Partial, convert as _conv
from .tekton import Tekton as _Tekton
from . import ptolemaic as _ptolemaic


class DemiclassHelper(_MROClassHelper):

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.body.awaiting_mroclass_names.append('._DemiBase_')


@_ptolemaic.Kind.register
class Demiurge(_Tekton):

    @classmethod
    def _yield_bodymeths(meta, body, /):
        yield from super()._yield_bodymeths(body)
        yield 'demiclass', property(DemiclassHelper)

    def __call__(cls, arg0=NotImplemented, /, *argn, **kwargs):
        if arg0 is not NotImplemented:
            if not argn:
                if not kwargs:
                    try:
                        return cls.demiconvert(arg0)
                    except ValueError:
                        pass
        return super().__call__(arg0, *argn, **kwargs)


class _DemiurgeBase_(metaclass=Demiurge):

    cacheable = True

    @classmethod
    def _get_returnanno(cls, /):
        return cls

    @classmethod
    @_abc.abstractmethod
    def _dispatch_(cls, params, /) -> _Partial:
        raise NotImplementedError

    @classmethod
    def _construct_(cls, params, /):
        kls, klsargs, klskwargs = cls._dispatch_(params)
        return kls._construct_(kls._parameterise_(*klsargs, **klskwargs))

    @classmethod
    def _instantiate_(cls, params, /):
        kls, klsargs, klskwargs = cls._dispatch_(params)
        return kls._instantiate_(kls._parameterise_(*klsargs, **klskwargs))

    @classmethod
    def __class_alt_call__(cls, /, *args, **kwargs):
        return cls._instantiate_(cls._parameterise_(*args, **kwargs))

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
        cls._demiclasses_ = cls.convert(tuple(cls._DemiBase_.__subclasses__()))


    class _DemiBase_(mroclass, metaclass=_Tekton):

        ...


###############################################################################
###############################################################################
