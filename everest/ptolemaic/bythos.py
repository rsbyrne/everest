###############################################################################
''''''
###############################################################################


import abc as _abc

from .essence import Essence as _Essence


BYTHOSMETHODS = (
    '__contains__', '__includes__'
    )


class Bythos(_Essence):

    for methname in BYTHOSMETHODS:
        exec('\n'.join((
            f"@property",
            f"def {methname}(cls, /):",
            f"    return cls.__class_{methname.strip('_')}__",
            )))
    del methname


class _BythosBase_(metaclass=Bythos):

    # Special-cased, so no need for @classmethod
    @_abc.abstractmethod
    def __class_getitem__(cls, arg, /):
        raise NotImplementedError


###############################################################################
###############################################################################
