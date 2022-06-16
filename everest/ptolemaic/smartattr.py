###############################################################################
''''''
###############################################################################


import functools as _functools

from everest import ur as _ur

from .sprite import Sprite as _Sprite
from .classbody import Directive as _Directive
from .utilities import BindableObject as _BindableObject


class SmartAttr(_BindableObject, _Directive, metaclass=_Sprite):

    __slots__ = ('cachedname', 'degenerate')

    arg: object
    hint: (type, str, tuple)
    note: str

    __merge_dyntyp__ = dict
    __merge_fintyp__ = _ur.DatDict
    _slotcached_ = False

    @staticmethod
    def mangle_name(name, /):
        return f'_{name}_'

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__merge_name__ = f"__{cls.__name__.lower()}s__"

    @classmethod
    def __body_construct__(cls, body, *args, **kwargs):
        return cls(*args, **kwargs)

    @classmethod
    def __body_call__(cls, body, arg=None, /, **kwargs):
        if arg is None:
            return _functools.partial(cls.__body_call__, body, **kwargs)
        return cls.__body_construct__(body, arg=arg, **kwargs)

    def __init__(self, /):
        super().__init__()
        self.degenerate = not bool(self.arg)

    def __bound_owner_get__(self, owner, name, /):
        return self

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
        mangledname = self.mangle_name(name)
        body[mangledname] = self.arg
        body['__mangled_names__'][name] = mangledname


###############################################################################
###############################################################################
