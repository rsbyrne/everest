###############################################################################
''''''
###############################################################################


import inspect as _inspect
import functools as _functools
import hashlib as _hashlib
import itertools as _itertools
import more_itertools as _mitertools

from . import _utilities

_caching = _utilities.caching
_word = _utilities.word


def get_hintstr(hint):
    if isinstance(hint, tuple):
        return f"({', '.join(map(get_hintstr, hint))})"
    if isinstance(hint, type):
        return hint.__name__
    return repr(hint)


def get_hint(hints):
    nhints = len(hints)
    if nhints:
        if nhints == 1:
            return hints[0]
        return hints
    return _inspect._empty


class ParamMeta(type):

    _kinds = dict(zip(
        _inspect._ParameterKind,
        ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs')
        ))
    _revkinds = dict(zip(_kinds.values(), _kinds.keys()))
    _defaultkind = _inspect._ParameterKind.POSITIONAL_OR_KEYWORD

    def __new__(meta,
            name, bases, namespace,
            kind=None,
            hint=_inspect._empty,
            **kwargs
            ):

        bases = tuple(_mitertools.unique_everseen(bases))

        if isinstance(kind, str):
            kind = meta._revkinds[kind]
        bks = (base.kind for base in bases if isinstance(base, meta))
        kinds = (*bks, kind)
        kinds = tuple(set(kind for kind in kinds if kind is not None))
        nkinds = len(kinds)
        if nkinds:
            if nkinds > 1:
                raise TypeError
            kind = kinds[0]
        else:
            kind = None
        kindstr = meta._kinds[meta._defaultkind if kind is None else kind]

        bhs = (base.hints for base in reversed(bases) if isinstance(base, meta))
        hints = (*_itertools.chain.from_iterable(bhs), hint)
        hints = tuple(hint for hint in hints if hint is not _inspect._empty)
        hintstr = get_hintstr(hints)[1:-1]

        namespace.update(
            hints=hints,
            hint=get_hint(hints),
            kind=kind,
            _rootname=name,
            )

        name += f".{kindstr}"
        if hintstr:
            name += f"[{hintstr}]"

        return super().__new__(meta, name, bases, namespace, **kwargs)

    def __getitem__(cls, arg, /):
        if arg is cls:
            return cls
        if isinstance(arg, type(cls)):
            return type(cls)(arg._rootname, (cls, arg), {}, kind=arg.kind)
        return type(cls)(cls._rootname, (cls,), {}, hint=arg, kind=cls.kind)


class Param(metaclass=ParamMeta):

    __slots__ = ('name', 'default', 'parameter',)

    def __init__(self, name, default=_inspect.Parameter.empty, /):
        self.name, self.default = name, default
        kind = self.kind
        if kind is None:
            kind = type(self)._defaultkind
        self.parameter = _inspect.Parameter(
            name, kind, default=default, annotation=self.hint,
            )

    def __get__(self, instance, /, owner=None):
        return getattr(instance.params, self.name)

    def _repr(self):
        return f"name={self.name}, default={self.default}"

    def __repr__(self):
        return f"{type(self).__name__}({self._repr()})"


for name in Param._revkinds:
    subcls = type(Param)(Param._rootname, (Param,), {}, kind=name)
    setattr(Param, name, subcls)


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
