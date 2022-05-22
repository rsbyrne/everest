###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import inspect as _inspect

from everest.utilities import pretty as _pretty
from everest import ur as _ur

from .ousia import Ousia as _Ousia, ProvisionalParams as _ProvisionalParams


class Sprite(_Ousia):
    ...


class SpriteBase(metaclass=Sprite):

    MERGENAMES = ('__params__',)
    __params__ = ()

    @classmethod
    def _yield_paramnames(cls, /):
        yield from cls.__params__

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from super()._yield_concrete_slots()
        yield from cls._yield_paramnames()

    def initialise(self, /):
        for name, val in self.params._asdict().items():
            setattr(self, name, val)
        super().initialise()


class Funcc(metaclass=Sprite):

    __params__ = ('func',)

    @property
    def __call__(self, /):
        return self.func

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(ptolcls, self.func)

    def _content_repr(self, /):
        return repr(self.func)

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_function(self.func, p, cycle, root=root)


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
            root = self.__ptolemaic_class__.__qualname__
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
        return (type(dct)(zip(map(str, dct.keys()), dct.values())),)

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


###############################################################################
###############################################################################
