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

from . import (
    caching as _caching,
    word as _word,
    )


class Param:

    __slots__ = ('annotation', 'kind')

    def __init__(self,
            annotation: str = _Parameter.empty, /, *,
            kind: _ParameterKind
            ):
        self.annotation, self.kind = annotation, kind

    def __call__(self, name: str, default=_Parameter.empty, /):
        return _Parameter(
            name, self.kind,
            default=default, annotation=self.annotation,
            )

    def __repr__(self):
        return (
            f"{type(self).__name__}"
            f"({self.annotation}, kind={self.kind})"
            )


for kind, alias in zip(
        _ParameterKind,
        ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs'),
        ):
    setattr(Param, alias, _functools.partial(Param, kind=kind))


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


class Bind:

    __slots__ = ('checker', 'args', 'kwargs')

    def __init__(self, checker, /):
        self.checker = checker
        self.args, self.kwargs = [], {}

    def __call__(self, /, *args, **kwargs):
        self.args.extend(args)
        self.kwargs.update(kwargs)

    def get_params(self, signature, /):
        args, kwargs = self.args, self.kwargs
        bad = tuple(_itertools.filterfalse(
            self.checker, _itertools.chain(args, kwargs.values())
            ))
        if bad:
            raise TypeError(f"Bad inputs: {bad}")
        return Params(signature, *args, **kwargs)


###############################################################################
###############################################################################
