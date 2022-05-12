###############################################################################
''''''
###############################################################################


import types as _types

from everest.utilities import pretty as _pretty

from .ousia import Ousia as _Ousia


class Composite(_Ousia):
    ...


class CompositeBase(metaclass=Composite):

    MERGETUPLES = ('__field_slots__',)

    __field_slots__ = ()

    @classmethod
    def pre_create_concrete(cls, /):
        name, bases, namespace = super().pre_create_concrete()
        namespace['__slots__'] = (
            *namespace['__slots__'], *cls.__field_slots__
            )
        return name, bases, namespace

    @property
    def __field_vals__(self, /):
        return tuple(
            object.__getattribute__(self, fieldname)
            for fieldname in self.__field_slots__
            )

    @property
    def fields(self, /):
        return _types.MappingProxyType(dict(zip(
            self.__field_slots__, self.__field_vals__
            )))

    def initialise(self, fieldvals: tuple, /):
        for name, val in zip(
                self.__field_slots__,
                map(self.__process_attr__, fieldvals),
                ):
            object.__setattr__(self, name, val)
        super().initialise()

    def remake(self, /, **kwargs):
        return self.__ptolemaic_class__.instantiate(
            tuple({**self.fields, **kwargs}.values())
            )

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, arg, /):
        if not isinstance(arg, tuple):
            try:
                return super().__class_getitem__(arg)
            except AttributeError as exc:
                raise TypeError(cls, type(arg)) from exc
        return cls.instantiate(arg)

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
            f"{key}={repr(val)}" for key, val in self.fields.items()
            )

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self.fields, p, cycle, root=root)


###############################################################################
###############################################################################
