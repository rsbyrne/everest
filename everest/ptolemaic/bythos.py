###############################################################################
''''''
###############################################################################


from everest.incision import (
    Incisable as _Incisable,
    IncisionProtocol as _IncisionProtocol,
    )

from everest.ptolemaic.essence import Essence as _Essence


class Bythos(_Essence):

    def __getitem__(cls, arg, /):
        return cls.__incise__(arg, caller=cls)

    @property
    def __contains__(cls, /):
        return cls.__class_contains__

    @classmethod
    def __class_contains__(cls, arg, /):
        return False

    @property
    def __iter__(cls, /):
        return cls.__class_iter__

    def __class_iter__(cls, /):
        raise NotImplementedError

#     def __class_getitem__(cls, arg, /):
#         return cls.__incise__(arg, caller=cls)

    ### Incision protocol:

    @property
    def __incise__(cls, /):
        return cls.__class_incise__

    @property
    def __chain_incise__(cls, /):
        return cls.__class_chain_incise__

    @property
    def __incise_trivial__(cls, /):
        return cls.__class_incise_trivial__

    @property
    def __incise_slyce__(cls, /):
        return cls.__class_incise_slyce__

    @property
    def __incise_retrieve__(cls, /):
        return cls.__class_incise_retrieve__

    @property
    def __incise_fail__(cls, /):
        return cls.__class_incise_fail__

    @property
    def __incise_generic__(cls, /):
        try:
            return cls.__class_incise_generic__
        except AttributeError:
            raise _IncisionProtocol.GENERIC.exc(cls)

    @property
    def __incise_variable__(cls, /):
        try:
            return cls.__class_incise_variable__
        except AttributeError:
            raise _IncisionProtocol.VARIABLE.exc(cls)

    __class_incise__ = _Incisable.__incise__
    __class_incise_trivial__ = _Incisable.__incise_trivial__
    __class_incise_slyce__ = _Incisable.__incise_slyce__
    __class_incise_retrieve__ = _Incisable.__incise_retrieve__
    __class_incise_fail__ = _Incisable.__incise_fail__

#     @property
#     def issuperset(cls, /):
#         return cls.class_issuperset

#     @property
#     def issubset(cls, /):
#         return cls.class_issubset

#     __class_incise_generic__ = _Incisable.__incise_generic__
#     __class_incise_variable__ = _Incisable.__incise_variable__
#     class_issuperset = _Incisable.issuperset
#     class_issubset = _Incisable.issubset
#     __class_contains__ = _Incisable.__contains__


###############################################################################
###############################################################################
