###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import sys as _sys

from everest import ur as _ur
from everest.utilities import pretty as _pretty

from .sprite import Sprite as _Sprite


@_collabc.Collection.register
class ContentProxy(metaclass=_Sprite):

    __content_type__ = _ur.DatTuple
    __content_meths__ = ()

    content: object

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        # return
        return super().__class_call__(cls.__content_type__(*args, **kwargs))

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__signature__ = cls.__content_type__
        for methname in cls.__content_meths__:
            exec('\n'.join((
                f"@property",
                f"def {methname}(self, /):",
                f"    return self.content.{methname}",
                )))
            setattr(cls, methname, eval(methname))

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


@_collabc.Mapping.register
class Binding(ContentProxy):

    __content_type__ = _ur.DatDict
    __content_meths__ = (
        '__len__', '__contains__', '__iter__',
        '__getitem__', 'keys', 'items', 'values', 'get',
        )


class Kwargs(Binding):

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        dct = cls.__content_type__(*args, **kwargs)
        dct = type(dct)(zip(map(str, dct.keys()), dct.values()))
        return super().__class_call__(dct)

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
        '__len__', '__contains__', '__iter__',
        '__getitem__', 'dtype', 'shape',
        '__reversed__', 'index', 'count',
        )


class ModuleMate(metaclass=_Sprite):

    module: str

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
