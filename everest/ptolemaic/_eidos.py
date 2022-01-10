###############################################################################
''''''
###############################################################################


import inspect as _inspect
import types as _types
import weakref as _weakref

from everest.utilities import (
    format_argskwargs as _format_argskwargs,
    caching as _caching,
    )

from everest.ptolemaic.ousia import Ousia as _Ousia

from everest.ptolemaic.exceptions import ParameterisationException

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


def get_parameter_value(bases, namespace, name):
    if name in namespace:
        return namespace[name]
    for base in bases:
        if hasattr(base, name):
            return getattr(base, name)
    return _empty


class ParamProp:

    __slots__ = ('name',)

    def __init__(self, name: str, /):
        self.name = name

    def __get__(self, instance, _=None):
        try:
            return instance.params[self.name]
        except KeyError:
            raise AttributeError(self.name)
        except AttributeError:
            return self


class Eidos(_Ousia):

    @classmethod
    def collect_fields(meta, bases, namespace, /):
        if 'FIELDS' in namespace:
            yield from map(get_parameter, namespace['FIELDS'])
        if '__annotations__' in namespace:
            for name, note in namespace['__annotations__'].items():
                value = get_parameter_value(bases, namespace, name)
                yield _Parameter(name, 1, annotation=note, default=value)

    @classmethod
    def add_fields(meta, bases, namespace, /):
        fields = list(meta.collect_fields(bases, namespace))
        fields.sort(key=(lambda x: x.default is not _empty))
        fields.sort(key=(lambda x: x.kind))
        fields = namespace['FIELDS'] = tuple(fields)
        signature = namespace['_signature_'] = _inspect.Signature(fields)

    @classmethod
    def add_params(meta, namespace, /):
        for name in namespace['_signature_'].parameters:
            namespace[name] = ParamProp(name)
    
    @classmethod
    def pre_create_class(meta, *args):
        name, bases, namespace = super().pre_create_class(*args)
        meta.add_fields(bases, namespace)
        meta.add_params(namespace)
        return name, bases, namespace

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.premade = _weakref.WeakValueDictionary()

    @property
    def __signature__(cls, /):
        return cls._signature_

    @property
    def param_exc(cls, /):
        def func(message=None, /):
            def subfunc(args, kwargs):
                return ParameterisationException((args, kwargs), cls, message)
            return subfunc
        return func

    def __call__(cls, /, *args, **kwargs):
        cache = {}
        try:
            bound = cls.parameterise(cache, *args, **kwargs)
        except Exception as exc:
            raise cls.param_exc(exc)(args, kwargs)
        epitaph = cls.taphonomy.callsig_epitaph(
            cls._ptolemaic_class__, *bound.args, **bound.kwargs
            )
        if (hexcode := epitaph.hexcode) in (pre := cls.premade):
            return pre[hexcode]
        obj = object.__new__(cls.Concrete)
        obj._epitaph = epitaph
        obj._softcache = cache
        obj.params = _types.MappingProxyType(bound.arguments)
        obj.__init__()
        obj.freezeattr.toggle(True)
        pre[hexcode] = obj
        return obj


class EidosBase(metaclass=Eidos):

    MERGETUPLES = ('FIELDS',)

    _req_slots__ = ('params', 'args', 'kwargs', '_epitaph')

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    ### Implementing serialisation:

    @property
    def epitaph(self, /):
        return self._epitaph

    ### Representations:

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def __hash__(self, /):
        return self.hashint

    def _repr(self, /):
        return self.hashID

    def _str(self, /):
        return ', '.join(
            f"{name}={value}"
            for name, value in self.params.items()
            )

    def __str__(self, /):
        return f"{self._ptolemaic_class__}({self._str()})"

    def _repr_pretty_(self, p, cycle):
        root = repr(self)
        if cycle:
            p.text(root + '{...}')
        elif not (kwargs := self.params):
            p.text(root)
        else:
            with p.group(4, root + '(', ')'):
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


###############################################################################
###############################################################################
