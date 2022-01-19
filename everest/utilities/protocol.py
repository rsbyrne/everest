###############################################################################
''''''
###############################################################################


from enum import EnumMeta as _EnumMeta, Enum as _Enum
import weakref as _weakref


class _ProtocolMeta_(_EnumMeta):

    def __new__(meta, /, *args, **kwargs):
        typ = super().__new__(meta, *args, **kwargs)
        typ._compliant = _weakref.WeakKeyDictionary()
        typ.mandatory = tuple(
            protocol.methname for protocol in typ
            if protocol.mandatory
            )
        return typ


class Protocol(_Enum, metaclass=_ProtocolMeta_):

    @classmethod
    def defer(cls, obj, /):
        raise AttributeError

    @classmethod
    def complies(cls, ACls, /):
        compliant = cls._compliant
        try:
            return compliant[ACls]
        except KeyError:
            pass
        try:
            _ = cls.defer(ACls)
        except AttributeError:
            pass
        else:
            out = compliant[ACls] = True
            return out
        for methodname in cls.mandatory:
            for Base in ACls.__mro__:
                dct = Base.__dict__
                if methodname in dct:
                    break
                if '__slots__' in dct:
                    slots = dct['__slots__']
                    if methodname in slots:
                        break
            else:
                out = compliant[ACls] = False
                return out
        out = compliant[ACls] = True
        return out

    def __init__(self, methname, mandatory, /):
        super().__init__()
        self.methname, self.mandatory = methname, mandatory

    def __call__(self, obj, default = None, /):
        methname = self.methname
        try:
            return getattr(obj, methname)
        except AttributeError:
            try:
                return getattr(self.defer(obj), methname)
            except AttributeError:
                if default is None:
                    raise self.exc(obj)
                return default

    def exc(self, obj, /):
        return AttributeError(obj, self.methname)


###############################################################################
###############################################################################
