###############################################################################
''''''
###############################################################################


from functools import partial as _partial
import abc as _abc
import weakref as _weakref
import itertools as _itertools
from collections import deque as _deque
from collections import abc as _collabc
import abc as _abc

from everest.utilities import pretty as _pretty

from .system import System as _System
from .pathget import PathGet as _PathGet


def _operator_bodymeth_(body, arg0=0, /, *argn, **kwargs):
    ns = body.namespace
    if isinstance(arg0, _PathGet):
        arg0 = arg0(ns)
    if isinstance(arg0, type):
        optyp = arg0
        args = argn
    else:
        if isinstance(arg0, int):
            if argn:
                raise ValueError(
                    "Cannot pass both int flag and sources "
                    "to operator constructor."
                    )
            args = tuple(NotImplemented for _ in range(arg0))
        else:
            args = (arg0, *argn)
        arity = len(args)
        if arity == 0:
            optyp = Constant
        elif arity == 1:
            optyp = Unary
        elif arity == 2:
            optyp = Ennary
        else:
            raise ValueError
    return body['organ'](
        **optyp.__signature__.bind_partial(*args, **kwargs).arguments,
        )(optyp)


class Algebra(_System):

    @classmethod
    def _yield_bodymeths(meta, body, /):
        yield from super()._yield_bodymeths(body)
        yield 'operator', _partial(_operator_bodymeth_, body)


class _AlgebraBase_(metaclass=Algebra):

    target: POSKW['.'] = ANCILLARY
    @prop
    def target(self, /):
        return self

    @prop
    def symbols(self, /):
        return frozenset()

    __slots__ = ('_registeredelements_',)

    def __init__(self, /):
        super().__init__()
        self._registeredelements_ = _weakref.WeakSet()

    def _register_element_(self, op, /):
        self._registeredelements_.add(op)

    def __contains__(self, other, /):
        return other in self._registeredelements_

    def canonise(self, other, /):
        if other in self:
            return other.canonise()
        raise ValueError(other)


class _Form_(metaclass=_System):

    operator: POS['Operator']

    @_abc.abstractmethod
    def canonise(self, /):
        return self


class Constant(_Form_):

    operator: FIXED = NotImplemented
    @prop
    def operator(self, /):
        return Ellipsis

    def __initialise__(self, /):
        super().__initialise__()
        self.algebra._register_element_(self)

    def canonise(self, /):
        return self

    @property
    def algebra(self, /):
        return self.__corpus__

    def _construct_(self, /):
        raise RuntimeError(
            "Constants should only be instantiated "
            "as organs of instances of algebras."
            )


class Operator(metaclass=_System):

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.algarity = cls.__fields__.npos - 1

    def _construct_(self, /):
        raise RuntimeError(
            "Operators should only be instantiated "
            "as organs of instances of algebras."
            )

    def __call__(self, /, *args, **kwargs):
        out = self._Operation_(self, *args, **kwargs)
        self.algebra._register_element_(out)
        return out

    @property
    def algebra(self, /):
        return self.__corpus__

    @property
    def target(self, /):
        return self.algebra.target

    class _Operation_(mroclass(_Form_)):

        operator: POS['Operator']

        def _pretty_repr_(self, p, cycle, root=None):
            _pretty.pretty_call(
                self.operator, (self.__params__[1:], {}),
                p, cycle, root=root,
                )


class Selector(Operator):

    alphabet: KW[_collabc.Container]

    class _Operation_(mroclass):

        symbol: POS = None

        @classmethod
        def __parameterise__(cls, /, *args, **kwargs):
            params = super().__parameterise__(*args, **kwargs)
            if params.symbol not in params.operator.alphabet:
                raise ValueError(params)
            return params

        def canonise(self, /):
            return self


def distribute(factors, under, /):
    chunks = _deque()
    buff = _deque()
    for factor in factors:
        if factor.operator is under:
            chunks.append(tuple(
                (*buff, term) for term in factor.arguments
                ))
            buff.clear()
        else:
            buff.append(factor)
    if chunks:
        chunks.append(tuple((*term, *buff) for term in chunks.pop()))
        return tuple(map(tuple, map(
            _itertools.chain.from_iterable, _itertools.product(*chunks)
            )))
    return (tuple(buff),)


class Unary(Operator):

    source: POS[_AlgebraBase_] = ANCILLARY
    @prop
    def source(self, /):
        return self.target
    idempotent: KW[bool] = False
    invertible: KW[bool] = False
    distributive: KW[Operator] = None

    class _Operation_(mroclass):

        argument: POS

        def canonise(self, /):
            argument = self.argument.canonise()
            operator = argument.operator
            if operator is self:
                if operator.idempotent:
                    return argument
                if operator.invertible:
                    return argument.argument.canonise()
                return self
            if operator is (distr := operator.distributive):
                return distr(
                    *(operator(arg) for arg in argument.arguments)
                    ).canonise()
            return argument

        def _pretty_repr_(self, p, cycle, root=None):
            _pretty.pretty_call(
                self.operator, (self.arguments, {}),
                p, cycle, root=root,
                )


class Ennary(Operator):

    source: POS[_AlgebraBase_] = ANCILLARY
    @prop
    def source(self, /):
        return self.target
    unique: KW[bool] = False
    commutative: KW[bool] = False
    associative: KW[bool] = False
    identity: KW[_Form_] = None
    inverse: KW[Operator] = None
    distributive: KW[Operator] = None

    def __call__(self, /, *args):
        if not args:
            identity = self.identity
            if identity is None:
                raise ValueError("No args!")
            return identity
        if len(args) == 1:
            return args[0]
        return super().__call__(*args)

    def unpack_associative(self, args, /):
        for arg in args:
            if arg.operator is operator:
                yield from arg.arguments
            else:
                yield arg

    def gather_distributive_inverses(self, args, /):
        isinv = False
        dinv = self.distributive.inverse
        if not dinv:
            return isinv, args
        out = _deque()
        for arg in args:
            if arg.operator is dinv

    class _Operation_(mroclass):

        arguments: ARGS

        def canonise(self, /):
            op = self.operator
            args = tuple(arg.canonise() for arg in self.arguments)
            if operator.associative:
                args = op.unpack_associative(args)
            if distr := op.distributive:
                newargs = []
                for arg in 
            if op.unique:
                if op.commutative:
                    args = sorted(set(args))
                else:
                    seen = set()
                    processed = []
                    for arg in args:
                        if arg not in seen:
                            processed.append(arg)
                            seen.add(arg)
                    args = tuple(args)
            elif op.commutative:
                args = sorted(args)
            if op.identity:
                args = tuple(arg for arg in args if arg is not op.identity)

            # operator = self.operator
            # inargs = args = tuple(map(
            #     operator.source.canonise,
            #     self.arguments,
            #     ))
            # if operator.associative:
            #     args = self._unpack_associative(args)
            # if operator.unique:
            #     if operator.commutative:
            #         args = sorted(set(args))
            #     else:
            #         seen = set()
            #         processed = []
            #         for arg in args:
            #             if arg not in seen:
            #                 processed.append(arg)
            #                 seen.add(arg)
            #         args = tuple(args)
            # elif operator.commutative:
            #     args = sorted(args)
            # if ide:
            #     args = tuple(arg for arg in args if arg is not identity)
#             if (inverse := operator.inverse):
#                 if operator.commutative:
#                     args = _deque(args)
#                     while args:
#                         chosen = args.popleft()
#                         for i, arg in enumerate(args):
#                             if arg.operator is inverse:
                                
#                     for arg in args:
#                         if
            # if (distr := operator.distributive):
            #     out = distr(
            #         *(operator(*factors)
            #         for factors in distribute(args, distr))
            #         )
            #     if out is self:
            #         return out
            #     return out.canonise()
            # return operator(*args)

###############################################################################
###############################################################################


# class Binary(mroclass('.Operator')):

#     lsource: POS[_AlgebraBase_] = ANCILLARY
#     @prop
#     def lsource(self, /):
#         return self.target
#     rsource: POS[_AlgebraBase_] = ANCILLARY
#     @prop
#     def rsource(self, /):
#         return self.target
#     lidentity: KW[_Form_] = None
#     ridentity: KW[_Form_] = None
#     linverse: KW[Unary] = None
#     rinverse: KW[Unary] = None

#     @classmethod
#     def __parameterise__(cls, /, *args, **kwargs):
#         params = super().__parameterise__(*args, **kwargs)
#         ids = set((params.lidentity, params.ridentity))
#         if len(ids) > 1 and None not in ids:
#             raise ValueError(
#                 "A binary operator cannot have two different identities."
#                 )
#         return params

#     def canonise(self, /):
#         operator = self.operator
#         lid, rid = self.lidentity, self.ridentity
#         linv, rinv = self.linverse, self.rinverse
#         (larg, rarg) = (arg.canonise() for arg in self.arguments)
#         if distr := self.distributive:
#             dinv = distr.inverse
#             if larg.operator is dinv:
#                 linv = True
#                 larg = larg.argument
#             if rarg.operator is dinv:
#                 rinv = True
#                 rarg = rarg.argument
#             dide = distr.identity
#             if any(arg.operator is dide for arg in (larg, rarg)):
#                 return dide
#             if larg is lid:
#                 return rarg
#             if rarg is rid:
#                 return larg
#             if larg.operator is linv:
#                 if larg.argument is rarg:
#                     return lid
#             if rarg.operator is rinv:
#                 if rarg.argument is larg:
#                     return rid
