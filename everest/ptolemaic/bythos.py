###############################################################################
''''''
###############################################################################


from everest.incision import IncisionProtocol as _IncisionProtocol

from everest.ptolemaic.essence import Essence as _Essence


class Bythos(_Essence):

    def __getitem__(cls, arg, /):
        return cls.__incision_manager__.__incise__(arg, caller=cls)

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

    ### Incision protocol:

    @property
    def __incision_manager__(cls, /):
        return cls.__class_get_incision_manager__()

    def __class_get_incision_manager__(cls, /):
        raise NotImplementedError

    @property
    def __incise__(cls, /):
        return _IncisionProtocol.INCISE(cls.__incision_manager__)

    @property
    def __incise_trivial__(cls, /):
        return _IncisionProtocol.TRIVIAL(cls.__incision_manager__)

    @property
    def __incise_retrieve__(cls, /):
        return _IncisionProtocol.RETRIEVE(cls.__incision_manager__)

    @property
    def __incise_slyce__(cls, /):
        return _IncisionProtocol.SLYCE(cls.__incision_manager__)

    @property
    def __incise_fail__(cls, /):
        return _IncisionProtocol.FAIL(cls.__incision_manager__)


###############################################################################
###############################################################################
