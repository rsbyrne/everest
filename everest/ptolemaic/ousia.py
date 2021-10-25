###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
import weakref as _weakref
import inspect as _inspect

from .primitive import Primitive as _Primitive


class _ConcreteMetaBase(_ABCMeta):

    ...


class Ousia(_ABCMeta):
    '''
    The deepest metaclass of the Ptolemaic system.
    '''

    __slots__ = ()

    _req_slots__ = ()
    _ousia_slots__ = '_softcache', '_weakcache', '__weakref__'

    _ousia_concrete__ = False

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

    def _ousia_concrete_namespace__(cls, /):
        slots = tuple(sorted(set((*cls._ousia_slots__, *cls._req_slots__))))
        return dict(
            __slots__=slots,
            _ousia_concrete__=True,
            )

    def _ousia_signature__(cls, /):
        return _inspect.signature(cls.__init__)

    def _ousia_Concrete(cls, /):

        class ConcreteMeta(type(cls), _ConcreteMetaBase):

            def __new__(meta, base, /,):
                name = f"{base.__qualname__}.Concrete"
                namespace = base._ousia_concrete_namespace__()
                bases = (base,)
                return super().__new__(meta, name, bases, namespace, _concrete=True)

            def __init__(cls, /, *args, **kwargs):
                cls.__signature__ = cls.basecls.__signature__
                super().__init__(*args, **kwargs)

            def __call__(cls, /, *args, **kwargs):
                return cls.basecls(*args, **kwargs)

            def subclass(cls, /, *args, **kwargs):
                return cls.basecls(*args, **kwargs)
#                 raise TypeError("Cannot directly call a Concrete class.")

        return ConcreteMeta

    def _class_init__(cls, /, *args, **kwargs):
        cls.__signature__ = cls._ousia_signature__()
        cls.Concrete = cls._ousia_Concrete()(cls)
        cls._cls_inits_()

    def _cls_inits_(cls, /):
        for name in dir(cls):
            if name.startswith('_cls_') and name.endswith('_init_'):
                getattr(cls, name)()

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls._ousia_concrete__:
            return
        cls._class_init__()

    def _ousia_create_object__(cls, /):
        obj = object.__new__(cls.Concrete)
        obj._softcache = dict()
        obj._weakcache = _weakref.WeakValueDictionary()
        return obj

    def construct(cls, /, *args, **kwargs):
        obj = cls._ousia_create_object__()
        obj.__init__(*args, **kwargs)
        return obj

    def __call__(cls, /, *args, **kwargs):
        return cls.construct(*args, **kwargs)

    def _cls_repr(cls, /):
        return super().__repr__()

    def __repr__(cls, /):
        return cls._cls_repr()

    def __contains__(cls, arg, /):
        return cls._class_contains__(arg)

    def _class_contains__(cls, arg, /):
        return isinstance(arg, cls)

    def subclass(cls, /, *bases, name=None, **namespace):
        bases = (*bases, cls)
        if name is None:
            name = '_'.join(map(repr, bases))
        return type(name, bases, namespace)

    def __class_getitem__(cls, arg, /):
        if isinstance(arg, Ousia):
            return arg
        if isinstance(arg, type):
            if issubclass(arg, _Primitive):
                return arg
            return cls.subclass(arg)
        raise TypeError(arg, type(arg))

    def __getitem__(cls, arg, /):
        return cls.__class_getitem__(arg)


class Blank(metaclass=Ousia):
    ...


###############################################################################
###############################################################################
