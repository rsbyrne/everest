###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import sys as _sys
import itertools as _itertools
import types as _types
import weakref as _weakref

from everest.armature import Armature as _Armature

# from .ousia import Ousia as _Ousia
from . import ptolemaic as _ptolemaic


def _get_calling_scope_name_(name):
    frame = _inspect.stack()[1][0]
    while name not in frame.f_locals:
        frame = frame.f_back
        if frame is None:
            return None
    return frame.f_locals[name]


@_ptolemaic.Ptolemaic.register
class _SteleMeta_(_Armature):

    @property
    def __instancecheck__(cls, /):
        return _abc.ABCMeta.__instancecheck__.__get__(cls)

    @property
    def __subclasscheck__(cls, /):
        return _abc.ABCMeta.__subclasscheck__.__get__(cls)

    def commence(cls, /):
        name = _get_calling_scope_name_('__name__')
        modules = _sys.modules
        module = modules[name]
        if isinstance(module, cls):
            return module
        if isinstance(module, _types.ModuleType):
            stele = (
                module.__dict__.get('_Stele_', cls)
                .__instantiate__(name)
                )
            stele._module_ = module
            stele.name = module.__name__
            modules[name] = stele
            return stele
        raise ValueError("Only module types can be converted to Stele.")

    def __enter__(cls, /):
        return cls.commence()

    def complete(cls, /):
        name = _get_calling_scope_name_('__name__')
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

    __slots__ = ('_module_', '__dict__', '_innerobjs')

    name: str

    _ISSTELE_ = True

    @classmethod
    def __parameterise__(cls, name, /):
        return super().__parameterise__(name=name)

    def __initialise__(self, /):
        module = self._module_
        # del self._module_
        self.__dict__ = {
            name: self._process_val_(name, val)
            for name, val in module.__dict__.items()
            if not name.startswith('_')
            }
        super().__initialise__()
        try:
            innerobjs = self._innerobjs
        except AttributeError:
            pass
        else:
            for name, obj in innerobjs.items():
                obj.__initialise__()
            object.__delattr__(self, '_innerobjs')

    def _make_epitaph_(self, taph, /):
        return taph(self._module_)

    def register_innerobj(self, name, obj, /):
        try:
            innerobjs = self._innerobjs
        except AttributeError:
            innerobjs = self._innerobjs = {}
        innerobjs[name] = obj
        obj._configure_as_innerobj(self, name)

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


commence = Stele.__enter__
complete = Stele.__exit__


###############################################################################
###############################################################################
