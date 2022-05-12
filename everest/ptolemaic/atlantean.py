###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
from collections import abc as _collabc

import numpy as _np

from everest.utilities import pretty as _pretty, caching as _caching
from everest import epitaph as _epitaph

from everest.ur import Dat as _Dat
from everest.primitive import Primitive as _Primitive

from .ousia import Ousia as _Ousia


class Atlantean(_Ousia):
    ...


def convert(val, /):
        if isinstance(val, _Dat):
            return val
        if isinstance(val, _np.ndarray):
            return Arraay(val)
        if isinstance(val, _collabc.Mapping):
            return Binding(**val)
        if isinstance(val, _collabc.Sequence):
            return Tuuple(val)
        raise TypeError(
            f"Object {val} of type {type(val)} cannot be converted to a _Dat."
            )


@_Dat.register
class AtlanteanBase(metaclass=Atlantean):

    def __process_attr__(self, val, /):
        return convert(val)

    @property
    @_caching.soft_cache()
    def epitaph(self, /):
        return self.make_epitaph()

    @property
    @_caching.soft_cache()
    def contentrepr(self, /):
        return self._content_repr()

    def __reduce__(self, /):
        return self.epitaph, ()


@AtlanteanBase.register
class Tuuple(tuple):

    def __new__(cls, iterable=(), /):
        return super().__new__(cls, map(convert, iterable))

    def __repr__(self, /):
        return f"Tuuple{super().__repr__()}"

    @property
    def epitaph(self, /):
        return AtlanteanBase.taphonomy.callsig_epitaph(type(self), tuple(self))


class Binding(dict, metaclass=Atlantean):

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update({convert(key): convert(val) for key, val in self.items()})

    @property
    def __setitem__(self, /):
        if self.freezeattr:
            raise NotImplementedError
        return super().__setitem__

    @property
    def __delitem__(self, /):
        if self.freezeattr:
            raise NotImplementedError
        return super().__delitem__

    def __repr__(self, /):
        valpairs = ', '.join(map(':'.join, zip(
            map(repr, self),
            map(repr, self.values()),
            )))
        return f"<{self.__ptolemaic_class__}{{{valpairs}}}>"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_dict(self, p, cycle, root=root)

    def __hash__(self, /):
        return self.hashint

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(ptolcls, dict(self))

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return hash(self) < hash(other)

    def __gt__(self, other, /):
        return hash(self) < hash(other)


class Kwargs(Binding):

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self, p, cycle, root=root)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(
            ptolcls, **self
            )


class Arraay(metaclass=Atlantean):

    __req_slots__ = ('_array',)

    def __init__(self, arg, /, dtype=None):
        if isinstance(arg, bytes):
            arr = _np.frombuffer(arg, dtype=dtype)
        else:
            arr = _np.array(arg, dtype=dtype).copy()
        object.__setattr__(self, '_array', arr)

    for methname in (
            'dtype', 'shape', '__len__',
            ):
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self._array.{methname}",
            )))
    del methname

    def __getitem__(self, arg, /):
        out = self._array[arg]
        if isinstance(out, _np.ndarray):
            return self.__ptolemaic_class__(out)
        return out

    def _content_repr(self, /):
        return _np.array2string(self._array, threshold=100)[:-1]

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_array(self._array, p, cycle, root=root)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        content = f"{repr(bytes(self._array))},{repr(str(self.dtype))}"
        return ptolcls.taphonomy(
            f"""m('everest.ptolemaic.atlantean').Arraay({content})""",
            {},
            )


###############################################################################
###############################################################################
