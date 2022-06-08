###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import weakref as _weakref
import types as _types
import functools as _functools
from collections import abc as _collabc

from everest.utilities import (
    caching as _caching,
    switch as _switch,
    # ARITHMOPS as _ARITHMOPS, REVOPS as _REVOPS,
    )
from everest.bureau import FOCUS as _FOCUS
from everest import ur as _ur

from .ptolemaic import Ptolemaic as _Ptolemaic
from .pleroma import Pleroma as _Pleroma


_SERIAL_ = 0

def get_serial():
    global _SERIAL_
    return _SERIAL_

def increment_serial():
    global _SERIAL_
    out = _SERIAL_ + 1
    _SERIAL_ = out
    return out

_PREMADE_ = _weakref.WeakValueDictionary()
PREMADE = _types.MappingProxyType(_PREMADE_)


class AnnotationHandler(dict):

    __slots__ = ('meth',)

    def __init__(self, meth, /):
        self.meth = meth

    def __setitem__(self, name, val, /):
        self.meth(name, val)


class Directive(metaclass=_abc.ABCMeta):

    __slots__ = ()

    @_abc.abstractmethod
    def __directive_call__(self, body, name, /) -> tuple[str, object]:
        raise NotImplementedError


class Skip(Directive):

    __slots__ = ()

    def __directive_call__(self, body, name, /):
        return None, None


class MROClass(Directive):

    __slots__ = ('kls',)

    def __init__(self, kls=None, /):
        self.kls = kls

    @staticmethod
    def _gather_mrobases(bases: tuple, name: str, /):
        for base in bases:
            try:
                candidate = getattr(base, name)
            except AttributeError:
                continue
            if candidate is not None:
                yield candidate

    @staticmethod
    def _check_isinnerclass(kls, body, /):
        if kls.__module__ != body['__module__']:
            return False
        stump = '.'.join(kls.__qualname__.split('.')[:-1])
        return stump == body['__qualname__']

    def get_mroclass(self, body, name, /):
        bases = body.bases
        mrobases = tuple(self._gather_mrobases(bases, name))
        kls = self.kls
        if kls is None:
            if not mrobases:
                return None
            return type(
                name,
                mrobases,
                dict(
                    __module__=body['__module__'],
                    __qualname__=f"{body['__qualname__']}.{name}",
                    ),
                body=body,
                )
        isinner = self._check_isinnerclass(kls, body)
        if not mrobases:
            return kls
        klsname = kls.__qualname__.split('.')[-1]
        if (not isinner) or (klsname != name):
            return type(
                name,
                (kls, *mrobases),
                dict(
                    __module__=body['__module__'],
                    __qualname__=f"{body['__qualname__']}.{name}",
                    ),
                body=body,
                )
        kls = type(
            name,
            (kls, *mrobases),
            dict(
                __qualname__=kls.__qualname__,
                __module__=kls.__module__,
                __mrobase__=kls,
                ),
            body=body,
            )
        newqn = f"{kls.__qualname__}.__mrobase__"
        type.__setattr__(kls.__mrobase__, '__qualname__', newqn)
        return kls

    def __call__(self, body, name, /):
        return name, self.get_mroclass(body, name)


class ClassBody(dict):

    SKIP = Skip()

    def __init__(self, meta, name, bases, /, *, body=None):
        self.body = body
        global increment_serial
        serials = self.serials = (
            *(() if body is None else body.serials),
            increment_serial(),
            )
        super().__init__(
            _=self,
            # __name__=name,  # Breaks things in a really interesting way!
            __class_serials__=serials,
            __slots__=(),
            _clsfreezeattr=_switch.Switch(False),
            )
        redirect = self._redirect = dict(
            _=self,
            __annotations__=AnnotationHandler(self.__setanno__),
            )
        self._protected = set(self) | set(redirect)
        self.suspended = _switch.Switch(False)
        self.meta = meta
        self.__dict__.update(meta._yield_bodymeths(self))
        self.name = name
        self.bases = meta.process_bases(name, bases)

    def suspend(self, /):
        return self.suspended.as_(True)

    def __getitem__(self, name, /):
        try:
            return self._redirect[name]
        except KeyError:
            return super().__getitem__(name)

    def __directsetitem__(self, name, val, /):
        super().__setitem__(name, val)

    def __setitem__(self, name, val, /):
        if self.suspended:
            return
        if isinstance(val, Directive):
            name, val = val.__directive_call__(self, name)
        name, val = self.meta._process_bodyitem(self, name, val)
        if name is None:
            return
        if name in self._protected:
            raise RuntimeError(
                f"Cannot override protected names in class body: {name}"
                )
        super().__setitem__(name, val)

    def __setanno__(self, name, val, /):
        self.__setitem__(*self.meta._process_bodyanno(
            self, name, val, self.pop(name, NotImplemented)
            ))

    def safe_set(self, name, val, /):
        if name in self:
            raise RuntimeError(
                "Cannot safe-set a name that is already in use."
                )
        self.__setitem__(name, val)
        self._protected.add(name)

    def classcache(self, arg, /):
        name = arg.__name__
        self.classslots.add(name)
        self[f"_class_get_{name}_"] = classmethod(arg)
        return self.SKIP

    def __repr__(self, /):
        return f"{type(self).__qualname__}({super().__repr__()})"


@_Ptolemaic.register
class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

    @classmethod
    def __meta_init__(meta, /):
        meta.__mergenames__ = _ur.DatUniqueTuple(meta._yield_mergenames())

    @classmethod
    def _yield_bodymeths(meta, body, /):
        yield 'skip', Skip
        yield 'mroclass', MROClass

    @classmethod
    def _yield_mergenames(meta, /):
        return
        yield
        # yield from ('MROCLASSES', 'OVERCLASSES')

    @classmethod
    def _yield_mergees(meta, bases, name, /):
        for base in bases:
            if hasattr(base, name):
                out = getattr(base, name)
                yield out

    @classmethod
    def _yield_mergednames(meta, body, /):
        for name, dyntyp, fintyp in meta.__mergenames__:
            mergees = meta._yield_mergees(body.bases, name)
            if issubclass(dyntyp, _collabc.Mapping):
                iterable = _itertools.chain.from_iterable(
                    mp.items() for mp in mergees
                    )
            else:
                iterable = _itertools.chain.from_iterable(mergees)
            yield name, dyntyp(iterable)

    @classmethod
    def __prepare__(meta, name, bases, /, **kwargs):
        '''Called before class body evaluation as the namespace.'''
        body =  ClassBody(meta, name, bases, **kwargs)
        # for name, obj in meta._yield_mergednames(body)
        body.update(meta._yield_mergednames(body))
        return body

    @classmethod
    def _process_bodyitem(meta, body, name, val, /):
        return name, val

    @classmethod
    def _process_bodyanno(meta, body, name, hint, val, /):
        raise TypeError(f"Annotations not supported for {meta}.")

    ### Creating the object that is the class itself:

    @classmethod
    def expand_bases(meta, bases):
        '''Expands any pseudoclasses from the input list of bases.'''
        seen = set()
        for base in bases:
            if isinstance(base, Essence):
                base = base.__ptolemaic_class__
            if base not in seen:
                seen.add(base)
                yield base

    @classmethod
    def process_bases(meta, name, bases, /):
        bases = list(meta.expand_bases(bases))
        for basetyp in meta.basetypes:
            if basetyp is object:
                continue
            for base in bases:
                if basetyp in base.__mro__:
                    break
            else:
                bases.append(basetyp)
        return tuple(bases)

    @classmethod
    def decorate(meta, obj, /):
        raise NotImplementedError(
            f"Metaclass {meta} cannot be used as a decorator"
            )

    @classmethod
    def __meta_call__(meta, arg0=None, /, *argn, **kwargs):
        if not argn:
            if arg0 is None:
                return _functools.partial(meta.decorate, **kwargs)
            else:
                return meta.decorate(arg0, **kwargs)
        _, __, body = args = (arg0, *argn)
        out = meta.__class_construct__(body)
        meta.__init__(out, *args, **kwargs)
        return out

    def __new__(meta, name, bases, ns, /, **kwargs):
        '''Called when using the type constructor directly, '''
        '''e.g. type(name, bases, namespace); '''
        '''__init__ is called implicitly.'''
        body = meta.__prepare__(name, bases, **kwargs)
        body.update(ns)
        return meta.__class_construct__(body)

    @classmethod
    def __class_construct__(meta, body: ClassBody, /):
        name, bases, ns = body.name, body.bases, dict(body)
        for mname, dyntyp, fintyp in meta.__mergenames__:
            ns[mname] = fintyp(ns[mname])
        out = super().__new__(meta, name, bases, ns)
        global _PREMADE_
        _PREMADE_[out.__class_serials__[-1]] = out
        return out

    @property
    def __class_serial__(cls, /):
        return cls.__class_serials__[-1]

    @property
    def __class_corpuses__(cls, /):
        try:
            return cls._class_corpuses
        except AttributeError:
            global _PREMADE_
            corpuses = tuple(
                _PREMADE_[serial] for serial in cls.__class_serials__[:-1]
                )
            type.__setattr__(cls, '_class_corpuses', corpuses)
            return corpuses

    @property
    def __class_corpus__(cls, /):
        try:
            return cls.__class_corpuses__[-1]
        except IndexError:
            return None

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(cls, *args, **kwargs)
        cls.__class_deep_init__()
        cls.freezeattr.toggle(True)

    ### Storage:

#     @_caching.attr_property(weak=True, dictlook=True)
#     def tray(cls, /):
#         return _FOCUS.request_session_storer(cls)

#     @_caching.attr_property(weak=True, dictlook=True)
#     def drawer(cls, /):
#         return _FOCUS.request_bureau_storer(cls)

    @property
    def taphonomy(cls, /):
        return _FOCUS.bureau.taphonomy

    ### Implementing the attribute-freezing behaviour for classes:

    @property
    def freezeattr(cls, /):
        return cls._clsfreezeattr

    @property
    def mutable(cls, /):
        return cls.freezeattr.as_(False)

    # def __getattr__(cls, name, /):
    #     if name in type.__getattribute__(cls, '__classbody_classslots__'):
    #         val = type.__getattribute__(cls, f"_class_get_{name}_")()
    #         super().__setattr__(name, val)
    #         return val
    #     raise AttributeError(name)

    def __setattr__(cls, name, val, /):
        if cls.freezeattr:
            raise AttributeError(
                "Cannot alter class attribute while immutable."
                )
        super().__setattr__(name, val)

    def __delattr__(cls, name, /):
        if cls.freezeattr:
            raise AttributeError(
                "Cannot alter class attribute while immutable."
                )
        super().__delattr__(name)

    ### Aliases:

    # @property
    # def __ptolemaic_class__(cls, /):
    #     return cls

    def get_attributes(cls, /):
        lst = list()
        for ACls in reversed(cls.__mro__):
            preserve = ACls.__dict__.get('PRESERVEORDER', set())
            for name in ACls.__dict__:
                if name.startswith('__'):
                    continue
                if name in lst:
                    if name in preserve:
                        continue
                    else:
                        lst.remove(name)
                        lst.append(name)
                else:
                    lst.append(name)
        return tuple(lst)

    @property
    def attributes(cls, /):
        return cls.get_attributes()

    def __class_instancecheck__(cls, obj, /):
        return issubclass(type(obj), cls)

    @property
    def __instancecheck__(cls, /):
        return cls.__class_instancecheck__

    ### What happens when the class is called:

    @property
    def __call__(cls, /):
        return cls.__class_call__

    ### Methods relating to class serialisation:

    @property
    def metacls(cls, /):
        return type(cls.__ptolemaic_class__)

    @property
    def epitaph(cls, /):
        cls = cls.__ptolemaic_class__
        try:
            return cls.__dict__['_clsepitaph']
        except KeyError:
            corpus = cls.__class_corpus__
            if corpus is None:
                epi = cls.taphonomy.auto_epitaph(cls)
            else:
                nm = cls.__qualname__.split('.')[-1]
                epi = cls.taphonomy.getattr_epitaph(corpus, nm)
            type.__setattr__(cls, '_clsepitaph', epi)
            return epi

    ### Operations:

    def __bool__(cls, /):
        return True

    ### Representations:

    def __class_repr__(cls, /):
        return f"{type(cls).__name__}:{cls.__qualname__}"

    def __class_str__(cls, /):
        return cls.__name__

    def __repr__(cls, /):
        return cls.__ptolemaic_class__.__class_repr__()

    def __str__(cls, /):
        return cls.__ptolemaic_class__.__class_str__()

    def _repr_pretty_(cls, p, cycle, root=None):
        if root is not None:
            raise NotImplementedError
        p.text(cls.__qualname__)

    @property
    def hexcode(cls, /):
        return cls.epitaph.hexcode

    @property
    def hashint(cls, /):
        return cls.epitaph.hashint

    @property
    def hashID(cls, /):
        return cls.epitaph.hashID


@_Ptolemaic.register
class EssenceBase(metaclass=Essence):

    @classmethod
    def __class_deep_init__(cls, /):
        cls.__ptolemaic_class__ = cls
        cls.__class_init__()

    @classmethod
    def __class_init__(cls, /):
        pass


###############################################################################
###############################################################################


    # @classmethod
    # def _yield_affixfiltered(
    #         meta, bases, ns, /, overname: str, prefix: str, suffix: str
    #         ):
    #     for base in reversed(bases):
    #         try:
    #             dct = type.__getattribute__(cls, overname)
    #         except AttributeError:
    #             continue
    #         yield from dct.items()
    #     for name, val in ns.items():
    #         if name.startswith(prefix) and name.endswith(suffix):
    #             stump = name.removeprefix(prefix).removesuffix(suffix)
    #             yield stump, dct[name]


#     ### Implementing mroclasses:

#     def _gather_mrobases(cls, name: str, /):
#         for base in cls.__bases__:
#             try:
#                 candidate = getattr(base, name)
#             except AttributeError:
#                 continue
#             try:
#                 yield candidate.__mroclass__
#             except AttributeError:
#                 yield candidate

#     @property
#     def __mroclass__(cls, /):
#         return cls.__dict__.get('_mroclass', cls.__ptolemaic_class__)

#     def _make_mroclass(cls, name: str, /):
#         bases = tuple(cls._gather_mrobases(name))
#         if not all(isinstance(base, Essence) for base in bases):
#             raise TypeError("All mroclass bases must be Essences.", bases)
#         if name in cls.__dict__:
#             homebase = cls.__dict__[name]
#             try:
#                 homebase = homebase.__mroclass__
#             except AttributeError:
#                 raise TypeError(homebase)
#             if not isinstance(homebase, Essence):
#                 raise TypeError(
#                     "All mroclass bases must be Essences.", homebase
#                     )
#             mrobasename = f"<mrobase_{name}>"
#             # setattr(cls, mrobasename, homebase)
#             if is_innerclass(homebase, cls):
#                 with homebase.mutable:
#                     homebase.__qualname__ = \
#                         f"{cls.__qualname__}.{mrobasename}"
#             bases = (homebase, *bases)
#         if not bases:
#             bases = (Essence.BaseTyp,)
#             # return
#         mrofusedname = f"<mrofused_{name}>"
#         ns = {
#             '_ptolemaic_contexts': (*cls.contexts, cls),
#             '__module__': cls.__module__,
#             '__qualname__': f"{cls.__qualname__}.{mrofusedname}",
#             }
#         fused = type(name, bases, ns)
#         # setattr(cls, mrofusedname, fused)
#         bases = (fused, *(
#             getattr(cls, oname)
#             for oname in fused.OVERCLASSES
#             if hasattr(cls, oname)
#             ))
#         ns = {
#             '_ptolemaic_owners': (*cls.contexts, cls),
#             '__module__': cls.__module__,
#             '__qualname__': f"{cls.__qualname__}.{name}",
#             '_mroclass': fused,
#             }
#         final = type(name, bases, ns)
#         setattr(cls, name, final)
#         try:
#             meth = final.__set_name__
#         except AttributeError:
#             pass
#         else:
#             meth(cls, name)
#         return final

#     def _add_mroclass(cls, name: str, /):
#         setattr(cls, name, cls._make_mroclass(name))

#     def _add_mroclasses(cls, /):
#         for name in cls.MROCLASSES:
#             cls._add_mroclass(name)

#     @property
#     def contexts(cls, _default=(), /):
#         return cls.__ptolemaic_class__.__dict__.get(
#             '_ptolemaic_contexts', _default
#             )

#     @property
#     def context(cls, /):
#         try:
#             return cls.contexts[-1]
#         except IndexError:
#             return None

#     @property
#     def truecontext(cls, /):
#         try:
#             return cls.contexts[0]
#         except IndexError:
#             return None


#     ### Descriptor stuff:

#     def __set_name__(cls, owner, name, /):
#         try:
#             meth = cls.__class_set_name__
#         except AttributeError:
#             pass
#         else:
#             meth(owner, name)

#     def __get__(cls, instance, owner=None, /):
#         try:
#             meth = cls.__class_get__
#         except AttributeError:
#             return cls
#         else:
#             return meth(instance, owner)

#     def __set__(cls, instance, value, /):
#         try:
#             meth = cls.__class_set__
#         except AttributeError as exc:
#             raise AttributeError from exc
#         else:
#             return cls.__class_set__(instance, value)

#     def __delete__(cls, instance, /):
#         try:
#             meth = cls.__class_delete__
#         except AttributeError as exc:
#             raise AttributeError from exc
#         else:
#             return meth(instance)

#     ### Arithmetic:

#     for methname in _itertools.chain(_ARITHMOPS, _REVOPS):
#         exec('\n'.join((
#             f"@property",
#             f"def {methname}(cls, /):",
#             f"    try:",
#             f"        return cls.__class_{methname.strip('_')}__",
#             f"    except AttributeError:",
#             f"        raise NotImplementedError",
#             )))
#     del methname