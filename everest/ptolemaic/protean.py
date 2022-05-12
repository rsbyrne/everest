###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import types as _types

from everest.ur import Var as _Var, Dat as _Dat

from .ousia import Ousia as _Ousia


class Protean(_Ousia):
    ...


class SetView:

    __slots__ = ('content',)

    def __init__(self, content: set, /):
        self.content = content

    for methname in {'__len__', '__iter__', '__contains__'}:
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self.content.{methname}",
            )))
    del methname

    def __repr__(self, /):
        return f"{type(self)}({super().__repr__()})"


@_Var.register
class ProteanBase(metaclass=Protean):

    MERGETUPLES = ('_var_slots__',)

    __req_slots__ = ('_dependants', '_state',)

    @classmethod
    def corporealise(cls, /):
        obj = super().corporealise()
        object.__setattr__(obj, '_dependents', _weakref.WeakSet())
        object.__setattr__(obj, '_state', {})
        return obj

    @property
    def dependants(self, /):
        return SetView(self._dependants)

    def add_dependant(self, obj, /):
        self._dependants.add(obj)

    @property
    def state(self, /):
        return _types.MappingProxyType(self._state)

    def __setattr__(self, name, val, /):
        if name in type(self)._var_slots__:
            object.__setattr__(self, name, val)
        else:
            if isinstance(val, _Var):
                val.add_dependant(self)
            elif not isinstance(val, _Dat):
                raise TypeError
            super().__setattr__(name, val)

    def __getstate__(self, /):
        return self._state

    def __setstate__(self, state, /):
        _state = self._state
        _state.clear()
        _state.update(state)


###############################################################################
###############################################################################
