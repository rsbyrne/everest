###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import weakref as _weakref
import types as _types
from collections import abc as _collabc, deque as _deque

import numpy as _np

from everest.primitive import Primitive as _Primitive
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


class OusiaBase(metaclass=Ousia):

    MERGENAMES = ('__req_slots__',)
    __req_slots__ = (
        '__weakref__',
        'softcache', 'weakcache', 'freezeattr', '_sessioncacheref',
        '_epitaph',
        )

    ## Configuring the class:

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from cls.__req_slots__

    @classmethod
    def pre_create_concrete(cls, /):
        return (
            f"Concrete_{cls.__ptolemaic_class__.__name__}",
            (cls,),
            dict(
                __slots__=tuple(sorted(set(cls._yield_concrete_slots()))),
                _basecls=cls,
                __class_init__=lambda: None,
                ),
            )

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.premade = _weakref.WeakValueDictionary()

    ### Object creation:

    @classmethod
    def _process_field(cls, val, /):
        if isinstance(val, _Primitive):
            return val
        if isinstance(val, OusiaBase):
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
            f"Object {val} of type {type(val)} "
            f"cannot be converted to an Ousia."
            )

    def initialise(self, /, *args, **kwargs):
        self.__init__(*args, **kwargs)

    @classmethod
    def instantiate(cls, /, *args, **kwargs):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        object.__setattr__(obj, 'freezeattr', switch := _Switch(False))
        object.__setattr__(obj, 'softcache', {})
        object.__setattr__(obj, 'weakcache', _weakref.WeakValueDictionary())
        obj.initialise(*args, **kwargs)
        object.__setattr__(obj, '_epitaph', obj.make_epitaph())
        switch.toggle(True)
        return obj

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        obj = cls.instantiate(*args, **kwargs)
        return cls.premade.setdefault(hash(obj), obj)

    ### Some aliases:

    @property
    def __ptolemaic_class__(self, /):
        return self.__class__.__ptolemaic_class__

    @property
    def taphonomy(self, /):
        return self.__ptolemaic_class__.taphonomy

    ### Storage:

    @property
    # @_caching.weak_cache()
    def _sessioncache(self, /):
        try:
            out = object.__getattribute__(self, '_sessioncacheref')()
            if out is None:
                raise AttributeError
            return out
        except AttributeError:
            if not self.freezeattr:
                raise AttributeError(
                    "Cannot request session cache when object is mutable."
                    )
            out = _FOCUS.request_session_storer(self)
            object.__setattr__(self, '_sessioncacheref', _weakref.ref(out))
            return out

    # @property
    # @_caching.weak_cache()
    # def drawer(self, /):
    #     return _FOCUS.request_bureau_storer(self)

    ### Implementing the attribute-freezing behaviour for instances:

    @property
    def mutable(self, /):
        return self.freezeattr.as_(False)

    def __getattr__(self, name, /):
        if self.freezeattr:
            try:
                return self._sessioncache[name]
            except KeyError as exc:
                raise AttributeError from exc

    def __setattr__(self, name, val, /):
        if self.freezeattr:
            if name in self.__slots__:
                raise AttributeError(
                    "Cannot alter slot attribute while immutable."
                    )
            self._sessioncache[name] = val
        else:
            object.__setattr__(self, name, val)

    def __delattr__(self, name, /):
        if self.freezeattr:
            if name in self.__slots__:
                raise AttributeError(
                    "Cannot alter slot attribute while immutable."
                    )
            del self._sessioncache[name]
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

    @_abc.abstractmethod
    def make_epitaph(self, /):
        raise NotImplementedError

    @property
    def epitaph(self, /):
        return object.__getattribute__(self, '_epitaph')

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

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return self.hashint < other

    def __gt__(self, other, /):
        return self.hashint < other

    def __hash__(self, /):
        return self.hashint


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


@_collabc.Sequence.register
class Tuuple(metaclass=Ousia):

    __req_slots__ = ('_content',)

    def __init__(self, /, *args, **kwargs):
        self._content = tuple(map(
            self._process_field, tuple(*args, **kwargs)
            ))

    for methname in (
            '__getitem__', '__len__', '__contains__', '__iter__',
            '__reversed__', '__index__', '__count__',
            ):
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self._content.{methname}",
            )))
    del methname

    def _content_repr(self, /):
        return repr(self._content)

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_tuple(self._content, p, cycle, root=root)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(ptolcls, self._content)


@_collabc.Mapping.register
class Binding(metaclass=Ousia):

    __req_slots__ = ('_content',)

    def __init__(self, /, *args, **kwargs):
        self._content = {
            self._process_field(key): self._process_field(val)
            for key, val in dict(*args, **kwargs).items()
            }

    for methname in (
            '__getitem__', '__len__', '__contains__', '__iter__',
            'keys', 'items', 'values', 'get',
            ):
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self._content.{methname}",
            )))
    del methname

    def _content_repr(self, /):
        return ', '.join(map(':'.join, zip(
            map(repr, self),
            map(repr, self.values()),
            )))

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_dict(self._content, p, cycle, root=root)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(ptolcls, **self._content)


class Kwargs(Binding):

    def __init__(self, /, *args, **kwargs):
        self._content = {
            str(key): self._process_field(val)
            for key, val in dict(*args, **kwargs).items()
            }

    def _content_repr(self, /):
        return ', '.join(map(':'.join, zip(
            map(str, self),
            map(repr, self.values()),
            )))

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


# @OusiaLike.register
# class Tuuple(OusiaLike, tuple):

#     def __new__(cls, iterable=(), /):
#         return super().__new__(cls, map(convert, iterable))

#     def __repr__(self, /):
#         return f"Tuuple{super().__repr__()}"

#     @property
#     def epitaph(self, /):
#         return OusiaBase.taphonomy.callsig_epitaph(type(self), tuple(self))


# class Binding(dict, metaclass=Ousia):

#     def __init__(self, /, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.update({convert(key): convert(val) for key, val in self.items()})

#     @property
#     def __setitem__(self, /):
#         if self.freezeattr:
#             raise NotImplementedError
#         return super().__setitem__

#     @property
#     def __delitem__(self, /):
#         if self.freezeattr:
#             raise NotImplementedError
#         return super().__delitem__

#     def __repr__(self, /):
#         valpairs = ', '.join(map(':'.join, zip(
#             map(repr, self),
#             map(repr, self.values()),
#             )))
#         return f"<{self.__ptolemaic_class__}{{{valpairs}}}>"

#     def _repr_pretty_(self, p, cycle, root=None):
#         if root is None:
#             root = self.__ptolemaic_class__.__qualname__
#         _pretty.pretty_dict(self, p, cycle, root=root)

#     def make_epitaph(self, /):
#         ptolcls = self.__ptolemaic_class__
#         return ptolcls.taphonomy.callsig_epitaph(ptolcls, dict(self))
