###############################################################################
''''''
###############################################################################


from functools import partial as _partial

from .system import System as _System
from .essence import Essence as _Essence
from .pathget import PathGet as _PathGet


class Noum(metaclass=_System):

    operator: POS['Basic.Operator']
    arguments: ARGS['Noum']

    @prop
    def canonical(self, /):
        out = self.operator.canonise(*self.arguments)
        if out is NotImplemented:
            return self
        return out


def _operator_bodymeth_(body, /, arg0=0, *argn, **kwargs):
    if isinstance(arg0, _PathGet):
        arg0 = arg0(body.namespace)
    if isinstance(arg0, Basic.Operator):
        optyp = arg0
        args = argn
    else:
        if isinstance(arg0, int):
            if argn:
                raise ValueError(
                    "Cannot pass both int flag and sources to operator constructor."
                    )
            args = tuple(NotImplemented for _ in range(arg0))
        else:
            args = (arg0, *argn)
        arity = len(args)
        if arity == 0:
            optyp = body['Nullary']
        elif arity == 1:
            optyp = body['Unary']
        elif arity == 2:
            optyp = body['Binary']
        else:
            raise ValueError
    return body['organ'](
        **optyp.__signature__.bind_partial(
            body['pathget']('.'), *args, **kwargs
            ).arguments,
        )(optyp)


class Algebra(_System):

    @classmethod
    def _yield_bodymeths(meta, body, /):
        yield from super()._yield_bodymeths(body)
        yield 'operator', _partial(_operator_bodymeth_, body)


class Basic(metaclass=Algebra):


    class Operator(mroclass, metaclass=_System):

        # @classmethod
        # @_lru_cache
        # def __class_get__(cls, instance, owner=None):
        #     if instance is None:
        #         return cls
        #     return _partial(cls, instance)

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            cls.algarity = cls.__fields__.npos - 1

        target: POS

        def __call__(self, /, *args):
            if len(args) != self.algarity:
                raise ValueError(
                    f"Wrong number of args for this operator: "
                    f"{len(args)} != arity={self.algarity}"
                    )
            return Noum(self, *args)


    class Nullary(mroclass('.Operator')):

        ...


    class Unary(mroclass('.Operator')):

        source = field('target', kind=POS, hint='Basic')
        idempotent: KW[bool] = False
        invertible: KW[bool] = False

        def canonise(self, arg: Noum, /):
            if isinstance(arg, Noum):
                if arg.operator is self:
                    if self.idempotent:
                        return arg
                    if self.invertible:
                        return arg.arguments[0]
            return NotImplemented


    class Binary(mroclass('.Operator')):

        lsource = rsource = field('target', kind=POS, hint='Basic')
        commutative: KW[bool] = False
        associative: KW[bool] = False
        identity: KW[Noum] = None
        distributive: KW['Basic.Operator'] = None


###############################################################################
###############################################################################
