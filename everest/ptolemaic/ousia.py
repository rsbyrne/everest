###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import weakref as _weakref
import collections as _collections
import functools as _functools

from everest.utilities import pretty as _pretty
from everest.utilities.switch import Switch as _Switch
from everest.bureau import FOCUS as _FOCUS
from everest import ur as _ur

from .essence import Essence as _Essence
from . import exceptions as _exceptions


class ConcreteMeta:

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
        raise NotImplementedError

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

    @property
    def arity(cls, /):
        return len(cls.Params._fields)


class _Params_:

    def __new__(cls, /, *args, **kwargs):
        tup = super().__new__(cls, *args, **kwargs)
        return super().__new__(cls, *_ur.DatTuple(tup))


@_functools.wraps(_collections.namedtuple)
def paramstuple(*args, **kwargs):
    nt = _collections.namedtuple(*args, **kwargs)
    return type(f"Params_{nt.__name__}", (_Params_, nt), {})


class ProvisionalParams(dict):

    def __setitem__(self, name, val, /):
        if name not in self:
            raise KeyError(name)
        super().__setitem__(name, val)

    @property
    def __delitem__(self, /):
        raise AttributeError

    def __getattr__(self, name, /):
        return self[name]

    def __setattr__(self, name, val, /):
        return self.__setitem__(name, val)

    def __iter__(self, /):
        return iter(self.values())

    @property
    def _fields(self, /):
        return tuple(self.values())


@_ur.Dat.register
class OusiaBase(metaclass=Ousia):

    MERGENAMES = ('__req_slots__',)
    __req_slots__ = (
        '__weakref__',
        'freezeattr',
        'params',
        '_sessioncacheref',
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
        cls.Params = cls._make_params_type()

    @classmethod
    @_abc.abstractmethod
    def _make_params_type(cls, /) -> type:
        return paramstuple(cls.__name__, ())

    @classmethod
    def _get_signature(cls, /):
        return _inspect.signature(cls.Params)

    ### Object creation:

    @classmethod
    def parameterise(cls, /, *args, **kwargs) -> _collections.Mapping:
        return ProvisionalParams(cls.Params(*args, **kwargs)._asdict())

    @classmethod
    def paramexc(cls, /, *args, message=None, **kwargs):
        return _exceptions.ParameterisationException(
            (args, kwargs), cls, message
            )

    def initialise(self, /):
        self.__init__()

    @classmethod
    def instantiate(cls, params: _collections.Sequence, /):
        params = cls.Params(*params)
        premade = cls.premade
        Concrete = cls.Concrete
        try:
            return premade[params]
        except KeyError:
            obj = premade[params] = Concrete.__new__(Concrete)
            switch = _Switch(False)
            object.__setattr__(obj, 'freezeattr', switch)
            object.__setattr__(obj, 'params', params)
            obj.initialise()
            switch.toggle(True)
            return obj

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        
        return cls.instantiate(cls.parameterise(*args, **kwargs))

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, arg, /):
        if cls.arity == 1:
            arg = (arg,)
        return cls.instantiate(arg)

    def remake(self, /, **kwargs):
        return self.__ptolemaic_class__.instantiate(
            tuple({**self.params._asdict(), **kwargs}.values())
            )

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
        objs = (
            type(ptolcls).__qualname__, ptolcls.__qualname__,
            self.hashID + '_' + str(id(self)),
            )
        return ':'.join(map(str, objs))

    @property
    # @_caching.soft_cache()
    def rootrepr(self, /):
        return self._root_repr()

    def _content_repr(self, /):
        return ', '.join(
            f"{key}={repr(val)}" for key, val in self.params._asdict().items()
            )

    @property
    # @_caching.soft_cache()
    def contentrepr(self, /):
        return self._content_repr()

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    def __repr__(self, /):
        return f"<{self.rootrepr}>"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self.params._asdict(), p, cycle, root=root)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        params = self.params
        if ptolcls.arity == 1:
            params = params[0]
        return ptolcls.taphonomy.getitem_epitaph(ptolcls, params)

    @property
    def epitaph(self, /):
        try:
            return object.__getattribute__(self, '_epitaph')
        except AttributeError:
            obj = self.make_epitaph()
            object.__setattr__(self, '_epitaph', obj)
            return obj

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
