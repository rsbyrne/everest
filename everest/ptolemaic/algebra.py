###############################################################################
''''''
###############################################################################


from functools import partial as _partial, lru_cache as _lru_cache

from .system import System as _System
from .essence import Essence as _Essence


class Realm(metaclass=_System):


    class Subject(mroclass, metaclass=_System):

        realm: POS['..']

        @classmethod
        @_lru_cache
        def __class_get__(cls, instance, owner=None, /):
            if instance is None:
                return cls
            return _partial(cls, instance)


    class Operation(mroclass('.Subject')):

        realm: POS['..']
        operator: POS['Algebra.Subject']
        arguments: ARGS['Realm.Subject']


class Algebra(Realm):


    def __call__(self, opname, target, *sources, **properties):
        arity = len(sources)
        if arity == 0:
            cll = self.Nullary
        if arity == 1:
            cll = self.Unary
        elif arity == 2:
            cll = self.Binary
        else:
            raise ValueError
        return cll(opname, target, *sources, **properties)


    class Subject(mroclass):

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            cls.algarity = cls.__fields__.npos - 2

        target: POS[Realm]

        def __call__(self, /, *args):
            if len(args) != self.algarity:
                raise ValueError(
                    f"Wrong number of args for this operator: "
                    f"{len(args)} != arity={self.algarity}"
                    )
            return self.target.Operation(self, *args)


    class Nullary(mroclass('.Subject')):

        ...


    class Unary(mroclass('.Subject')):

        source = field('target', kind=POS, hint=Realm)
        idempotent: KW[bool] = False
        invertible: KW[bool] = False

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)


    class Binary(mroclass('.Subject')):

        lsource = rsource = field('target', kind=POS, hint=Realm)
        commutative: KW[bool] = False
        associative: KW[bool] = False
        identity: KW['Realm.Subject'] = None
        distributive: KW['Algebra.Subject'] = None


###############################################################################
###############################################################################
