###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools

from everest import ur as _ur

from .sprite import Sprite as _Sprite
from .classbody import Directive as _Directive
from . import ptolemaic as _ptolemaic


class SmartAttr(_Directive, metaclass=_Sprite):

    __slots__ = ('cachedname', 'degenerate')

    hint: (object, str, tuple)
    note: str

    __merge_dyntyp__ = dict
    __merge_fintyp__ = _ptolemaic.PtolTuple
    _slotcached_ = False

    @staticmethod
    def _mangle_name_(name, /):
        return f'_{name}_'

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__merge_name__ = f"__{cls.__name__.lower()}s__"

    @classmethod
    def __body_call__(cls, body, arg=None, /, **kwargs):
        if arg is None:
            return _functools.partial(cls.__body_call__, body, **kwargs)
        return cls.semi_call(arg, **kwargs)

    def __init__(self, /):
        if self.__cosmic__:
            raise RuntimeError("SmartAttrs cannot be top-level objects.")
        super().__init__()

    def __directive_call__(self, body, name, /):
        body[self.__merge_name__][name] = self
        body.enroll_shade(name)
        if self._slotcached_:
            try:
                slots = body['__req_slots__']
            except KeyError:
                pass
            else:
                slots.append(name)
        mangledname = self._mangle_name_(name)
        body['__mangled_names__'][name] = mangledname
        return mangledname, self

    def __get__(self, instance, owner=None, /):
        return self


###############################################################################
###############################################################################
