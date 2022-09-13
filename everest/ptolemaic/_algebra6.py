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
        if arg0 is Ellipsis:
            optyp = Ennary
            args = (NotImplemented,)
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
                raise ValueError("Arity must be greater than zero.")
            elif arity == 1:
                optyp = Unary
            elif arity == 2:
                raise ValueError
            else:
                raise ValueError
    return body['organ'](
        **optyp.__signature__.bind_partial(*args, **kwargs).arguments,
        )(optyp)

def _constant_bodymeth_(body, symbol, /):
    return body['prop'](symbol=symbol)('self(symbol)')


class _AlgebraMeta_(_System):

    @classmethod
    def _yield_bodymeths(meta, body, /):
        yield from super()._yield_bodymeths(body)
        yield 'operator', _operator_bodymeth_.__get__(body)
        yield 'constant', _constant_bodymeth_.__get__(body)


class Algebra(metaclass=_AlgebraMeta_):

    target: POS = ANCILLARY
    target = prop('self')

    @prop
    def truetarget(self, /):
        target = self.target
        if target is self:
            return target
        return target.truetarget

    @prop
    def isprimary(self, /):
        return self.target is self

    def __contains__(self, other, /):
        if isinstance(other, _Form_):
            return other.canonical.truetarget is self.truetarget
        return False

    def recognise_symbol(self, symbol, /):
        return False

    def __call__(self, symbol, /):
        return _Constant_(self, symbol)


class _Form_(metaclass=_System):

    operator: POS['Operator']
    arguments: ARGS['_Form_']

    @prop
    def canonical(self, /):
        out = self.operator.canonise(*self.arguments)
        if out is NotImplemented:
            return self
        return out

    def _pretty_repr_(self, p, cycle, root=None):
        _pretty.pretty_call(
            self.operator, (self.arguments, {}),
            p, cycle, root=root,
            )

    @prop
    def argument(self, /):
        args = self.arguments
        if len(args) == 1:
            return next(iter(args))
        raise AttributeError

    @property
    def target(self, /):
        return self.operator.target

    @property
    def truetarget(self, /):
        return self.operator.truetarget


class _Constant_(_Form_):

    operator: FIXED
    operator = prop('...')
    arguments: FIXED
    arguments = prop('()')
    algebra: POS[Algebra]
    symbol: POS

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        if not params.algebra.recognise_symbol(params.symbol):
            raise ValueError(
                "The symbol provided to a constant "
                "must be recognised by the algebra."
                )
        return params

    def canonical(self, /):
        return self

    @property
    def target(self, /):
        return self.algebra.target

    @property
    def truetarget(self, /):
        return self.algebra.truetarget

    def _pretty_repr_(self, p, cycle, root=None):
        _pretty.pretty_call(
            self.algebra, ((self.symbol,), {}),
            p, cycle, root=root,
            )


class Operator(metaclass=_System):

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.algarity = cls.__fields__.npos - 1

    @classmethod
    def _convert_opprop(cls, val, /):
        if isinstance(val, str):
            return _PathGet('..' + val)
        if isinstance(val, _collabc.Iterable):
            return tuple(map(cls._convert_opprop, val))
        return val

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        params.__dict__.update({
            key: cls._convert_opprop(val)
            for key, val in params.__dict__.items()
            })
        return params

    def _construct_(self, /):
        raise RuntimeError(
            "Operators should only be instantiated "
            "as organs of instances of algebras."
            )

    def __call__(self, /, *args, **kwargs):
        return _Form_(self, *args, **kwargs)

    @property
    def algebra(self, /):
        return self.__corpus__

    @property
    def target(self, /):
        return self.algebra.target

    @property
    def truetarget(self, /):
        return self.algebra.truetarget

    def canonise(self, /, *args):
        return NotImplemented


class Unary(Operator):

    source: POS[Algebra] = ANCILLARY
    source = prop('self.target')
    idempotent: KW[bool] = False
    reversible: KW[bool] = False
    distributive: KW[Operator] = None

    def canonise(self, argument, /):
        argument = argument.canonical
        argop = argument.operator
        if argop is self:
            if argop.idempotent:
                return argument
            if argop.reversible:
                return argument.argument
        elif distr := self.distributive:
            if argument is distr.identity:
                return argument
            if argop is distr:
                return self.distributive(
                    *(self(arg) for arg in argument.arguments)
                    ).canonical
        return super().canonise(argument)

    def __call__(self, arg, /):
        if not arg in self.source:
            raise TypeError(arg)
        return super().__call__(arg)


class Ennary(Operator):

    source: POS[Algebra] = ANCILLARY
    source = prop('self.target')
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
        if not all(map(self.source.__contains__, args)):
            raise TypeError(arg)
        return super().__call__(*args)

    def unpack_associative(self, args, /):
        for arg in args:
            if arg.operator is operator:
                yield from arg.arguments
            else:
                yield arg

    def yield_unique(self, args, /):
        if self.commutative:
            yield from sorted(set(args))
        else:
            seen = set()
            for arg in args:
                if arg not in seen:
                    yield arg
                    seen.add(arg)

    def commutative_sort(self, arg, /):
        if isinstance(arg, self.inverse):
            return arg.argument.hashint + 1
        return arg.hashint

    def distribute(self, factors, /):
        under = self.distributive
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

    def canonise(self, /, *args):
        args = tuple(arg.canonical for arg in args)
        if self.associative:
            args = self.unpack_associative(args)
        args = tuple(arg for arg in args if arg is not self.identity)
        if self.unique:
            args = tuple(self.yield_unique(args))
        elif self.commutative:
            args = sorted(args, key=self.commutative_sort)
        if self.inverse:
            args = self.eliminate(args)
        if (distr := self.distributive):
            return distr(*(
                self(*coeffs) for coeffs in self.distribute(args)
                )).canonical
        return self(*args)


###############################################################################
###############################################################################
