###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import weakref as _weakref
import types as _types
import functools as _functools
from collections import abc as _collabc

from everest.bureau import FOCUS as _FOCUS
from everest import ur as _ur

from .ptolemaic import Ptolemaic as _Ptolemaic
from .pleroma import Pleroma as _Pleroma
from .utilities import Switch as _Switch


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


# class MROClass(Directive):

#     __slots__ = ('kls',)

#     def __init__(self, kls=None, /):
#         self.kls = kls

#     @staticmethod
#     def _gather_mrobases(bases: tuple, name: str, /):
#         for base in bases:
#             try:
#                 candidate = getattr(base, name)
#             except AttributeError:
#                 continue
#             if candidate is not None:
#                 yield candidate

#     @staticmethod
#     def _check_isinnerclass(kls, body, /):
#         if kls.__module__ != body['__module__']:
#             return False
#         stump = '.'.join(kls.__qualname__.split('.')[:-1])
#         return stump == body['__qualname__']

#     def get_mroclass(self, body, name, /):
#         bases = body.bases
#         mrobases = tuple(self._gather_mrobases(bases, name))
#         kls = self.kls
#         if kls is None:
#             if not mrobases:
#                 raise RuntimeError("No bases provided for mroclass!")
#             kls = type(
#                 name,
#                 mrobases,
#                 dict(),
#                 location=(
#                     body['__module__'],
#                     f"{body['__qualname__']}.{name}",
#                     ),
#                 )
#         else:
#             isinner = self._check_isinnerclass(kls, body)
#             if mrobases:
#                 klsname = kls.__qualname__.split('.')[-1]
#                 if (not isinner) or (klsname != name):
#                     kls = type(
#                         name,
#                         (kls, *mrobases),
#                         dict(),
#                         location=(
#                             body['__module__'],
#                             f"{body['__qualname__']}.{name}",
#                             ),
#                         )
#                 else:
#                     kls = type(
#                         name,
#                         (kls, *mrobases),
#                         dict(__mrobase__=kls),
#                         location=(kls.__module__, kls.__qualname__),
#                         )
#                     newqn = f"{kls.__qualname__}.__mrobase__"
#                     type.__setattr__(kls.__mrobase__, '__qualname__', newqn)
#             elif isinner:
#                 # Have to deal with this somehow...
#                 pass
#         return kls

#     def __directive_call__(self, body, name, /):
#         return name, self.get_mroclass(body, name)


class ClassBody(dict):

    BODIES = _weakref.WeakValueDictionary()

    def __init__(
            self, meta, name, bases, /, *,
            location=None,
            mroclasses=(),
            _bodymeths=_ur.DatDict(),
            _nametriggers=_ur.DatDict(),
            _typetriggers=_ur.DatDict(),
            **kwargs,
            ):
        self._nametriggers = {**_nametriggers}
        # self._typetriggers = {**_typetriggers}
        self.__dict__.update({
            name: _functools.partial(meth, self)
            for name, meth in _bodymeths.items()
            })
        if location is not None:
            self.module, self.qualname = location
        super().__init__(
            _=self,
            # __name__=name,  # Breaks things in a really interesting way!
            __slots__=(),
            innerclasses=[],
            _clsiscosmic=None,
            __class_relname__=name,
            _clsmutable=_Switch(True),
            )
        self._redirects = dict(
            _=self,
            __annotations__=AnnotationHandler(self.__setanno__),
            )
        self._protected = set(self)
        self._suspended = _Switch(False)
        self.meta = meta
        self.name = name
        self._rawbases = bases
        self.mroclasses = tuple(mroclasses)

    @property
    def suspended(self, /):
        return self._suspended

    @suspended.setter
    def suspended(cls, val, /):
        self._suspended.toggle(val)

    def __getitem__(self, name, /):
        try:
            return self._redirects[name]
        except KeyError:
            return super().__getitem__(name)

    def _process_nameval(self, name, val, /):
        if isinstance(val, Directive):
            name, val = val.__directive_call__(self, name)
        try:
            meth = self._nametriggers[name]
        except KeyError:
            pass
        else:
            name, val = meth(self, val)
        # try:
        #     meth = self._typetriggers[type(val)]
        # except KeyError:
        #     pass
        # else:
        #     name, val = meth(self, name, val)
        return name, val

    def __setitem__(self, name, val, /):
        if self.suspended:
            return
        name, val = self._process_nameval(name, val)
        if name is None:
            return
        if name in self._protected:
            raise RuntimeError(
                f"Cannot override protected names in class body: {name}"
                )
        super().__setitem__(name, val)

    def __direct_setitem__(self, name, val, /):
        super().__setitem__(name, val)

    @property
    def module(self, /):
        return self._module

    @module.setter
    def module(self, val, /):
        try:
            _ = self.module
        except AttributeError:
            self._module = val
            super().__setitem__('__module__', val)
        else:
            raise AttributeError

    @property
    def qualname(self, /):
        return self._qualname

    @qualname.setter
    def qualname(self, val, /):
        try:
            _ = self.qualname
        except AttributeError:
            self._qualname = val
            super().__setitem__('__qualname__', val)
            self._post_prepare()
        else:
            raise AttributeError

    def _post_prepare(self, /):
        module, qualname = self.module, self.qualname
        BODIES = type(self).BODIES
        BODIES[module, qualname] = self
        stump = '.'.join(qualname.split('.')[:-1])
        name = self.name
        bases = self.meta.process_bases(name, self._rawbases)
        try:
            obody = BODIES[module, stump]
        except KeyError:
            self.outerbody = None
            iscosmic = self.iscosmic = True
        else:
            self.outerbody = obody
            iscosmic = self.iscosmic = False
            # if self.ismroclass:
            #     mrobases = tuple(obody.meta.gather_mrobases(obody.bases, name))
            #     bases = (*mrobases, *(bs for bs in bases if bs not in mrobases))
        self._bases = bases
        super().__setitem__('_clsiscosmic', iscosmic)
        self.meta._body_post_prepare(self)

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

    @property
    def bases(self, /):
        return self._bases

    def __repr__(self, /):
        return f"{type(self).__qualname__}({super().__repr__()})"


@_Ptolemaic.register
class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

    ### Descriptor stuff:

    def __set_name__(cls, owner, name, /):
        if cls.mutable:
            cls.__class_relname__ = name
            cls.__class_corpus__ = owner
            cls.__qualname__ = owner.__qualname__ + '.' + name
            owner.register_innerclass(cls)

    @property
    def __corpus__(cls, /):
        try:
            return cls.__dict__['__class_corpus__']
        except KeyError:
            return None

    @property
    def __cosmic__(cls, /):
        return cls.__corpus__ is None

    @property
    def __relname__(cls, /):
        try:
            return cls.__dict__['__class_relname__']
        except KeyError:
            return cls.__qualname__

    ### Meta init:

    @classmethod
    def _yield_bodynametriggers(meta, /):
        yield (
            f"__module__",
            lambda body, val: (None, setattr(body, 'module', val))
            )
        yield (
            f"__qualname__",
            lambda body, val: (None, setattr(body, 'qualname', val))
            )

    @classmethod
    def _yield_bodytypetriggers(meta, /):
        return
        yield

    @classmethod
    def _yield_bodymeths(meta, /):
        return
        yield

    @classmethod
    def _yield_mergenames(meta, /):
        return
        yield

    @classmethod
    def __meta_init__(meta, /):
        meta.__mergenames__ = _ur.DatUniqueTuple(meta._yield_mergenames())
        meta._bodymeths = dict(meta._yield_bodymeths())
        meta._bodynametriggers = dict(meta._yield_bodynametriggers())
        meta._bodytypetriggers = dict(meta._yield_bodytypetriggers())

    ### Class construction:

    @classmethod
    def _yield_mergees(meta, bases, name, /):
        for base in bases:
            if hasattr(base, name):
                out = getattr(base, name)
                yield out

    @classmethod
    def _body_add_mergednames(meta, body, /):
        genericfunc = lambda meth, body, val: (None, meth(val))
        for mname, dyntyp, _ in meta.__mergenames__:
            mergees = meta._yield_mergees(body.bases, mname)
            if issubclass(dyntyp, _collabc.Mapping):
                dynobj = dyntyp(_itertools.chain.from_iterable(
                    mp.items() for mp in mergees
                    ))
                meth = dynobj.update
            else:
                dynobj = dyntyp(_itertools.chain.from_iterable(mergees))
                meth = dynobj.extend
            body[mname] = dynobj
            body._nametriggers[mname] = _functools.partial(genericfunc, meth)

    @classmethod
    def __prepare__(meta, name, bases, /, **kwargs):
        '''Called before class body evaluation as the namespace.'''
        return ClassBody(
            meta, name, bases,
            _bodymeths=meta._bodymeths,
            _nametriggers=meta._bodynametriggers,
            _typetriggers=meta._bodytypetriggers,
            **kwargs,
            )

    @classmethod
    def _body_post_prepare(meta, body, /):
        meta._body_add_mergednames(body)

    @classmethod
    def _process_bodyitem(meta, body, name, val, /):
        return name, val

    @classmethod
    def _process_bodyanno(meta, body, name, hint, val, /):
        raise TypeError(f"Annotations not supported for {meta}.")

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
    def gather_mrobases(meta, bases: tuple, name: str, /):
        for base in bases:
            try:
                candidate = getattr(base, name)
            except AttributeError:
                continue
            if candidate is not None:
                yield candidate

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
        return super().__new__(meta, body.name, body.bases, body)

    @property
    def __ptolemaic_class__(cls, /):
        return cls._get_ptolemaic_class()

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(cls, *args, **kwargs)
        iscosmic = cls._clsiscosmic
        del cls._clsiscosmic
        if iscosmic:
            cls.__class_deep_init__()
            cls.__class_inner_init__()
            cls.mutable = False

    @classmethod
    def _get_qualname(cls, /):
        try:
            corpus = cls.__corpus__
        except AttributeError:
            return cls.__relname__
        return corpus.__relname__ + '.' + cls.__relname__

    ### Storage:

    @property
    def taphonomy(cls, /):
        return _FOCUS.bureau.taphonomy

    ### Implementing the attribute-freezing behaviour for classes:

    @property
    def mutable(cls, /):
        return cls.__dict__['_clsmutable']
    @mutable.setter
    def mutable(cls, val, /):
        cls.mutable.toggle(val)

    def __setattr__(cls, name, val, /):
        if cls.mutable:
            super().__setattr__(name, val)
        else:
            raise AttributeError(
                "Cannot alter class attribute while immutable."
                )

    def __delattr__(cls, name, /):
        if cls.mutable:
            super().__delattr__(name)
        else:
            raise AttributeError(
                "Cannot alter class attribute while immutable."
                )

    ### Aliases:

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
            epi = cls.taphonomy.auto_epitaph(cls)
            corpus = cls.__corpus__
            if corpus is None:
                epi = cls.taphonomy.auto_epitaph(cls)
            else:
                epi = cls.taphonomy.getattr_epitaph(
                    corpus, cls.__relname__
                    )
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
    def __class_inner_init__(cls, /):
        for inner in cls.innerclasses:
            inner.__class_deep_init__()
            inner.__class_inner_init__()
            inner.mutable = False

    @classmethod
    def register_innerclass(cls, other, /):
        if cls.mutable:
            cls.innerclasses.append(other)
        else:
            raise RuntimeError(
                "Cannot register a new inner class "
                "after a class has been made immutable "
                "(i.e. after it has been completely initialised): "
                f"{cls}"
                )

    @classmethod
    def __class_deep_init__(cls, /):
        cls.__class_init__()
        for mname, _, fintyp in cls.__mergenames__:
            setattr(cls, mname, fintyp(cls.__dict__[mname]))
        cls.innerclasses = tuple(cls.__dict__['innerclasses'])

    @classmethod
    def __class_init__(cls, /):
        pass

    @classmethod
    def _get_ptolemaic_class(cls, /):
        return cls


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