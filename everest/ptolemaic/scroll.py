###############################################################################
''''''
###############################################################################


import inspect as _inspect
import sys as _sys
import itertools as _itertools

from .system import System as _System
from . import ptolemaic as _ptolemaic


def _get_calling_scope_name_(name):
    frame = _inspect.stack()[1][0]
    while name not in frame.f_locals:
        frame = frame.f_back
        if frame is None:
            return None
    return frame.f_locals[name]


class Scroll(metaclass=_System):

    __slots__ = ('_module_',)

    name: str

    def initialise(self, /):
        dct = self._module_.__dict__
        dct.update(_itertools.starmap(self.process_name_val, tuple(dct.items())))
        super().initialise()

    def process_name_val(self, name, val, /):
        if isinstance(val, (_ptolemaic.Ideal, _ptolemaic.Case)):
            if val.mutable:
                self.register_innerobj(name, val)
        elif not name.startswith('_'):
            val = _ptolemaic.convert(val)
        return name, val

    @classmethod
    def commence(cls, /):
        name = _get_calling_scope_name_('__name__')
        modules = _sys.modules
        module = modules[name]
        scroll = module.__dict__.get('_Scroll_', cls).instantiate((name,))
        scroll._module_ = module
        module._ISSCROLL_ = True
        modules[name] = scroll
        return scroll

    @classmethod
    def complete(cls, /):
        name = _get_calling_scope_name_('__name__')
        scroll = _sys.modules[name]
        if not isinstance(scroll, Scroll):
            raise RuntimeError("Cannot complete incomplete scroll.")
        if not scroll.mutable:
            raise RuntimeError("Cannot complete already-complete scroll.")
        _sys.modules[name].initialise()

    def __getattr__(self, name, /):
        try:
            super().__getattr__(name)
        except AttributeError as exc:
            return getattr(self._module_, name)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy(self._module_)

    def __repr__(self, /):
        return self._module_.__name__

    def __str__(self, /):
        return self._module_.__name__

    def _repr_pretty_(self, p, cycle, root=None):
        p.text(repr(self))


commence = Scroll.commence
complete = Scroll.complete


###############################################################################
###############################################################################
