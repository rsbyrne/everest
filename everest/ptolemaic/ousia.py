###############################################################################
''''''
###############################################################################


import functools as _functools
import weakref as _weakref
import abc as _abc

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.abstract import ProxyAbstract as _ProxyAbstract


def master_unreduce(loadcls, *args):
    return _ProxyAbstract.unproxy_arg(loadcls).reconstruct(*args)


class Ousia(_Essence):
    '''
    The metaclass of all Ptolemaic types that can be instantiated,
    pure instances of itself are types that can be instantiated
    but cannot accept arguments.
    '''

    @property
    def __call__(cls):
        return cls.construct

    def reconstruct(cls, /):
        return cls()

    class BASETYP(_Essence.BASETYP):

        __slots__ = ()

        _ptolemaic_mergetuples__ = (
            '_req_slots__',
            '_ptolemaic_mroclasses__',
            '_ptolemaic_concretebases__',
            )
        _req_slots__ = ('_softcache', '_weakcache', '__weakref__')
        _ptolemaic_mroclasses__ = ()
        _ptolemaic_concretebases__ = ()

        def initialise(self, /, *args, **kwargs):
            self._softcache = dict()
            self._weakcache = _weakref.WeakValueDictionary()
            self.__init__(*args, **kwargs)

        @classmethod
        def construct(cls, /, *args, **kwargs):
            obj = cls.create_object()
            obj.initialise(*args, **kwargs)
            return obj

        def get_unreduce_args(self, /):
            yield type(self).classproxy

        def __reduce__(self, /):
            return master_unreduce, tuple(self.get_unreduce_args())

    class ConcreteMetaBase(type):

        def get_classproxy(cls, /):
            return cls.basecls.get_classproxy()

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
            return _abc.ABCMeta.__new__(
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
            _abc.ABCMeta.__init__(cls, *args, **kwargs)

        def __repr__(cls, /):
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

    def _ptolemaic_concrete_slots__(cls, /):
        return cls._req_slots__

    def _ptolemaic_concrete_namespace__(cls, /):
        return dict(
            basecls=cls,
            __slots__=cls._ptolemaic_concrete_slots__(),
            __class_init__=lambda: None,
            )

    def _add_mroclass(cls, name: str, /):
        adjname = f'_mroclassbase_{name}__'
        fusename = f'_mroclassfused_{name}__'
        if name in cls.__dict__:
            setattr(cls, adjname, cls.__dict__[name])
        inhclasses = []
        for mcls in cls.__mro__:
            searchname = adjname if isinstance(mcls, Ousia) else name
            if searchname in mcls.__dict__:
                inhcls = mcls.__dict__[searchname]
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
        cls.create_object = _functools.partial(cls.__new__, cls.Concrete)


###############################################################################
###############################################################################
