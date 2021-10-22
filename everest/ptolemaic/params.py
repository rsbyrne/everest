###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import functools as _functools
import inspect as _inspect
import hashlib as _hashlib

from .ousia import Ousia as _Ousia, Blank as _Blank
from .primitive import Primitive as _Primitive
from . import _utilities

_caching = _utilities.caching
_word = _utilities.word


KINDS = dict(zip(
    ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs'),
    _inspect._ParameterKind,
    ))


def sort_params(params, /):
    params = sorted(params, key=(lambda x: x.default is not _inspect._empty))
    params = sorted(params, key=(lambda x: KINDS[x.kind]))
    return params


class ParamProp:
    
    __slots__ = ('param', 'kind', 'hint', 'name', 'default', 'parameter',)

    def __init__(self, param, name, default=_inspect.Parameter.empty, /):
        self.param = param
        self.name, self.default = name, default
        kind = self.kind = param.kind
        hint = self.hint = param.hint
        self.parameter = _inspect.Parameter(
            name, KINDS[param.kind], default=default, annotation=param.hint,
            )

    def __get__(self, instance, /, owner=None):
        return getattr(instance.params, self.name)

    def _repr(self):
        return f"name={self.name}, default={self.default}"

    def __repr__(self):
        return f"{type(self).__name__}({self._repr()})"


# class ParamProxy:

#     __slots__ = ('kind',)

#     def __init__(self, kind, /):
#         self.kind = kind

#     def __call__(self, *args, **kwargs):
#         return Param(self.kind, *args, **kwargs)

#     def __getitem__(self, arg, /):
#         return self.


class _ParamMeta(_Ousia):

    def __getattr__(cls, name, /):
        if name in KINDS:
            return Param(name)
        return super().__getattr__(name)


class Param(metaclass=_ParamMeta):

    KINDS = KINDS

    __slots__ = ('kind', 'hint',)

    @classmethod
    def _check_hint(cls, hint, /):
        if isinstance(hint, _Ousia):
            return hint
        if isinstance(type(hint), _Ousia):
            return hint
        if issubclass(hint, _Primitive):
            return hint
        raise TypeError(hint, type(hint))

    def __init__(self, kind='PosKw', hint=_Blank, /):
        if not kind in self.KINDS:
            raise ValueError(kind)
        self.kind = kind
        self.hint = self._check_hint(hint)

    def __call__(self, *args, **kwargs):
        return ParamProp(self, *args, **kwargs)

    @classmethod
    def __class_getitem__(cls, arg, /):
        return cls()[arg]

    def __getitem__(self, arg, /):
        return type(self)(self.kind, self.hint[arg])

    def __repr__(self, /):
        return f"Param.{self.kind}[{repr(self.hint)}]"


class Params(_collabc.Mapping):

    __slots__ = ('bound', 'arguments', '_getter', '_softcache')

    def parameterise(self, /, *args, **kwargs):
        return args, kwargs

    signed = False

    def __init__(self, /, *args, **kwargs):
        args, kwargs = self.parameterise(*args, **kwargs)
        bound = self.bound = self.sig.bind(*args, **kwargs)
        bound.apply_defaults()
        self.arguments = bound.arguments

    def __getattr__(self, name):
        if name in (arguments := self.arguments):
            return arguments[name]
        return super().__getattr__(name)

    @_caching.soft_cache()
    def __str__(self):
        args = self.arguments
        return ', '.join(map('='.join, zip(args, map(repr, args.values()))))

    @_caching.soft_cache()
    def __repr__(self):
        return f"{type(self).__name__}({self.__str__()})"

    @property
    @_caching.soft_cache()
    def hashcode(self):
        content = str(self).encode()
        return _hashlib.md5(content).hexdigest()

    @property
    @_caching.soft_cache()
    def hashint(self):
        return int(self.hashcode, 16)

    @property
    @_caching.soft_cache()
    def hashID(self):
        return _word.get_random_english(seed=self.hashint, n=2)

    def __getitem__(self, arg, /):
        return self.arguments[arg]

    def __iter__(self, /):
        return iter(self.arguments)

    def __len__(self, /):
        return len(self.arguments)

    @classmethod
    def __init_subclass__(cls, /, *, sig, parameterise, **kwargs):
        if cls.signed:
            raise TypeError(f"{type(cls)} already signed.")
        cls.sig = sig
        cls.parameterise = parameterise
        cls.signed = True
        super().__init_subclass__(**kwargs)

    @classmethod
    def __class_getitem__(cls, arg, /):
        return type(cls)(
            f"{cls.__name__}[{repr(arg)}]",
            (cls,),
            dict(),
            sig=arg.__signature__,
            parameterise=arg.parameterise,
            )


###############################################################################
###############################################################################
