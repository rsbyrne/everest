###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import sys as _sys
import inspect as _inspect

from everest.utilities import pretty as _pretty

from .sprite import Sprite as _Sprite
from . import ptolemaic as _ptolemaic


@_collabc.Collection.register
class ContentProxy(metaclass=_Sprite):

    __content_type__ = _ptolemaic.PtolTuple
    __content_meths__ = ()

    content: ...

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        return super().__parameterise__(cls.__content_type__(*args, **kwargs))

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        return self.content._repr_pretty_(p, cycle, root=root)


@_collabc.Sequence.register
class Tuuple(ContentProxy):

    __content_meths__ = (
        '__len__', '__contains__', '__iter__',
        '__getitem__', '__reversed__', 'index', 'count',
        )

    with escaped('methname'):
        for methname in __content_meths__:
            exec('\n'.join((
                f"@property",
                f"def {methname}(self, /):",
                f"    return self.content.{methname}",
                )))


@_collabc.Mapping.register
class Binding(ContentProxy):

    __content_type__ = _ptolemaic.PtolDict
    __content_meths__ = (
        '__len__', '__contains__', '__iter__',
        '__getitem__', 'keys', 'items', 'values', 'get',
        )

    with escaped('methname'):
        for methname in __content_meths__:
            exec('\n'.join((
                f"@property",
                f"def {methname}(self, /):",
                f"    return self.content.{methname}",
                )))


class Kwargs(Binding):

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        dct = cls.__content_type__(*args, **kwargs)
        dct = type(dct)(zip(map(str, dct.keys()), dct.values()))
        return super().__parameterise__(dct)

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self.content, p, cycle, root=root)

    def __taphonomise__(self, taph, /):
        return taph.callsig_epitaph(self.__ptolemaic_class__, **self)


@_collabc.Sequence.register
class Arraay(ContentProxy):

    __content_type__ = _ptolemaic.PtolArray
    __content_meths__ = (
        '__len__', '__contains__', '__iter__',
        '__getitem__', 'dtype', 'shape',
        '__reversed__', 'index', 'count',
        )

    with escaped('methname'):
        for methname in __content_meths__:
            exec('\n'.join((
                f"@property",
                f"def {methname}(self, /):",
                f"    return self.content.{methname}",
                )))


###############################################################################
###############################################################################
