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
    if isinstance(val, _collabc.Mapping):
        return Diict(**val)
    if isinstance(val, _collabc.Sequence):
        return Tuuple(val)
    raise TypeError(
        f"Object {val} of type {type(val)} cannot be converted to a _Dat."
        )


@_Dat.register
class AtlanteanBase(metaclass=Atlantean):

    @_abc.abstractmethod
    def make_epitaph(self, /):
        raise NotImplementedError

    @property
    @_caching.soft_cache()
    def epitaph(self, /):
        return self.make_epitaph()

    def __setattr__(self, name, val, /):
        super().__setattr__(name, convert(val))


@AtlanteanBase.register
class Tuuple(tuple):

    def __new__(cls, iterable=(), /):
        return super().__new__(cls, map(convert, iterable))

    def __repr__(self, /):
        return f"Tuuple{super().__repr__()}"

    @property
    def epitaph(self, /):
        return _epitaph.TAPHONOMY.callsig_epitaph(type(self), tuple(self))


class Diict(dict, metaclass=Atlantean):

    # @classmethod
    # def __class_call__(cls, /, *args, **kwargs):
    #     obj = cls.instantiate()
    #     dict.__init__(obj, *args, **kwargs)
    #     object.__setattr__(obj, 'freezeattr', _Switch(True))
    #     return obj

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
        return f"<{self._ptolemaic_class__}{{{valpairs}}}>"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_dict(self, p, cycle, root=root)

    def __hash__(self, /):
        return self.hashint

    def make_epitaph(self, /):
        return _epitaph.TAPHONOMY.callsig_epitaph(
            self._ptolemaic_class__, dict(self)
            )

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


class Kwargs(Diict):

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self, p, cycle, root=root)

    def make_epitaph(self, /):
        ptolcls = self._ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(
            ptolcls, **self
            )


class Arraay(metaclass=Atlantean):

    _req_slots__ = ('_array',)

    def __init__(self, arg, /, dtype=None):
        if isinstance(arg, bytes):
            arr = _np.frombuffer(arg, dtype=dtype)
        else:
            arr = _np.array(arg, dtype=dtype).copy()
        object.__setattr__(self, '_array', arr)

    for methname in (
            'dtype', 'shape', '__len__', '__getitem__'
            ):
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self._array.{methname}",
            )))
    del methname

    def _content_repr(self, /):
        return _np.array2string(self._array, threshold=100)[:-1]

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_array(self._array, p, cycle, root=root)

    def make_epitaph(self, /):
        ptolcls = self._ptolemaic_class__
        content = f"{repr(bytes(self._array))},{repr(str(self.dtype))}"
        return ptolcls.taphonomy(
            f"""m('everest.ptolemaic.atlantean').Arraay({content})""",
            {},
            )


###############################################################################
###############################################################################
