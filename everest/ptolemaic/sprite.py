###############################################################################
''''''
###############################################################################


import inspect as _inspect
from collections import abc as _collabc
import types as _types

import numpy as _np

from everest.utilities import pretty as _pretty

from .ousia import Ousia as _Ousia


class Sprite(_Ousia):
    ...


class SpriteBase(metaclass=Sprite):

    MERGENAMES = ('__params__',)
    __params__ = ()

    @classmethod
    def _yield_paramnames(cls, /):
        yield from cls.__params__

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from super()._yield_concrete_slots()
        yield from cls._yield_paramnames()

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        paramstr = ', '.join(cls.__params__)
        exec('\n'.join((
            f"@classmethod",
            f"def parameterise(cls, /, {paramstr}):",
            f"    return ({paramstr})",
            )))
        cls.parameterise = eval('parameterise')

    def initialise(self, /):
        for name, val in self.params._asdict().items():
            setattr(self, name, val)
        super().initialise()


###############################################################################
###############################################################################




# class Funcc(metaclass=Sprite):

#     __params__ = ('func',)

#     @property
#     def __call__(self, /):
#         return self.func

#     def make_epitaph(self, /):
#         ptolcls = self.__ptolemaic_class__
#         return ptolcls.taphonomy.callsig_epitaph(ptolcls, self.func)

#     def _content_repr(self, /):
#         return repr(self.func)

#     def _repr_pretty_(self, p, cycle, root=None):
#         if root is None:
#             root = self.__ptolemaic_class__.__qualname__
#         _pretty.pretty_function(self.func, p, cycle, root=root)


# @_collabc.Sequence.register
# class Tuuple(metaclass=Ousia):

#     __req_slots__ = ('_content',)

#     def __init__(self, /, *args, **kwargs):
#         self._content = tuple(map(
#             self._process_field, tuple(*args, **kwargs)
#             ))

#     for methname in (
#             '__getitem__', '__len__', '__contains__', '__iter__',
#             '__reversed__', '__index__', '__count__',
#             ):
#         exec('\n'.join((
#             f"@property",
#             f"def {methname}(self, /):",
#             f"    return self._content.{methname}",
#             )))
#     del methname

#     def _content_repr(self, /):
#         return repr(self._content)

#     def _repr_pretty_(self, p, cycle, root=None):
#         if root is None:
#             root = self.__ptolemaic_class__.__qualname__
#         _pretty.pretty_tuple(self._content, p, cycle, root=root)

#     def make_epitaph(self, /):
#         ptolcls = self.__ptolemaic_class__
#         return ptolcls.taphonomy.callsig_epitaph(ptolcls, self._content)


# @_collabc.Mapping.register
# class Binding(metaclass=Ousia):

#     __req_slots__ = ('_content',)

#     def __init__(self, /, *args, **kwargs):
#         self._content = {
#             self._process_field(key): self._process_field(val)
#             for key, val in dict(*args, **kwargs).items()
#             }

#     for methname in (
#             '__getitem__', '__len__', '__contains__', '__iter__',
#             'keys', 'items', 'values', 'get',
#             ):
#         exec('\n'.join((
#             f"@property",
#             f"def {methname}(self, /):",
#             f"    return self._content.{methname}",
#             )))
#     del methname

#     def _content_repr(self, /):
#         return ', '.join(map(':'.join, zip(
#             map(repr, self),
#             map(repr, self.values()),
#             )))

#     def _repr_pretty_(self, p, cycle, root=None):
#         if root is None:
#             root = self.__ptolemaic_class__.__qualname__
#         _pretty.pretty_dict(self._content, p, cycle, root=root)

#     def make_epitaph(self, /):
#         ptolcls = self.__ptolemaic_class__
#         return ptolcls.taphonomy.callsig_epitaph(ptolcls, **self._content)


# class Kwargs(Binding):

#     def __init__(self, /, *args, **kwargs):
#         self._content = {
#             str(key): self._process_field(val)
#             for key, val in dict(*args, **kwargs).items()
#             }

#     def _content_repr(self, /):
#         return ', '.join(map(':'.join, zip(
#             map(str, self),
#             map(repr, self.values()),
#             )))

#     def _repr_pretty_(self, p, cycle, root=None):
#         if root is None:
#             root = self.__ptolemaic_class__.__qualname__
#         _pretty.pretty_kwargs(self, p, cycle, root=root)

#     def make_epitaph(self, /):
#         ptolcls = self.__ptolemaic_class__
#         return ptolcls.taphonomy.callsig_epitaph(
#             ptolcls, **self
#             )


# class Arraay(metaclass=Ousia):

#     __req_slots__ = ('_array',)

#     def __init__(self, arg, /, dtype=None):
#         if isinstance(arg, bytes):
#             arr = _np.frombuffer(arg, dtype=dtype)
#         else:
#             arr = _np.array(arg, dtype=dtype).copy()
#         object.__setattr__(self, '_array', arr)

#     for methname in (
#             'dtype', 'shape', '__len__',
#             ):
#         exec('\n'.join((
#             f"@property",
#             f"def {methname}(self, /):",
#             f"    return self._array.{methname}",
#             )))
#     del methname

#     def __getitem__(self, arg, /):
#         out = self._array[arg]
#         if isinstance(out, _np.ndarray):
#             return self.__ptolemaic_class__(out)
#         return out

#     def _content_repr(self, /):
#         return _np.array2string(self._array, threshold=100)[:-1]

#     def _repr_pretty_(self, p, cycle, root=None):
#         if root is None:
#             root = self.__ptolemaic_class__.__qualname__
#         _pretty.pretty_array(self._array, p, cycle, root=root)

#     def make_epitaph(self, /):
#         ptolcls = self.__ptolemaic_class__
#         content = f"{repr(bytes(self._array))},{repr(str(self.dtype))}"
#         return ptolcls.taphonomy(
#             f"""m('everest.ptolemaic.ousia').Arraay({content})""",
#             {},
#             )
