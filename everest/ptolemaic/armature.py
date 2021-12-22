###############################################################################
''''''
###############################################################################


import inspect as _inspect
import types as _types
import weakref as _weakref
import collections as _collections

from everest.utilities import (
    format_argskwargs as _format_argskwargs
    )

from everest.ptolemaic.ptolemaic import (
    Ptolemaic as _Ptolemaic,
    )

_Parameter = _inspect.Parameter
_empty = _inspect._empty


def get_parameter(arg, /):
    if isinstance(arg, _Parameter):
        return arg
    if isinstance(arg, str):
        return _Parameter(arg, 1)
    if isinstance(arg, tuple):
        return _Parameter(*arg)
    if isinstance(arg, dict):
        return _Parameter(**arg)
    raise TypeError(type(arg))


def collect_fields(cls, /):
    yield from map(get_parameter, cls.FIELDS)
    anno = cls.__annotations__
    values = tuple(
        getattr(cls, name) if hasattr(cls, name) else _empty
        for name in anno
        )
    for name, note, value in zip(anno, anno.values(), values):
        yield _Parameter(name, 1, annotation=note, default=value)


class Armature(_Ptolemaic):

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.premade = _weakref.WeakValueDictionary()
        cls.add_fields()


class ArmatureBase(metaclass=Armature):

    MERGETUPLES = ('FIELDS',)

    FIELDS = ()

    __slots__ = ('arguments', 'args', 'kwargs', '_epitaph')

    @classmethod
    def add_fields(cls, /):
        FIELDS = cls.FIELDS = tuple(sorted(
            sorted(collect_fields(cls), key = lambda x: x.kind),
            key = lambda x: x.default is not _empty,
            ))
        sig = cls.__signature__ = _inspect.Signature(FIELDS)
        for name in sig.parameters:
            exec('\n'.join((
                f"@property",
                f"def {name}(self, /):",
                f"    try:",
                f"        return self.arguments['{name}']",
                f"    except IndexError:",
                f"        raise AttributeError({repr(name)})",
                )))
            setattr(cls, name, eval(name))

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    @classmethod
    def get_instance_epitaph(cls, args, kwargs, /):
        return cls.taphonomy.callsig_epitaph(
            cls._ptolemaic_class__, *args, **kwargs
            )

    @classmethod
    def instantiate(cls, /, *args, **kwargs):
        cache = {}
        bound = cls.parameterise(cache, *args, **kwargs)
        epitaph = cls.get_instance_epitaph(bound.args, bound.kwargs)
#         if (hexcode := epitaph.hexcode) in (pre := cls.premade):
#             return pre[hexcode]
        return super().instantiate(
            bound, epitaph, _softcache=cache, _weakcache=None
            )

    def initialise(self, bound, epitaph, /, _softcache=None, _weakcache=None):
        self.args = bound.args
        self.kwargs = _types.MappingProxyType(bound.kwargs)
        self.arguments = _types.MappingProxyType(bound.arguments)
        self._epitaph = epitaph
        super().initialise(_softcache=_softcache, _weakcache=_weakcache)

    def finalise(self, /):
#         self._ptolemaic_class__.premade[self.hexcode] = self
        super().finalise()

    def _repr(self, /):
        return f"'{self.hashID}'"

    def _str(self, /):
        return _format_argskwargs(*self.args, **self.kwargs)

    def __str__(self, /):
        return f"{self._ptolemaic_class__}({self._str()})"

    def _repr_pretty_(self, p, cycle):
        typnm = repr(self._ptolemaic_class__)
        if cycle:
            p.text(typnm + '{...}')
        else:
            with p.group(4, typnm + '(', ')'):
                if args := self.args:
                    argit = iter(args)
                    p.breakable()
                    p.pretty(next(argit))
                    for val in argit:
                        p.text(',')
                        p.breakable()
                        p.pretty(val)
                    p.text(',')
                if kwargs := self.kwargs:
                    kwargit = iter(kwargs.items())
                    p.breakable()
                    key, val = next(kwargit)
                    p.text(key)
                    p.text(' = ')
                    p.pretty(val)
                    for key, val in kwargit:
                        p.text(',')
                        p.breakable()
                        p.text(key)
                        p.text(' = ')
                        p.pretty(val)
                    p.text(',')
                p.breakable()

    def get_epitaph(self, /):
        return self._epitaph

    @property
    def epitaph(self, /):
        return self._epitaph


###############################################################################
###############################################################################

