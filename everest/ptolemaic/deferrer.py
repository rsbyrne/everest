###############################################################################
''''''
###############################################################################


from everest import utilities as _utilities
from everest.ptolemaic.aspect import Aspect as _Aspect


class DeferrerClass(_Aspect):

    _ptolemaic_mergetuples__ = ('_DEFERMETHS',)
    _DEFERMETHS = ()

    _req_slots__ = ('_obj',)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        for meth in cls._DEFERMETHS:
            _utilities.classtools.add_defer_meth(cls, meth, '_obj')

    def __init__(self, obj, /, *args, **kwargs):
        self._obj = obj
        super().__init__(*args, **kwargs)


###############################################################################
###############################################################################
