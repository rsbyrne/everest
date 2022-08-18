###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import sys as _sys
import types as _types
import weakref as _weakref
from functools import partial as _partial
from collections import abc as _collabc, deque as _deque

from everest.switch import Switch as _Switch
from everest.ur import (
    Dat as _Dat, Primitive as _Primitive,
    PrimitiveUniTuple as _PrimitiveUniTuple,
    )

from .pleroma import Pleroma as _Pleroma
from .shadow import Shadow as _Shadow, Shade as _Shade
from . import ptolemaic as _ptolemaic
from .wisp import (
    Wisp as _Wisp, Property as _Property, Classmethod as _Classmethod
    )
from .pathget import PathGet as _PathGet, PathError as _PathError


class AnnotationHandler(dict):

    __slots__ = ('meth',)

    def __init__(self, meth, /):
        self.meth = meth

    def __setitem__(self, name, val, /):
        self.meth(name, val)


class Directive(metaclass=_abc.ABCMeta):

    __slots__ = ()

    @_abc.abstractmethod
    def __directive_call__(self, body, name, /):
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, kls, /):
        if cls is Directive:
            for methname in cls.__abstractmethods__:
                for Base in kls.__mro__:
                    if methname in Base.__dict__:
                        break
                else:
                    return NotImplemented
            return True
        return NotImplemented


class Escaped:

    __slots__ = ('escaped', 'escapedvals', 'names', 'managed')

    def __init__(self, body, /, *names):
        self.escaped, self.escapedvals, self.names = \
            body.escaped, body.escapedvals, names

    def __enter__(self, /):
        escaped = self.escaped
        managed = self.managed = set(
            name for name in self.names
            if name not in escaped
            )
        escaped.update(managed)

    def __exit__(self, /, *_):
        escaped, escapedvals, managed = \
            self.escaped, self.escapedvals, self.managed
        for name in managed:
            escaped.remove(name)
            try:
                del escapedvals[name]
            except KeyError:
                pass


class MroclassMerger(dict):

    def __setitem__(self, name, val):
        try:
            deq = self[name]
        except KeyError:
            deq = _deque()
            super().__setitem__(name, deq)
        if isinstance(val, str):
            val = _PathGet(val)
        elif isinstance(val, tuple):
            if val:
                val = _PathGet(*val)
            else:
                val = None
        if val is not None:
            if not isinstance(val, (type, _PathGet)):
                raise TypeError(val)
            if val not in deq:
                deq.appendleft(val)
            else:
                deq.extendleft(_itertools.filterfalse(deq.__contains__, val))

    def update(self, vals, /):
        for key, val in dict(vals).items():
            if key not in self:
                super().__setitem__(key, _deque())
            for subval in val:
                self[key] = subval


class ClassBodyHelper:

    __slots__ = ('body',)

    def __init__(self, body, /):
        self.body = body


class PtolemaicHelper(ClassBodyHelper):

    def __mro_entries__(self, bases, /):
        return (self.body._defaultbasetyp,)


class MROClassHelper(ClassBodyHelper):

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        body = self.body
        body.lock.toggle(True)
        body.awaiting_mroclass = True

    def __mro_entries__(self, bases, /):
        if len(bases) != 1:
            raise RuntimeError(bases)
        return (self.body._defaultbasetyp,)

    def __call__(self, /, *mrobases):
        self.body.awaiting_mroclass_names.extendleft(mrobases)
        return self


class ClassBody(dict):

    BODIES = _weakref.WeakValueDictionary()

    @property
    class namespace:

        __slots__ = ('classbody', 'dct')

        def __init__(self, classbody, /):
            outer = classbody.outer
            if isinstance(outer, ClassBody):
                outer = outer.namespace
            dct = dict(__corpus__ = outer)
            object.__setattr__(self, 'dct', dct)
            object.__setattr__(self, 'classbody', classbody)

        def __getattr__(self, name, /):
            try:
                return self.dct[name]
            except KeyError:
                pass
            try:
                return self.classbody[name]
            except KeyError as exc:
                raise AttributeError from exc

        def __setattr__(self, name, val, /):
            self.classbody[name] = val

    def __init__(
            self, meta, name, bases, /, *,
            modname=None, qualroot=None, qualname=None,
            _staticmeta_=False,
            **kwargs,
            ):
        pubnames = self._publicnames = []
        for nm, val in dict(
                # __name__=name,  # Breaks things in a really interesting way!
                __slots__=(),
                __class_relname__=name,
                _clsmutable=_Switch(True),
                _clspublicnames=pubnames,
                ).items():
            super().__setitem__(nm, val)
        self.lock = _Switch(False)
        # self._add_mroclass_sugar()
        self.kwargs = kwargs
        self.outer = None
        self.innerobjs = {}
        self.awaiting_mroclass = False
        self.awaiting_mroclass_names = _deque()
        self._nametriggers = dict(
            __module__=(lambda val: setattr(self, 'modname', val)),
            __qualname__=(lambda val: setattr(self, 'qualname', val)),
            __slots__=self.handle_slots,
            )
        # self._sugar = _Switch(withsugar)
        self._redirects = dict(
            _=self,
            # sugar=self._sugar,
            __annotations__=AnnotationHandler(self.__setanno__),
            )
        self._registeredorgans = dict()
        self._shades = dict()
        self._protected = set(self)
        self._rawmeta = meta
        self._staticmeta = _staticmeta_
        self.name = name
        self._rawbases = tuple(base for base in bases)
        self._fullyprepared = False
        self.escaped = set()
        self.escapedvals = dict()
        self.mergenames = dict()
        if modname is None:
            if any(val is not None for val in (qualroot, qualname)):
                raise ValueError(
                    "Cannot provide qualroot or qualname kwargs "
                    "when module is not also provided."
                    )
        else:
            if qualroot is None:
                if qualname is None:
                    qualname = name
            elif qualname is not None:
                raise ValueError(
                    "Cannot provide both qualroot and qualname."
                    )
            else:
                qualname = f"{qualroot}.{name}"
            self.modname, self.qualname = modname, qualname

    def protect_name(self, name, /):
        self._protected.add(name)

    def enroll_shade(self, name, /):
        self._shades[name] = _Shade(str(name))
        # self.protect_name(name)

    def handle_slots(self, slots, /):
        if slots:
            self.meta.handle_slots(self, slots)

    def __getitem__(self, name, /):
        if name in self.escaped:
            return self.escapedvals[name]
        try:
            redir = self._redirects[name]
        except KeyError:
            pass
        else:
            if isinstance(redir, property):
                return redir.__get__(self)
            return redir
        try:
            return self._shades[name]
        except KeyError:
            pass
        return super().__getitem__(name)

    def _check_is_localfunc(self, func, /):
        return '.'.join(func.__qualname__.split('.')[:-1]) == self._qualname

    def __setitem__(self, name, val, /):
        if self.lock:
            raise RuntimeError(
                "Cannot set item while classbody is locked!"
                )
        if val is NotImplemented:
            return
        if name in self.escaped:
            self.escapedvals[name] = val
            return
        try:
            meth = self._nametriggers[name]
        except KeyError:
            pass
        else:
            meth(val)
            return
        if name in self._protected:
            raise RuntimeError(
                f"Cannot alter protected names in class body: {name}"
                )
        if isinstance(val, _Shadow):
            self.meta.process_shadow(self, name, val)
            return
        while isinstance(val, Directive):
            name, val = val.__directive_call__(self, name)
        if val is NotImplemented:
            return
        if name is None:
            return
        if not name.startswith('_'):
            self._publicnames.append(name)
            if isinstance(val, _types.FunctionType):
                if self._check_is_localfunc(val):
                    self._register_organ(name, val)
            elif isinstance(val, property):
                subvals = []
                for strn in ('fget', 'fset', 'fdel'):
                    newname = f'_{name}_{strn}'
                    subval = getattr(val, strn)
                    subvals.append(subval)
                    if subval is not None:
                        if self._check_is_localfunc(subval):
                            self._register_organ(newname, subval)
                            super().__setitem__(newname, subval)
                val = _Property(*subvals)
            elif isinstance(val, classmethod):
                func = val.__func__
                if self._check_is_localfunc(func):
                    self._register_organ(f"_classmethod_{name}", func)
                val = _Classmethod(func)
            elif isinstance(val, staticmethod):
                pass
            else:
                val = _Wisp.convert(val)
        super().__setitem__(name, val)

    def __delitem__(self, name, /):
        if name in self.escaped:
            del self.escapedvals[name]
        super().__delitem__(name)

    def _register_organ(self, name, val, /):
        val.__corpus__ = Ellipsis
        self._registeredorgans[name] = val

    def _pathget_bodymeth(self, /, *args, live=False, **kwargs):
        getter = _PathGet(*args, **kwargs)
        if live:
            body['__livepaths__'][name] = getter
        return getter

    @property
    def modname(self, /):
        return self._modname

    @modname.setter
    def modname(self, val, /):
        try:
            _ = self.modname
        except AttributeError:
            if not isinstance(val, str):
                raise TypeError(type(val))
            self._modname = val
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
            if not isinstance(val, str):
                raise TypeError(type(val))
            self._qualname = val
            super().__setitem__('__qualname__', val)
            self._post_prepare()
        else:
            raise AttributeError

    def _post_prepare_ismroclass(self, /):
        outer = self.outer
        if isinstance(outer, ClassBody):
            name, made = self.name, outer.mroclassesmade
            try:
                if made[name]:
                    raise RuntimeError("Mroclass already created!")
            except KeyError:
                pass
            else:
                outer.anticipate_mroclass(name)
                self.ismroclass = True
                return
        self.ismroclass = False

    def _post_prepare_bases(self, /):
        bases = []
        safeadd = lambda kls: (
            None if any(issubclass(base, kls) for base in bases)
            else bases.append(kls)
            )
        if self.ismroclass:
            # if self._rawbases:
            #     raise RuntimeError
            name, outer = self.name, self.outer
            for obase in outer.bases:
                try:
                    mrobase = getattr(obase, name)
                except AttributeError:
                    continue
                safeadd(mrobase)
            for item in outer['__mroclasses__'][name]:
                if isinstance(item, _PathGet):
                    try:
                        item = item(self.outer.namespace, self.module.__dict__)
                    except _PathError:
                        continue
                safeadd(item)
                # bases.extend(
                #     entry for entry in base.__mro_entries__
                #     if entry not in bases
                #     )
        # else:
        for base in self._rawbases:
            if isinstance(base, type):
                if base not in bases:
                    bases.append(base)
            else:
                raise TypeError(type(base))
        meta = self._rawmeta
        try:
            basetyp = meta.BaseTyp
        except AttributeError:
            pass
        else:
            if basetyp not in bases:
                bases.append(basetyp)
        if not self._staticmeta:
            metas = tuple(map(type, bases))
            for meta in metas:
                if all(issubclass(meta, mt) for mt in metas):
                    break
            else:
                raise RuntimeError(
                    "Could not identify proper metaclass.",
                    self.name, bases
                    )
        for metabase in (meta, *meta.__bases__):
            try:
                basetyp = metabase.BaseTyp
            except AttributeError:
                continue
            safeadd(basetyp)
            if (maxgens := meta._maxgenerations_) is not None:
                counts = map(basetyp.count_generation, bases)
                maxcount = max(val for val in counts if val is not None)
                if maxcount == maxgens:
                    raise TypeError(
                        "Max generation exceeded:",
                        metabase, self.modname, self.qualname,
                        )
        self.meta = meta
        self.bases = tuple(bases)

    def _gather_mergenames(self, mname, dyntyp, /):
        mergees = (
            getattr(base, mname) for base in self.bases
            if hasattr(base, mname)
            )
        dynobj = dyntyp()
        maplike = isinstance(dynobj, _collabc.Mapping)
        if maplike:
            addmeth = dynobj.update
        else:
            addmeth = dynobj.extend
        try:
            metameth = getattr(self.meta, f"_yield_{mname.strip('_')}")
        except AttributeError:
            pass
        else:
            addmeth(metameth())
        if maplike:
            addmeth(_itertools.chain.from_iterable(
                mp.items() for mp in mergees
                ))
        else:
            addmeth(_itertools.chain.from_iterable(mergees))
        return addmeth, dynobj

    def _add_mergechannel(self, mname, /):
        genericfunc = lambda addmeth, val: addmeth(val)
        nametriggers = self._nametriggers
        dyntyp, fintyp = self.mergenames[mname]
        addmeth, dynobj = self._gather_mergenames(mname, dyntyp)
        super().__setitem__(mname, dynobj)
        nametriggers[mname] = _partial(genericfunc, addmeth)

    def _update_mergenames(self, dct, /):
        meta = self.meta
        dct = {
            key: (
                (val[0], _Dat.convert_type(val[1]))
                if isinstance(val, tuple)
                else (val, _Dat.convert_type(val))
                )
            for key, val in dct.items()
            }
        mergenames = self.mergenames
        oldnames = set(mergenames)
        mergenames.update(dct)
        for mname in set(mergenames).difference(oldnames):
            self._add_mergechannel(mname)

    def _post_prepare_mergednames(self, /):
        _, dynobj = self._gather_mergenames('__mergenames__', dict)
        dynobj['__mroclasses__'] = (MroclassMerger, dict)
        dynobj['__livepaths__'] = dict
        self._update_mergenames(dynobj)
        self._nametriggers['__mergenames__'] = self._update_mergenames
        self._nametriggers['__livepaths__'] = self._update_livepaths

    def _post_prepare_livepaths(self, /):
        for name, getter in self['__livepaths__'].items():
            self[name] = getter

    def _update_mroclasses(self, vals, /):
        mroclasses, mroclassesmade = self['__mroclasses__'], self.mroclassesmade
        mroclasses.update(vals)
        nametriggers = self._nametriggers
        redirects = self._redirects
        for key in mroclasses:
            mroclassesmade.setdefault(key, False)
            if not mroclassesmade[key]:
                nametriggers[key] = _partial(self.add_mroclass, key)
                redirects[key] = property(_partial(type(self).add_mroclass, name=key))

    def _update_livepaths(self, vals, /):
        livepaths = self['__livepaths__']
        for name, getter in dict(vals).items():
            livepaths[name] = getter
            self[name] = getter

    def _post_prepare_mroclasses(self, /):
        self.mroclassesmade = {key: False for key in self['__mroclasses__']}
        self._nametriggers['__mroclasses__'] = self._update_mroclasses
        self['__mroclasses__'] = dict(self.meta._yield_mroclasses())

    def _post_prepare_bodymeths(self, /):
        toadd = dict(
            (name, meth)
            for name, meth in self.meta._yield_bodymeths(self)
            )
        toadd['escaped'] = _partial(Escaped, self)
        toadd['pathget'] = self._pathget_bodymeth
        toadd['ptolemaic'] = property(PtolemaicHelper)
        toadd['mroclass'] = property(MROClassHelper)
        self._redirects.update(toadd)
        self._protected.update(toadd)

    def _post_prepare_nametriggers(self, /):
        triggers = self._nametriggers
        triggers.update(
            (name, _partial(meth, self))
            for name, meth in self.meta._yield_bodynametriggers()
            )
        triggers.update(
            (name, _partial(self.add_mroclass, name))
            for name in self.mroclassesmade
            )

    def _post_prepare(self, /):
        modname, qualname = self.modname, self.qualname
        module = self.module = _sys.modules[modname]
        BODIES = type(self).BODIES
        BODIES[modname, qualname] = self
        stump = '.'.join(qualname.split('.')[:-1])
        name = self.name
        try:
            outer = BODIES[modname, stump]
        except KeyError:
            # if False:  # if modname == '__main__':
            #     iscosmic = False
            #     outer = module
            # else:
            try:
                module._ISSTELE_
            except AttributeError:
                iscosmic = True
                outer = None
            else:
                iscosmic = False
                outer = module
        else:
            if outer.awaiting_mroclass:
                outer.lock.toggle(False)
                outer['__mroclasses__'] = {
                    name: outer.awaiting_mroclass_names,
                    }
                outer.awaiting_mroclass = False
                outer.awaiting_mroclass_names.clear()
            iscosmic = False
        self.outer = outer
        self.iscosmic = iscosmic
        super().__setitem__('_clsiscosmic', iscosmic)
        self._post_prepare_ismroclass()
        self._post_prepare_bases()
        self._post_prepare_mergednames()
        self._post_prepare_livepaths()
        self._post_prepare_mroclasses()
        self._post_prepare_bodymeths()
        self._post_prepare_nametriggers()
        self.meta.__post_prepare__(self, **self.kwargs)
        self._fullyprepared = True

    def add_notion(self, name, base=None):
        if base is None:
            base = self._defaultbasetyp
        out = self[name] = type(
            name, (base,), {},
            modname=self.modname, qualroot=self.qualname,
            )
        return out

    def anticipate_mroclass(self, name):
        self.mroclassesmade[name] = True
        self._nametriggers[name] = _partial(self.add_mroclass_premade, name)

    def add_mroclass_premade(self, name, val):
        # super().__setitem__(name, val)
        del self._nametriggers[name]
        del self._redirects[name]
        self[name] = val
        self.mroclassesmade[name] = True
        self.protect_name(name)

    def add_mroclass(self, name, base=None):
        del self._nametriggers[name]
        del self._redirects[name]
        out = self.add_notion(name, base)
        self.mroclassesmade[name] = True
        self.protect_name(name)
        return out

    def _finalise_mergenames(self, /):
        mergenames = self.mergenames
        for mname, (_, fintyp) in mergenames.items():
            super().__setitem__(mname, fintyp(super().__getitem__(mname)))
        super().__setitem__(
            '__mergenames__', _Dat.convert(mergenames)
            )

    def _finalise_mroclasses(self, /):
        for mroname, check in self.mroclassesmade.items():
            if not check:
                self.add_notion(mroname, self.get(mroname, None))

    def _register_innerobj(self, obj, name, /):
        self.innerobjs[name] = obj

    def finalise(self, /):
        assert self._fullyprepared, (self.name,)
        self._finalise_mergenames()
        self._finalise_mroclasses()
        # try:
        out = _abc.ABCMeta.__new__(
            self.meta, self.name, self.bases, dict(self)
            )
        # except TypeError as exc:
        #     for base in self.bases[:]:
        #         print('------')
        #         print(repr(base))
        #         print(base.__mro__[1:-2])
        #     raise exc
        if self.iscosmic:
            type.__setattr__(out, '_clsiscosmic', True)
        else:
            name, outer = self.name, self.outer
            try:
                meth = outer._register_innerobj
            except AttributeError:
                _ptolemaic.configure_as_innerobj(out, outer, name)
            else:
                meth(name, out)
            type.__setattr__(out, '_clsiscosmic', False)
        type.__setattr__(out, '_clsinnerobjs', {})
        for name, innerobj in self.innerobjs.items():
            out._register_innerobj(innerobj, name)
        for funcname, func in self._registeredorgans.items():
            func.__relname__, func.__corpus__ = funcname, out
        return out

    def __setanno__(self, name, val, /):
        self.meta.body_handle_anno(
            self, name, val, self.pop(name, NotImplemented)
            )

    def safe_set(self, name, val, /):
        if name in self:
            raise RuntimeError(
                "Cannot safe-set a name that is already in use."
                )
        self.__setitem__(name, val)
        self.protect_name(name)

    def __repr__(self, /):
        return f"{type(self).__qualname__}({super().__repr__()})"


###############################################################################
###############################################################################
