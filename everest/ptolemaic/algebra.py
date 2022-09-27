###############################################################################
''''''
###############################################################################


import abc as _abc
from functools import lru_cache as _lru_cache

from everest.utilities import pretty as _pretty

from .system import System as _System
from .essence import Essence as _Essence
from .pathget import PathGet as _PathGet
from .demiurge import Demiurge as _Demiurge
from .prop import Prop as _Prop


class Expression(metaclass=_Essence):

    ...


class Expressor(metaclass=_Demiurge):


    symbol: POS
    sources: ARGS['Realm']
    valence: KW[int, type(...)] = None
    opkwargs: KWARGS

    @classmethod
    def _parameterise_(
            cls, symbol, arg0=NotImplemented, /, *argn, **kwargs
            ):
        if isinstance(arg0, int) or arg0 is Ellipsis:
            if argn:
                raise ValueError
            params = super()._parameterise_(symbol, valence=arg0, **kwargs)
        elif arg0 is NotImplemented:
            params = super()._parameterise_(symbol, **kwargs)
        else:
            params = super()._parameterise_(symbol, arg0, *argn, **kwargs)
        valence = params.valence
        if valence is None:
            valence = len(params.sources)
        elif not valence is Ellipsis:
            valence = int(valence)
        params.valence = valence
        return params

    @classmethod
    def _dispatch_(cls, params, /):
        valence = params.valence
        if valence == 0:
            kls = cls.Nullary
        elif valence == 1:
            kls = cls.Unary
        elif valence is Ellipsis:
            kls = cls.Ennary
        else:
            raise ValueError(valence)
        return kls.partial(params.symbol, *params.sources, **params.opkwargs)


    class _DemiBase_(ptolemaic):


        symbol: POS


        class _Expression_(mroclass(Expression), metaclass=_System):

            symbol: POS
            contents = ()


        @_abc.abstractmethod
        def check_arguments(self, caller, args, /):
            raise NotImplementedError

        def __call__(self, caller, /, *args, **kwargs) -> _Expression_:
            if not self.check_arguments(caller, args):
                raise ValueError(args)
            return self._Expression_(self.symbol, *args, **kwargs)


    class Nullary(demiclass):

        def check_arguments(self, caller, args, /):
            return not args


    class Unary(demiclass):


        source: POS['Realm'] = None


        class _Expression_(mroclass):

            content: POS
            iterations: KW = 1
            
            contents = prop('(self.content,)')

            @classmethod
            def _parameterise_(cls, /, *args, **kwargs):
                params = super()._parameterise_(*args, **kwargs)
                iterations = int(params.iterations)
                if iterations <= 0:
                    raise ValueError(iterations)
                content = params.content
                if content.symbol is params.symbol:
                    params.content = content.content
                    iterations += content.iterations
                params.iterations = iterations
                return params

        def check_arguments(self, caller, args, /):
            if len(args) != 1:
                return False
            source = caller if (source := self.source) is None else source
            return (arg := args[0]) in source


    class Ennary(demiclass):


        source: POS['Realm'] = None
        minargs: int = 0


        class _Expression_(mroclass):

            contents: ARGS
            repetitions: KW = 1

            @classmethod
            def _parameterise_(cls, /, *args, **kwargs):
                params = super()._parameterise_(*args, **kwargs)
                repetitions = params.repetitions
                contents = params.contents
                if repetitions is not Ellipsis:
                    repetitions = params.repetitions = int(repetitions)
                    if repetitions <= 0:
                        raise ValueError(repetitions)
                return params


        def check_arguments(self, caller, args, /):
            source = caller if (source := self.source) is None else source
            return all(arg in source for arg in args)


class Realm(metaclass=_System):


    __slots__ = ('operators', 'symbols')

    expressors: KWARGS[Expressor]

    @classmethod
    def _instantiate_(cls, params, /):
        obj = super()._instantiate_(params)
        operators = {}
        symbols = {}
        for name, exp in params.expressors.items():
            op = cls.Operator.__class_alt_call__(exp)
            obj._register_innerobj(name, op)
            operators[name] = op
            symbols[exp.symbol] = op
        obj.operators = operators
        obj.symbols = symbols
        return obj
    
    def __getattr__(self, name, /):
        try:
            return object.__getattribute__(self, 'operators')[name]
        except (AttributeError, KeyError):
            return super().__getattr__(name)

    def __contains__(self, other: Expression, /):
        symbols, symbol = self.symbols, other.symbol
        try:
            op = symbols[symbol]
        except KeyError:
            return False
        exp = op.expressor
        if not isinstance(other, exp._Expression_):
            return False
        return exp.check_arguments(self, other.contents)


    class Operator(mroclass, metaclass=_System):

        expressor: POS[Expressor]

        def __call__(self, /, *args, **kwargs):
            return self.expressor(self.__corpus__, *args, **kwargs)


# class Operator(_Prop):

#     asorgan: bool = True

#     @classmethod
#     def __body_call__(cls, body, /, *args, **kwargs):
#         return super().__body_call__(
#             body, Expressor, bindings=((NotImplemented, *args), kwargs)
#             )


# class Algebra(_System):

#     @classmethod
#     def _yield_smartattrtypes(meta, /):
#         yield from super()._yield_smartattrtypes()
#         yield Operator


# class _AlgebraBase_(Realm, metaclass=Algebra):

#     @prop
#     def operators(self, /):
#         return {
#             (op := getattr(self, name)).symbol: op
#             for name in self._abstract_class_.__operators__
#             }

#     def __contains__(self, other, /):
#         if isinstance(other, Expression):
#             return other in self.operators[other.symbol]


###############################################################################
###############################################################################


# class Axiom(metaclass=_Demiurge):


#     class _DemiBase_(Realm):

#         @prop
#         @_abc.abstractmethod
#         def operator(self, /) -> Operator:
#             raise NotImplementedError

#         def __call__(self, /, *args, **kwargs):
#             return self.operator(*args, **kwargs)


#     class Unary(demiclass):

#         topic: POS[Realm]

#         @classmethod
#         def _parameterise_(cls, /, *args, **kwargs):
#             params = super()._parameterise_(*args, **kwargs)
#             if not isinstance(params.topic, Operator.Unary):
#                 raise ValueError(params.topic)
#             return params

#         @_abc.abstractmethod
#         def _canonise_(self, exp: Expression, /):
#             raise NotImplementedError

#         def canonise(self, exp: Expression, /):
#             exp = super().canonise(exp)
#             topic = self.topic
#             return topic.canonise(self._canonise_(topic.canonise(exp)))

#         def operator(self, /):
#             topic = self.topic
#             if isinstance(topic, Axiom):
#                 return topic.operator
#             return topic

#         _contains_ = prop('self.topic._contains_')


# class Idempotent(Axiom.Unary):

#     def _canonise_(self, exp: Expression, /):
#         argument = exp.contents[0]
#         if argument.operator is self.operator:
#             return argument
#         return exp