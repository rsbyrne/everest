###############################################################################
''''''
###############################################################################


import weakref as _weakref

from .meta import PtolemaicMeta as _PtolemaicMeta


class Aspect(metaclass=_PtolemaicMeta):
    '''
    Aspect classes are compatible as bases for other classes.
    '''


class Singleton(Aspect):

    @classmethod
    def _cls_extra_init_(cls, /):
        cls.premade = _weakref.WeakValueDictionary()

    @classmethod
    def prekey(cls, params):
        return params.__str__()

    @classmethod
    def instantiate(cls, params):
        premade = cls.__dict__['premade']
        prekey = cls.prekey(params)
        if prekey in premade:
            return premade[prekey]
        obj = type(cls).instantiate(cls, params)
        premade[prekey] = obj
        return obj


###############################################################################
###############################################################################
