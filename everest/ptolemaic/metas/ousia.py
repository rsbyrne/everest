###############################################################################
''''''
###############################################################################


import weakref as _weakref

from everest.ptolemaic.metas.essence import Essence as _Essence


class Ousia(_Essence):
    '''
    The metaclass of all Ptolemaic types that can be instantiated,
    pure instances of itself are types that can be instantiated
    but cannot accept arguments.
    '''

    _ptolemaic_mergetuples__ = (
        '_req_slots__',
        '_ptolemaic_mroclasses__',
        '_ptolemaic_concretebases__',
        )
    _req_slots__ = ('_softcache', '_weakcache', '__weakref__')
    _ptolemaic_mroclasses__ = ()
    _ptolemaic_concretebases__ = ()

    class ConcreteMetaBase(type):

        @property
        def isconcrete(cls, /):
            return True

        def __new__(meta, basecls, /):
            if not isinstance(basecls, type):
                raise TypeError(
                    "ConcreteMeta only accepts one argument:"
                    " the class to be concreted."
                    )
            if isinstance(basecls, basecls.ConcreteMetaBase):
                raise TypeError("Cannot subclass a Concrete type.")
            return super().__new__(
                meta,
                f"{basecls.__name__}_Concrete",
                (basecls, *basecls._ptolemaic_concretebases__),
                basecls._ptolemaic_concrete_namespace__(),
                )

        def construct(cls, /, *args, **kwargs):
            return cls.basecls.construct(*args, **kwargs)

        @property
        def __signature__(cls, /):
            return cls.basecls.__signature__

        def __init__(cls, /, *args, **kwargs):
            type.__init__(cls, *args, **kwargs)

        def __class_repr__(cls, /):
            return repr(cls.basecls)

    @classmethod
    def _pleroma_init__(meta, /):
        super()._pleroma_init__()
        if not issubclass(meta, meta.ConcreteMetaBase):
            meta.ConcreteMeta = type(
                f"{meta.__name__}_ConcreteMeta",
                (meta.ConcreteMetaBase, meta),
                dict(metabasecls=meta),
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

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._add_mroclasses()
        cls.Concrete = type(cls).ConcreteMeta(cls)

    def create_object(cls, /, **kwargs):
        obj = object.__new__(cls.Concrete)
        obj._softcache = dict()
        obj._weakcache = _weakref.WeakValueDictionary()
        for key, val in kwargs.items():
            setattr(obj, key, val)
        return obj

    def construct(cls, /):
        obj = cls.create_object()
        obj.__init__()
        return obj


###############################################################################
###############################################################################
