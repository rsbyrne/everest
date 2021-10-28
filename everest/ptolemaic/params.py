###############################################################################
''''''
###############################################################################


import inspect as _inspect
import hashlib as _hashlib
import collections as _collabc

from .ousia import Ousia as _Ousia
from .eidos import Eidos as _Eidos
from . import _utilities

_caching = _utilities.caching
_word = _utilities.word


KINDS = dict(zip(
    ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs'),
    _inspect._ParameterKind,
    ))


class ParamMeta(_Ousia):

    for kind in KINDS:
        exec('\n'.join((
            '@property',
            f'def {kind}(cls, /):'
            f"    return cls(kind='{kind}')"
            )))


class Param(metaclass=ParamMeta):

    _req_slots__ = ('name', 'value', 'kind', 'hint', 'parameter', 'inps')

    @classmethod
    def _check_hint(cls, hint, /):
        return hint

    def __init__(self, /, *,
            name='anon',
            hint=_Eidos,
            kind='PosKw',
            value=NotImplemented,
            ):
        if not kind in KINDS:
            raise ValueError(kind)
        hint = self._check_hint(hint)
        self.kind, self.hint = kind, hint
        if kind in {'Args', 'Kwargs'}:
            if value is not NotImplemented:
                raise TypeError
        self.name, self.value = name, value
        default = (
            _inspect.Parameter.empty if value is NotImplemented
            else value
            )
        self.parameter = _inspect.Parameter(
            name, KINDS[kind], default=default, annotation=hint,
            )
        self.inps = dict(
            name=self.name, hint=self.hint, kind=self.kind, value=self.value
            )
        super().__init__()

    def __call__(self, **kwargs):
        return type(self).construct(**(self.inps | kwargs))

    def __getitem__(self, arg, /):
        if isinstance(arg, Param):
            return self(**{**arg.inps, 'hint': self.hint[arg.hint]})
        return self(hint=self.hint[arg])

    def __repr__(self, /):
        return (
            f"Param.{self.kind}[{repr(self.hint)}]"
            f"({self.name}={self.value})"
            )

    def __get__(self, instance, /, owner=None):
        return instance.params[self.name]


class Signature(_collabc.Mapping, metaclass=_Ousia):

    _req_slots__ = ('parameters', 'signature', 'paramdict')

    @staticmethod
    def sort_params(params, /):
        params = sorted(
            params,
            key=(lambda x: x.parameter.default is not _inspect._empty)
            )
        params = sorted(
            params,
            key=(lambda x: x.parameter.kind)
            )
        return params

    def __init__(self, *parameters):
        parameters = self.parameters = tuple(self.sort_params(parameters))
        self.signature = _inspect.Signature(
            param.parameter for param in parameters
            )
        self.paramdict = {param.name: param for param in parameters}
        super().__init__()

    def __iter__(self, /):
        return self.paramdict.__iter__()

    def __len__(self, /):
        return self.paramdict.__len__()

    def __getitem__(self, key, /):
        return self.paramdict.__getitem__(key)

    def __getattr__(self, name):
        if name in (paramdict := self.paramdict):
            return paramdict[name]
        return super().__getattr__(name)

    def bind(self, /, *args, **kwargs):
        bound = self.signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    def __call__(self, /, *args, **kwargs):
        bound = self.signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return Params(**bound.arguments)


class Params(_collabc.Mapping, metaclass=_Ousia):

    _req_slots__ = ('parameters',)

    def __init__(self, **parameters):
        super().__init__()
        self.parameters = parameters

    def __getattr__(self, name):
        if name in (parameters := self.parameters):
            return parameters[name]
        return super().__getattr__(name)

    @_caching.soft_cache()
    def __str__(self):
        args = self.parameters
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
        return self.parameters[arg]

    def __iter__(self, /):
        return iter(self.parameters)

    def __len__(self, /):
        return len(self.parameters)


# class Registrar:

#     __slots__ = ('_args', '_kwargs', 'signature', 'bound')

#     def __init__(self, signature, /):
#         self.signature = signature
#         self._args, self._kwargs = [], {}
#         self.bound = signature.bind_partial()

#     def __call__(self, *args, **kwargs):
#         _args, _kwargs = self._args, self._kwargs
#         self._args.extend(args)
#         self._kwargs.update(kwargs)
#         try:
#             _ = self.signature.bind_partial(*_args, **_kwargs)
#         except TypeError as exc:
#             raise TypeError from exc

#     @staticmethod
#     def _process_int_key(arguments, key):
#         if isinstance(key, int):
#             key = tuple(arguments.keys()).index(key)
#         return key

#     def __getitem__(self, key, /):
#         arguments = self.bound.arguments
#         key = self._process_int_key(arguments, key)
#         return arguments[key]

#     def __setitem__(self, key, val, /):
#         arguments = self.bound.arguments
#         key = self._process_int_key(arguments, key)
#         arguments[key] = val

#     def __delitem__(self, key, /):
#         arguments = self.bound.arguments
#         key = self._process_int_key(arguments, key)
#         del arguments[key]


###############################################################################
###############################################################################
