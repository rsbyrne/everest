###############################################################################
''''''
###############################################################################


import abc as _abc

from .urgon import Urgon as _Urgon
from .enumm import Enumm as _Enumm
from .ousia import Ousia as _Ousia
from .tekton import Tekton as _Tekton
from .message import Message as _Message


class Algebra(_Urgon):

    def register_algclass(cls, kls, /):
        cls.__algclasses__.append(kls)

    def __call__(cls, arg0, /, *argn, **kwargs):
        if not (argn or kwargs):
            if isinstance(arg0, cls):
                return arg0
            for kls in cls.__mro__:
                try:
                    meth = kls.__dict__['_algconvert_']
                except KeyError:
                    continue
                out = meth.__func__(cls, arg0)
                if out is not NotImplemented:
                    return out
        return super().__call__(arg0, *argn, **kwargs)


class AbstractAlgebra(metaclass=Algebra):

    @classmethod
    def __subalgebra_init__(cls, corpus, /):
        pass

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        Base = cls.__Base__
        assert Base.__corpus__ is cls, (cls, Base, Base.__corpus__)
        cls.register(Base)
        if cls is not __class__:
            for kls in Base.__bases__:
                if issubclass(kls, __class__.__Base__):
                    # i.e. the algebra should be a subclass
                    # of all of its base's bases' algebras.
                    kls.algebra.register(cls)
        Base.algebra = cls
        if isinstance(corpus := cls.__corpus__, Algebra):
            cls.__subalgebra_init__(corpus)
        algclasses = cls.__algclasses__ = tuple(
            kls for kls in (getattr(cls, nm) for nm in cls.__mroclasses__)
            if (issubclass(kls, Base) and kls is not Base)
            )
        Nullary = cls.__Nullary__
        for kls in algclasses:
            if issubclass(kls, Nullary) and kls is not Nullary:
                name = kls.__relname__
                upper = name.strip('_').upper()
                if name == upper:
                    raise RuntimeError(name, upper)
                if isinstance(kls, _Ousia):
                    obj = kls.__class_alt_call__()
                    cls._register_innerobj(upper, obj)
                else:
                    obj = kls()
                setattr(cls, upper, obj)

    @classmethod
    def _algconvert_(cls, arg, /):
        return NotImplemented


    class __Base__(mroclass, metaclass=_Tekton):

        ...


    AlgebraType = __Base__


    class __Nullary__(mroclass('.__Base__')):

        ...


    class __Unary__(mroclass('.__Base__')):

        idempotent = False
        invertible = False

        arg: POS['..__Base__']

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            cls.srcalg = cls.__signature__.parameters['arg'].annotation

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            arg = cls.srcalg(params.arg)
            if isinstance(arg, cls):
                if cls.idempotent:
                    cls.altreturn(arg)
                if cls.invertible:
                    cls.altreturn(arg.arg)
            params.arg = arg
            return params


    class __Ennary__(mroclass('.__Base__'), metaclass=_Tekton):

        unique=False
        commutative=False
        associative=False
        identity=None

        args: ARGS['..__Base__']

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            srcalg = cls.__signature__.parameters['args'].annotation
            if not isinstance(srcalg, Algebra):
                srcalg = srcalg.algebra
            cls.srcalg = srcalg

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            args = map(cls.srcalg, params.args)
            if cls.associative:
                args = _itertools.chain.from_iterable(
                    arg.args if isinstance(arg, cls) else (arg,)
                    for arg in args
                    )
            if cls.unique:
                if cls.commutative:
                    args = sorted(set(args))
                else:
                    seen = set()
                    processed = []
                    for arg in args:
                        if arg not in seen:
                            processed.append(arg)
                            seen.add(arg)
                    args = tuple(args)
            elif cls.commutative:
                args = sorted(args)
            if hasidentity := (identity := cls.identity) is not None:
                args = tuple(arg for arg in args if arg is not identity)
            else:
                args = tuple(args)
            nargs = len(args)
            if nargs == 0:
                if hasidentity:
                    cls.altreturn(identity)
                raise ValueError("No arguments.")
            if nargs == 1:
                cls.altreturn(args[0])
            params.args = args
            return params


###############################################################################
###############################################################################
