###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import hashlib as _hashlib

from . import _utilities

from .pleroma import Pleroma as _Pleroma
from .shade import Shade as _Shade
from .ousia import Ousia as _Ousia
from .hypostasis import Hypostasis as _Hypostasis
from .primitive import Primitive as _Primitive

from . import exceptions as _exceptions


_caching = _utilities.caching
_word = _utilities.word


class Ptolemaic(_Hypostasis, metaclass=_Ousia):

    _ptolemaic_mroclasses__ = ('BadParameter',)

    class BadParameter(_exceptions.ParameterisationException):

        __slots__ = ('param',)

        def __init__(self, param, /):
            self.param = param

        def message(self, /):
            yield from super().message()
            yield "when an object of unrecognised type was passed as a parameter."
            try:
                rep = repr(self.param)
            except Exception as exc:
                yield 'While writing this message, another exception occurred:'
                yield str(exc)
            else:
                yield 'The object looked something like this:'
                yield rep

    @classmethod
    def __class_init__(cls, /):
        type(cls).__class_init__(cls)

    @classmethod
    def check_param(cls, arg, /):
        if isinstance(arg, _Pleroma):
            return arg
        if isinstance(arg, Ptolemaic):
            return arg
        if isinstance(arg, _Primitive):
            return arg
        if isinstance(arg, tuple):
            return Tuuple(*arg)
        if isinstance(arg, dict):
            return Mapp(**arg)
        raise cls.BadParameter(arg)

    def _repr(self, /):
        return ', '.join(
            '='.join((pair[0], repr(pair[1])))
            for pair in self.params.arguments.items()
            )

    def __repr__(self, /):
        return f"<{repr(type(self))}({self._repr()})>"

    @property
    @_caching.soft_cache()
    def hashcode(self):
        content = repr(self).encode()
        return _hashlib.md5(content).hexdigest()

    @property
    @_caching.soft_cache()
    def hashint(self):
        return int(self.hashcode, 16)

    @property
    @_caching.soft_cache()
    def hashID(self):
        return _word.get_random_english(seed=self.hashint, n=2)


class Proxy(_Shade):

    _ptolemaic_mergetuples__ = ('defermeths',)

    defermeths = ()

    _req_slots__ = ('_obj',)

    @classmethod
    def __class_init__(cls, /):
        type(cls).__class_init__(cls)
        for meth in cls.defermeths:
            _utilities.classtools.add_defer_meth(cls, meth, '_obj')


class ProxyCollection(Proxy, _collabc.Sequence):

    defermeths = ('__getitem__', '__len__', '__iter__')


class Tuuple(ProxyCollection, Ptolemaic, _collabc.Sequence):

    defermeths = ('__contains__', '__reversed__', 'index', 'count')

    def __init__(self, /, *args):
        self._obj = args

    def _repr(self, /):
        return ', '.join(map(repr, self._obj))


class Mapp(ProxyCollection, Ptolemaic, _collabc.Mapping):

    defermeths = (
        '__contains__', 'keys', 'items',
        'values', 'get', '__eq__', '__ne__',
        )

    def __init__(self, /, **kwargs):
        self._obj = kwargs

    def __getattr__(self, name):
        if name in (obj := self._obj):
            return obj[name]
        return super().__getattr__(name)

    def _repr(self, /):
        return ', '.join(
            '='.join((pair[0], repr(pair[1])))
            for pair in self._obj.items()
            )


###############################################################################
###############################################################################
