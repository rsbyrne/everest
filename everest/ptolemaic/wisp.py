###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc
from types import FunctionType as _FunctionType
import types as _types
from types import SimpleNamespace as _SimpleNamespace
from weakref import WeakKeyDictionary as _WeakKeyDictionary

from everest.dclass import DClass as _DClass
from everest import ur as _ur
from everest.utilities import pretty as _pretty

from . import ptolemaic as _ptolemaic


@_ptolemaic.Kind.register
class Wisp(_DClass):

    _convtyps = {}

    @classmethod
    def convert(meta, arg, /):
        if isinstance(arg, _ptolemaic.Ptolemaic):
            return arg
        if isinstance(arg, property):
            return Property(arg.fget, arg.fset, arg.fdel, arg.__doc__)
        try:
            convtyp = meta._convtyps[type(arg)]
        except KeyError as exc:
            pass
        else:
            return convtyp(arg)
        return _ur.Primitive.convert(arg)


@_ptolemaic.Case.register
class _WispBase_(_DClass.BaseTyp):

    @property
    def __ptolemaic_class__(self, /):
        return self.__abstract_class__


Wisp.BaseTyp = _WispBase_


class Classmethod(metaclass=Wisp):

    func: _types.FunctionType

    __slots__ = ('_bndmeths',)

    def __init__(self, /):
        super().__init__()
        self._bndmeths = _WeakKeyDictionary()

    def __get__(self, instance, owner, /):
        bndmeths = self._bndmeths
        try:
            return bndmeths[owner]
        except KeyError:
            meth = bndmeths[owner] = self.func.__get__(owner)
            return meth


class Property(metaclass=Wisp):

    fget: _FunctionType = None
    fset: _FunctionType = None
    fdel: _FunctionType = None
    doc: str = None

    __slots__ = ('__doc__', '_namelookup')

    def __init__(self, /):
        super().__init__()
        self.__doc__ = self.doc
        self._namelookup = {}

    def __set_name__(self, owner, name):
        self._namelookup[owner] = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if (fget := self.fget) is None:
            name = self._namelookup[obj.__ptolemaic_class__]
            raise AttributeError(f'Unreadable attribute {name}.')
        return fget(obj)

    def __set__(self, obj, value):
        if (fset := self.fset) is None:
            name = self._namelookup[obj.__ptolemaic_class__]
            raise AttributeError(f"Can't set attribute {name}.")
        fset(obj, value)

    def __delete__(self, obj):
        if (fdel := self.fdel) is None:
            name = self._namelookup[obj.__ptolemaic_class__]
            raise AttributeError(f"Can't delete attribute {name}.")
        fdel(obj)


@_collabc.Collection.register
class Pentheros(metaclass=Wisp):

    __slots__ = ('_content',)

    __content_type__ = object
    __content_meths__ = ()

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        if cls is not __class__:
            if (typ := cls.__content_type__) not in (dct := Wisp._convtyps):
                dct[typ] = cls

    @classmethod
    def __class_get_signature__(cls, /):
        return _inspect.signature(cls.__content_type__)

    def __init__(self, /):
        super().__init__()
        self._content = self._make_content()

    @_abc.abstractmethod
    def _make_content(self, /):
        raise NotImplementedError


@_collabc.Sequence.register
class Tuuple(Pentheros):

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.arity = None

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        try:
            return tuple(*args, **kwargs)
        except TypeError:
            return tuple(args, **kwargs)

    def _make_content(self, /):
        return self.__params__

    __content_type__ = tuple
    __content_meths__ = (
        '__len__', '__contains__', '__iter__',
        '__getitem__', '__reversed__', 'index', 'count',
        )

    for methname in __content_meths__:
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self._content.{methname}",
            )))
    del methname


@_collabc.Mapping.register
class Binding(Pentheros):

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        dct = dict(*args, **kwargs)
        return tuple(map(Tuuple, (dct.keys(), dct.values())))

    def _make_content(self, /):
        return dict(zip(*self.__params__))

    __content_type__ = dict
    __content_meths__ = (
        '__len__', '__contains__', '__iter__',
        '__getitem__', 'keys', 'items', 'values', 'get',
        )

    for methname in __content_meths__:
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self._content.{methname}",
            )))
    del methname

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_dict(self._content, p, cycle, root=root)


class Kwargs(Binding):

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        keys, vals = super()._parameterise_(*args, **kwargs)
        if not all(type(key) is str for key in keys):
            raise ValueError(
                f"Only string keys are permitted "
                f"as inputs to {__class__.__name__}."
                )
        return keys, vals

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self._content, p, cycle, root=root)

    def __taphonomise__(self, taph, /):
        return taph.callsig_epitaph(self.__ptolemaic_class__, **self)


class Namespace(Kwargs):

    __content_type__ = _SimpleNamespace

    @classmethod
    def _parameterise_(cls, arg=None, **kwargs):
        if arg is not None:
            if kwargs:
                raise ValueError
            if not isinstance(arg, _SimpleNamespace):
                arg = _SimpleNamespace(**dict(arg))
            kwargs = arg.__dict__
        return tuple(map(Tuuple, (kwargs.keys(), kwargs.values())))

    def __getattr__(self, name, /):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError from exc


# @_collabc.Sequence.register
# class Arraay(Collection):

#     __content_type__ = _ur.DatArray
#     __content_meths__ = (
#         '__len__', '__contains__', '__iter__',
#         '__getitem__', 'dtype', 'shape',
#         '__reversed__', 'index', 'count',
#         )

    # for methname in __content_meths__:
    #     exec('\n'.join((
    #         f"@property",
    #         f"def {methname}(self, /):",
    #         f"    return self._content.{methname}",
    #         )))
    # del methname


###############################################################################
###############################################################################
