###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import inspect as _inspect
from collections import namedtuple as _namedtuple
import sys as _sys

from everest.utilities import pretty as _pretty
from everest import ur as _ur

from .composite import Composite as _Composite, paramstuple as _paramstuple


class Sprite(_Composite):
    ...


class SpriteBase(metaclass=Sprite):

    MERGENAMES = ('__params__', ('__defaults__', tuple))
    __params__ = ()
    __defaults__ = ()

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from super()._yield_concrete_slots()
        yield from cls.__params__

    @classmethod
    def _make_params_type(cls, /):
        return _paramstuple(
            cls.__name__,
            cls.__params__,
            defaults=cls.__defaults__,
            )

    @classmethod
    def _get_signature(cls, /):
        return _inspect.signature(cls.Params)


@_collabc.Collection.register
class ContentProxy(metaclass=Sprite):

    __params__ = ('content',)
    MERGENAMES = ('__content_meths__',)
    __content_type__ = _ur.DatTuple
    __content_meths__ = ('__len__', '__contains__', '__iter__')

    @classmethod
    def _get_signature(cls, /):
        return _inspect.signature(cls.__content_type__)

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        return (cls.__content_type__(*args, **kwargs),)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        for methname in cls.__content_meths__:
            exec('\n'.join((
                f"@property",
                f"def {methname}(self, /):",
                f"    return self.content.{methname}",
                )))
            setattr(cls, methname, eval(methname))

    def _content_repr(self, /):
        return repr(self.content)

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        return self.content._repr_pretty_(p, cycle, root=root)


@_collabc.Sequence.register
class Tuuple(ContentProxy):

    __content_meths__ = (
        '__getitem__', '__reversed__', 'index', 'count'
        )


@_collabc.Mapping.register
class Binding(ContentProxy):

    __content_type__ = _ur.DatDict
    __content_meths__ = ('__getitem__', 'keys', 'items', 'values', 'get')


class Kwargs(Binding):

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        dct = cls.__content_type__(*args, **kwargs)
        return (
            type(dct)(zip(map(str, dct.keys()), dct.values())),
            )

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self.content, p, cycle, root=root)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(ptolcls, **self)


@_collabc.Sequence.register
class Arraay(ContentProxy):

    __content_type__ = _ur.DatArray
    __content_meths__ = (
        '__getitem__', 'dtype', 'shape',
        '__reversed__', '__index__', '__count__',
        )


class ModuleMate(metaclass=Sprite):

    __params__ = ('module',)

    @classmethod
    def __class_call__(cls, name, /):
        _sys.modules[name] = \
            super().__class_call__(_sys.modules[name])

    def __init__(self, /):
        _sys.modules[self.module.__name__] = self

    def __getattr__(self, name, /):
        try:
            super().__getattr__(name)
        except AttributeError:
            return getattr(self.module, name)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy(self.module)

    def __repr__(self, /):
        return self.module.__name__

    def __str__(self, /):
        return self.module.__name__

    def _repr_pretty_(self, p, cycle, root=None):
        p.text(repr(self))


###############################################################################
###############################################################################
