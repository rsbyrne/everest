###############################################################################
''''''
###############################################################################


import types as _types
import weakref as _weakref

from everest.utilities import pretty as _pretty
from everest.exceptions import (
    FrozenAttributesException as _FrozenAttributesException
    )

from .essence import Essence as _Essence
from .sprite import Sprite as _Sprite
from .ousia import Ousia as _Ousia


class Diict(metaclass=_Sprite):

    _req_slots__ = ('_content_',)

    for name in (
            '__getitem__', '__len__', '__iter__', '__contains__',
            'keys', 'values', 'items', 'get',
            ):
        exec('\n'.join((
            f'@property',
            f'def {name}(self, /):',
            f"    return self._content_.{name}",
            )))
    del name

    @classmethod
    def __class_call__(cls, _content_: dict = None, /, *args, **kwargs):
        if _content_ is None:
            _content_ = kwargs
        elif kwargs:
            _content_ = dict(_content_) | kwargs
        obj = super().__class_call__(*args)
        with obj.mutable:
            obj._content_ = _content_
        return obj

    def get_epitaph(self, /):
        ptolcls = self._ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(
            ptolcls, self._content_
            )

    def __repr__(self, /):
        valpairs = ', '.join(map(':'.join, zip(
            map(repr, _content_ := self._content_),
            map(repr, _content_.values()),
            )))
        return f"<{self._ptolemaic_class__}{{{valpairs}}}>"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_dict(self._content_, p, cycle, root=root)


class Kwargs(Diict):

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        out = super().__class_call__(*args, **kwargs)
        if not all(map(str.__instancecheck__, out)):
            raise TypeError("All keys of Kwargs must be str type.")
        return out

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self._content_, p, cycle, root=root)


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
            return super().__getattr__(name)
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


    # for name in (
    #         '__setitem__', '__delitem__',
    #         'pop', 'popitem', 'clear', 'update', 'setdefault'
    #         ):
    #     exec('\n'.join((
    #         f'@property',
    #         f'def {name}(self, /):',
    #         f"    return self._content_.{name}",
    #         )))
    # del name