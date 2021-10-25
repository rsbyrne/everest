###############################################################################
''''''
###############################################################################


import weakref as _weakref

from . import _Shade


class Singleton(_Shade):

    @classmethod
    def __class_init__(cls, /):
        cls.premade = _weakref.WeakValueDictionary()
        super().__class_init__()

    @classmethod
    def prekey(cls, params):
        return params.__str__()

    @classmethod
    def instantiate(cls, params):
        premade = cls.premade
        prekey = cls.prekey(params)
        if prekey in premade:
            return premade[prekey]
        obj = cls.metacls.instantiate(cls, params)
        premade[prekey] = obj
        return obj


###############################################################################
###############################################################################
