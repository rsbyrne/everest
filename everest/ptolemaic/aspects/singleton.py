###############################################################################
''''''
###############################################################################


import weakref as _weakref

from .aspect import Aspect as _Aspect


class Singleton(_Aspect):

    @classmethod
    def _cls_extra_init_(cls, /):
        print("Singleton cls init called")
        cls.premade = _weakref.WeakValueDictionary()
        super()._cls_extra_init_()

    @classmethod
    def prekey(cls, params):
        return params.__str__()

    @classmethod
    def instantiate(cls, params):
        premade = cls.premade
        prekey = cls.prekey(params)
        if prekey in premade:
            return premade[prekey]
        obj = type(cls).instantiate(cls, params)
        premade[prekey] = obj
        return obj


###############################################################################
###############################################################################
