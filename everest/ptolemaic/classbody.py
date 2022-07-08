###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import sys as _sys
import weakref as _weakref
from functools import partial as _partial
from collections import abc as _collabc

from everest.switch import Switch as _Switch

from .pleroma import Pleroma as _Pleroma
from .shadow import Shadow as _Shadow, Shade as _Shade
from . import ptolemaic as _ptolemaic


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


class ClassBody(dict):

    BODIES = _weakref.WeakValueDictionary()

    def __init__(
            self, meta, name, bases, /, *,
            modname=None, qualroot=None, qualname=None,
            _staticmeta_=False,
            **kwargs,
            ):
        for nm, val in dict(
                # __name__=name,  # Breaks things in a really interesting way!
                __slots__=(),
                __class_relname__=name,
                _clsmutable=_Switch(True),
                ).items():
            super().__setitem__(nm, val)
        self.innerobjs = {}
        self._nametriggers = dict(
            __module__=(lambda val: setattr(self, 'modname', val)),
            __qualname__=(lambda val: setattr(self, 'qualname', val)),
            __slots__=self.handle_slots,
            __mergenames__=self._update_mergenames,
            )
        # self._sugar = _Switch(withsugar)
        self._redirects = dict(
            _=self,
            # sugar=self._sugar,
            __annotations__=AnnotationHandler(self.__setanno__),
            )
        self._shades = dict()
        self._protected = set(self)
        self._rawmeta = meta
        self._staticmeta = _staticmeta_
        self.name = name
        self._rawbases = bases
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
            return self._redirects[name]
        except KeyError:
            pass
        try:
            return self._shades[name]
        except KeyError:
            pass
        return super().__getitem__(name)

    def __setitem__(self, name, val, /):
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
        if isinstance(val, Directive):
            name, val = val.__directive_call__(self, name)
        if val is NotImplemented:
            return
        if name is None:
            return
        super().__setitem__(name, val)

    def __delitem__(self, name, /):
        if name in self.escaped:
            del self.escapedvals[name]
        super().__delitem__(name)

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
        if not isinstance(outer, ClassBody):
            check = False
        else:
            name, made = self.name, outer.mroclassesmade
            try:
                madecheck = made[name]
            except KeyError:
                check = False
            else:
                if madecheck:
                    raise RuntimeError("Mroclass already created!")
                check = True
                outer.anticipate_mroclass(name)
        self.ismroclass = check

    def _post_prepare_bases(self, /):
        bases = []
        if self.ismroclass:
            name, outer = self.name, self.outer
            for overclassname in outer.meta.__mroclasses__[name]:
                try:
                    base = outer[overclassname]
                except KeyError:
                    base = outer.add_notion(overclassname)
                bases.append(base)
            for obase in outer.bases:
                try:
                    mrobase = getattr(obase, name)
                except AttributeError:
                    continue
                if mrobase not in bases:
                    bases.append(mrobase)
        for base in self._rawbases:
            if isinstance(base, type):
                if base not in bases:
                    bases.append(base)
            else:
                raise TypeError(type(base))
                # bases.extend(
                #     entry for entry in base.__mro_entries__
                #     if entry not in bases
                #     )
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
                raise RuntimeError("Could not identify proper metaclass.")
        for metabase in (meta, *meta.__bases__):
            try:
                basetyp = metabase.BaseTyp
            except AttributeError:
                continue
            if not any(issubclass(base, basetyp) for base in bases):
                bases.append(basetyp)
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
        if isinstance(dyntyp, type):
            if issubclass(dyntyp, _collabc.Mapping):
                dynobj = dyntyp(_itertools.chain.from_iterable(
                    mp.items() for mp in mergees
                    ))
                addmeth = dynobj.update
            else:
                dynobj = dyntyp(_itertools.chain.from_iterable(mergees))
                addmeth = dynobj.extend
        else:
            dynobj = dyntyp(_itertools.chain.from_iterable(mergees))
            addmeth = dynobj.extend
        return addmeth, dynobj

    def _add_mergechannel(self, mname, /):
        genericfunc = lambda addmeth, val: addmeth(val)
        nametriggers = self._nametriggers
        dyntyp, fintyp = self.mergenames[mname]
        addmeth, dynobj = self._gather_mergenames(mname, dyntyp)
        super().__setitem__(mname, dynobj)
        nametriggers[mname] = _partial(genericfunc, addmeth)

    def _update_mergenames(self, dct, /):
        mergenames = self.mergenames
        oldnames = set(mergenames)
        mergenames.update(dct)
        for mname in set(mergenames).difference(oldnames):
            self._add_mergechannel(mname)

    def _post_prepare_mergednames(self, /):
        addmeth, dynobj = self._gather_mergenames('__mergenames__', dict)
        dynobj.update(
            (nm, (dyntyp, fintyp))
            for nm, dyntyp, fintyp in self.meta._yield_mergenames()
            )
        self._update_mergenames(dynobj)

    def _post_prepare_mroclasses(self, /):
        self.mroclassesmade = {key: False for key in self.meta.__mroclasses__}

    def _post_prepare_bodymeths(self, /):
        toadd = dict(
            (name, meth)
            for name, meth in self.meta._yield_bodymeths(self)
            )
        toadd['escaped'] = _partial(Escaped, self)
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
            try:
                _ = module._ISSTELE_
            except AttributeError:
                iscosmic = True
                outer = None
            else:
                iscosmic = False
                outer = module
        else:
            iscosmic = False
        self.outer = outer
        self.iscosmic = iscosmic
        super().__setitem__('_clsiscosmic', iscosmic)
        self._post_prepare_ismroclass()
        self._post_prepare_bases()
        self._post_prepare_mergednames()
        self._post_prepare_mroclasses()
        self._post_prepare_bodymeths()
        self._post_prepare_nametriggers()
        self._fullyprepared = True

    def add_notion(self, name, base=None, /):
        if base is None:
            base = self.meta._defaultbasetyp
        out = self[name] = type(
            name, (base,), {},
            modname=self.modname, qualroot=self.qualname,
            )
        return out

    def anticipate_mroclass(self, name, /):
        self._nametriggers[name] = _partial(self.add_mroclass_premade, name)

    def add_mroclass_premade(self, name, val, /):
        super().__setitem__(name, val)
        self.protect_name(name)
        self.mroclassesmade[name] = True

    def add_mroclass(self, name, base=None, /):
        del self._nametriggers[name]
        out = self.add_notion(name, base)
        self.mroclassesmade[name] = True
        self.protect_name(name)
        return out

    def _finalise_mergenames(self, /):
        mergenames = self.mergenames
        for mname, (_, fintyp) in mergenames.items():
            super().__setitem__(mname, fintyp(super().__getitem__(mname)))
        super().__setitem__(
            '__mergenames__', _ptolemaic.convert(mergenames)
            )

    def _finalise_mroclasses(self, /):
        for mroname, check in self.mroclassesmade.items():
            if not check:
                self.add_notion(mroname, self.get(mroname, None))

    def register_innerobj(self, obj, name, /):
        self.innerobjs[name] = obj

    def finalise(self, /):
        assert self._fullyprepared, (self.name,)
        self._finalise_mergenames()
        self._finalise_mroclasses()
        self.meta.classbody_finalise(self)
        out = _abc.ABCMeta.__new__(
            self.meta, self.name, self.bases, dict(self)
            )
        if self.iscosmic:
            type.__setattr__(out, '_clsiscosmic', True)
        else:
            self.outer.register_innerobj(self.name, out)
            type.__setattr__(out, '_clsiscosmic', False)
        type.__setattr__(out, '_clsinnerobjs', {})
        for name, innerobj in self.innerobjs.items():
            out.register_innerobj(innerobj, name)
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
