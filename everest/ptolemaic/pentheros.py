###############################################################################
''''''
###############################################################################


from collections import deque as _deque
from inspect import Signature as _Signature, Parameter as _Parameter, _empty
import weakref as _weakref
import types as _types

from everest.utilities import (
    caching as _caching, pretty as _pretty
    )

from .ousia import Ousia as _Ousia
from .sig import Sig as _Sig
from . import exceptions as _exceptions


class Pentheros(_Ousia):

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    @property
    def fields(cls, /):
        return cls.sig.sigfields

    @property
    @_caching.soft_cache()
    def fieldnames(cls, /):
        return tuple(cls.sig.keys())


class PentherosBase(metaclass=Pentheros):

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.sig = cls._get_sig()

    @classmethod
    def _get_sig(cls, /):
        return _Sig(cls)

    @classmethod
    def pre_create_concrete(cls, /):
        name, bases, namespace = super().pre_create_concrete()
        namespace['__slots__'] = tuple(sorted(set((
            *namespace['__slots__'], *cls.sig.keys()
            ))))
        # namespace.update({
        #     key: _Param(key) for key in cls.__signature__.parameters
        #     })
        return name, bases, namespace

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.premade = _weakref.WeakValueDictionary()

    @classmethod
    def paramexc(cls, /, *args, message=None, **kwargs):
        return _exceptions.ParameterisationException(
            (args, kwargs), cls, message
            )

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    @classmethod
    def instantiate(cls, fieldvals: tuple, /):
        try:
            return cls.premade[fieldvals]
        except KeyError:
            obj = cls.premade[fieldvals] = cls.corporealise()
            for name, val in zip(cls.fieldnames, fieldvals):
                object.__setattr__(obj, name, val)
            obj.initialise()
            return obj

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.instantiate(tuple(
            cls.parameterise(*args, **kwargs).arguments.values()
            ))

    def __class_getitem__(cls, arg, /):
        if not isinstance(arg, tuple):
            try:
                return super().__class_getitem__(arg)
            except AttributeError as exc:
                raise TypeError(cls, type(arg)) from exc
        return cls.instantiate(arg)

    @property
    @_caching.soft_cache()
    def fieldvals(self, /):
        return tuple(
            object.__getattribute__(self, fieldname)
            for fieldname in self.fieldnames
            )

    @property
    def fieldnames(self, /):
        return self._ptolemaic_class__.fieldnames

    @property
    def fields(self, /):
        return _types.MappingProxyType(dict(zip(
            self.fieldnames, self.fieldvals
            )))

    def remake(self, /, **kwargs):
        ptolcls = self._ptolemaic_class__
        bound = ptolcls.__signature__.bind_partial()
        bound.arguments.update(self.fields)
        bound.arguments.update(kwargs)
        return ptolcls(*bound.args, **bound.kwargs)

    def make_epitaph(self, /):
        ptolcls = self._ptolemaic_class__
        return ptolcls.taphonomy.getitem_epitaph(ptolcls, self.fieldvals)

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def _root_repr(self, /):
        ptolcls = self._ptolemaic_class__
        objs = (
            type(ptolcls).__qualname__, ptolcls.__qualname__,
            self.hashID + '_' + str(id(self)),
            )
        return ':'.join(map(str, objs))

    def _content_repr(self, /):
        return ', '.join(
            f"{key}={repr(val)}" for key, val in self.fields.items()
            )

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self.fields, p, cycle, root=root)

    def __hash__(self, /):
        return self.hashint


###############################################################################
###############################################################################
