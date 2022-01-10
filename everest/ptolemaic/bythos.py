###############################################################################
''''''
###############################################################################


from everest.ptolemaic.chora import Chora as _Chora
from everest.ptolemaic.essence import Essence as _Essence


class Bythos(_Essence):

#     chora = _UNIVERSE

#     def __init__(cls, /, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if cls.chora is None:
#             raise RuntimeError(
#                 "Classes inheriting from `Bythos` must provide a chora."
#                 )

    @property
    def __incise__(cls, /):
        return cls.__class_incise__

    @classmethod
    def __class_incise__(cls, incisor, /, *, caller):
        raise NotImplementedError
#         return cls.chora.__chain_incise__(incisor, caller=caller)

    @property
    def __contains__(cls, /):
        return cls.__class_contains__

    def __class_contains__(cls, arg, /):
        raise NotImplementedError
#         return arg in cls.chora

    def __getitem__(cls, arg, /):
        return cls.__incise__(arg, caller=cls)

#     def __class_getitem__(cls, arg, /):
#         return cls.__incise__(arg, caller=cls)

    @property
    def __chain_incise__(cls, /):
        return cls.__class_chain_incise__
    
    def __class_chain_incise__(cls, incisor, /, *, caller):
        return _Chora.__chain_incise__(cls, incisor, caller=caller)

    @property
    def __incise_trivial__(cls, /):
        return cls.__class_incise_trivial__

    def __class_incise_trivial__(cls, /):
        return cls

    @property
    def __incise_slyce__(cls, /):
        return cls.__class_incise_slyce__

    def __class_incise_slyce__(cls, incisor, /):
        return _Chora.__incise_slyce__(cls, incisor)

    @property
    def __incise_retrieve__(cls, /):
        return cls.__class_incise_retrieve__

    @classmethod
    def __class_incise_retrieve__(cls, incisor, /):
        return _Chora.__incise_retrieve__(cls, incisor)

    @property
    def __incise_fail__(cls, /):
        return cls.__class_incise_fail__

    def __class_incise_fail__(cls, /, *args):
        return _Chora.__incise_fail__(cls, *args)

    @property
    def __incise_generic__(cls, /):
        return cls.__class_incise_generic__

    def __class_incise_generic__(cls, /):
        return _Chora.__incise_generic__(cls)

    @property
    def __incise_variable__(cls, /):
        return cls.__class_incise_variable__

    def __class_incise_variable__(cls, /):
        return _Chora.__incise_variable__(cls)

    @property
    def issuperset(cls, /):
        return cls.class_issuperset

    def class_issuperset(cls, other, /):
        return _Chora.issuperset(other)

    @property
    def issubset(cls, /):
        return cls.class_issubset

    def class_issubset(cls, other, /):
        return _Chora.issubset(other)


###############################################################################
###############################################################################
