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
    PtolemaicMeta as _PtolemaicMeta,
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


class ArmatureMeta(_PtolemaicMeta):
    ...


class Armature(_Ptolemaic, metaclass=ArmatureMeta):

    MERGETUPLES = ('FIELDS',)

    FIELDS = ()

    __slots__ = ('_arguments', '_args', '_kwargs', '_epitaph')

    premade = _weakref.WeakValueDictionary()

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
                f"        return self._arguments['{name}']",
                f"    except IndexError:",
                f"        raise AttributeError({repr(name)})",
                )))
            setattr(cls, name, eval(name))

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.add_fields()

    @classmethod
    def parameterise(cls, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    @classmethod
    def instantiate(cls, bound, epitaph, /):
        obj = cls.create_object()
        obj._args, obj._kwargs = bound.args, bound.kwargs
        obj._arguments = _types.MappingProxyType(bound.arguments)
        obj._epitaph = epitaph
        obj.__init__()
        return obj

    @classmethod
    def get_instance_epitaph(cls, args, kwargs, /):
        return cls.clstaphonomy.callsig_epitaph(
            cls._ptolemaic_class__, *args, **kwargs
            )

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        bound = cls.parameterise(*args, **kwargs)
        epitaph = cls.get_instance_epitaph(bound.args, bound.kwargs)
#         if (hexcode := epitaph.hexcode) in (pre := Armature.premade):
#             return pre[hexcode]
        obj = super().__class_call__(bound, epitaph)
#         pre[hexcode] = obj
        return obj

    def _repr(self, /):
        return _format_argskwargs(*self._args, **self._kwargs)

    def get_epitaph(self, /):
        raise NotImplementedError

    @property
    def epitaph(self, /):
        return self._epitaph


###############################################################################
###############################################################################
