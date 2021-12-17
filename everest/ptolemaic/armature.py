###############################################################################
''''''
###############################################################################


import inspect as _inspect
import types as _types
import weakref as _weakref

from everest.utilities import (
    format_argskwargs as _format_argskwargs
    )

from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic


def get_parameter(arg, /):
    if isinstance(arg, _inspect.Parameter):
        return arg
    if isinstance(arg, str):
        return _inspect.Parameter(arg, 1)
    if isinstance(arg, tuple):
        return _inspect.Parameter(*arg)
    if isinstance(arg, dict):
        return _inspect.Parameter(**arg)
    raise TypeError(type(arg))


class Armature(_Ptolemaic):

    MERGETUPLES = ('FIELDS',)

    FIELDS = ()

    __slots__ = ('_arguments', '_args', '_kwargs', '_epitaph')

    premade = _weakref.WeakValueDictionary()

    @classmethod
    def add_fields(cls, /):
        sig = cls.__signature__ = \
            _inspect.Signature(map(get_parameter, cls.FIELDS))
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
        if (hexcode := epitaph.hexcode) in (pre := Armature.premade):
            return pre[hexcode]
        obj = super().__class_call__(bound, epitaph)
        pre[hexcode] = obj
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
