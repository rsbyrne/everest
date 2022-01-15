###############################################################################
''''''
###############################################################################


import itertools as _itertools
import weakref as _weakref
import types as _types

from everest.ptolemaic.ousia import Ousia as _Ousia

from everest.utilities import reseed as _reseed


class Protean(_Ousia):

    def __call__(cls, basis=None, /):
        obj = object.__new__(cls.Concrete)
        obj.basis = basis
        for name in cls._var_slots__:
            obj._alt_setattr__(name, None)
        obj.__init__()
        obj.freezeattr.toggle(True)
        return obj


class ProteanBase(metaclass=Protean):

    MERGETUPLES = ('_var_slots__',)
    _var_slots__ = ()
    _req_slots__ = ('basis',)

    reseed = _reseed.GLOBALRAND

    @classmethod
    def pre_create_concrete(cls, /):
        name, bases, namespace = super().pre_create_concrete()
        namespace['__slots__'] = tuple(sorted(set(_itertools.chain(
            namespace['__slots__'], cls._var_slots__
            ))))
        return name, bases, namespace

    @property
    def varvals(self, /):
        return _types.MappingProxyType({
            key: getattr(self, key) for key in self._var_slots__
            })
        
    def __setattr__(self, name, value, /):
        if name in self._var_slots__:
            self._alt_setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def __delattr__(self, name, /):
        if name in self._var_slots__:
            self._alt_delattr__(name)
        else:
            super().__delattr__(name)

    ### Representations:

    def _var_reprs(self, /):
        for key in self._var_slots__:
            yield f"{key}={getattr(self, key)}"

    def _repr(self, /):
        return repr(self.basis)

    def __repr__(self, /):
        return f"<{type(self)}({self._repr()})>"

    def _repr_pretty_(self, p, cycle):
        p.text('<')
        root = repr(self._ptolemaic_class__)
        if cycle:
            p.text(root + '{...}')
        elif not (kwargs := self.varvals):
            p.text(root + '()')
        else:
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
                p.breakable()
        p.text('>')


###############################################################################
###############################################################################
