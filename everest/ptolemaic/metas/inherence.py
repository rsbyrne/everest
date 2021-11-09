###############################################################################
''''''
###############################################################################


import inspect as _inspect
import itertools as _itertools

from everest.ptolemaic.primitive import Primitive as _Primitive
from everest.ptolemaic.metas.ousia import Ousia as _Ousia
from everest.ptolemaic import exceptions as _exceptions


class BadParameters(_exceptions.ParameterisationException):

    __slots__ = ('bads',)

    @classmethod
    def check(cls, acls, args, /):
        exc = cls(acls, args)
        if exc:
            raise exc

    def __init__(self, raisedby, args, /):
        if not isinstance(raisedby, Inherence):
            raise TypeError(raisedby)
        super().__init__(raisedby)
        self.bads = tuple(_itertools.filterfalse(self.check_arg, args))

    def check_arg(self, arg, /):
        for typ in self.raisedby._ptolemaic_knowntypes__:
            if isinstance(arg, typ):
                return True
        return False

    def message(self, /):
        yield from super().message()
        yield "when one or more objects of unrecognised type"
        yield "were passed as parameters:"
        for param in self.bads:
            yield f"{repr(param)}, {repr(type(param))}"
        yield 'Note that the class only accepts parameters'
        yield 'that are instances of one or more of the following:'
        yield from map(repr, self.raisedby._ptolemaic_knowntypes__)

    def __bool__(self, /):
        return bool(self.bads)


class Registrar:

    __slots__ = ('owner', 'args', 'kwargs')

    def __init__(self, owner, /, *args, **kwargs):
        self.owner = owner
        self.args, self.kwargs = [], {}
        self(*args, **kwargs)

    def __call__(self, /, *args, **kwargs):
        self.args.extend(args)
        self.kwargs.update(kwargs)

    def __repr__(self, /):
        argtup = ', '.join(map(repr, self.args))
        kwargtup = ', '.join(f"{key}: {repr(val)}" for key, val in self.kwargs.items())
        return f"{type(self).__name__}(*({argtup}), **{{{kwargtup}}})"


class Inherence(_Ousia):
    '''
    The metaclass of all Ptolemaic types
    that can be instantiated with arguments.
    '''

    _ptolemaic_mergetuples__ = (
        '_ptolemaic_knowntypes__',
        )
    _ptolemaic_knowntypes__ = ()

    BadParameters = BadParameters
    Registrar = Registrar

    @property
    def __signature__(cls, /):
        return (
            (sig := _inspect.signature(cls.__init__))
            .replace(
                parameters=tuple(sig.parameters.values())[1:],
                return_annotation=cls,
                )
            )

    def parameterise(cls, register, /, *args, **kwargs):
        raise NotImplementedError

    @property
    def registrar(cls, /):
        return cls.Registrar(cls)

    def construct(cls, /, *args, **kwargs):
        cls.parameterise(registrar := cls.registrar, *args, **kwargs)
        args, kwargs = registrar.args, registrar.kwargs
        cls.BadParameters.check(cls, _itertools.chain(args, kwargs.values()))
        params = cls.__signature__.bind(*args, **kwargs)
        params.apply_defaults()
        obj = cls.create_object(params=params)
        obj.__init__(*params.args, **params.kwargs)
        return obj


###############################################################################
###############################################################################
