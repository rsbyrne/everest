###############################################################################
''''''
###############################################################################


MODULEDUNDERS = tuple(vars())


import abc as _abc
import sys as _sys
import itertools as _itertools
import types as _types
import weakref as _weakref

from everest.switch import Switch as _Switch
from everest.armature import (
    Armature as _Armature, ImmutableError as _ImmutableError
    )

# from .ousia import Ousia as _Ousia
from . import ptolemaic as _ptolemaic


@_ptolemaic.Ptolemaic.register
class _SteleMeta_(_Armature):

    @property
    def __instancecheck__(cls, /):
        return _abc.ABCMeta.__instancecheck__.__get__(cls)

    @property
    def __subclasscheck__(cls, /):
        return _abc.ABCMeta.__subclasscheck__.__get__(cls)

    def commence(cls, /):
        name = _ptolemaic.get_calling_scope_name('__name__')
        modules = _sys.modules
        module = modules[name]
        if isinstance(module, cls):
            return module
        if isinstance(module, _types.ModuleType):
            stele = (
                module.__dict__.get('_Stele_', cls)
                .__instantiate__((name,))
                )
            object.__setattr__(stele, '_inblock_', _Switch(False))
            stele._module_ = module
            stele.name = module.__name__
            stele._innerobjs = {}
            modules[name] = stele
            return stele
        raise ValueError("Only module types can be converted to Stele.")

    def __enter__(cls, /):
        return cls.commence()

    def complete(cls, /):
        name = _ptolemaic.get_calling_scope_name('__name__')
        stele = _sys.modules[name]
        if not isinstance(stele, cls):
            raise RuntimeError("Cannot complete uncommenced stele.")
        if not stele.mutable:
            raise RuntimeError("Cannot initialise already initialised stele.")
        _sys.modules[name].__initialise__()

    def __exit__(cls, /, *_):
        cls.complete()

    @property
    def param_convert(cls, /):
        return _ptolemaic.convert


@_ptolemaic.Ptolemaic.register
class Stele(metaclass=_SteleMeta_):

    __slots__ = ('_module_', '__dict__', '_innerobjs', '_inblock_')

    name: str

    _ISSTELE_ = True

    @classmethod
    def __parameterise__(cls, name, /):
        return super().__parameterise__(name=name)

    def initialise_innerobjs(self, skip=frozenset(), /):
        for name in tuple(innerobjs := self._innerobjs):
            if name not in skip:
                innerobjs.pop(name).__initialise__()

    def __init__(self, /):
        module = self._module_
        # del self._module_
        self.__dict__ = {
            name: self._process_val_(name, val)
            for name, val in module.__dict__.items()
            if self._filter_nameval(name, val)
            }
        super().__init__()
        self.initialise_innerobjs()

    def __taphonomise__(self, taph, /):
        return taph(self._module_)

    def register_innerobj(self, name, obj, /):
        _ptolemaic.configure_as_innerobj(obj, self, name)
        if self.mutable:
            self._innerobjs[name] = obj
        else:
            try:
                meth = obj.__initialise__
            except AttributeError:
                pass
            else:
                meth()

    def _filter_nameval(self, name, val, /):
        if val is self:
            return False
        if name in MODULEDUNDERS:
            return False
        if hasattr(self, name):
            return False
        return not (name.startswith('_') and not name.endswith('_'))

    def _process_val_(self, name, val, /):
        if val is self:
            return name, _weakref.proxy(self)
        if isinstance(val, (_ptolemaic.Ideal, _ptolemaic.Case)):
            if val.mutable:
                self.register_innerobj(name, val)
        else:
            val = _ptolemaic.convert(val)
        return val

    def __repr__(self, /):
        return self.name

    def __str__(self, /):
        return self.name

    def _repr_pretty_(self, p, cycle, root=None):
        p.text(repr(self))


    @property
    class block:

        __slots__ = ('stele', '_skipnames')

        def __init__(self, stele, /):
            self.stele = stele

        def __enter__(self, /):
            stele = self.stele
            inblock = stele._inblock_
            if inblock:
                raise RuntimeError(
                    "Cannot enter a stele block from inside a stele block."
                    )
            self._skipnames = set(stele._innerobjs)
            inblock.toggle(True)

        def __exit__(self, exctype, /, *_):
            stele = self.stele
            if exctype is None:
                stele.initialise_innerobjs(self._skipnames)
            stele._inblock_.toggle(False)


    def __setattr__(self, name, val, /):
        val = super().__setattr__(name, val)
        if self._inblock_:
            setattr(self._module_, name, val)
        return val


commence = Stele.__enter__
complete = Stele.__exit__


###############################################################################
###############################################################################
