###############################################################################
''''''
###############################################################################


import functools as _functools
import weakref as _weakref
import abc as _abc
import inspect as _inspect
import itertools as _itertools

from everest.utilities import caching as _caching, word as _word

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

    ### Defining the parent class of all Ousia instance instances:

    class ConcreteMetaBase(type):
        '''
        The metaclass of all concrete subclasses of Ousia instances.
        '''

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
                f"Concrete{basecls.__name__}",
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

        ### Legibility and serialisation for classes:

        def get_classproxy(cls, /):
            return cls.basecls.get_classproxy()

        @property
        def _ptolemaic_class__(cls, /):
            return cls.basecls

#         def __repr__(cls, /):
#             return repr(cls.basecls)

    ### Implementing the class concretion mechanism:

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

    ### Defining the mandatory basetype for instances of this metaclass:

    @classmethod
    def _get_basetyp(meta, /):
        try:
            return Sprite
        except NameError:
            return super()._get_basetyp()

    ### Setting some class properties that wrap baseclass methods:

    @property
    def __signature__(cls, /):
        return cls.get_signature()

    @property
    def registrar(cls, /):
        return cls.Registrar(cls)

    ### Methods relating to Unidex and class legibility:

    def reconstruct(cls, inputs, /):
        args, kwargs = inputs
        return cls(*args, **kwargs)


class Registrar(_exceptions.ParameterisationException):
    '''
    Handles parameterisation and type checking
    on behalf of its outer class.
    '''

    __slots__ = ('known', 'args', 'kwargs', 'bads')

    def __init__(self, owner, /):
        super().__init__(owner)
        self.known = owner._ptolemaic_knowntypes__
        self.args, self.kwargs = [], {}

    ### Basic functionality to check and process parameters:

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

    ### Defining how the Registrar performs its final type checks:

    def check(self, /):
        vals = _itertools.chain(self.args, self.kwargs.values())
        bads = tuple(_itertools.filterfalse(self.recognised, vals))
        if bads:
            self.bads = bads
            raise self

    def message(self, /):
        yield from super().message()
        yield "when one or more objects of unrecognised type"
        yield "were passed as parameters:"
        for param in self.bads:
            yield f"{repr(param)}, {repr(type(param))}"
        yield 'Note that the class only accepts parameters'
        yield 'that are instances of one or more of the following:'
        yield from map(repr, self.raisedby._ptolemaic_knowntypes__)

    ### Basic object legibility:

    def __repr__(self, /):
        argtup = ', '.join(map(repr, self.args))
        kwargtup = ', '.join(
            f"{key}: {repr(val)}"
            for key, val in self.kwargs.items()
            )
        return f"{self.basecls.__name__}(*({argtup}), **{{{kwargtup}}})"


class Sprite(metaclass=Ousia):
    '''
    The basetype of all Ousia instances.
    '''

    __slots__ = ()

    _ptolemaic_mergetuples__ = (
        '_req_slots__',
        '_ptolemaic_knowntypes__',
        )
    _req_slots__ = (
        '_softcache', '_weakcache', '__weakref__', '_argskwargs'
        )
    _ptolemaic_knowntypes__ = (_Primitive,)
    _ptolemaic_mroclasses__ = ('ConcreteBase', 'Registrar')

    class ConcreteBase(_abc.ABC):
        '''The base class for this class's `Concrete` subclass.'''

    ### Implementing bespoke class instantiation protocol:

    @classmethod
    def get_signature(cls, /):
        return (
            (sig := _inspect.signature(cls.__init__))
            .replace(
                parameters=tuple(sig.parameters.values())[1:],
                return_annotation=cls,
                )
            )

    ### Defining the Registrar, which handles parameterisation:

    Registrar = Registrar

    ### What actually happens when the class is called:

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

    ### Methods relating to class legibility and serialisation:

    @property
    def argskwargs(self, /):
        return self._argskwargs

    def get_unreduce_args(self, /):
        yield from super().get_unreduce_args()
        yield self.argskwargs

    @classmethod
    def _ptolemaic_isinstance__(cls, arg, /):
        return issubclass(type(arg), cls)

    def __reduce__(self, /):
        return master_unreduce, tuple(self.get_unreduce_args())

    def _repr(self, /):
        args, kwargs = self.argskwargs
        return ', '.join(_itertools.chain(
            map(repr, args),
            map('='.join, zip(kwargs, map(repr, kwargs.values()))),
            ))

    @_caching.soft_cache()
    def __repr__(self, /):
        content = f"({rep})" if (rep := self._repr()) else ''
        return f"<{repr(type(self))}{content}>"

    def _get_hashcode(self):
        content = self.__repr__().encode()
        return _hashlib.md5(content).hexdigest()

    @property
    @_caching.soft_cache()
    def hashcode(self):
        return self._get_hashcode()

    @property
    @_caching.soft_cache()
    def hashint(self):
        return int(self.hashcode, 16)

    @property
    @_caching.soft_cache()
    def hashID(self):
        return _word.get_random_english(seed=self.hashint, n=2)


###############################################################################
###############################################################################
