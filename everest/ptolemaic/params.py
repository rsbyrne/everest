###############################################################################
''''''
###############################################################################


from inspect import (
    Parameter as _Parameter,
    _ParameterKind,
    )
import functools as _functools
import hashlib as _hashlib
import itertools as _itertools

from . import _utilities

_caching = _utilities.caching
_word = _utilities.word


class Param:

    __slots__ = ('name', 'default', 'parameter',)

    hint = _Parameter.empty
    kind = _ParameterKind.POSITIONAL_OR_KEYWORD

    def __init__(self, name, default=_Parameter.empty, /):
        self.name, self.default = name, default
        self.parameter = _Parameter(
            name, self.kind,
            default=default, annotation=self.hint,
            )

    def __get__(self, instance, /, owner=None):
        return getattr(instance.params, self.name)

    @classmethod
    def __class_getitem__(cls, arg: type, /):
        return type(
            f"{cls.__name__}[{arg.__name__}]",
            (cls,),
            dict(hint=arg),
            )

    def _repr(self):
        return f"name={self.name}, default={self.default}"

    def __repr__(self):
        return f"{type(self).__name__}({self._repr()})"


for kind, nm in zip(_ParameterKind, ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs')):
    if nm == 'PosKw':
        subcls = Param
    else:
        subcls = type(f"{Param.__name__}.{nm}", (Param,), dict(kind=kind))
    setattr(Param, nm, subcls)


class Params:

    __slots__ = ('bound', 'arguments', '_getter', '_softcache')

    def __init__(self, signature, /, *args, **kwargs):
        object.__setattr__(self, '_softcache', dict())
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        object.__setattr__(self, 'bound', bound)
        arguments = bound.arguments
        object.__setattr__(self, 'arguments', arguments)
        getter = bound.arguments.__getitem__
        object.__setattr__(self, '_getter', getter)

    @property
    def __getattr__(self):
        return self._getter

    def __setattr__(self, *args):
        raise TypeError(f"Cannot set attributes on {type(self)}")

    def __delattr__(self, *args):
        raise TypeError(f"Cannot delete attributes on {type(self)}")

    @property
    def args(self):
        return self.bound.args

    @property
    def kwargs(self):
        return self.bound.kwargs

    @_caching.soft_cache(None)
    def __str__(self):
        args = self.arguments
        return ', '.join(map('='.join, zip(args, map(repr, args.values()))))

    @_caching.soft_cache(None)
    def __repr__(self):
        return f"{type(self).__name__}({self.__str__()})"

    @_caching.soft_cache(None)
    def hashcode(self):
        content = str(self).encode()
        return _hashlib.md5(content).hexdigest()

    @_caching.soft_cache(None)
    def hashint(self):
        return int(self.hashcode(), 16)

    @_caching.soft_cache(None)
    def hashstr(self):
        return _word.get_random_english(
            seed=self.hashint(),
            n=2,
            )


class Binder:

    __slots__ = ('args', 'kwargs')

    def __init__(self, /):
        self.args, self.kwargs = [], {}

    def __call__(self, /, *args, **kwargs):
        self.args.extend(args)
        self.kwargs.update(kwargs)


###############################################################################
###############################################################################
