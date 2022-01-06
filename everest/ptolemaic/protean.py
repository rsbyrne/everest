###############################################################################
''''''
###############################################################################


import itertools as _itertools
import weakref as _weakref

from everest.ptolemaic import ptolemaic as _ptolemaic
from everest.ptolemaic.ousia import Ousia as _Ousia


class Protean(_Ousia):

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.premade = _weakref.WeakValueDictionary()


class ProteanBase(metaclass=Protean):

    MERGETUPLES = ('_var_slots__',)
    _var_slots__ = ()
    _req_slots__ = ('basis',)

    defaultbasis = None

    @classmethod
    def get_concrete_bases(cls, /):
        yield cls.ConcreteBase
        yield _ptolemaic.PtolemaicVar
        yield cls

    @classmethod
    def get_concrete_slots(cls, /):
        return tuple(sorted(set(
            name for name in _itertools.chain(
                cls._req_slots__,
                cls._var_slots__,
                )
            if not hasattr(cls, name)
            )))

    class ConcreteBase:

        __slots__ = ()

        def initialise(self, basis=None, /, **kwargs):
            self.basis = self.defaultbasis if basis is None else basis
            super().initialise(**kwargs)

        @classmethod
        def __class_call__(cls,
                basis=None, /, *, identity=None, _softcache=None
                ):
            premade = cls.premade
            if identity is None:
                out = super().__class_call__(basis, _softcache=_softcache)    
            else:
                key = (basis, identity)
                if key in premade:
                    return premade[key]
                out = super().__class_call__(identity, _softcache=_softcache)
            premade[basis, out.identity] = out
            return out

        ### Representations:

        def _repr(self, /):
            out = super()._repr()
            if (basis := self.basis is None):
                return out
            return f"{repr(self.basis)}, {out}"


###############################################################################
###############################################################################
