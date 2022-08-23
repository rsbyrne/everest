###############################################################################
''''''
###############################################################################


from functools import partial as _partial
import abc as _abc
import weakref as _weakref
import itertools as _itertools
from collections import deque as _deque
import abc as _abc

from everest.utilities import pretty as _pretty

from .system import System as _System
from .pathget import PathGet as _PathGet
from .demiurge import Demiurge as _Demiurge
from .tekton import Tekton as _Tekton


def distribute(factors, under, /):
    chunks = _deque()
    buff = _deque()
    for factor in factors:
        if isinstance(factor, Operator._Operation_):
            if factor.operator is under:
                chunks.append(tuple(
                    (*buff, term) for term in factor.arguments
                    ))
                buff.clear()
            else:
                buff.append(factor)
        else:
            buff.append(factor)
    if chunks:
        chunks.append(tuple((*term, *buff) for term in chunks.pop()))
        return tuple(map(tuple, map(
            _itertools.chain.from_iterable, _itertools.product(*chunks)
            )))
    return (tuple(buff),)


class Operator(metaclass=_System):

    algebra: POS['_AlgebraBase_']

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.algarity = cls.__fields__.npos - 1

    def _register_operation_(self, op, /):
        self.algebra._registeredoperations_.add(op)

    def __call__(self, /, *args, **kwargs):
        out = self._Operation_(self, *args, **kwargs)
        self._register_operation_(out)
        return out

    @property
    def realm(self, /):
        return self.algebra.realm

    class _Operation_(mroclass, metaclass=_System):

        operator: POS['Operator']

        @_abc.abstractmethod
        def canonise(self, /, *_):
            raise NotImplementedError


class Nullary(Operator):

    class _Operation_(mroclass):

        def canonise(self, /):
            return self


class Unary(Operator):

    source = field('algebra.realm', kind=POS, hint='Realm')
    idempotent: KW[bool] = False
    invertible: KW[bool] = False

    class _Operation_(mroclass):

        argument: POS

        def canonise(self, /):
            operator, argument = self.operator, self.argument
            argument = operator.source.canonise(argument)
            if isinstance(argument, _Operation_):
                if argument.operator is self:
                    if operator.idempotent:
                        return argument
                    if operator.invertible:
                        return argument.source.canonise(
                            argument.argument
                            )
            return argument

        def _pretty_repr_(self, p, cycle, root=None):
            _pretty.pretty_call(
                self.operator, ((self.argument,), {}),
                p, cycle, root=root,
                )


class Ennary(Operator):

    source = field('algebra.realm', kind=POS, hint='Realm')
    unique: KW[bool] = False
    commutative: KW[bool] = False
    associative: KW[bool] = False
    identity: KW = None
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

    class _Operation_(mroclass):

        arguments: ARGS

        def _unpack_associative(self, args, /):
            for arg in args:
                if isinstance(arg, Operator._Operation_):
                    if arg.operator is self:
                        yield from arg.arguments
                    else:
                        yield arg
                else:
                    yield arg

        def canonise(self, /):
            operator = self.operator
            inargs = args = tuple(map(
                operator.source.algebra.canonise,
                self.arguments,
                ))
            if operator.associative:
                args = self._unpack_associative(args)
            if operator.unique:
                if operator.commutative:
                    args = sorted(set(args))
                else:
                    seen = set()
                    processed = []
                    for arg in args:
                        if arg not in seen:
                            processed.append(arg)
                            seen.add(arg)
                    args = tuple(args)
            elif operator.commutative:
                args = sorted(args)
            if hasidentity := (identity := operator.identity) is not None:
                args = tuple(arg for arg in args if arg is not identity)
            else:
                args = tuple(args)
            if (distr := operator.distributive):
                return distr(
                    *(operator(*factors)
                    for factors in distribute(args, distr))
                    )
            return operator(*args)

        def _pretty_repr_(self, p, cycle, root=None):
            _pretty.pretty_call(
                self.operator, (self.arguments, {}),
                p, cycle, root=root,
                )


    #     class Binary(mroclass('.Operator')):

    #         lsource = rsource = field('realm', kind=POS, hint='Realm')
    #         commutative: KW[bool] = False
    #         associative: KW[bool] = False
    #         identity: KW[Noum] = None
    #         distributive: KW['Realm.Operator'] = None

    #         def canonise(self, larg, rarg, /):
    #             if self.commutative:
    #                 larg, rarg = sorted((larg, rarg))


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
            optyp = Nullary
        elif arity == 1:
            optyp = Unary
        elif arity == 2:
            optyp = Ennary
        else:
            raise ValueError
    return body['organ'](
        **optyp.__signature__.bind_partial(
            _PathGet('.'), *args, **kwargs
            ).arguments,
        )(optyp)


class Algebra(_System):

    @classmethod
    def _yield_bodymeths(meta, body, /):
        yield from super()._yield_bodymeths(body)
        yield 'operator', _partial(_operator_bodymeth_, body)


class _AlgebraBase_(metaclass=Algebra):


    realm: POS['Realm']

    __slots__ = ('_registeredoperations_',)

    def __init__(self, /):
        super().__init__()
        self._registeredoperations_ = _weakref.WeakSet()

    def __contains__(self, other, /):
        if other in self.realm.symbols:
            return True
        return other in self._registeredoperations_

    def canonise(self, other, /):
        if other in self.realm.symbols:
            return other
        if other in self._registeredoperations_:
            return other.canonise()
        raise ValueError(other)


class Realm(metaclass=_System):

    @property
    def symbols(self, /):
        return frozenset()

    @organ(realm=pathget('.'))
    class algebra(mroclass, metaclass=Algebra):
        ...

    def __contains__(self, other, /):
        return other in self.algebra


###############################################################################
###############################################################################
