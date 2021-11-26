###############################################################################
''''''
###############################################################################


import inspect as _inspect
import itertools as _itertools

from everest.ptolemaic.primitive import Primitive as _Primitive
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.abstract import ProxyAbstract as _ProxyAbstract
from everest.ptolemaic import exceptions as _exceptions


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
            param if self.recognised(param) else self.process_param(param)
            for param in params
            )

    def register_args(self, args, /):
        self.args.extend(self.process_params(args))

    def register_kwargs(self, kwargs, /):
        self.kwargs.update(zip(kwargs, self.process_params(kwargs.values())))

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
            f"{key}: {repr(val)}" for key, val in self.kwargs.items()
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


class Inherence(_Ousia):
    '''
    The metaclass of all Ptolemaic types
    that can be instantiated with arguments.
    '''

    def reconstruct(cls, inputs, /):
        args, kwargs = inputs
        return cls(*args, **kwargs)
  
    class BASETYP(_Ousia.BASETYP):

        __slots__ = ()

        _ptolemaic_mergetuples__ = ('_ptolemaic_knowntypes__',)
        _ptolemaic_knowntypes__ = ()
        _ptolemaic_mroclasses__ = ('Registrar',)
        _req_slots__ = ('_argskwargs',)

        Registrar = Registrar

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
            self._argskwargs = (args, kwargs)
            args, kwargs = _ProxyAbstract.unproxy_argskwargs(args, kwargs)
            super().initialise(*args, **kwargs)

        @classmethod
        def construct(cls, /, *args, **kwargs):
            cls.parameterise(registrar := cls.registrar, *args, **kwargs)
            registrar.check()
            bound = cls.__signature__.bind(*registrar.args, **registrar.kwargs)
            bound.apply_defaults()
            args, kwargs = bound.args, bound.kwargs
            return super().construct(*args, **kwargs)

        @property
        def argskwargs(self, /):
            return self._argskwargs

        def get_unreduce_args(self, /):
            yield from super().get_unreduce_args()
            yield self.argskwargs

    @property
    def __signature__(cls, /):
        return cls.get_signature()

    @property
    def registrar(cls, /):
        return cls.Registrar(cls)


###############################################################################
###############################################################################
