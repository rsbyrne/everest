###############################################################################
''''''
###############################################################################


import types as _types
import weakref as _weakref
import collections as _collections

from everest.utilities import pretty as _pretty, caching as _caching

from .sig import Sig as _Sig
from .ousia import Ousia as _Ousia
from . import exceptions as _exceptions


class DClass(_Ousia):

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    @property
    def fields(cls, /):
        return cls.sig.sigfields


class ProvisionalParams(_types.SimpleNamespace):

    def __iter__(self, /):
        return iter(self.__dict__.values())


class Param:

    __slots__ = ('name',)

    def __set_name__(self, owner, name, /):
        self.name = name

    def __get__(self, instance, owner=None, /):
        return getattr(instance.params, self.name)


class DClassBase(metaclass=DClass):

    MERGENAMES = ('__field_names__',)
    __field_names__ = ()
    __req_slots__ = ('params',)

    @classmethod
    def _get_sig(cls, /):
        return _Sig(cls)

    @classmethod
    def __class_init__(cls, /):
        cls.__field_names__ = tuple(cls.sig.keys())
        super().__class_init__()
        cls.premade = _weakref.WeakValueDictionary()
        fieldnames = cls.__field_names__
        for name in fieldnames:
            setattr(cls, name, param := Param())
            param.__set_name__(cls, name)
        cls.Params = _collections.namedtuple(
            f"{cls.__name__}Params",
            fieldnames,
            )

    @classmethod
    def paramexc(cls, /, *args, message=None, **kwargs):
        return _exceptions.ParameterisationException(
            (args, kwargs), cls, message
            )

    @classmethod
    def __process_field__(cls, val, /):
        return val

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return ProvisionalParams(**bound.arguments)

    def initialise(self, params, /):
        object.__setattr__(self, 'params', params)
        super().initialise()

    @classmethod
    def instantiate(cls, fieldvals: tuple, /):
        fieldvals = tuple(map(cls.__process_field__, fieldvals))
        try:
            return cls.premade[fieldvals]
        except KeyError:
            obj = cls.premade[fieldvals] = \
                super().instantiate(cls.Params(*fieldvals))
            return obj

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.instantiate(tuple(cls.parameterise(*args, **kwargs)))

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, arg, /):
        if not isinstance(arg, tuple):
            try:
                return super().__class_getitem__(arg)
            except AttributeError as exc:
                raise TypeError(cls, type(arg)) from exc
        return cls.instantiate(arg)

    def remake(self, /, **kwargs):
        return self.__ptolemaic_class__.instantiate(
            tuple({**self.params._asdict(), **kwargs}.values())
            )

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.getitem_epitaph(ptolcls, self.params)

    def _root_repr(self, /):
        ptolcls = self.__ptolemaic_class__
        objs = (
            type(ptolcls).__qualname__, ptolcls.__qualname__,
            self.hashID + '_' + str(id(self)),
            )
        return ':'.join(map(str, objs))

    def _content_repr(self, /):
        return ', '.join(
            f"{key}={repr(val)}" for key, val in self.params._asdict().items()
            )

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self.params._asdict(), p, cycle, root=root)


###############################################################################
###############################################################################
