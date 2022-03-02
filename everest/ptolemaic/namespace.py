###############################################################################
''''''
###############################################################################


import weakref as _weakref

from everest.utilities import pretty as _pretty
from everest.exceptions import (
    FrozenAttributesException as _FrozenAttributesException
    )

from .ousia import Ousia as _Ousia


class Namespace(metaclass=_Ousia):

    _dcttype = dict

    _req_slots__ = ('_content_',)

    for name in (
            '__len__', '__iter__', '__contains__', 'keys', 'values', 'items',
            ):
        exec('\n'.join((
            f'@property',
            f'def {name}(self, /):',
            f"    return self._content_.{name}",
            )))
    del name

    def __init__(self, /):
        super().__init__()
        self._content_ = self._dcttype({})

    def __getattr__(self, name, /):
        try:
            return object.__getattribute__(self, name)
        except AttributeError as exc:
            if name == '_content_':
                raise exc
            try:
                return self._content_[name]
            except KeyError:
                raise exc

    def _set_val(self, name, val, /):
        if not isinstance(name, str):
            raise TypeError(type(name))
        self._content_[name] = val

    def __setattr__(self, name, val, /):
        try:
            super().__setattr__(name, val)
        except _FrozenAttributesException:
            self._set_val(name, val)

    def __delattr__(self, name, /):
        try:
            super().__delattr__(name)
        except _FrozenAttributesException:
            del self._content_[name]

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self._content_, p, cycle, root=root)


class WeakNamespace(Namespace):

    _dcttype = _weakref.WeakValueDictionary


###############################################################################
###############################################################################
