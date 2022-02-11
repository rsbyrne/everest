###############################################################################
''''''
###############################################################################


from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionHandler as _IncisionHandler,
    )

from everest.ptolemaic.essence import Essence as _Essence


class Bythos(_Essence):

    @property
    def __contains__(cls, /):
        return _IncisionProtocol.CONTAINS(cls)

    @property
    def __includes__(cls, /):
        return _IncisionProtocol.INCLUDES(cls)

    @property
    def __len__(cls, /):
        return _IncisionProtocol.LENGTH(cls)

    def __bool__(cls, /):
        return True

    @property
    def __iter__(cls, /):
        return _IncisionProtocol.ITER(cls)

    ### Incision protocol:

    @property
    def __incision_manager__(cls, /):
        return cls.__class_incision_manager__

    @property
    def __incise__(cls, /):
        return cls.__class_incise__

    @property
    def __incise_trivial__(cls, /):
        return cls.__class_incise_trivial__

    @property
    def __incise_retrieve__(cls, /):
        return cls.__class_incise_retrieve__

    @property
    def __incise_slyce__(cls, /):
        return cls.__class_incise_slyce__

    @property
    def __incise_fail__(cls, /):
        return cls.__class_incise_fail__

    @property
    def __incise_degenerate__(cls, /):
        return cls.__class_incise_degenerate__

    @property
    def __incise_empty__(cls, /):
        return cls.__class_incise_empty__

    @property
    def __incise_contains__(cls, /):
        return cls.__class_incise_contains__

    @property
    def __incise_includes__(cls, /):
        return cls.__class_incise_includes__

    @property
    def __incise_length__(cls, /):
        return cls.__class_incise_length__

    @property
    def __incise_iter__(cls, /):
        return cls.__class_incise_iter__

    ### Armature protocol:

    @property
    def __armature_brace__(cls, /):
        return cls.__class_armature_brace__

    @property
    def __armature_generic__(cls, /):
        return cls.__class_armature_generic__

    @property
    def __armature_variable__(cls, /):
        return cls.__class_armature_variable__


class BythosBase(metaclass=Bythos):

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incise_trivial__ = lambda: cls

    # Doesn't need to be decorated with classmethod for some reason:
    def __class_getitem__(cls, arg, /):
        return _IncisionProtocol.INCISE(cls)(arg, caller=cls)


###############################################################################
###############################################################################
