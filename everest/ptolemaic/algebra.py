###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools

from .essence import Essence as _Essence
from .enumm import Enumm as _Enumm
from .system import System as _System
from . import ptolemaic as _ptolemaic


class Algebra(_Essence):

    @classmethod
    def _yield_mroclasses(meta, /):
        yield from super()._yield_mroclasses()
        yield 'Base', ()
        # yield 'Error', ()
        yield 'Identity', '.Base'
        yield 'Operation', ()
        yield 'Nullary', '.Operation'
        yield 'Unary', '.Operation'
        yield 'Ennary', '.Operation'


class _AlgebraBase_(metaclass=Algebra):


    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        Base = cls.Base
        cls.register(Base)
        Base.algebra = cls
        for enumm in cls.Identity.enumerators:
            setattr(cls, enumm.name, enumm)
        cls.Operation.convert = cls.convert

    @classmethod
    def __class_call__(cls, arg, /):
        return cls.convert(arg)

    @classmethod
    def convert(cls, arg, /):
        out = cls._convert_(arg)
        if out is NotImplemented:
            raise TypeError(type(arg))
        return out

    @classmethod
    def _convert_(cls, arg, /):
        if isinstance(arg, cls):
            return arg
        return NotImplemented


    class Error(RuntimeError):

        ...


    class Base(metaclass=_Essence):

        ...


    class Identity(metaclass=_Enumm):

        ...


    class Operation(metaclass=_Essence):

        __mergenames__ = dict(__algparams__=(dict, dict))

        @classmethod
        @_abc.abstractmethod
        def convert(cls, arg, /):
            raise NotImplementedError


    class Nullary(metaclass=_System):

        ...


    class Unary(metaclass=_System):

        __algparams__ = dict(
            idempotent=False,
            invertible=False,
            )

        arg: get('__corpus__.Base')

        @classmethod
        def __class_call__(cls, /, *args, **kwargs):
            params = cls.__parameterise__(*args, **kwargs)
            algparams = cls.__algparams__
            if isinstance(arg := params.arg, cls):
                if algparams['idempotent']:
                    return arg
                if algparams['invertible']:
                    return arg.arg
            return cls.__retrieve__(tuple(params.__dict__.values()))

        @classmethod
        def __parameterise__(cls, /, *args, **kwargs):
            params = super().__parameterise__(*args, **kwargs)
            arg = cls.convert(params.arg)
            algparams = cls.__algparams__
            if algparams['idempotent']:
                if isinstance(arg, cls):
                    arg = arg.arg
            params.arg = arg
            return params


    class Ennary(metaclass=_System):

        __algparams__ = dict(
            unique=False,
            commutative=False,
            associative=False,
            arity=None,
            )

        args: ARGS[get('__corpus__.Base')]

        @classmethod
        def __parameterise__(cls, /, *args, **kwargs):
            params = super().__parameterise__(*args, **kwargs)
            args = map(cls.convert, params.args)
            algparams = cls.__algparams__
            if algparams['associative']:
                args = _itertools.chain.from_iterable(
                    arg.args if isinstance(arg, cls) else (arg,)
                    for arg in args
                    )
            if algparams['unique']:
                if algparams['commutative']:
                    args = sorted(set(args))
                else:
                    args = _ptolemaic.PtolUniTuple(args)
            elif algparams['commutative']:
                args = sorted(args)
            if (arity := algparams['arity']) is not None:
                if len(args) != arity:
                    raise ValueError("Wrong arity.")
            params.args = tuple(args)
            return params


class CompanionAlgebra(Algebra):

    @classmethod
    def __post_prepare__(meta, body, /, **kwargs):
        super().__post_prepare__(body)
        if body.iscosmic:
            body['Element'] = Algebra.BaseTyp
        else:
            body['Element'] = body.outer.namespace


class _CompanionAlgebraBase_(metaclass=CompanionAlgebra):

    __mroclasses__ = dict(
        Base='.Element.Operation',
        )

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        if not cls.__cosmic__:
            cls.Element = cls.__corpus__


###############################################################################
###############################################################################
