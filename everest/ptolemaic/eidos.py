###############################################################################
''''''
###############################################################################


import inspect as _inspect
import types as _types
import weakref as _weakref

from everest.utilities import (
    format_argskwargs as _format_argskwargs,
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
    def process_namespace(meta, name, bases, namespace):
        namespace = super().process_namespace(name, bases, namespace)
        meta.add_fields(bases, namespace)
        meta.add_params(namespace)
        return namespace

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


class EidosBase(metaclass=Eidos):

    MERGETUPLES = ('FIELDS',)

    FIELDS = ()

    _req_slots__ = ('params', 'args', 'kwargs', '_epitaph')

    @classmethod
    def get_instance_epitaph(cls, args, kwargs, /):
        return cls.taphonomy.callsig_epitaph(
            cls._ptolemaic_class__, *args, **kwargs
            )

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    class ConcreteBase:

        __slots__ = ()

        @classmethod
        def construct(cls, /, *args, **kwargs):
            cache = {}
            try:
                bound = cls.parameterise(cache, *args, **kwargs)
            except Exception as exc:
                raise cls.param_exc(exc)(args, kwargs)
            epitaph = cls.get_instance_epitaph(bound.args, bound.kwargs)
            if (hexcode := epitaph.hexcode) in (pre := cls.premade):
                return pre[hexcode]
            return super().construct(
                bound, epitaph, _softcache=cache
                )

        def initialise(self, bound, epitaph, /, _softcache=None):
            self.args = bound.args
            self.kwargs = _types.MappingProxyType(bound.kwargs)
            self.params = _types.MappingProxyType(bound.arguments)
            self._epitaph = epitaph
            super().initialise(_softcache=_softcache)

        def finalise(self, /):
            self._ptolemaic_class__.premade[self.hexcode] = self
            super().finalise()

        ### Serialisation:

        def get_epitaph(self, /):
            return self._epitaph

        @property
        def epitaph(self, /):
            return self._epitaph

        ### Representations:

        def _repr(self, /):
            return f"{self.hashID}"

        def _str(self, /):
            return _format_argskwargs(*self.args, **self.kwargs)

        def __str__(self, /):
            return f"{self._ptolemaic_class__}({self._str()})"

        def _repr_pretty_(self, p, cycle):
            root = repr(self._ptolemaic_class__)
            if cycle:
                p.text(root + '{...}')
            elif not (args := self.args) or (kwargs := self.kwargs):
                return
            with p.group(4, root + '(', ')'):
                if args:
                    argit = iter(args)
                    p.breakable()
                    p.pretty(next(argit))
                    for val in argit:
                        p.text(',')
                        p.breakable()
                        p.pretty(val)
                    p.text(',')
                if kwargs:
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
