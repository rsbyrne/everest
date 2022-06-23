###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import types as _types
import inspect as _inspect

from .essence import Essence as _Essence


class Urgon(_Essence):

    @classmethod
    def _yield_bodymeths(meta, /):
        yield from super()._yield_bodymeths()
        for typ in meta._smartattrtypes:
            nm = typ.__name__.lower()
            yield nm, getattr(typ, '__body_call__')
    
    @classmethod
    def _yield_smartattrtypes(meta, /):
        return
        yield

    @classmethod
    def _yield_mergenames(meta, body, /):
        yield from super()._yield_mergenames(body)
        for typ in meta._smartattrtypes:
            yield (
                typ.__merge_name__,
                typ.__merge_dyntyp__,
                typ.__merge_fintyp__,
                )

    @classmethod
    def __meta_init__(meta, /):
        meta._smartattrtypes = tuple(meta._yield_smartattrtypes())
        super().__meta_init__()


class _UrgonBase_(metaclass=Urgon, _isbasetyp_=True):

    @classmethod
    def _get_signature(cls, /):
        try:
            func = cls.__class_call__
        except AttributeError:
            func = lambda: None
        return _inspect.signature(func)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__signature__ = cls._get_signature()
        cls._premade = _weakref.WeakValueDictionary()

    @classmethod
    @_abc.abstractmethod
    def construct(cls, params, /):
        raise NotImplementedError

    parameterise = _types.SimpleNamespace

    @classmethod
    def _retrieve_(cls, params: tuple, /):
        premade = cls._premade
        try:
            return premade[params]
        except KeyError:
            obj = premade[params] = cls._construct_(params)
            return obj

    @classmethod
    def retrieve(cls, params: tuple, /):
        return cls._retrieve_(tuple(map(cls.param_convert, params)))

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.retrieve(tuple(
            cls.parameterise(*args, **kwargs)
            .__dict__.values()
            ))

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, arg, /):
        return cls.retrieve(arg)


###############################################################################
###############################################################################
