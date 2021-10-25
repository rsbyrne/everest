###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import inspect as _inspect

from .pleroma import Pleroma as _Pleroma
from .primitive import Primitive as _Primitive


class _ConcreteMetaBase(_abc.ABCMeta, metaclass=_Pleroma):

    ...


class Ousia(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The deepest metaclass of the Ptolemaic system.
    '''

    __slots__ = ()
    _ousia_slots__ = ('_softcache', '_weakcache', '__weakref__')
    _req_slots__ = ()

    _ptolemaic_concrete__ = False

    @classmethod
    def __prepare__(meta, name, bases, /):
        return dict()

    def __new__(meta, name, bases, namespace, /, *, _concrete=False):
        if any(isinstance(base, _ConcreteMetaBase) for base in bases):
            raise TypeError("Cannot subclass a Concrete type.")
        if _concrete:
            return super().__new__(meta, name, bases, namespace)
        namespace['__slots__'] = ()
        namespace['metacls'] = meta
        cls = super().__new__(meta, name, bases, namespace)
        cls.basecls = cls
        return cls

    def _ptolemaic_concrete_namespace__(cls, /):
        slots = tuple(sorted(set((*cls._ousia_slots__, *cls._req_slots__))))
        return dict(
            __slots__=slots,
            _ptolemaic_concrete__=True,
            )

    def _ptolemaic_signature__(cls, /):
        return _inspect.signature(cls.__init__)

    def _ptolemaic_Concrete(cls, /):

        class ConcreteMeta(type(cls), _ConcreteMetaBase):

            def __new__(meta, base, /,):
                name = f"{base.__qualname__}.Concrete"
                namespace = base._ptolemaic_concrete_namespace__()
                bases = (base,)
                return super().__new__(meta, name, bases, namespace, _concrete=True)

            def __init__(cls, /, *args, **kwargs):
                cls.__signature__ = cls.basecls.__signature__
                super().__init__(*args, **kwargs)

            def construct(cls, /, *args, **kwargs):
                return cls.basecls.construct(*args, **kwargs)

            def subclass(cls, /, *args, **kwargs):
                return cls.basecls(*args, **kwargs)
#                 raise TypeError("Cannot directly call a Concrete class.")

        return ConcreteMeta

    def __class_init__(cls, /, *args, **kwargs):
        cls.__signature__ = cls._ptolemaic_signature__()
        cls.Concrete = cls._ptolemaic_Concrete()(cls)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls._ptolemaic_concrete__:
            return
        cls.__class_init__()

    def _ptolemaic_create_object__(cls, /):
        obj = object.__new__(cls.Concrete)
        obj._softcache = dict()
        obj._weakcache = _weakref.WeakValueDictionary()
        return obj

    def construct(cls, /, *args, **kwargs):
        obj = cls._ptolemaic_create_object__()
        obj.__init__(*args, **kwargs)
        return obj

    def __call__(cls, /, *args, **kwargs):
        return cls.construct(*args, **kwargs)

    def _cls_repr(cls, /):
        return super().__repr__()

    def __repr__(cls, /):
        return cls._cls_repr()


###############################################################################
###############################################################################
