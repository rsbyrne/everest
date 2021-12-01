###############################################################################
''''''
###############################################################################


import functools as _functools
import weakref as _weakref
import abc as _abc
import inspect as _inspect
import itertools as _itertools
import pickle as _pickle

from everest.utilities import caching as _caching
from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.abstract import ProxyAbstract as _ProxyAbstract
from everest.ptolemaic import exceptions as _exceptions


def pass_fn(arg, /):
    return arg


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
                (basecls.ConcreteBase, basecls),
                basecls._ptolemaic_concrete_namespace__(),
                )

        def construct(cls, /, *args, **kwargs):
            return cls.basecls.construct(*args, **kwargs)

        @property
        def __signature__(cls, /):
            return cls.basecls.__signature__

        def __init__(cls, /, *args, **kwargs):
            _abc.ABCMeta.__init__(cls, *args, **kwargs)

        ### Class representations and aliases:

        @property
        def _ptolemaic_class__(cls, /):
            return cls.basecls

        @property
        def epitaph(cls, /):
            return cls._ptolemaic_class__.epitaph

    ### Implementing the class concretion mechanism:

    @classmethod
    def _pleroma_init__(meta, /):
        super()._pleroma_init__()
        meta.premade = _weakref.WeakValueDictionary()
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

    ### Setting some class properties that wrap baseclass methods:

    @property
    def __signature__(cls, /):
        return cls.get_signature()

    @property
    def registrar(cls, /):
        return cls.Registrar(cls)


class Registrar(_exceptions.ParameterisationException):
    '''
    Handles parameterisation and type checking
    on behalf of its outer class.
    '''

    __slots__ = ('args', 'kwargs', 'bads')

    def __init__(self, owner, /):
        super().__init__(owner)
        self.args, self.kwargs, self.bads = [], {}, []

    ### Basic functionality to check and process parameters:

    def process_param(self, param, /):
        return param

    def __call__(self, /, *args, **kwargs):
        self.args.extend(map(self.process_param, args))
        self.kwargs.update(zip(
            kwargs,
            map(self.process_param, kwargs.values())
            ))

    ### Defining how the Registrar performs its final type checks:

    def check(self, /):
        passmetaclass=_abc.ABCMeta

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


# def master_unreduce(loadcls, /, **kwargs):
#     return _ProxyAbstract.unproxy_arg(loadcls).reconstruct(**kwargs)


def yield_args_kwargs(dct):
    '''
    Takes a `dict` representing a set of function args and kwargs
    where the args are represented as numerical kwargs
    and returns the args and kwargs separately.
    '''
    grpby = itertools.groupby(dct, str.isnumeric)
    _, argkeys = next(grpby)
    yield tuple(map(dct.__getitem__, argkeys))
    _, kwargkeys = next(grpby)
    kwargkeys = tuple(kwargkeys)
    yield dict(zip(kwargkeys, map(dct.__getitem__, kwargkeys)))


def master_unreduce(obj, /, *args):
    return obj.revive(*args)


class OusiaBase(metaclass=Ousia):
    '''
    The basetype of all Ousia instances.
    '''

    __slots__ = ()

    _ptolemaic_mergetuples__ = ('_req_slots__',)
    _req_slots__ = (
        '_softcache', '_weakcache', '_epitaph', '_inputs', '__weakref__'
        )
    _ptolemaic_mroclasses__ = ('Registrar', 'ConcreteBase')

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
        args, kwargs = _ProxyAbstract.unproxy_argskwargs(args, kwargs)
        self.__init__(*args, **kwargs)

    @classmethod
    def construct(cls, /, *args, **kwargs):
        cls.parameterise(registrar := cls.registrar, *args, **kwargs)
        registrar.check()
        bound = cls.__signature__.bind(*registrar.args, **registrar.kwargs)
        bound.apply_defaults()
        args, kwargs = bound.args, bound.kwargs
        epitaph = cls.get_instance_epitaph(args, kwargs)
        hashcode, premade = str(epitaph), cls.premade
        if hashcode in premade:
            return premade[hashcode]
        obj = cls.create_object()
        premade[hashcode] = obj
        obj._epitaph = epitaph
        obj._inputs = (args, kwargs)
        obj._softcache = dict()
        obj._weakcache = _weakref.WeakValueDictionary()
        obj.initialise(*args, **kwargs)
        return obj

    @property
    def inputs(self, /):
        return self._inputs

    ### Implementing chora-like behaviour:

    @classmethod
    def _ptolemaic_isinstance__(cls, arg, /):
        return issubclass(type(arg), cls)

    ### Defining special behaviours for the concrete subclass:

    class ConcreteBase(metaclass=_abc.ABCMeta):
        '''The base class for this class's `Concrete` subclass.'''

        __slots__ = ()

        ### Implementing serialisation of instances:

        @property
        @_caching.soft_cache()
        def epitaph(self, /):
            return self._epitaph

        ### Defining some aliases:

        @property
        def _ptolemaic_class__(self, /):
            return self.basecls

        @property
        def metacls(self, /):
            return self._ptolemaic_class__.metacls

        @property
        def taphonomy(self, /):
            return self.metacls.taphonomy

        @property
        def hashcode(self, /):
            return self.epitaph.hashcode

        @property
        def hashint(self, /):
            return self.epitaph.hashint

        @property
        def hashID(self, /):
            return self.epitaph.hashID

    ### Epitaph support:

    @classmethod
    def get_instance_epitaph(cls, args, kwargs, /):
        taph = cls.taphonomy
        return taph.custom_epitaph(
            *taph.posformat_callsig(cls, args, kwargs)
            )

    ### Defining ways that class instances can be represented:

    def _repr(self, /):
        args, kwargs = self.inputs
        return ', '.join(_itertools.chain(
            map(repr, args),
            map('='.join, zip(map(repr, kwargs), map(repr, kwargs.values()))),
            ))

    @_caching.soft_cache()
    def __repr__(self, /):
        content = f"({rep})" if (rep := self._repr()) else ''
        return f"<{repr(type(self)._ptolemaic_class__)}{content}>"


###############################################################################
###############################################################################
