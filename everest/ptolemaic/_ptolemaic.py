###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta

from . import _classtools


class PtolemaicMeta(_ABCMeta):
    def instantiate(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.__init__(*args, **kwargs)
        return obj
    def __call__(cls, *args, **kwargs):
        return cls.instantiate(*args, **kwargs)


@_classtools.Diskable
class Ptolemaic(metaclass = PtolemaicMeta):
    __slots__ = ('__dict__', '__weakref__')


###############################################################################
###############################################################################
