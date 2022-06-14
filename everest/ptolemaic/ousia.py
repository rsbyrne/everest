###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import itertools as _itertools

from everest.utilities import reseed as _reseed
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


class Ousia(_Urgon):

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
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        yield '__req_slots__', list, _ur.DatUniqueTuple

    @classmethod
    def _yield_bodynametriggers(meta, /):
        yield from super()._yield_bodynametriggers()
        yield (
            '__slots__',
            lambda body, val: body.__setitem__('__req_slots__', val)
            )


class _OusiaBase_(metaclass=Ousia):

    __slots__ = (
        '__weakref__',
        '_mutable', '_pyhash', '_sessioncacheref', '_epitaph',
        '_dependants', '_corpus',
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

    ### Object creation:

    @classmethod
    def construct(cls,
            params: tuple, /, *args,
            _corpus_=None, **kwargs
            ):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        switch = _Switch(True)
        object.__setattr__(obj, '_mutable', switch)
        obj._pyhash = _reseed.rdigits(16)
        if _corpus_:
            corpus, relname = _corpus_
            obj._corpus, obj._relname = _weakref.ref(corpus), relname
        # obj._dependants = _weakref.WeakSet()
        obj.params = params
        obj.__init__(*args, **kwargs)
        switch.toggle(False)
        return obj

    @property
    def __corpus__(self, /):
        try:
            return self._corpus()
        except AttributeError:
            return None

    @property
    def __cosmic__(cls, /):
        return cls.__corpus__ is None

    @property
    def __relname__(self, /):
        try:
            return self._relname
        except AttributeError:
            return None

    ### Storage:

    def __getattr__(self, name, /):
        if name in self.__getattribute__('__slots__'):
            raise AttributeError(name)
        try:
            return self.__dict__[name]
        except KeyError as exc:
            raise AttributeError from exc

    def __setattr__(self, name, val, /):
        if name in self.__getattribute__('__slots__'):
            if not self.__getattribute__('_mutable'):
                raise AttributeError(
                    name, "Cannot alter slot while frozen."
                    )
        try:
            super().__setattr__(name, val)
        except AttributeError:
            self.__getattribute__('__dict__')[name] = val

    def __delattr__(self, name, /):
        if name in self.__getattribute__('__slots__'):
            if not self.__getattribute__('_mutable'):
                raise AttributeError(
                    name, "Cannot alter slot while frozen."
                    )
        try:
            super().__delattr__(name)
        except AttributeError:
            dct = self.__getattribute__('__dict__')
            try:
                del dct[name]
            except KeyError as exc:
                raise AttributeError from exc

    @property
    # @_caching.weak_cache()
    def __dict__(self, /):
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
        self.__dict__.clear()
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
        try:
            return self._epitaph
        except AttributeError:
            epi = self.make_epitaph()
            super().__setattr__(self, '_epitaph', epi)
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
