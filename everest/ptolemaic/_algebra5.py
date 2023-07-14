###############################################################################
''''''
###############################################################################


import abc as _abc
import types as _types
from collections import abc as _collabc
from functools import partial as _partial

from .system import System as _System
from .enumm import Enumm as _Enumm
from .wisp import Namespace as _Namespace


class Property(metaclass=_Enumm):

    IDEMPOTENT: None
    INVERTIBLE: None

    UNIQUE: None
    COMMUTATIVE: None
    ASSOCIATIVE: None


class RelationshipType(metaclass=_Enumm):

    IDENTITY: None
    INVERSE: None
    DISTROVER: None

    def __call__(self, /, *args, **kwargs):
        return Relationship(self, *args, **kwargs)


class Relationship(metaclass=_System):

    typ: POS[RelationshipType]
    participants: ARGS[str]


class Operator(metaclass=_System):
    '''Instances of this class represent algebraic operators '''
    '''like addition, multiplication, or negation.'''

    sources: tuple['Algebra'] = ()
    properties: tuple[Property] = ()
    relationships: tuple[Relationship] = ()

    @classmethod
    def _construct_(cls, params, /):
        raise RuntimeError(
            "Operators should only be instantiated as organs of algebras."
            )

    def __call__(self, /, *args):
        return Form(self, *args)


class Specification(metaclass=_System):

    sources: tuple['Algebra'] = ()
    properties: tuple[Property] = ()
    relationships: tuple[Relationship] = ()

    def __call__(self, algebra, /):
        return Operator.__class_alt_call__(
            self.sources, self.properties, self.relationships
            )


class Algebra(metaclass=_System):

    specs: KWARGS[Specification]

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        params.specs = {
            name: Specification(*spec) 
            if not isinstance(spec, Specification)
            else spec
            for name, spec in params.specs.items()
            }
        return params

    __slots__ = ('operators',)

    def __init__(self, /):
        super().__init__()
        ops = self.operators = {
            name: spec(self) for name, spec in self.specs.items()
            }
        for name, op in ops.items():
            self._register_innerobj(name, op)

    def __getattribute__(self, name, /):
        try:
            return object.__getattribute__(self, 'operators')[name]
        except (AttributeError, KeyError):
            return super().__getattribute__(name)


class Form(metaclass=_System):
    '''Instances of this type '''
    '''represent the results of algebraic operations '''
    '''as carried out by instances of the Operator class.'''

    operator: POS[Operator]
    arguments: ARGS['Form']


###############################################################################


alg = Algebra(
    zero = (),
    one = (),
    neg = (
        (None,),
        (),
        (RelationshipType.DISTROVER('add')),
        ),
    add = (
        (None, None),
        (Property.ASSOCIATIVE, Property.COMMUTATIVE),
        (
            RelationshipType.INVERSE('neg'),
            RelationshipType.IDENTITY('zero')
            ),
        ),
    rec = (
        (None,),
        (),
        (RelationshipType.DISTROVER('mul')),
        ),
    mul = (
        (None, None),
        (Property.ASSOCIATIVE, Property.COMMUTATIVE),
        (
            RelationshipType.INVERSE('neg'),
            RelationshipType.DISTROVER('add'),
            RelationshipType.IDENTITY('one')
            ),
        ),
    )
alg


###############################################################################


#     operators: KWARGS[Operator]

#     __slots__ = ('ops',)

#     def __init__(self, /):
#         super().__init__()
#         self.ops = _Namespace(**{
#             opname: _partial(Form, self, opname)
#             for opname in self.operators
#             })

#     @classmethod
#     def _canonise_unary_(cls, form, /):
#         operator = form.operator
#         arg = form.argument.canonical
#         if arg.operator is operator:
#             if operator.idempotent:
#                 return arg
#             if operator.invertible:
#                 return arg.argument
#             return arg
#         if dnames := operator.distrovers:
#             for dname in dnames:
#                 dop = 

#     def canonise(self, form, /):
#         if form.algebra is not self:
#             return form
#         if isinstance(form, Unary):
#             return self._canonise_unary_(form)

#     __slots__ = ('operators',)

#     def __initialise__(self, /):
#         ops = {}
#         for name, spec in self.specifications.items():
#             op = ops[name] = spec(self)
#             self._register_innerobj(name, op)
#         self.operators = ops
#         super().__initialise__()


#     class Specification(mroclass, metaclass=System):
#         '''Instances of this type '''
#         '''abstractly represent operators and their relationships '''
#         '''within the context of a certain type of Algebra.'''

#         name: POS[str]
#         typ: POS[str]
#         target: POS[Realm]
#         sources: ARGS[Realm]
#         properties: KWARGS

#         def __call__(self, algebra, /):
#             return getattr(algebra, self.typ).__class_alt_call__(
#                 self.target, *self.sources, **self.properties
#                 )


# class Realm(metaclass=_System):
#     '''Instances of this class abstractly represent the 'spaces' '''
#     '''between which algebraic operators operator.'''

#     def __contains__(self, other, /):
#         return False


# class Subject(metaclass=_System):
#     '''Instances of this class abstractly represent the sorts of entities '''
#     '''that Realms are imagined to contain. '''
#     '''Realms 'recognise' their subjects but not vice versa.'''

#     name: POS


# class Operator(metaclass=_System):
#     '''Instances of this class represent algebraic operators '''
#     '''like addition, multiplication, or negation.'''

#     target: POS[Realm]

#     @_abc.abstractmethod
#     def canonise_form(self, algebra, opname, /, *_, **__):
#         raise NotImplementedError


# class Unary(Operator):
#     '''Instances of this class represent algebraic operators '''
#     '''with only one argument, like negation (-a).'''

#     source: POS[Realm] = None
#     idempotent: KW[bool] = False
#     invertible: KW[bool] = False
#     distrovers: KW[tuple[str]] = ()

#     @classmethod
#     def _parameterise_(cls, /, *args, **kwargs):
#         params = super()._parameterise_(*args, **kwargs)
#         if params.source is None:
#             params.source = params.target
#         return params


# class Ennary(Operator):
#     '''Instances of this class represent algebraic operators '''
#     '''with multiple arguments, '''
#     '''with the proviso that all the arguments come from the same 'realm'; '''
#     '''a familiar example would be simple addition: (a+b).'''

#     source: POS[Realm] = None
#     unique: KW[bool] = False
#     commutative: KW[bool] = False
#     associative: KW[bool] = False
#     # identity: KW[_Form_] = None
#     # inverse: KW[Operator] = None
#     distrovers: KW[tuple[str]] = ()

#     @classmethod
#     def _parameterise_(cls, /, *args, **kwargs):
#         params = super()._parameterise_(*args, **kwargs)
#         if params.source is None:
#             params.source = params.target
#         return params
