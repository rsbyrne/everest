###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import itertools as _itertools
from collections import abc as _collabc

from everest.utilities import pretty as _pretty, reseed as _reseed
from everest.bureau import FOCUS as _FOCUS
from everest import ur as _ur

from .urgon import Urgon as _Urgon
from .utilities import Switch as _Switch


class ConcreteBase:

    __slots__ = ()

    for methname in (
            '__class_call__',
            'create_concrete', 'pre_create_concrete',
            ):
        exec('\n'.join((
            f"@classmethod",
            f"def {methname}(cls, /, *_, **__):",
            f"    raise AttributeError(",
            f"        '{methname} not supported on Concrete subclasses.'",
            f"        )",
            )))
    del methname

    @classmethod
    def __mro_entries__(cls, bases: tuple, /):
        return (cls.__ptolemaic_class__,)


# class ClassBody(_Urgon.ClassBody):

#     def __init__(self, /, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.extraslots = self['__classbody_added_slots__'] = set()

#     def slotcache(self, arg, /):
#         name = arg.__name__
#         self.extraslots.add(name)
#         self[f"_get_{name}_"] = arg
#         return self.Flags.NULL

#     def weakcache(self, arg, /):
#         name = arg.__name__
#         weakname = f"{name}_weakref"
#         methname = f"_get_{name}_"
#         self.extraslots.add(weakname)
#         self[methname] = arg
#         @property
#         def dereferencer(self, /):
#             ref = object.__getattribute__(self, weakname)
#             try:
#                 return ref()
#             except ReferenceError:
#                 val = type.__getattribute__(type(self), methname)(self)
#                 object.__setattr__(self, weakname, _weakref.ref(val))
#                 return val
#         self[name] = dereferencer
#         return self.SKIP


class Ousia(_Urgon):

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        yield ('__req_slots__', list, _ur.DatUniqueTuple)

    @property
    def Concrete(cls, /):
        cls = cls.__ptolemaic_class__
        try:
            return cls.__dict__['_Concrete']
        except KeyError:
            with cls.mutable:
                out = cls._Concrete = _abc.ABCMeta.__new__(
                    type(cls), *cls.pre_create_concrete()
                    )
                out.mutable = False
            return out

    @classmethod
    def _yield_bodynametriggers(meta, /):
        yield from super()._yield_bodynametriggers()
        yield (
            '__slots__',
            lambda body, val: (None, body.__setitem__('__req_slots__', val))
            )


class OusiaBase(metaclass=Ousia):

    __slots__ = (
        '__weakref__',
        '_mutable', '_pyhash', '_sessioncacheref', '_epitaph',
        '_dependants',
        )

    ## Configuring the class:

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from ()

    @classmethod
    def pre_create_concrete(cls, /):
        cls = cls.__ptolemaic_class__
        return (
            f"{cls.__name__}_Concrete",
            (ConcreteBase, cls),
            dict(
                __slots__=tuple(sorted(set(_itertools.chain(
                    cls.__req_slots__,
                    cls._yield_concrete_slots(),
                    )))),
                _get_ptolemaic_class=(lambda: cls),
                _clsmutable=_Switch(True),
                _clsiscosmic=False,
                ),
            )

    @classmethod
    def create_concrete(cls, /):
        return type(*cls.pre_create_concrete())

#     @classmethod
#     def _define_attrmethods(cls, /):

#         # getters, setters, deleters = cls.getters, cls.setters, cls.deleters
#         slots = cls.__req_slots__

#         def __getattr__(self, name, /):
#             # try:
#             #     meth = getters[name]
#             # except KeyError as exc:
#             #     pass
#             # else:
#             #     val = meth(self)
#             #     setattr(self, name, val)
#             #     return val
#             if name in slots:
#                 raise AttributeError(name)
#             else:
#                 return getattr(type(self), name)
#             # try:
#             #     return object.__getattribute__(self, '__vardict__')[name]
#             # except KeyError as exc:
#             #     pass

#         def __setattr__(self, name, val, /):
#             # try:
#             #     meth = setters[name]
#             # except KeyError as exc:
#             #     pass
#             # else:
#             #     meth(self, val)
#             #     return
#             if name in slots:
#                 if object.__getattribute__(self, 'freezeattr'):
#                     raise AttributeError(
#                         name, "Cannot alter slot while frozen."
#                         )
#             object.__setattr__(self, name, val)

#         def __delattr__(self, name, /):
#             # try:
#             #     meth = deleters[name]
#             # except KeyError as exc:
#             #     pass
#             # else:
#             #     meth(self)
#             #     return
#             if name in slots:
#                 if object.__getattribute__(self, 'freezeattr'):
#                     raise AttributeError(
#                         name, "Cannot alter slot while frozen."
#                         )
#             object.__delattr__(self, name)

#         return __getattr__, __setattr__, __delattr__
        

    # @classmethod
    # def __class_init__(cls, /):
    #     super().__class_init__()
    #     # for nm in ('getters', 'setters', 'deleters'):
    #     #     meths = cls._yield_affixfiltered(nm, f"_{nm[:3]}_", "_")
    #     #     setattr(cls, nm, _ur.DatDict(meths))
    #     cls.__getattr__, cls.__setattr__, cls.__delattr__ = \
    #         cls._define_attrmethods()

    ### Object creation:

    @_abc.abstractmethod
    def set_params(self, params, /):
        raise NotImplementedError

    @classmethod
    def construct(cls, params: tuple, /, *args, _epitaph=None, **kwargs):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        switch = _Switch(False)
        object.__setattr__(obj, '_mutable', _Switch(True))
        obj._epitaph = _epitaph
        obj._pyhash = _reseed.rdigits(16)
        # obj._dependants = _weakref.WeakSet()
        obj.set_params(params)
        obj.__init__(*args, **kwargs)
        switch.toggle(True)
        return obj

    ### Storage:

    @property
    # @_caching.weak_cache()
    def __vardict__(self, /):
        try:
            out = super().__getattribute__('_sessioncacheref')()
            if out is None:
                raise AttributeError
            return out
        except AttributeError:
            out = _FOCUS.request_session_storer(self)
            try:
                super().__setattr__('_sessioncacheref', _weakref.ref(out))
            except AttributeError:
                raise RuntimeError(
                    "Could not set the session cache on this object."
                    )
            return out

#     @property
#     def dependants(self, /):
#         return tuple(sorted(self._dependants))

#     def add_dependant(self, other, /):
#         self._dependants.add(other)

    def reset(self, /):
        self.__vardict__.clear()
        for dep in self.dependants:
            dep.reset()

    # @property
    # @_caching.weak_cache()
    # def drawer(self, /):
    #     return _FOCUS.request_bureau_storer(self)

    ### Implementing the attribute-freezing behaviour for instances:

    @property
    def mutable(self, /):
        return self._mutable

    @mutable.setter
    def mutable(self, value, /):
        self.mutable.toggle(value)

    def __setattr__(self, name, val, /):
        if name in object.__getattribute__(self, '__slots__'):
            if not object.__getattribute__(self, '_mutable'):
                raise AttributeError(
                    name, "Cannot alter slot while frozen."
                    )
        object.__setattr__(self, name, val)

    def __delattr__(self, name, /):
        if name in object.__getattribute__(self, '__slots__'):
            if not object.__getattribute__(self, '_mutable'):
                raise AttributeError(
                    name, "Cannot alter slot while frozen."
                    )
        object.__delattr__(self, name)

    ### Representations:

    def _root_repr(self, /):
        return self.__ptolemaic_class__.__qualname__

    @property
    # @_caching.soft_cache()
    def rootrepr(self, /):
        return self._root_repr()

    @_abc.abstractmethod
    def _content_repr(self, /):
        return ''

    @property
    # @_caching.soft_cache()
    def contentrepr(self, /):
        return self._content_repr()

    def __repr__(self, /):
        return f"<{self.rootrepr}, id={id(self)}>"

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    @_abc.abstractmethod
    def make_epitaph(self, /):
        raise NotImplementedError

    @property
    def epitaph(self, /):
        epi = self._epitaph
        if epi is None:
            epi = self.make_epitaph()
            with self.mutable:
                self._epitaph = epi
        return epi

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
        return object.__getattribute__(self, '_pyhash')

    @property
    def __ptolemaic_class__(self, /):
        return type(self)._get_ptolemaic_class()


###############################################################################
###############################################################################
