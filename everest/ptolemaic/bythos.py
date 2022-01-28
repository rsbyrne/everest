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
        return cls.__class_contains__

    @property
    def __includes__(cls, /):
        return cls.__class_includes__

    @property
    def __iter__(cls, /):
        return cls.__class_iter__

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

    ### Class init:

    def __class_deep_init__(cls, /, *args, **kwargs):
        super().__class_deep_init__(*args, **kwargs)
        cls.__class_incise_trivial__ = lambda: cls


class BythosBase(metaclass=Bythos):

    # Doesn't need to be decorated with classmethod for some reason:
    def __class_getitem__(cls, arg, /):
        return _IncisionProtocol.INCISE(cls)(arg, caller=cls)

    __class_incise_retrieve__ = \
        classmethod(_IncisionHandler.__incise_retrieve__)
    __class_incise_slyce__ = \
        classmethod(_IncisionHandler.__incise_slyce__)
    __class_incise_fail__ = \
        classmethod(_IncisionHandler.__incise_fail__)        


###############################################################################
###############################################################################
