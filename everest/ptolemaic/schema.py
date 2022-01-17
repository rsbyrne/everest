###############################################################################
''''''
###############################################################################


import functools as _functools
import collections as _collections
import operator as _operator
import weakref as _weakref
import types as _types
import inspect as _inspect

from everest.utilities import caching as _caching, reseed as _reseed
from everest.ur import Dat as _Dat

from everest.ptolemaic.tekton import Tekton as _Tekton, TektOid as _TektOid
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.chora import Chora as _Chora
from everest.ptolemaic.sig import (Params as _Params, Param as _Param)
from everest.ptolemaic import exceptions as _exceptions


class Schema(_Tekton, _Ousia):

    @property
    def __construct__(cls, /):
        return cls

    def __class_get_incision_manager__(cls, /):
        return SchemOid(cls, cls.sig)

    def __call__(cls, /, *args, **kwargs):
        bound = cls.parameterise(cache := {}, *args, **kwargs)
        obj = cls.__incise_retrieve__(_Params(bound))
        obj.softcache.update(cache)
        return obj


class SchemOid(_TektOid):

    def __incise_retrieve__(self, params: _Params, /) -> 'Concrete':
        obj = object.__new__(self.subject.Concrete)
        obj.params = params
        obj.__init__()
        obj.freezeattr.toggle(True)
        return obj


class SchemaBase(metaclass=Schema):

    _req_slots__ = ('params',)

    CACHE = False

    @classmethod
    def pre_create_concrete(cls, /):
        name, bases, namespace = super().pre_create_concrete()
        namespace.update({key: _Param(key) for key in cls.fields})
        return name, bases, namespace

    @classmethod
    def paramexc(cls, /, *params, message=None):
        return _exceptions.ParameterisationException(params, cls, message)

    @classmethod
    def __class_incise_slyce__(cls, sig, /):
        return Schemoid(cls, sig)

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    ### Serialisation

    def get_epitaph(self, /):
        return self.taphonomy.custom_epitaph(
            "$a[$b]",
            a=self._ptolemaic_class__, b=self.params,
            )

    @property
    @_caching.soft_cache()
    def epitaph(self, /):
        return self.get_epitaph()

    ### Representations:

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def _repr(self, /):
        return f"hashID={self.hashID}"

    @_caching.soft_cache()
    def __hash__(self, /):
        return _reseed.rdigits(12)

    def _repr_pretty_(self, p, cycle):
#         p.text('<')
        root = ':'.join((
            self._ptolemaic_class__.__name__,
            str(id(self)),
            ))
        if cycle:
            p.text(root + '{...}')
        elif not (kwargs := self.params):
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
#         p.text('>')


_Dat.register(Schema)


###############################################################################
###############################################################################
