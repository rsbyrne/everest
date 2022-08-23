###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
from collections import abc as _collabc

from everest.utilities import reseed as _reseed, pretty as _pretty
from everest.bureau import FOCUS as _FOCUS
from everest.switch import Switch as _Switch
from everest import ur as _ur

from . import ptolemaic as _ptolemaic
from .urgon import Urgon as _Urgon, Params as _Params
from .essence import Essence as _Essence


class ConcreteBase(metaclass=_Essence):

    with escaped('methname'):
        for methname in (
                '_parameterise_', '__parameterise__',
                '_construct_', '__construct__',
                '_retrieve_', '__retrieve__',
                '_instantiate_', '__instantiate__',
                '_create_concrete', '_pre_create_concrete',
                ):
            exec('\n'.join((
                f"@classmethod",
                f"def {methname}(cls, /, *_, **__):",
                f"    raise AttributeError(",
                f"        '{methname} not supported on Concrete subclasses.'",
                f"        )",
                )))


@_ptolemaic.Kind.register
class Ousia(_Urgon):

    @property
    def Concrete(cls, /):
        cls = cls.__ptolemaic_class__
        try:
            return cls.__dict__['_Concrete']
        except KeyError:
            with cls.__mutable__:
                out = cls._Concrete = _abc.ABCMeta.__new__(
                    type(cls), *cls._pre_create_concrete()
                    )
                out.__mutable__ = False
            return out

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        yield '__req_slots__', (dict, dict)

    @classmethod
    def handle_slots(meta, body, slots, /):
        if not isinstance(slots, _collabc.Mapping):
            slots = zip(slots, _itertools.repeat(None))
        body['__req_slots__'].update(slots)


@_ptolemaic.Case.register
class _OusiaBase_(metaclass=Ousia):

    __slots__ = (
        '__weakref__',
        '__params__', 'params', '_mutable', '_pyhash', '_sessioncacheref',
        '_innerobjs', '__corpus__', '__relname__', '_instancesignature',
        )

    cacheable = True

    @property
    def __progenitor__(self, /):
        return self.__ptolemaic_class__

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, cls)

    @classmethod
    def __class_includes__(cls, arg, /):
        return issubclass(arg, cls)

    @property
    def __signature__(self, /):
        try:
            return object.__getattribute__(self, '_instancesignature')
        except AttributeError:
            try:
                meth = self.__get_signature__
            except AttributeError:
                raise TypeError(self.__ptolemaic_class__)
            sig = meth()
            object.__setattr__(self, '_instancesignature', sig)
            return sig

    ### Descriptor behaviours for class and instance:

    def _register_innerobj(self, name, obj, /):
        _ptolemaic.configure_as_innerobj(obj, self, name)
        if self.__mutable__:
            self._innerobjs[name] = obj
        else:
            obj.__initialise__()
            obj.__mutable__ = False

    ## Configuring the class:

    @classmethod
    def _yield_slots(cls, /):
        yield from cls.__req_slots__.items()

    @classmethod
    def _pre_create_concrete(cls, /):
        cls = cls.__ptolemaic_class__
        return (
            f"{cls.__name__}_Concrete",
            (ConcreteBase, cls),
            dict(
                __slots__=_ur.DatDict(cls._yield_slots()),
                _get_ptolemaic_class=(lambda: cls),
                _clsmutable=_Switch(True),
                _clsiscosmic=False,
                ),
            )

    @classmethod
    def _create_concrete(cls, /):
        return type(*cls._pre_create_concrete())

    ### Object creation:

    def __initialise__(self, /):
        self.__init__()
        innerobjs = self._innerobjs
        for name, obj in innerobjs.items():
            obj.__initialise__()
        for obj in innerobjs.values():
            obj.__mutable__ = False
        del self._innerobjs

    @classmethod
    def _instantiate_(cls, params: _Params, /):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        switch = _Switch(True)
        object.__setattr__(obj, '_mutable', switch)
        obj._pyhash = _reseed.rdigits(16)
        obj.params = params
        obj.__params__ = tuple(params.values())
        obj._innerobjs = {}
        return obj

    @classmethod
    def __instantiate__(cls, params: _Params, /):
        return cls._instantiate_(_Params(params))

    @classmethod
    def _construct_(cls, params: _Params, /):
        obj = cls._instantiate_(params)
        obj.__corpus__ = obj.__relname__ = None
        obj.__initialise__()
        obj.__mutable__ = False
        return obj

    @classmethod
    def __class_alt_call__(cls, /, *args, **kwargs):
        return cls._instantiate_(cls.__parameterise__(*args, **kwargs))

    ### Storage:

    def __setattr__(self, name, val, /):
        if self.__mutable__:
            if not name.startswith('_'):
                val = self.__ptolemaic_class__.convert(val)
            object.__setattr__(self, name, val)
            return val
        raise RuntimeError("Cannot alter value while immutable.")

    def __delattr__(self, name, /):
        if self.__mutable__:
            object.__delattr__(self, name)
        else:
            raise RuntimeError("Cannot alter value while immutable.")


    ### Implementing the attribute-freezing behaviour for instances:

    @property
    def __mutable__(self, /):
        return self._mutable

    @__mutable__.setter
    def __mutable__(self, value, /):
        self.__mutable__.toggle(value)

    ### Representations:

    def _content_repr(self, /):
        return repr(self.__params__)

    def _root_repr(self, /):
        return self.__ptolemaic_class__.__qualname__

    @property
    # @_caching.soft_cache()
    def rootrepr(self, /):
        return self._root_repr()

    @property
    # @_caching.soft_cache()
    def contentrepr(self, /):
        return self._content_repr()

    def __repr__(self, /):
        if self.__corpus__ is None:
            return f"<{self.rootrepr}, id={id(self)}>"
        return f"{self.__corpus__}.{self.__relname__}"

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    def __taphonomise__(self, taph, /):
        if self.__corpus__ is None:
            return taph.getitem_epitaph(
                self.__ptolemaic_class__, self.__params__
                )
        return taph.getattr_epitaph(self.__corpus__, self.__relname__)

    @property
    def _taphonomy_(self, /):
        return self.__ptolemaic_class__._taphonomy_

    @property
    def _epitaph_(self, /):
        return self._taphonomy_[self]

    def __reduce__(self, /):
        return self._epitaph_, ()

    @property
    def hexcode(self, /):
        return self._epitaph_.hexcode

    @property
    def hashint(self, /):
        return self._epitaph_.hashint

    @property
    def hashID(self, /):
        return self._epitaph_.hashID

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        if isinstance(other, _OusiaBase_):
            other = other.hashint
        return self.hashint < other

    def __gt__(self, other, /):
        if isinstance(other, _OusiaBase_):
            other = other.hashint
        return self.hashint < other

    def __hash__(self, /):
        return object.__getattribute__(self, '_pyhash')

    @property
    def __ptolemaic_class__(self, /):
        return type(self)._get_ptolemaic_class()

    def _pretty_repr_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self.params, p, cycle, root=root)

    def _repr_pretty_(self, p, cycle, root=None):
        if (corpus := self.__corpus__) is None:
            self._pretty_repr_(p, cycle, root=root)
        else:
            _pretty.pretty_attribute(
                self.__relname__, corpus, p, cycle, root=root
                )


###############################################################################
###############################################################################
