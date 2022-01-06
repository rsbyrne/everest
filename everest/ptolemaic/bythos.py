###############################################################################
''''''
###############################################################################


from everest.ptolemaic.chora import Chora as _Chora, UNIVERSE as _UNIVERSE
from everest.ptolemaic.essence import Essence as _Essence


class Bythos(_Essence):

#     chora = _UNIVERSE

#     def __init__(cls, /, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if cls.chora is None:
#             raise RuntimeError(
#                 "Classes inheriting from `Bythos` must provide a chora."
#                 )

    def __incise__(cls, incisor, /, *, caller):
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
    
    def __chain_incise__(cls, incisor, /, *, caller):
        return _Chora.__chain_incise__(cls, incisor, caller=caller)

    def __incise_trivial__(cls, /):
        return cls

    def __incise_slyce__(cls, incisor, /):
        return _Chora.__incise_slyce__(cls, incisor)

    def __incise_retrieve__(cls, incisor, /):
        return _Chora.__incise_retrieve__(cls, incisor)

    def __incise_fail__(cls, /, *args):
        return _Chora.__incise_fail__(cls, *args)

    def __incise_generic__(cls, /):
        return _Chora.__incise_generic__(cls)

    def __incise_variable__(cls, /):
        return _Chora.__incise_variable__(cls)


###############################################################################
###############################################################################
