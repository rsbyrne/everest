###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import weakref as _weakref
import types as _types
from collections import abc as _collabc

import numpy as _np

from everest.utilities import (
    pretty as _pretty, caching as _caching, reseed as _reseed
    )
from everest.utilities.switch import Switch as _Switch
from everest.bureau import FOCUS as _FOCUS

from .essence import Essence as _Essence


class ConcreteMeta:

    @classmethod
    def pre_create_class(meta, name, bases, namespace, /):
        return name, bases, namespace

    @classmethod
    def __meta_call__(meta, basecls, /):
        assert not hasattr(basecls, 'Construct')
        if not isinstance(basecls, type):
            raise TypeError(
                "ConcreteMeta only accepts one argument:"
                " the class to be concreted."
                )
        if isinstance(basecls, ConcreteMeta):
            raise TypeError("Cannot subclass a Concrete type.")
        return super().__class_construct__(*basecls.pre_create_concrete())

    @property
    def __ptolemaic_class__(cls, /):
        return cls._basecls

    @property
    def __signature__(cls, /):
        return cls.__ptolemaic_class__.__signature__

    def __call__(cls, /):
        raise AttributeError

    @classmethod
    def __meta_init__(meta, /):
        pass


class Ousia(_Essence):

    @classmethod
    def concretemeta_namespace(meta, /):
        return {}

    @classmethod
    def __meta_init__(meta, /):
        super().__meta_init__()
        meta.ConcreteMeta = type(
            f"{meta.__name__}_ConcreteMeta",
            (ConcreteMeta, meta),
            meta.concretemeta_namespace(),
            )

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with cls.mutable:
            cls.Concrete = cls.ConcreteMeta(cls)


def convert(val, /):
    if isinstance(val, _Dat):
        return val
    if isinstance(val, _np.ndarray):
        return Arraay(val)
    if isinstance(val, _collabc.Mapping):
        return Binding(**val)
    if isinstance(val, _collabc.Sequence):
        return Tuuple(val)
    if isinstance(val, _types.FunctionType):
        return Fuunction(val)
    raise TypeError(
        f"Object {val} of type {type(val)} cannot be converted to a _Dat."
        )


class OusiaBase(metaclass=Ousia):

    MERGETUPLES = ('__req_slots__',)
    __req_slots__ = (
        '__weakref__',
        'softcache', 'weakcache', 'freezeattr', '_pyhash'
        )

    @classmethod
    def __process_field__(cls, val, /):
        return convert(val)

    ## Configuring the concrete class:

    @classmethod
    def _yield_cache_slots(cls, /):
        for attr in cls.__dict__.values():
            if isinstance(attr, property):
                attr = attr.fget
            if isinstance(attr, _types.FunctionType):
                try:
                    yield attr.__attr_cache_storedname__
                except AttributeError:
                    pass

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__cache_slots__ = tuple(cls._yield_cache_slots())

    @classmethod
    def pre_create_concrete(cls, /):
        name = f"Concrete_{cls.__ptolemaic_class__.__name__}"
        bases = (cls,)
        namespace = dict(
            __slots__=(*cls.__req_slots__, *cls.__cache_slots__),
            _basecls=cls,
            __class_init__=lambda: None,
            )
        return name, bases, namespace

    ### Object creation:

    def initialise(self, /, *args, **kwargs):
        self.__init__(*args, **kwargs)

    @classmethod
    def instantiate(cls, /, *args, **kwargs):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        switch = _Switch(False)
        object.__setattr__(obj, 'freezeattr', switch)
        object.__setattr__(obj, 'softcache', {})
        object.__setattr__(obj, 'weakcache', _weakref.WeakValueDictionary())
        object.__setattr__(obj, '_pyhash', _reseed.rdigits(16))
        obj.initialise(*args, **kwargs)
        switch.toggle(True)
        return obj

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.instantiate(*args, **kwargs)

    def _repr_pretty_(self, p, cycle, root=None):
        pass

    ### Some aliases:

    @property
    def __ptolemaic_class__(self, /):
        return self.__class__.__ptolemaic_class__

    @property
    def taphonomy(self, /):
        return self.__ptolemaic_class__.taphonomy

    ### Storage:

    @property
    @_caching.weak_cache()
    def tray(self, /):
        return _FOCUS.request_session_storer(self)

    @property
    @_caching.weak_cache()
    def drawer(self, /):
        return _FOCUS.request_bureau_storer(self)

    ### Implementing the attribute-freezing behaviour for instances:

    @property
    def mutable(self, /):
        return self.freezeattr.as_(False)

    def __getattr__(self, name, /):
        try:
            return self.tray[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, val, /):
        if self.freezeattr:
            if name in self.__slots__:
                raise AttributeError("Cannot alter slot attribute while immutable.")
            self.tray[name] = val
        else:
            object.__setattr__(self, name, val)

    def __delattr__(self, name, /):
        if self.freezeattr:
            if name in self.__slots__:
                raise AttributeError("Cannot alter slot attribute while immutable.")
            del self.tray[name]
        else:
            object.__delattr__(self, name)

    ### Representations:

    def _root_repr(self, /):
        ptolcls = self.__ptolemaic_class__
        return ':'.join(map(str,
            (type(ptolcls).__qualname__, ptolcls.__qualname__, id(self))
            ))

    @property
    @_caching.soft_cache()
    def rootrepr(self, /):
        return self._root_repr()

    def _content_repr(self, /):
        return ''

    @property
    @_caching.soft_cache()
    def contentrepr(self, /):
        return self._content_repr()

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    def __repr__(self, /):
        return f"<{self.rootrepr}>"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        p.text(f"{root}({self.contentrepr})")

    def __hash__(self, /):
        return id(self)

    @_abc.abstractmethod
    def make_epitaph(self, /):
        raise NotImplementedError

    @property
    @_caching.soft_cache()
    def epitaph(self, /):
        return self.make_epitaph()

    def __reduce__(self, /):
        return self.epitaph, ()

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def __hash__(self, /):
        return self._pyhash

    ### Rich comparisons to support ordering of objects:

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return hash(self) < hash(other)

    def __gt__(self, other, /):
        return hash(self) < hash(other)


class Funcc(metaclass=Ousia):

    __req_slots__ = ('func',)

    def __init__(self, func: _types.FunctionType, /):
        self.func = func

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


@OusiaBase.register
class Tuuple(tuple):

    def __new__(cls, iterable=(), /):
        return super().__new__(cls, map(convert, iterable))

    def __repr__(self, /):
        return f"Tuuple{super().__repr__()}"

    @property
    def epitaph(self, /):
        return OusiaBase.taphonomy.callsig_epitaph(type(self), tuple(self))


class Binding(dict, metaclass=Ousia):

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update({convert(key): convert(val) for key, val in self.items()})

    @property
    def __setitem__(self, /):
        if self.freezeattr:
            raise NotImplementedError
        return super().__setitem__

    @property
    def __delitem__(self, /):
        if self.freezeattr:
            raise NotImplementedError
        return super().__delitem__

    def __repr__(self, /):
        valpairs = ', '.join(map(':'.join, zip(
            map(repr, self),
            map(repr, self.values()),
            )))
        return f"<{self.__ptolemaic_class__}{{{valpairs}}}>"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_dict(self, p, cycle, root=root)

    def __hash__(self, /):
        return self.hashint

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(ptolcls, dict(self))

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return hash(self) < hash(other)

    def __gt__(self, other, /):
        return hash(self) < hash(other)


class Kwargs(Binding):

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self, p, cycle, root=root)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(
            ptolcls, **self
            )


class Arraay(metaclass=Ousia):

    __req_slots__ = ('_array',)

    def __init__(self, arg, /, dtype=None):
        if isinstance(arg, bytes):
            arr = _np.frombuffer(arg, dtype=dtype)
        else:
            arr = _np.array(arg, dtype=dtype).copy()
        object.__setattr__(self, '_array', arr)

    for methname in (
            'dtype', 'shape', '__len__',
            ):
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self._array.{methname}",
            )))
    del methname

    def __getitem__(self, arg, /):
        out = self._array[arg]
        if isinstance(out, _np.ndarray):
            return self.__ptolemaic_class__(out)
        return out

    def _content_repr(self, /):
        return _np.array2string(self._array, threshold=100)[:-1]

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_array(self._array, p, cycle, root=root)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        content = f"{repr(bytes(self._array))},{repr(str(self.dtype))}"
        return ptolcls.taphonomy(
            f"""m('everest.ptolemaic.ousia').Arraay({content})""",
            {},
            )


###############################################################################
###############################################################################
