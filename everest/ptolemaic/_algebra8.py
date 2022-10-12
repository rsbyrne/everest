###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc, deque as _deque

from everest.utilities import pretty as _pretty

from .system import System as _System
from .essence import Essence as _Essence
from .pathget import PathGet as _PathGet
from .demiurge import Demiurge as _Demiurge
from .prop import Prop as _Prop
from .enumm import Enumm as _Enumm


class Fixity(metaclass=_Enumm):

    PREFIX: 'Denotes an operator where the sign precedes the operands.'
    INFIX: 'Denotes an operator where the sign is between the operands.'
    POSTFIX: 'Denotes an operator where the sign postcedes the operands.'


class Algebra(metaclass=_System):


    __slots__ = ('symbols',)


    class Expression(mroclass, metaclass=_Essence):

        ...


    class Operator(mroclass, metaclass=_Demiurge):


        symbol: POS
        sources: ARGS['..']
        valence: KW[int, type(...)] = None
        opkwargs: KWARGS

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            cls.valencemap = cls.convert({
                kls.valence: kls for kls in cls._demiclasses_
                })

        @classmethod
        def _demiconvert_(cls, arg, /):
            if isinstance(arg, tuple):
                return cls(*arg)
            return NotImplemented

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
            elif valence is not Ellipsis:
                valence = int(valence)
            params.valence = valence
            return params

        @classmethod
        def _dispatch_(cls, params, /):
            return cls.valencemap[params.valence].partial(
                params.symbol, *params.sources, **params.opkwargs
                )


        class _DemiBase_(ptolemaic):


            symbol: POS

            valence = None


            class Expression(mroclass('..Expression'), metaclass=_System):

                head: POS
                body = ()


            def __call__(self, *args, **kwargs) -> Expression:
                return self.Expression(self.symbol, *args, **kwargs)


            class Bound(mroclass, metaclass=_System):

                operator: POS['...']
                algebra: POS['....']

                valence = prop('self.operator.valence')
                Expression = prop('self.operator.Expression')
                symbol = prop('self.operator.symbol')

                @_abc.abstractmethod
                def check_arguments(self, args, /):
                    raise NotImplementedError

                def __call__(self, /, *args, **kwargs):
                    if not self.check_arguments(args):
                        raise ValueError(args)
                    return self.operator(*args, **kwargs)


        class Nullary(demiclass):


            valence = 0


            class Bound(mroclass):

                def check_arguments(self, args, /):
                    return not args


        class Unary(demiclass):


            valence = 1

            source: POS['...'] = ANCILLARY
            fixity: KW[Fixity] = Fixity.PREFIX


            class Expression(mroclass):

                arg: POS
                iterations: KW = 1

                body = prop('(self.arg,)')

                @classmethod
                def _parameterise_(cls, /, *args, **kwargs):
                    params = super()._parameterise_(*args, **kwargs)
                    iterations = int(params.iterations)
                    if iterations <= 0:
                        raise ValueError(iterations)
                    arg = params.arg
                    if arg.head == params.head:
                        params.arg = arg.arg
                        iterations += arg.iterations
                    params.iterations = iterations
                    return params


            class Bound(mroclass):

                @prop
                def source(self, /):
                    try:
                        return self.operator.source
                    except AttributeError:
                        return self.algebra

                def check_arguments(self, args, /):
                    if len(args) != 1:
                        return False
                    return (arg := args[0]) in self.source


        class Binary(demiclass):


            valence = 2

            lsource: POS['...'] = ANCILLARY
            rsource: POS['...'] = ANCILLARY


            class Expression(mroclass):

                larg: POS
                rarg: POS

                body = prop('(self.larg, self.rarg)')


            class Bound(mroclass):

                @prop
                def lsource(self, /):
                    try:
                        return self.operator.lsource
                    except AttributeError:
                        return self.algebra

                @prop
                def rsource(self, /):
                    try:
                        return self.operator.rsource
                    except AttributeError:
                        return self.algebra

                def check_arguments(self, args, /):
                    try:
                        larg, rarg = args
                    except ValueError:
                        return False
                    return larg in self.lsource and rarg in self.rsource


        class Ennary(demiclass):

            valence = ...

            source: POS['...'] = ANCILLARY
            minargs: KW[int] = 0
            fixity: KW[Fixity] = Fixity.PREFIX


            class Expression(mroclass):

                body: ARGS
                repetitions: KW = 1

                @classmethod
                def _parameterise_(cls, /, *args, **kwargs):
                    params = super()._parameterise_(*args, **kwargs)
                    repetitions = params.repetitions
                    body = params.body
                    if repetitions is not Ellipsis:
                        repetitions = params.repetitions = int(repetitions)
                        if repetitions <= 0:
                            raise ValueError(repetitions)
                    return params


            class Bound(mroclass):

                @prop
                def source(self, /):
                    try:
                        return self.operator.source
                    except AttributeError:
                        return self.algebra

                def check_arguments(self, args, /):
                    return all(arg in self.source for arg in args)


    operators: tuple['.Operator']
    operators: ARGS['.Operator']

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        params.operators = tuple(map(cls.Operator, params.operators))
        return params

    @classmethod
    def _instantiate_(cls, params, /):
        obj = super()._instantiate_(params)
        symbols = {}
        for op in params.operators:
            symbols[op.symbol] = op.Bound(op, obj)
        obj.symbols = symbols
        return obj

    def __contains__(self, other: Expression, /):
        symbols, head = self.symbols, other.head
        try:
            op = symbols[head]
        except KeyError:
            return False
        return op.check_arguments(other.body)

    def process_tokens(self, tokens: _deque, /):
        if not tokens:
            return
        token = tokens.popleft()
        symbols = self.symbols
        try:
            op = symbols[token]
        except KeyError:
            op, valence = token, None
        else:
            valence = op.valence
        if valence is None:
            yield op
        else:
            stream = op.algebra.process_tokens(tokens)
            body = _deque()
            if valence is Ellipsis:
                body.extend(stream)
            else:
                while len(body) < valence:
                    body.append(next(stream))
            yield op(*body)
        yield from self.process_tokens(tokens)

    def __call__(self, /, *tokens):
        out = tuple(self.process_tokens(_deque(tokens)))
        if len(out) != 1:
            raise ValueError
        return out[0]

    def from_str(self, strn: str, /, delimiter=None):
        if delimiter is None:
            return self(*strn)
        return self(*strn.split(delimiter))


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


algebra = Algebra(
    '0',
    ('S', 1),
    ('+', 2),
    ('*', 2),
    )

exp = algebra.from_str('+++00+0S00')
assert exp in algebra


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
