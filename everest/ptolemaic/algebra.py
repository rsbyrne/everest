###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.utilities import pretty as _pretty

from .system import System as _System
from .essence import Essence as _Essence
from .pathget import PathGet as _PathGet
from .demiurge import Demiurge as _Demiurge


class Expression(metaclass=_Essence):

    ...


class Algebra(metaclass=_Essence):

    @_abc.abstractmethod
    def __call__(self, /, *_, **__) -> Expression:
        raise NotImplementedError

    @_abc.abstractmethod
    def __contains__(self, other: Expression, /):
        raise NotImplementedError


class Axiom(Algebra, metaclass=_System):

    @_abc.abstractmethod
    def get_operator(self, symbol, /):
        raise NotImplementedError

    def __call__(self, symbol, /, *args, **kwargs):
        return self.get_operator(symbol)(*args, source=self, **kwargs)


class Operator(metaclass=_Demiurge):


    valence: POS[int]
    args: ARGS
    kwargs: KWARGS

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        if (valence := params.valence) is not Ellipsis:
            params.valence = int(valence)
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
            raise ValueError
        return kls.partial(*params.args, **params.kwargs)


    class _DemiBase_(Algebra):

        symbol: POS

        def __contains__(self, other: Expression, /):
            if isinstance(other, self.Expression):
                return other.symbol == self.symbol

        def __call__(self, /, *args, **kwargs):
            return self.Expression(self.symbol, *args, **kwargs)

        class Expression(mroclass(Expression), metaclass=_System):

            symbol: POS

            arguments = prop(())


    class Nullary(demiclass):

        ...


    class NonNullary(demiclass):

        source: POS[Algebra] = ANCILLARY
        source = prop('self')

        def __contains__(self, other, /):
            if super().__contains__(other):
                return all(arg in self.source for arg in other.arguments)

        def __call__(self, /, *args, **kwargs):
            if (source := self.source) is self:
                source = kwargs.pop('source', source)
            return super().__call__(*args, source=source, **kwargs)

        class Expression(mroclass):

            @classmethod
            def _parameterise_(cls, /, arg0, *argn, source=None, **kwargs):
                if source is not None:
                    if not all(arg in source for arg in argn):
                        raise ValueError(
                            "All arguments of an expression "
                            "must be valid members of the given source."
                            )
                return super()._parameterise_(arg0, *argn, **kwargs)


    class Unary(demiclass('.NonNullary')):

        class Expression(mroclass):

            argument: POS[Expression]
            arguments = '(self.argument,)'


    class Ennary(demiclass('.NonNullary')):

        class Expression(mroclass):

            arguments: ARGS[Expression]


###############################################################################
###############################################################################
