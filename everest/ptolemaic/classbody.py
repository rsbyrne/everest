###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import weakref as _weakref
import functools as _functools
from collections import abc as _collabc

from everest import ur as _ur

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


class ClassBody(dict):

    BODIES = _weakref.WeakValueDictionary()

    def __init__(
            self, meta, name, bases, /, *,
            location=None, _staticmeta_=False,
            **kwargs,
            ):
        super().__init__(
            _=self,
            # __name__=name,  # Breaks things in a really interesting way!
            __slots__=(),
            innerclasses=[],
            _clsiscosmic=None,
            __class_relname__=name,
            _clsmutable=_Switch(True),
            )
        self._nametriggers = dict(
            __module__=(lambda val: (None, setattr(self, 'module', val))),
            __qualname__=(lambda val: (None, setattr(self, 'qualname', val))),
            )
        self._redirects = dict(
            _=self,
            __annotations__=AnnotationHandler(self.__setanno__),
            )
        self._protected = set(self)
        self._suspended = _Switch(False)
        self._rawmeta = meta
        if _staticmeta_:
            self.meta = meta
        self.name = name
        self._rawbases = bases
        if location is not None:
            self.module, self.qualname = location

    def protect_name(self, name, /):
        self._protected.add(name)

    @property
    def protected(self, /):
        return frozenset(self._protected)

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
            name, val = meth(val)
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

    @property
    def ismroclass(self, /):
        try:
            return self._ismroclass
        except AttributeError:
            if not self.iscosmic:
                if self.name in self.outerbody.mroclasses:
                    out = self._ismroclass = True
                    return out
            out = self._ismroclass = False
            return out

    def _post_prepare_mroclasses(self, /):
        # if not '__mroclasses__' in self:
        #     super().__setitem__('__mroclasses__', ())
        # self.mroclasses = self['__mroclasses__']
        self.mroclasses = ()

    def _post_prepare_bases(self, /):
        out = []
        bases = self._rawbases
        if self.ismroclass:
            name = self.name
            for base in self.outerbody.bases:
                if hasattr(base, name):
                    if base not in out:
                        out.append(base)
        for base in bases:
            if base not in out:
                out.append(base)
        self.bases = tuple(out)

    def _post_prepare_meta(self, /):
        if hasattr(self, 'meta'):
            return
        metas = []
        for meta in map(type, self.bases):
            if isinstance(meta, _Pleroma):
                if not any(issubclass(meta, mt) for mt in metas):
                    metas.append(meta)
        if not metas:
            metas.append(self._rawmeta)
        self.meta = type("VirtualMeta", tuple(metas), {})

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
            self._nametriggers[mname] = _functools.partial(genericfunc, meth)

    def _post_prepare_bodymeths(self, /):
        self.__dict__.update(
            (name, _functools.partial(meth, self))
            for name, meth in self.meta._yield_bodymeths()
            )

    def _post_prepare_nametriggers(self, /):
        self._nametriggers.update(
            (name, _functools.partial(meth, self))
            for name, meth in self.meta._yield_bodynametriggers()
            )
        self._nametriggers.update(
            (name, _functools.partial(self._add_innerclass, name))
            for name in self.mroclasses
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
        self._post_prepare_mroclasses()
        self._post_prepare_bases()
        self._post_prepare_meta()
        self._post_prepare_mergednames()
        self._post_prepare_bodymeths()
        self._post_prepare_nametriggers()

    def _add_innerclass(self, name, base, /):
        super().__setitem__(name, type(
            name, (base,), {},
            location=(self.module, f"{self.qualname}.{name}"),
            ))
        self.protect_name(name)

    def finalise(self, /):
        for nm in self.mroclasses:
            if nm not in self:
                _, body[nm] = self._add_innerclass(nm, body, Essence.BaseTyp)
        for mname, _, fintyp in self.mergenames:
            super().__setitem__(mname, fintyp(self[mname]))
        return self.name, self.bases, dict(self)

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

    def __repr__(self, /):
        return f"{type(self).__qualname__}({super().__repr__()})"


###############################################################################
###############################################################################
