###############################################################################
''''''
###############################################################################


from everest.incision import Incisable as _Incisable
from everest.ptolemaic.essence import Essence as _Essence


class Bythos(_Essence):

#     chora = _UNIVERSE

#     def __init__(cls, /, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if cls.chora is None:
#             raise RuntimeError(
#                 "Classes inheriting from `Bythos` must provide a chora."
#                 )

    def __getitem__(cls, arg, /):
        return cls.__incise__(arg, caller=cls)

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
        return cls.__class_incise_generic__

    @property
    def __incise_variable__(cls, /):
        return cls.__class_incise_variable__

    @property
    def issuperset(cls, /):
        return cls.class_issuperset

    @property
    def issubset(cls, /):
        return cls.class_issubset

    @property
    def __contains__(cls, /):
        return cls.__class_contains__

    __class_incise__ = _Incisable.__incise__
    __class_chain_incise__ = _Incisable.__chain_incise__
    __class_incise_trivial__ = _Incisable.__incise_trivial__
    __class_incise_slyce__ = _Incisable.__incise_slyce__
    __class_incise_retrieve__ = _Incisable.__incise_retrieve__
    __class_incise_fail__ = _Incisable.__incise_fail__
    __class_incise_generic__ = _Incisable.__incise_generic__
    __class_incise_variable__ = _Incisable.__incise_variable__
    class_issuperset = _Incisable.issuperset
    class_issubset = _Incisable.issubset
    __class_contains__ = _Incisable.__contains__


###############################################################################
###############################################################################
