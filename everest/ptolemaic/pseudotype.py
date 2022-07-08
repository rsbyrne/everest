###############################################################################
''''''
###############################################################################


import weakref as _weakref
import functools as _functools
import abc as _abc

from .essence import Essence as _Essence
from . import ptolemaic as _ptolemaic


class PseudoType(_Essence):

    _maxgenerations_ = 2

    @classmethod
    def __meta_init__(meta, /):
        super().__meta_init__()
        meta._premade = _weakref.WeakValueDictionary()

    @classmethod
    def __meta_getitem__(meta, args: tuple, /):
        args = tuple(args)
        premade = meta._premade
        try:
            return premade[args]
        except KeyError:
            out = meta.__class_construct__(
                meta.__name__,
                (),
                dict(
                    args=_ptolemaic.convert(args),
                    ),
                modname=__name__,
                )
            premade[args] = out
            return out


class _PseudoTypeBase_(metaclass=PseudoType):

    @classmethod
    def _class_make_epitaph_(cls, taph, /):
        return taph.getitem_epitaph(type(cls), tuple(cls.args))

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        try:
            args = getattr(cls, 'args')
        except AttributeError:
            pass
        else:
            cls.__subclasshook__ = classmethod(cls._get_subclasshook(args))

    @classmethod
    @_abc.abstractmethod
    def _get_subclasshook(cls, args, /):
        raise NotImplementedError


class TypeIntersection(PseudoType):

    ...


class _TypeIntersectionBase_(metaclass=TypeIntersection):

    @classmethod
    def _get_subclasshook(cls, args, /):
        @_functools.lru_cache()
        def __subclasshook__(cls, other: type, /):
            for typ in args:
                if not issubclass(other, typ):
                    return False
            return True
        return __subclasshook__


###############################################################################
###############################################################################
