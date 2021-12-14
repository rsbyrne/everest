###############################################################################
''''''
###############################################################################


import abc as _abc


NoneType = type(None)
EllipsisType = type(Ellipsis)


class NotNone(_abc.ABC):

    @classmethod
    def __subclasshook__(cls, other, /):
        return not issubclass(other, type(None))


class Null(_abc.ABC):

    @classmethod
    def __subclasshook__(cls, other, /):
        return False


###############################################################################
###############################################################################
