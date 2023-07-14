###############################################################################
''''''
###############################################################################


import functools as _functools

from .demiurge import Demiurge as _Demiurge
from .ousia import Ousia as _Ousia
from .system import System as _System
from .essence import Essence as _Essence
from .pathget import PathGet as _PathGet
from .wisp import Namespace as _Namespace


class Algebraic(metaclass=_Essence):

    ...


class Operator(metaclass=_Demiurge):

    opname: POS[str]
    sources: ARGS['Algebra']
    properties: KWARGS

    @classmethod
    def _parameterise_(cls, opname, arg0=None, /, *argn, **kwargs):
        if arg0 is None:
            args = ()
        elif argn or kwargs:
            args = (arg0, *argn)
        else:
            args, kwargs = arg0
        return super()._parameterise_(opname, *args, **kwargs)

    @classmethod
    def _construct_(cls, params, /):
        sources, properties = params.sources, params.properties
        arity = len(sources)
        if arity == 0:
            kls = cls.Nullary
        if arity == 1:
            kls = cls.Unary
        elif arity == 2:
            kls = cls.Binary
        else:
            raise ValueError
        return kls(params.opname, *sources, **properties)


    class _DemiBase_(ptolemaic):

        opname: POS[str]

        def __call__(self, dest: 'Algebra', /, *args):
            return Operation(self, dest, *args)

        oparity = None


    class Nullary(demiclass):

        oparity = 0


    class Unary(demiclass):

        oparity = 1

        source: POS['Algebra']
        idempotent: KW[bool] = False
        invertible: KW[bool] = False


    class Binary(demiclass):

        oparity = 2

        lsource: POS['Algebra']
        rsource: POS['Algebra']
        commutative: KW[bool] = False
        associative: KW[bool] = False
        identity: KW['..Nullary'] = None
        distributive: KW['._Base_'] = None


class Operation(Algebraic, metaclass=_System):

    operator: POS[Operator]
    dest: POS['Algebra']
    args: ARGS[Algebraic]

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        if len(params.args) != params.operator.oparity:
            raise ValueError("Wrong number of arguments for operator.")
        return params


class Algebra(metaclass=_System):

    operators: ARGS[Operator]

    __slots__ = ('op',)

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        operators = params.operators
        if len(set(op.opname for op in operators)) != len(operators):
            raise ValueError("All operators must have unique names.")
        params.operators = tuple(sorted(
            params.operators, key = lambda op: (op.oparity, op.opname)
            ))
        return params

    def __init__(self, /):
        super().__init__()
        self.op = OperatorSet((op.opname, op) for op in self.operators)


class OperatorSet(_Namespace):

    algebra: Algebra

    def __init__(self, /):
        super().__init__()
        algebra = self.algebra
        for key, val in tuple((content := self._content).items()):
            content[key] = _functools.partial(val, algebra)


###############################################################################
###############################################################################
