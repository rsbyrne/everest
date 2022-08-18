###############################################################################
''''''
###############################################################################


import abc as _abc

from .essence import Essence as _Essence
from .ousia import Ousia as _Ousia
from .urgon import Urgon as _Urgon
from .enumm import Enumm as _Enumm
from .tekton import Tekton as _Tekton
from .system import System as _System


class Theorem(metaclass=_System):

    @_abc.abstractmethod
    def __call__(self, arg, /):
        raise NotImplementedError


class Theory(Theorem):

    ...


class _Naive_(Theory):

    def __call__(self, arg, /):
        return arg


NAIVE = _Naive_()


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
        Base = cls.Base
        assert Base.__corpus__ is cls, (cls, Base, Base.__corpus__)
        cls.register(Base)
        if cls is not __class__:
            for kls in Base.__bases__:
                if issubclass(kls, __class__.Base):
                    # i.e. the algebra should be a subclass
                    # of all of its base's bases' algebras.
                    kls.algebra.register(cls)
        Base.algebra = cls
        if isinstance(corpus := cls.__corpus__, Algebra):
            cls.__subalgebra_init__(corpus)

    @classmethod
    def _algconvert_(cls, arg, /):
        return NotImplemented


    class Base(mroclass, metaclass=_Urgon):

        @classmethod
        def _get_returnanno(cls, /):
            return cls.algebra.Base


    class Nullary(mroclass('.Form'), metaclass=_Enumm):

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            if cls.__corpus__ is (alg := cls.algebra):
                for enumm in cls._enumerators:
                    setattr(alg, enumm,name, enumm)


    class Unary(mroclass('.Base'), metaclass=_Tekton):

        idempotent = False
        invertible = False

        arg: POS['..Base']

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


    class Ennary(mroclass('.Base'), metaclass=_Tekton):

        unique = False
        commutative = False
        associative = False
        identity = None
        distributive = None

        args: ARGS['..Base']

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            srcalg = cls.__signature__.parameters['args'].annotation
            if not isinstance(srcalg, Algebra):
                srcalg = srcalg.algebra
            cls.srcalg = srcalg

        @classmethod
        def simple_distribute(cls, prefactors, terms, postfactors, /):
            return tuple((*prefactors, term, *postfactors) for term in terms)

        @classmethod
        def distribute(cls, args, distr, /):
            isdistrs = tuple(isinstance(arg, distr) for arg in args)
            if not any(isdistrs):
                return args
            # outterms = []
            # while True:
            buff = []
            newargs = []
            for arg, isdistr in zip(args, isdistrs):
                if isdistr:
                    newargs.append(simple_distribute(buff, arg, ()))
                    buff.clear()
                else:
                    buff.append(arg)
            if buff:
                newargs[-1] = tuple((*term, *buff) for term in newargs[-1])
            return newargs
                    

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
            if (distr := cls.distributive):
                args = cls._distribute_over(args, distr)
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


        # algclasses = cls.__algclasses__ = tuple(
        #     kls for kls in (getattr(cls, nm) for nm in cls.__mroclasses__)
        #     if (issubclass(kls, Base) and kls is not Base)
        #     )
        # Nullary = cls.__Nullary__
        # for kls in algclasses:
        #     if issubclass(kls, Nullary) and kls is not Nullary:
        #         name = kls.__relname__
        #         upper = name.strip('_').upper()
        #         if name == upper:
        #             raise RuntimeError(name, upper)
        #         if isinstance(kls, _Ousia):
        #             obj = kls.__class_alt_call__()
        #             cls._register_innerobj(upper, obj)
        #         else:
        #             obj = kls()
        #         setattr(cls, upper, obj)
