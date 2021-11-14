###############################################################################
''''''
###############################################################################


from everest import utilities as _utilities
from everest.ptolemaic.shades.shade import Shade as _Shade


class DeferrerClass(_Shade):

    _ptolemaic_mergetuples__ = ('defermeths',)
    defermeths = ()

    _req_slots__ = ('_obj',)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        for meth in cls.defermeths:
            _utilities.classtools.add_defer_meth(cls, meth, '_obj')

    def __init__(self, obj, /, *args, **kwargs):
        self._obj = obj
        super().__init__(*args, **kwargs)


###############################################################################
###############################################################################
