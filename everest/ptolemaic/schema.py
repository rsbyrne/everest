###############################################################################
''''''
###############################################################################


import functools as _functools
import collections as _collections
import operator as _operator
import inspect as _inspect
import weakref as _weakref

from everest.utilities import caching as _caching, FrozenMap as _FrozenMap
from everest.classtools import add_defer_meths as _add_defer_meths

from everest.ptolemaic.tekton import CallSig as _CallSig
from everest.ptolemaic.ousia import Ousia as _Ousia


KINDS = dict(zip(
    ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs'),
    _inspect._ParameterKind,
    ))


class Generic:

    def __class_getitem__(cls, arg, /):
        return arg


class ParamProp:

    __slots__ = ('name',)

    def __init__(self, name: str, /):
        self.name = name

    def __get__(self, instance, _=None):
        return instance.params[self.name]


class ParamMeta(_Ousia):

    for kind in KINDS:
        exec('\n'.join((
            '@property',
            f'def {kind}(cls, /):'
            f"    return cls(kind='{kind}')"
            )))


class Param(metaclass=ParamMeta):

    _req_slots__ = ('hint', 'value', 'kind')

    @classmethod
    def _check_hint(cls, hint, /):
        return hint

    def __init__(self, /,
            hint=Generic,
            value=NotImplemented,
            kind='PosKw',
            ):
        if not kind in KINDS:
            raise ValueError(kind)
        hint = self._check_hint(hint)
        self.kind, self.hint = kind, hint
        if kind in {'Args', 'Kwargs'}:
            if value is not NotImplemented:
                raise TypeError
        self.value = value
        super().__init__()

    @property
    def truekind(self, /):
        return KINDS[self.kind]

    @property
    def default(self, /):
        value = self.value
        return _inspect.Parameter.empty if value is NotImplemented else value

    def __call__(self, **kwargs):
        return self.__class__(**dict(
            hint=self.hint, kind=self.kind, value=self.value
            ) | kwargs)

    @classmethod
    def _ptolemaic_getitem__(cls, arg, /):
        return cls()[arg]

    def __getitem__(self, arg, /):
        if isinstance(arg, Param):
            return self(**{**arg.inps, 'hint': self.hint[arg.hint]})
        return self(hint=self.hint[arg])

    def __repr__(self, /):
        return (
            f"Param.{self.kind}[{repr(self.hint)}]"
            f"({self.name}={self.value})"
            )

    def get_parameter(self, name: str, /):
        return _inspect.Parameter(
            name, self.truekind,
            default=self.default, annotation=self.hint,
            )

    def __gt__(self, arg, /):
        if arg.value is NotImplemented:
            if self.value is not NotImplemented:
                return True
        return self.truekind > arg.truekind

    def __set_name__(self, owner, name):
        self.ownernames[owner._ptolemaic_class__] = name

    def __get__(self, instance, owner):
        owner = owner._ptolemaic_class__
        return instance.params[self.ownernames[owner]]


class Sig(metaclass=_Ousia):

    _req_slots__ = ('paramdict', 'signature')

    @classmethod
    def parameterise(cls, register, /, **params):
        register(**dict(sorted(params.items(), key=lambda x: x[1])))

    def __init__(self, **params):
        self.paramdict = _FrozenMap(params)
        self.signature = _inspect.Signature(
            param.get_parameter(name) for name, param in params.items()
            )
        super().__init__()

    def __call__(self, /, *args, **kwargs):
        return _CallSig.signature_call(self.signature, args, kwargs)

with Sig.clsmutable:
    _add_defer_meths('paramdict', like=dict)(Sig)


class Schema(_Ousia):
    '''
    The metaclass of all Schema classes.
    '''

    def _collect_params(cls, /):
        params = dict()
        clsdict = cls.__dict__
        for name, note in cls.__annotations__.items():
            deq = params.setdefault(name, _collections.deque())
            value = clsdict[name] if (non := name in clsdict) else NotImplemented
            if note is Param:
                param = note(value=value)
            elif isinstance(note, Param):
                if not non:
                    param = note(value=value)
            else:
                param = Param(note, value)
            deq.append(param)
        for base in cls.__bases__:
            if not isinstance(base, Schema):
                continue
            for name, param in base.sig.items():
                deq = params.setdefault(name, _collections.deque())
                deq.append(param)
        return {
            name: _functools.reduce(_operator.getitem, reversed(deq))
            for name, deq in params.items()
            }

    @property
    @_caching.soft_cache('_class_softcache')
    def sig(cls, /):
        return Sig(**cls._collect_params())

    def _ptolemaic_concrete_namespace__(cls, /):
        return {
            **super()._ptolemaic_concrete_namespace__(),
            **{name: ParamProp(name) for name in cls.sig},
            }


class SchemaBase(metaclass=Schema):

    __slots__ = ()

    @classmethod
    def get_signature(cls, /):
        return cls.sig.signature

    def initialise(self, /):
        self.__init__()


###############################################################################
###############################################################################
