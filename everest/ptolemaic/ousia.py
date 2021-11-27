###############################################################################
''''''
###############################################################################


import functools as _functools
import weakref as _weakref
import abc as _abc
import inspect as _inspect
import itertools as _itertools

from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic
from everest.ptolemaic.primitive import Primitive as _Primitive
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.abstract import ProxyAbstract as _ProxyAbstract
from everest.ptolemaic import exceptions as _exceptions


def master_unreduce(loadcls, /, **kwargs):
    return _ProxyAbstract.unproxy_arg(loadcls).reconstruct(**kwargs)


class Ousia(_Essence):
    '''
    The metaclass of all ptolemaic types that can be instantiated.
    All instances of `Ousia` types are instances of `Ptolemaic` by definition.
    '''

    @property
    def __call__(cls):
        return cls.construct

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
                (basecls, basecls.ConcreteBase),
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

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.Concrete = type(cls).ConcreteMeta(cls)
        cls.create_object = _functools.partial(cls.__new__, cls.Concrete)

    def reconstruct(cls, inputs, /):
        args, kwargs = inputs
        return cls(*args, **kwargs)

    class BASETYP(_Essence.BASETYP, _Ptolemaic):

        __slots__ = ()

        _ptolemaic_mergetuples__ = (
            '_req_slots__',
            '_ptolemaic_concretebases__',
            '_ptolemaic_knowntypes__',
            )
        _req_slots__ = (
            '_softcache', '_weakcache', '__weakref__', '_argskwargs'
            )
        _ptolemaic_knowntypes__ = ()
        _ptolemaic_mroclasses__ = ('Registrar', 'ConcreteBase')

        @classmethod
        def _ptolemaic_isinstance__(cls, arg, /):
            return issubclass(type(arg), cls)

        class Registrar(_exceptions.ParameterisationException):

            __slots__ = ('known', 'args', 'kwargs', 'bads')

            def __init__(self, owner, /):
                super().__init__(owner)
                self.known = owner._ptolemaic_knowntypes__
                self.args, self.kwargs = [], {}

            def process_param(self, param, /):
                return param

            def recognised(self, param):
                return isinstance(param, self.known)

            def process_params(self, params):
                return (
                    param if self.recognised(param)
                    else self.process_param(param)
                    for param in params
                    )

            def register_args(self, args, /):
                self.args.extend(self.process_params(args))

            def register_kwargs(self, kwargs, /):
                self.kwargs.update(
                    zip(kwargs, self.process_params(kwargs.values()))
                    )

            def __call__(self, /, *args, **kwargs):
                if args:
                    self.register_args(args)
                if kwargs:
                    self.register_kwargs(kwargs)

            def check(self, /):
                vals = _itertools.chain(self.args, self.kwargs.values())
                bads = tuple(_itertools.filterfalse(self.recognised, vals))
                if bads:
                    self.bads = bads
                    raise self

            def __repr__(self, /):
                argtup = ', '.join(map(repr, self.args))
                kwargtup = ', '.join(
                    f"{key}: {repr(val)}"
                    for key, val in self.kwargs.items()
                    )
                return f"{type(self).__name__}(*({argtup}), **{{{kwargtup}}})"

            def message(self, /):
                yield from super().message()
                yield "when one or more objects of unrecognised type"
                yield "were passed as parameters:"
                for param in self.bads:
                    yield f"{repr(param)}, {repr(type(param))}"
                yield 'Note that the class only accepts parameters'
                yield 'that are instances of one or more of the following:'
                yield from map(repr, self.raisedby._ptolemaic_knowntypes__)

            class ConcreteBase(_abc.ABC):
                '''The base class for this class's `Concrete` subclass.'''

        @classmethod
        def get_signature(cls, /):
            return (
                (sig := _inspect.signature(cls.__init__))
                .replace(
                    parameters=tuple(sig.parameters.values())[1:],
                    return_annotation=cls,
                    )
                )

        @classmethod
        def parameterise(cls, register, /, *args, **kwargs):
            register(*args, **kwargs)

        def initialise(self, /, *args, **kwargs):
            self._softcache = dict()
            self._weakcache = _weakref.WeakValueDictionary()
            self._argskwargs = (args, kwargs)
            args, kwargs = _ProxyAbstract.unproxy_argskwargs(args, kwargs)
            self.__init__(*args, **kwargs)

        @classmethod
        def construct(cls, /, *args, **kwargs):
            cls.parameterise(registrar := cls.registrar, *args, **kwargs)
            registrar.check()
            bound = cls.__signature__.bind(*registrar.args, **registrar.kwargs)
            bound.apply_defaults()
            args, kwargs = bound.args, bound.kwargs
            obj = cls.create_object()
            obj.initialise(*args, **kwargs)
            return obj

        @property
        def argskwargs(self, /):
            return self._argskwargs

        def get_unreduce_args(self, /):
            yield from super().get_unreduce_args()
            yield self.argskwargs

        def __reduce__(self, /):
            return master_unreduce, tuple(self.get_unreduce_args())

    @property
    def __signature__(cls, /):
        return cls.get_signature()

    @property
    def registrar(cls, /):
        return cls.Registrar(cls)


###############################################################################
###############################################################################
