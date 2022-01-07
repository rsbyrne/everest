###############################################################################
''''''
###############################################################################


import itertools as _itertools
import weakref as _weakref
import types as _types

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
            self.basis = basis
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

        @property
        def varvals(self, /):
            return _types.MappingProxyType({
                key: getattr(self, key) for key in self._var_slots__
                })

        ### Representations:

        def _var_reprs(self, /):
            for key in self._var_slots__:
                yield f"{key}={getattr(self, key)}"

        def _repr(self, /):
            return (
                f"{repr(self.basis)}, identity={super()._repr()}"
                )

        def _repr_pretty_(self, p, cycle):
            root = repr(self)
            if cycle:
                p.text(root + '{...}')
            elif not (kwargs := self.varvals):
                return
            with p.group(4, root + '(', ')'):
                kwargit = iter(kwargs.items())
                p.breakable()
                key, val = next(kwargit)
                p.text(key)
                p.text(' = ')
                p.pretty(val)
                for key, val in kwargit:
                    p.text(',')
                    p.breakable()
                    p.text(key)
                    p.text(' = ')
                    p.pretty(val)
                p.text(',')
            p.breakable()



###############################################################################
###############################################################################
