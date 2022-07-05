###############################################################################
''''''
###############################################################################


import inspect as _inspect
import sys as _sys
import itertools as _itertools
import types as _types
import weakref as _weakref

from .ousia import Ousia as _Ousia
from . import ptolemaic as _ptolemaic


def _get_calling_scope_name_(name):
    frame = _inspect.stack()[1][0]
    while name not in frame.f_locals:
        frame = frame.f_back
        if frame is None:
            return None
    return frame.f_locals[name]


class Stele(_Ousia):

    def commence(cls, /):
        name = _get_calling_scope_name_('__name__')
        modules = _sys.modules
        module = modules[name]
        if isinstance(module, cls):
            return module
        if isinstance(module, _types.ModuleType):
            stele = module.__dict__.get('_Stele_', cls).__instantiate__()
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


class _SteleBase_(metaclass=Stele):

    __slots__ = ('name', '_module_', '__dict__')

    _ISSTELE_ = True

    @classmethod
    def parameterise(cls, name, /):
        return super().parameterise(name=name)

    def __initialise__(self, /):
        module = self._module_
        del self._module_
        self.__dict__ = dict(_itertools.starmap(
            self._process_name_val_, module.__dict__.items()
            ))
        self._epitaph = self.__ptolemaic_class__.taphonomy(module)
        super().__initialise__()

    def _process_name_val_(self, name, val, /):
        if val is self:
            return name, _weakref.proxy(self)
        if isinstance(val, (_ptolemaic.Ideal, _ptolemaic.Case)):
            if val.mutable:
                self.register_innerobj(name, val)
        elif not name.startswith('_'):
            val = _ptolemaic.convert(val)
        return name, val

    def _make_epitaph_(self, /):
        raise NotImplementedError

    def __repr__(self, /):
        return self.name

    def __str__(self, /):
        return self.name

    def _repr_pretty_(self, p, cycle, root=None):
        p.text(repr(self))


commence = _SteleBase_.__enter__
complete = _SteleBase_.__exit__


###############################################################################
###############################################################################
