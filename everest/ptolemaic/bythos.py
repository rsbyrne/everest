###############################################################################
''''''
###############################################################################


import abc as _abc

from .essence import Essence as _Essence


BYTHOSMETHODS = (
    '__contains__', '__includes__', '__get__', '__set__', #'__del__'
    )


class Bythos(_Essence):

    for methname in BYTHOSMETHODS:
        exec('\n'.join((
            f"def {methname}(cls, /, *args, **kwargs):",
            f"    return cls.__class_{methname.strip('_')}__(*args, **kwargs)",
            )))
    del methname


class _BythosBase_(metaclass=Bythos):

    # Special-cased, so no need for @classmethod
    @_abc.abstractmethod
    def __class_getitem__(cls, arg, /):
        raise NotImplementedError

    @classmethod
    def __class_get__(cls, instance, owner=None, /):
        return cls

    @classmethod
    def __class_set__(cls, instance, value, /):
        raise AttributeError

    # @classmethod
    # def __class_del__(cls, instance, /):
    #     raise AttributeError


###############################################################################
###############################################################################
