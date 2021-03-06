################################################################################

from typing import Optional as _Optional
import weakref as _weakref

from . import _Function, _reseed, _generic

class Base(_Function, _generic.FuncyDatalike):
    __slots__ = ('downstream', 'name')
    def __init__(self, *, name: _Optional[str] = None, **kwargs) -> None:
        self.downstream = _weakref.WeakSet()
        if name is None:
            name = f"anon_{_reseed.randint(1e11, 1e12 - 1)}"
        self.name = name
        super().__init__(**kwargs)
    def register_downstream(self, registrant):
        self.downstream.add(registrant)
    def refresh(self):
        for down in self.downstream:
            down.purge()
    def _titlestr(self):
        return f"{super()._titlestr()} '{self.name}' "

################################################################################
