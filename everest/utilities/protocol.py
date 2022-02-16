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
        return getattr(obj, cls.DEFER.methname)

    @classmethod
    def _alt_defer(cls, obj, /):
        raise AttributeError

    @classmethod
    def defer_complies(cls, ACls, /):
        try:
            defername = cls.DEFER.methname
        except AttributeError:
            return False
        for Base in ACls.__mro__:
            if defername in Base.__dict__:
                return True
        return False

    @classmethod
    def complies(cls, ACls, /):
        compliant = cls._compliant
        try:
            return compliant[ACls]
        except KeyError:
            pass
        if cls.defer_complies(ACls):
            out = compliant[ACls] = True
            return out
        for methodname in cls.mandatory:
            for Base in ACls.__mro__:
                dct = Base.__dict__
                if methodname in dct:
                    break
            else:
                out = compliant[ACls] = False
                return out
        out = compliant[ACls] = True
        return out

    def __init__(self, methname, mandatory, /):
        super().__init__()
        if methname == 'DEFER':
            self.defer = self._alt_defer
        self.methname, self.mandatory = methname, mandatory

    def __call__(self, obj, default = None, /):
        methname = self.methname
        try:
            return getattr(obj, methname)
        except AttributeError:
            try:
                deferto = self.defer(obj)
            except (AttributeError, NotImplementedError):
                if default is None:
                    raise self.exc(obj)
                return default
            return self(deferto, default)

    def exc(self, obj, /):
        return AttributeError(obj, self.methname)


###############################################################################
###############################################################################
