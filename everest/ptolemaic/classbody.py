###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import weakref as _weakref
from functools import partial as _partial
from collections import abc as _collabc

from everest import ur as _ur

from .pleroma import Pleroma as _Pleroma
from .shadow import Shadow as _Shadow, Shade as _Shade
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
    def __directive_call__(self, body, name, /):
        raise NotImplementedError


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
                innerclasses=[],
                _clsiscosmic=None,
                __class_relname__=name,
                _clsmutable=_Switch(True),
                __mroclasses__=[],
                ).items():
            super().__setitem__(nm, val)
        self._nametriggers = dict(
            __module__=(lambda val: setattr(self, 'module', val)),
            __qualname__=(lambda val: setattr(self, 'qualname', val)),
            __mroclasses__=self._update_mroclasses,
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
            self.module, self.qualname = location

    def protect_name(self, name, /):
        self._protected.add(name)

    def enroll_shade(self, name, /):
        self._shades[name] = _Shade(str(name))
        self.protect_name(name)

    def _update_mroclasses(self, val, /):
        val = tuple(val)
        mroclasses = super().__getitem__('__mroclasses__')
        new = tuple(subval for subval in val if val not in mroclasses)
        mroclasses.extend(new)
        self._nametriggers.update(
            (name, _partial(self._add_innerclass, name))
            for name in new
            )

    def handle_slots(self, slots, /):
        if slots:
            self.meta.handle_slots(self, slots)

#     @property
#     def sugar(self, /):
#         return self._sugar

#     @sugar.setter
#     def sugar(cls, val, /):
#         self._sugar.toggle(val)

#     def __sugar_getitem__(self, name, /):
#         return self._sugardict[name]

    def __getitem__(self, name, /):
        try:
            return self._redirects[name]
        except KeyError:
            pass
        try:
            return super().__getitem__(name)
        except KeyError:
            pass
        return self._shades[name]

#     def __iter__(self, /):
#         return iter(self._content)

#     def __len__(self, /):
#         return len(self._content)

#     @property
#     def keys(self, /):
#         return self._content.keys

#     @property
#     def values(self, /):
#         return self._content.values

#     def __contains__(self, name, /):
#         return name in self._content

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
            val.__directive_call__(self, name)
            return
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

    @property
    def ismroclass(self, /):
        try:
            return self._ismroclass
        except AttributeError:
            if not self.iscosmic:
                name, obody = self.name, self.outerbody
                if name in obody['__mroclasses__']:
                    out = self._ismroclass = True
                    obody.anticipate_mroclass(name)
                    return out
            out = self._ismroclass = False
            return out

    def _post_prepare_bases(self, /):
        out = []
        if self.ismroclass:
            name = self.name
            for obase in self.outerbody.bases:
                try:
                    mrobase = getattr(obase, name)
                except AttributeError:
                    continue
                if mrobase not in out:
                    out.append(mrobase)
        for base in self._rawbases:
            if base not in out:
                out.append(base)
        self.bases = tuple(out)

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

    def _post_prepare_mergednames(self, /):
        bases = self.bases
        meta = self.meta
        mergenames = self.mergenames = \
            _ur.DatUniqueTuple(meta._yield_mergenames())
        genericfunc = lambda meth, val: (None, meth(val))
        for mname, dyntyp, _ in mergenames:
            mergees = (
                getattr(base, mname) for base in bases if hasattr(base, mname)
                )
            if issubclass(dyntyp, _collabc.Mapping):
                dynobj = dyntyp(_itertools.chain.from_iterable(
                    mp.items() for mp in mergees
                    ))
                meth = dynobj.update
            else:
                dynobj = dyntyp(_itertools.chain.from_iterable(mergees))
                meth = dynobj.extend
            super().__setitem__(mname, dynobj)
            self._nametriggers[mname] = _partial(genericfunc, meth)

    def _post_prepare_bodymeths(self, /):
        toadd = dict(
            (name, _partial(meth, self))
            for name, meth in self.meta._yield_bodymeths()
            )
        self._redirects.update(toadd)
        self._protected.update(toadd)

    def _post_prepare_nametriggers(self, /):
        self._nametriggers.update(
            (name, _partial(meth, self))
            for name, meth in self.meta._yield_bodynametriggers()
            )

    def _post_prepare_mroclasses(self, /):
        empty = ()
        gathered = _ur.DatUniqueTuple(_itertools.chain.from_iterable(
            getattr(base, '__mroclasses__', empty) for base in self.bases
            ))
        self._update_mroclasses(
            nm for nm in gathered
            if nm not in super().__getitem__('__mroclasses__')
            )

    def _post_prepare(self, /):
        module, qualname = self.module, self.qualname
        BODIES = type(self).BODIES
        BODIES[module, qualname] = self
        stump = '.'.join(qualname.split('.')[:-1])
        name = self.name
        try:
            obody = BODIES[module, stump]
        except KeyError:
            self.outerbody = None
            iscosmic = self.iscosmic = True
        else:
            self.outerbody = obody
            iscosmic = self.iscosmic = False
        super().__setitem__('_clsiscosmic', iscosmic)
        self._post_prepare_bases()
        self._post_prepare_meta()
        self._post_prepare_mergednames()
        self._post_prepare_bodymeths()
        self._post_prepare_nametriggers()
        self._post_prepare_mroclasses()
        self._fullyprepared = True

    def _add_innerclass(self, name, base=None, /):
        if base is None:
            base = self.meta._defaultbasetyp
        super().__setitem__(name, type(
            name, (base,), {},
            location=(self.module, f"{self.qualname}.{name}"),
            ))
        return None, None

    def _add_mroclass(self, name, mroclass, /):
        super().__setitem__(name, mroclass)
        self._nametriggers[name] = _partial(self._add_innerclass, name)
        return None, None

    def anticipate_mroclass(self, name, /):
        self._nametriggers[name] = _partial(self._add_mroclass, name)

    def _finalise_mroclasses(self, /):
        mroclasses = _ur.DatUniqueTuple(super().__getitem__('__mroclasses__'))
        super().__setitem__('__mroclasses__', mroclasses)
        if mroclasses:
            for mroname in mroclasses:
                if mroname not in self:
                    # self[mroname] = default
                    self._add_innerclass(mroname)

    def _finalise_mergenames(self, /):
        for mname, _, fintyp in self.mergenames:
            super().__setitem__(mname, fintyp(super().__getitem__(mname)))

    def finalise(self, /):
        assert self._fullyprepared
        self._finalise_mergenames()
        self._finalise_mroclasses()
        return self.name, self.bases, dict(self)

    def __setanno__(self, name, val, /):
        self.__setitem__(*self.meta.process_bodyanno(
            self, name, val, self.pop(name, NotImplemented)
            ))

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
