###############################################################################
''''''
###############################################################################


import weakref as _weakref
import inspect as _inspect


from .primitive import Primitive as _Primitive
from .essence import Essence as _Essence


class _ConcreteMetaBase(_Essence):

    @property
    def isconcrete(cls, /):
        return True

    def __new__(meta, basecls, /):
        if not isinstance(basecls, type):
            raise TypeError(
                "ConcreteMeta only accepts one argument:"
                " the class to be concreted."
                )
        if isinstance(basecls, _ConcreteMetaBase):
            raise TypeError("Cannot subclass a Concrete type.")
        return super().__new__(
            meta,
            f"{basecls.__name__}_Concrete",
            (basecls,),
            basecls._ptolemaic_concrete_namespace__(),
            )

    def subclass(cls, /, *args, **kwargs):
        return cls.basecls(*args, **kwargs)

    def construct(cls, /, *args, **kwargs):
        return cls.basecls.construct(*args, **kwargs)

    def _ptolemaic_signature__(cls, /):
        return cls.basecls.__signature__

    def __class_init__(cls, /):
        pass


class Ousia(_Essence):
#     '''
#     The deepest metaclass of the Ptolemaic system.
#     '''

    _ptolemaic_mergetuples__ = (
        '_req_slots__',
        '_ptolemaic_mroclasses__',
        '_ptolemaic_subclasses__',
        '_ptolemaic_fixedsubclasses__',
        )
    _req_slots__ = ('_softcache', '_weakcache', '__weakref__')
    _ptolemaic_mroclasses__ = tuple()
    _ptolemaic_subclasses__ = tuple()
    _ptolemaic_fixedsubclasses__ = tuple()

    @property
    def isconcrete(cls, /):
        return False

    @classmethod
    def _concretemeta_namespace(meta, /):
        return dict(metabasecls=meta)

    @classmethod
    def __meta_init__(meta, /):
        super().__meta_init__()
        if not issubclass(meta, _ConcreteMetaBase):
            meta._ConcreteMeta = type(
                f"{meta.__name__}_ConcreteMeta",
                (_ConcreteMetaBase, meta),
                meta._concretemeta_namespace(),
                )

    def _ptolemaic_concrete_namespace__(cls, /):
        return dict(
            basecls=cls,
            __slots__=cls._req_slots__,
            )

    def _add_mroclass(cls, name: str, /):
        adjname = f'_mroclassbase_{name}__'
        fusename = f'_mroclassfused_{name}__'
        if name in cls.__dict__:
            setattr(cls, adjname, cls.__dict__[name])
        inhclasses = []
        for mcls in cls.__mro__:
            if adjname in mcls.__dict__:
                inhcls = mcls.__dict__[adjname]
                if not inhcls in inhclasses:
                    inhclasses.append(inhcls)
        inhclasses = tuple(inhclasses)
        mroclass = type(name, inhclasses, {})
        setattr(cls, fusename, mroclass)
        setattr(cls, name, mroclass)

    def _add_mroclasses(cls, /):
        for name in cls._ptolemaic_mroclasses__:
            cls._add_mroclass(name)

    def _add_subclass(cls, name: str, /):
        adjname = f'_subclassbase_{name}__'
        fusename = f'_subclassfused_{name}__'
        if not hasattr(cls, adjname):
            if hasattr(cls, name):
                setattr(cls, adjname, getattr(cls, name))
            else:
                raise AttributeError(
                    f"No subclass base of name '{name}' or '{adjname}' "
                    "could be found."
                    )
        base = getattr(cls, adjname)
        subcls = type(name, (base, cls, SubClass), {'superclass': cls})
        setattr(cls, fusename, subcls)
        setattr(cls, name, subcls)
        cls._ptolemaic_subclass_classes__.append(subcls)

    def _add_subclasses(cls, /):
        cls._ptolemaic_subclass_classes__ = []
        for name in cls._ptolemaic_subclasses__:
            cls._add_subclass(name)
        attrname = '_ptolemaic_fixedsubclasses__'
        if attrname in cls.__dict__:
            for name in cls.__dict__[attrname]:
                cls._add_subclass(name)
        cls._ptolemaic_subclass_classes__ = tuple(
            cls._ptolemaic_subclass_classes__
            )

    def __class_init__(cls, /):
        super().__class_init__()
        cls._add_mroclasses()
        cls._add_subclasses()
        cls.Concrete = cls._ConcreteMeta(cls)

    def preinitialise(obj, /, *args, **kwargs):
        obj._softcache = dict()
        obj._weakcache = _weakref.WeakValueDictionary()

    def instantiate(cls, /, *args, **kwargs):
        obj = object.__new__(cls.Concrete)
        obj.preinitialise(*
        obj.__init__(*args, **kwargs)
        return obj

    def construct(cls, /, *args, **kwargs):
        return cls.instantiate(*args, **kwargs)


class SubClass(metaclass=Ousia):

    @classmethod
    def _merge_names_all(cls, overname, /, **kwargs):
        cls.metacls._merge_names_all(cls, overname, **kwargs)
        if overname == '_ptolemaic_mergetuples__':
            if (name := cls.__name__) in cls._ptolemaic_subclasses__:
                cls._ptolemaic_subclasses__ = tuple(
                    nm for nm in cls._ptolemaic_subclasses__ if nm != name
                    )


###############################################################################
###############################################################################
