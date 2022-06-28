###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import sys as _sys
import weakref as _weakref
from functools import partial as _partial
from collections import abc as _collabc

from everest import ur as _ur
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


class ClassBody(dict):

    BODIES = _weakref.WeakValueDictionary()

    def __init__(
            self, meta, name, bases, /, *,
            location=None, _staticmeta_=False,
            **kwargs,
            ):
        for nm, val in dict(
                # __name__=name,  # Breaks things in a really interesting way!
                __slots__=(),
                _clsinnerobjs=[],
                _clsiscosmic=None,
                __class_relname__=name,
                _clsmutable=_Switch(True),
                ).items():
            super().__setitem__(nm, val)
        self._nametriggers = dict(
            __module__=(lambda val: setattr(self, 'modulename', val)),
            __qualname__=(lambda val: setattr(self, 'qualname', val)),
            __slots__=self.handle_slots,
            )
        # self._sugar = _Switch(withsugar)
        self._redirects = dict(
            _=self,
            # sugar=self._sugar,
            __annotations__=AnnotationHandler(self.__setanno__),
            )
        self._shades = dict()
        self._protected = set(self)
        if _staticmeta_:
            self.meta = meta
        self.name = name
        self._rawbases = bases
        self._fullyprepared = False
        if location is not None:
            self.modulename, self.qualname = location

    def protect_name(self, name, /):
        self._protected.add(name)

    def enroll_shade(self, name, /):
        self._shades[name] = _Shade(str(name))
        self.protect_name(name)

    def handle_slots(self, slots, /):
        if slots:
            self.meta.handle_slots(self, slots)

    def __getitem__(self, name, /):
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
        if name is not None:
            super().__setitem__(name, val)

    @property
    def modulename(self, /):
        return self._modulename

    @modulename.setter
    def modulename(self, val, /):
        try:
            _ = self.modulename
        except AttributeError:
            self._modulename = val
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

    def _post_prepare_ismroclass(self, /):
        outer = self.outer
        if outer is None:
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
            if base not in bases:
                bases.append(base)
        self.bases = tuple(bases)

    def _post_prepare_meta(self, /):
        if hasattr(self, 'meta'):
            return
        metas = tuple(map(type, self.bases))
        for meta in metas:
            if all(issubclass(meta, mt) for mt in metas):
                break
        else:
            raise RuntimeError("Could not identify proper metaclass.")
        self.meta = meta

    def _post_prepare_mroclasses(self, /):
        self.mroclassesmade = {key: False for key in self.meta.__mroclasses__}

    def _post_prepare_mergednames(self, /):
        bases = self.bases
        meta = self.meta
        mergenames = self.mergenames = tuple(
            (nm, dyntyp, _ptolemaic.convert_type(fintyp))
            for nm, dyntyp, fintyp in meta._yield_mergenames()
            )
        genericfunc = lambda meth, val: meth(val)
        nametriggers = self._nametriggers
        for mname, dyntyp, _ in mergenames:
            mergees = (
                getattr(base, mname) for base in bases if hasattr(base, mname)
                )
            if isinstance(dyntyp, type):
                if issubclass(dyntyp, _collabc.Mapping):
                    dynobj = dyntyp(_itertools.chain.from_iterable(
                        mp.items() for mp in mergees
                        ))
                    meth = dynobj.update
                else:
                    dynobj = dyntyp(_itertools.chain.from_iterable(mergees))
                    meth = dynobj.extend
            else:
                dynobj = dyntyp(_itertools.chain.from_iterable(mergees))
                meth = dynobj.extend
            super().__setitem__(mname, dynobj)
            nametriggers[mname] = _partial(genericfunc, meth)

    def _post_prepare_bodymeths(self, /):
        toadd = dict(
            (name, _partial(meth, self))
            for name, meth in self.meta._yield_bodymeths()
            )
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
        modulename, qualname = self.modulename, self.qualname
        module = self.module = _sys.modules[modulename]
        BODIES = type(self).BODIES
        BODIES[modulename, qualname] = self
        stump = '.'.join(qualname.split('.')[:-1])
        name = self.name
        try:
            obody = BODIES[modulename, stump]
        except KeyError:
            self.outer = None
            try:
                module._ISSCROLL_
            except AttributeError:
                iscosmic = True
            else:
                iscosmic = False
        else:
            self.outer = obody
            iscosmic = False
        self.iscosmic = iscosmic
        super().__setitem__('_clsiscosmic', iscosmic)
        self._post_prepare_ismroclass()
        self._post_prepare_bases()
        self._post_prepare_meta()
        self._post_prepare_mroclasses()
        self._post_prepare_mergednames()
        self._post_prepare_bodymeths()
        self._post_prepare_nametriggers()
        self._fullyprepared = True

    def add_notion(self, name, base=None, /):
        if base is None:
            base = self.meta._defaultbasetyp
        out = self[name] = type(
            name, (base,), {},
            location=(self.module, f"{self.qualname}.{name}"),
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
        for mname, _, fintyp in self.mergenames:
            super().__setitem__(mname, fintyp(super().__getitem__(mname)))

    def _finalise_mroclasses(self, /):
        for mroname, check in self.mroclassesmade.items():
            if not check:
                self.add_notion(mroname, self.get(mroname, None))

    def finalise(self, /):
        assert self._fullyprepared, (self.name,)
        self._finalise_mergenames()
        self._finalise_mroclasses()
        self.meta.classbody_finalise(self)
        return _abc.ABCMeta.__new__(
            self.meta, self.name, self.bases, dict(self)
            )

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
