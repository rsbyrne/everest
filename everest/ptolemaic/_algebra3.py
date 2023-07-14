###############################################################################
''''''
###############################################################################


from functools import partial as _partial
import abc as _abc
import weakref as _weakref
import itertools as _itertools
from collections import deque as _deque

from .demiurge import Demiurge as _Demiurge
from .system import System as _System
from .essence import Essence as _Essence
from .pathget import PathGet as _PathGet


class Realm(metaclass=_System):

    ...


class Subject(metaclass=_System):

    identifier: POS['Form']

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        params.identifier = params.identifier.canonise()


class Form(metaclass=_System):

    operator: POS['Realm.Operator']
    arguments: ARGS['Form']

    def canonise(self, /):
        form = self.operator.canonise(*self.arguments)
        if form is NotImplemented:
            form = self
        return form

    @prop
    def subject(self, /):
        return Subject(self)


def distribute(factors, under, /):
    chunks = _deque()
    buff = _deque()
    for factor in factors:
        if factor.operator is under:
            chunks.append(tuple((*buff, term) for term in factor.arguments))
            buff.clear()
        else:
            buff.append(factor)
    if chunks:
        chunks.append(tuple((*term, *buff) for term in chunks.pop()))
        return tuple(map(tuple, map(
            _itertools.chain.from_iterable, _itertools.product(*chunks)
            )))
    return (tuple(buff),)


class Operator(metaclass=_Demiurge):


    class _DemiBase_(ptolemaic):

        realm: POS['Realm']

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            cls.algarity = cls.__fields__.npos - 1

        def __call__(self, /, *args):
            return Form(self, *args)

        @_abc.abstractmethod
        def canonise(self, /, *_):
            raise NotImplementedError


    class Nullary(demiclass):

        def canonise(self, /):
            return NotImplemented


    class Unary(demiclass):

        source = field('realm', kind=POS, hint='Realm')
        idempotent: KW[bool] = False
        invertible: KW[bool] = False

        def canonise(self, argument, /):
            argument = argument.canonise()
            if argument.operator is self:
                if self.idempotent:
                    return argument
                if self.invertible:
                    return argument.arguments[0]
            return NotImplemented


    class Ennary(demiclass):

        sources = field('realm', kind=POS, hint='Realm')
        unique: KW[bool] = False
        commutative: KW[bool] = False
        associative: KW[bool] = False
        identity: KW[Noum] = None
        distributive: KW['Realm.Operator'] = None

        def __call__(self, /, *args):
            if not args:
                identity = self.identity
                if identity is None:
                    raise ValueError("No args!")
                return identity
            if len(args) == 1:
                return args[0]
            return Form(self, *args)

        def canonise(self, /, *args):
            inargs = args = tuple(arg.canonise() for arg in args)
            if self.associative:
                args = _itertools.chain.from_iterable(
                    arg.arguments if arg.operator is self else (arg,)
                    for arg in args
                    )
            if self.unique:
                if self.commutative:
                    args = sorted(set(args))
                else:
                    seen = set()
                    processed = []
                    for arg in args:
                        if arg not in seen:
                            processed.append(arg)
                            seen.add(arg)
                    args = tuple(args)
            elif self.commutative:
                args = sorted(args)
            if hasidentity := (identity := self.identity) is not None:
                args = tuple(arg for arg in args if arg is not identity)
            else:
                args = tuple(args)
            if (distr := self.distributive):
                return distr(
                    *(self(*factors) for factors in distribute(args, distr))
                    )
            return self(*args)


    #     class Binary(mroclass('.Operator')):

    #         lsource = rsource = field('realm', kind=POS, hint='Realm')
    #         commutative: KW[bool] = False
    #         associative: KW[bool] = False
    #         identity: KW[Noum] = None
    #         distributive: KW['Realm.Operator'] = None

    #         def canonise(self, larg, rarg, /):
    #             if self.commutative:
    #                 larg, rarg = sorted((larg, rarg))
            


###############################################################################
###############################################################################


# class Algebra(_System):

#     @classmethod
#     def _yield_bodymeths(meta, body, /):
#         yield from super()._yield_bodymeths(body)
#         yield 'operator', _partial(_operator_bodymeth_, body)


# def _operator_bodymeth_(body, arg0=0, /, *argn, realm=None, **kwargs):
#     if realm is None:
#         realm = _PathGet('.')
#     if isinstance(arg0, _PathGet):
#         arg0 = arg0(body.namespace)
#     if isinstance(arg0, type):
#         optyp = arg0
#         args = argn
#     else:
#         if isinstance(arg0, int):
#             if argn:
#                 raise ValueError(
#                     "Cannot pass both int flag and sources to operator constructor."
#                     )
#             args = tuple(NotImplemented for _ in range(arg0))
#         else:
#             args = (arg0, *argn)
#         arity = len(args)
#         if arity == 0:
#             optyp = body['Nullary']
#         elif arity == 1:
#             optyp = body['Unary']
#         elif arity == 2:
#             optyp = body['Binary']
#         else:
#             raise ValueError
#     return body['organ'](
#         **optyp.__signature__.bind_partial(realm, *args, **kwargs).arguments,
#         )(optyp)