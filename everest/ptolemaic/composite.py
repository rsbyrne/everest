###############################################################################
''''''
###############################################################################


import types as _types
import weakref as _weakref
import collections as _collections

from everest.utilities import pretty as _pretty

from .ousia import Ousia as _Ousia


class Composite(_Ousia):
    ...


class Param:

    __slots__ = ('name',)

    def __set_name__(self, owner, name, /):
        self.name = name

    def __get__(self, instance, owner=None, /):
        return getattr(instance.params, self.name)


class CompositeBase(metaclass=Composite):

    MERGETUPLES = ('__field_names__',)
    __field_names__ = ()
    __req_slots__ = ('params',)

    @classmethod
    def __class_init__(cls, /):
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
    def __process_field__(cls, val, /):
        return val

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
        return ptolcls.taphonomy.getitem_epitaph(ptolcls, self.__field_vals__)

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
