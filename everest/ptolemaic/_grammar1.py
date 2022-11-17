###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc
import itertools as _itertools

from .system import System as _System
from .demiurge import Demiurge as _Demiurge
from .enumm import Enumm as _Enumm


class Clause(metaclass=_Demiurge):


    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.NOTHING = cls._Nothing_()


    class _DemiBase_(metaclass=_System):

        @_abc.abstractmethod
        def yield_subclauses(self, /):
            raise NotImplementedError

        def bind(self, grammar, index: int, /):
            return self.Bound(grammar, index)


        class Bound(mroclass, metaclass=_System):

            grammar: POS
            index: POS[int]

            @prop
            def clause(self, /):
                return self.grammar.clauses[index]

            # @_abc.abstractmethod
            def match(self, parser: 'Parser', /):
                raise NotImplementedError

#             @prop
#             @_abc.abstractmethod
#             def consumptive(self, /):
#                 raise NotImplementedError

#             @_abc.abstractmethod
#             def is_seed_parent(self, clause, /):
#                 raise NotImplementedError


    class Nullary(demiclass):

        def yield_subclauses(self, /):
            yield from ()


    class Terminal(demiclass('.Nullary')):

        ...


    class _Nothing_(demiclass('.Terminal')):

        ...


    class Collection(demiclass('.Terminal')):


        container: POS[_collabc.Container]


        class Bound(mroclass):

            def match(self, parser, /):
                if parser.current_symbol in self.container:
                    return 1


    class Nonterminal(demiclass('.Nullary')):

        symbol: POS


    class Operation(demiclass):

        ...


    class Unary(demiclass):

        subclause: POS['..']

        def yield_subclauses(self, /):
            yield self.subclause


    class OneOrMore(demiclass('.Unary')):

        ...


    class Predicate(demiclass('.Unary')):

        inverted: KW[bool] = False

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            if isinstance(subclause := params.subclause, cls):
                if params.inverted:
                    params.inverted = not subclause.inverted
                else:
                    params.inverted = subclause.inverted
                params.subclause = subclause.subclause
            return params


    class Ennary(demiclass):

        subclauses: ARGS['..']

        @classmethod
        @_abc.abstractmethod
        def unpack_subclause(cls, subclauses, /):
            raise NotImplementedError

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            params.subclauses = tuple(_itertools.chain.from_iterable(
                cls.unpack_subclause(cl) if isinstance(cl, cls) else (cl,)
                for cl in params.subclauses
                ))
            return params

        @classmethod
        def parameterise(cls, /, *args, **kwargs):
            params = super().parameterise(*args, **kwargs)
            if any(cl is cls.__corpus__.NOTHING for cl in params.subclauses):
                raise ValueError
            if len(params.subclauses) < 2:
                raise ValueError

        def yield_subclauses(self, /):
            for clause in self.subclauses:
                yield clause
                yield from clause.yield_subclauses()


    class Sequence(demiclass('.Ennary')):

        @classmethod
        def unpack_subclause(cls, subclause, /):
            yield from subclause.subclauses

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            params.subclauses = tuple(_itertools.chain.from_iterable(
                cl.subclauses if isinstance(cl, cls) else (cl,)
                for cl in params.subclauses
                ))
            return params


    class First(demiclass('.Ennary')):

        optional: KW[bool] = False

        @classmethod
        def unpack_subclause(cls, subclause, /):
            yield from subclause.subclauses
            if subclause.optional:
                yield cls.__corpus__.NOTHING

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            try:
                nothind = params.subclauses.index(cls.__corpus__.NOTHING)
            except ValueError:
                pass
            else:
                params.subclauses = tuple(params.subclauses[:nothind])
                params.optional = True
            return params


class Associativity(metaclass=_Enumm):

    LEFT: 'Declares left associativity.'
    RIGHT: 'Declares right associativity.'


class Rule(metaclass=_System):

    symbol: POS
    clause: POS[Clause]
    precedence: KW[int] = -1
    associativity: KW[Associativity] = None

    @prop
    def nonterminal(self, /):
        return Clause.Nonterminal(self.symbol)


class Grammar(metaclass=_System):

    rules: ARGS[Rule]

    # def _find_cycle_head_clauses(
    #         self,
    #         clause: Clause,
    #         discovered: set[Clause],
    #         finished: set[Clause],
    #         cycle_head_clauses_out: set[Clause],
    #         ):
    #     discovered.add(clause)
    #     for subcl in clause.yield_subclauses():
    #         if subcl in discovered:
    #             cycle_head_clauses_out.add(subcl)
    #         elif subcl not in finished:
    #             self._find_cycle_head_clauses(
    #                 subcl, discovered, finished, cycle_head_clauses_out
    #                 )
    #     discovered.remove(clause)
    #     finished.add(clause)

    @prop
    def lower_clauses(self, /):
        out = []
        for rule in self.rules:
            for clause in rule.clause.yield_subclauses():
                if clause not in out:
                    out.append(clause)
        return tuple(out)

    @prop
    def top_clauses(self, /):
        return tuple(
            rule.clause for rule in self.rules
            if rule.nonterminal not in self.lower_clauses
            )
        
        

    # @prop
    # def clauses(self, /):
    #     out = []
    #     for rule in self.rules:
    #         nonterminal, clause = rule.nonterminal, rule.clause
            

#     def yield_clauses(self, /):
#         for rule in self.rules:
#             yield from rule.clause.yield_clauses()

#     def sort_clauses(self, clauses, /):
#         return clauses

#     @prop
#     def clauses(self, /):
#         return tuple(self.sort_clauses(self.yield_clauses()))

#     @prop
#     def clauses(self, /):
#         return tuple(
#             cl.bind(self, i) for i, cl in enumerate(self.clauses)
#             )


###############################################################################
###############################################################################
