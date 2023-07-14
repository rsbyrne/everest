###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.utilities import pretty as _pretty

from .system import System as _System
from .essence import Essence as _Essence
from .pathget import PathGet as _PathGet
from .demiurge import Demiurge as _Demiurge
from .prop import Prop as _Prop


class Realm(metaclass=_Essence):

    @_abc.abstractmethod
    def __contains__(self, other: 'Expression', /):
        raise NotImplementedError


class Expression(metaclass=_Essence):

    ...


class Expressor(metaclass=_Demiurge):


    extends: POS[Realm]
    sources: ARGS[Realm]
    valence: KW[int, type(...)] = None
    opkwargs: KWARGS

    @classmethod
    def _parameterise_(
            cls, extends=None, arg0=NotImplemented, /, *argn, **kwargs
            ):
        if isinstance(arg0, int) or arg0 is Ellipsis:
            if argn:
                raise ValueError
            params = super()._parameterise_(extends, valence=arg0, **kwargs)
        elif arg0 is NotImplemented:
            params = super()._parameterise_(extends, **kwargs)
        else:
            params = super()._parameterise_(extends, arg0, *argn, **kwargs)
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
        return kls.partial(params.extends, *params.sources, **params.opkwargs)


    class _DemiBase_(Realm):


        extends: POS[Realm] = None
        extends = prop('self.__corpus__')
        symbol: KW = ANCILLARY
        symbol = prop('self')

        def __contains__(self, other, /):
            if isinstance(other, self._Expression_):
                return other.header is self.symbol


        class _Expression_(mroclass(Expression), metaclass=_System):

            header: POS
            contents = ()

            def _pretty_repr_(self, p, cycle, root=None):
                kwargs = {}
                for key, field in self._abstract_class_.__fields__.items():
                    if field.kind.value > 2:
                        val = getattr(self, key)
                        try:
                            default = field.default
                        except AttributeError:
                            pass
                        else:
                            if val == default:
                                continue
                        kwargs[key] = val
                _pretty.pretty_call(
                    self.header, (self.contents, kwargs),
                    p, cycle, root=root,
                    )


        def __call__(self, /, *args, **kwargs) -> _Expression_:
            return self._Expression_(self.symbol, *args, **kwargs)


    class Nullary(demiclass):

        def __call__(self, /, **kwargs) -> _Expression_:
            return super().__call__(**kwargs)


    class NonNullary(demiclass):

        source: POS[Realm] = ANCILLARY
        source = prop('self')

        @_abc.abstractmethod
        def check_content(self, other, /) -> bool:
            raise NotImplementedError

        def __contains__(self, other, /):
            if super().__contains__(other):
                return self.check_content(other)
            if (extends := self.extends) is not None:
                return other in extends


    class Unary(demiclass('.NonNullary')):


        def check_content(self, other, /) -> bool:
            return other.content in self.source


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
                if content.header is params.header:
                    params.content = content.content
                    iterations += content.iterations
                params.iterations = iterations
                return params


        def __call__(self, arg, /, **kwargs) -> _Expression_:
            if not arg in self.source:
                raise ValueError(arg)
            return super().__call__(arg, **kwargs)


    class Ennary(demiclass('.NonNullary')):


        minargs: int = 0

        def check_operands(self, contents: tuple, /):
            if len(contents) < self.minargs:
                return False
            return all(arg in self.source for arg in contents)

        def check_content(self, other, /):
            return self.check_operands(other.contents)

        def __contains__(self, other, /):
            if super().__contains__(other):
                return self.check_operands(other.contents)


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


        def __call__(self, /, *args, **kwargs):
            if not self.check_operands(args):
                raise ValueError(args)
            return super().__call__(*args, **kwargs)


class Operator(_Prop):

    asorgan: bool = True

    @classmethod
    def __body_call__(cls, body, /, *args, **kwargs):
        return super().__body_call__(
            body, Expressor, bindings=((NotImplemented, *args), kwargs)
            )


class Algebra(_System):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield Operator


class _AlgebraBase_(Realm, metaclass=Algebra):

    @prop
    def operators(self, /):
        return {
            (op := getattr(self, name)).symbol: op
            for name in self._abstract_class_.__operators__
            }

    def __contains__(self, other, /):
        if isinstance(other, Expression):
            return other in self.operators[other.header]


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
