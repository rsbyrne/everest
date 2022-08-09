###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools

from .essence import Essence as _Essence
from .enumm import Enumm as _Enumm
from .system import System as _System
from . import ptolemaic as _ptolemaic


class AlgebraType(metaclass=_Essence):

    @classmethod
    def __algebratype_init__(cls, /):
        pass

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        if cls is not cls.__class__:
            cls.__algebratype_init__()


class Algebra(_Essence):

    ...


class _AlgebraBase_(metaclass=Algebra):

    @classmethod
    def __subalgebra_init__(cls, corpus, /):
        pass

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        Base = cls.Base
        cls.register(Base)
        if cls is not __class__:
            for base in Base.__bases__:
                if issubclass(base, _AlgebraBase_.Base):
                    base.algebra.register(cls)
        Base.algebra = cls
        cls.Armature.algconvert = cls.algconvert
        if isinstance(corpus := cls.__corpus__, Algebra):
            cls.__subalgebra_init__(corpus)

    @classmethod
    def __class_call__(cls, arg, /):
        return cls.algconvert(arg)

    @classmethod
    def algconvert(cls, arg, /):
        out = cls._algconvert_(arg)
        if out is NotImplemented:
            raise TypeError(type(arg))
        return out

    @classmethod
    def _algconvert_(cls, arg, /):
        if isinstance(arg, cls):
            return arg
        return NotImplemented


    class Base(mroclass(AlgebraType)):

        ...


    class Special(mroclass('.Base'), metaclass=_Enumm):

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            if isinstance(corpus := cls.__corpus__, Algebra):
                for enumm in cls:
                    setattr(corpus, enumm.name, enumm)


    class Armature(mroclass(AlgebraType)):

        __mergenames__ = dict(__algparams__=(dict, dict))

        @classmethod
        @_abc.abstractmethod
        def algconvert(cls, arg, /):
            raise NotImplementedError


    class Nullary(mroclass('.Armature'), metaclass=_System):

        ...


    class Unary(mroclass, metaclass=_System):

        __algparams__ = dict(
            idempotent=False,
            invertible=False,
            )

        arg: get('..Base')

        @classmethod
        def __class_call__(cls, /, *args, **kwargs):
            params = cls._parameterise_(*args, **kwargs)
            algparams = cls.__algparams__
            if isinstance(arg := params.arg, cls):
                if algparams['idempotent']:
                    return arg
                if algparams['invertible']:
                    return arg.arg
            return cls.__retrieve__(tuple(params.__dict__.values()))

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            arg = cls.algconvert(params.arg)
            algparams = cls.__algparams__
            if algparams['idempotent']:
                if isinstance(arg, cls):
                    arg = arg.arg
            params.arg = arg
            return params


    class Ennary(mroclass('.Armature'), metaclass=_System):

        __algparams__ = dict(
            unique=False,
            commutative=False,
            associative=False,
            arity=None,
            )

        args: ARGS[pathget('..Base')]

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            args = map(cls.algconvert, params.args)
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


###############################################################################
###############################################################################
