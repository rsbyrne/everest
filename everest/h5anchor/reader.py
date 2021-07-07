###############################################################################
''''''
###############################################################################


import ast as _ast
import pickle as _pickle
import os as _os
from collections import deque as _deque
from collections.abc import Collection as _Collection
from functools import partial as _partial #, lru_cache as _lru_cache
import pickle as _pickle
from abc import ABC as _ABC, abstractmethod as _abstractmethod
import fnmatch as _fnmatch

import h5py as _h5py

from . import disk as _disk
from . import _utilities

_classtools = _utilities.classtools
_reseed = _utilities.reseed
_TypeMap = _utilities.misc.TypeMap
_makehash = _utilities.makehash


def resolve_eval(strn):
    out = _ast.literal_eval(strn)
    typout = type(out)
    if issubclass(typout, (list, tuple, frozenset)):
        return typout(resolve(sub) for sub in out)
    return out

stringresmeths = dict(
    _bytes_ = lambda x: pickle.loads(ast.literal_eval(x)),
    _eval_ = resolve_eval,
    _string_ = lambda x: x,
    )

def resolve_str(strn, /):
    for key, meth in stringresmeths.items():
        if strn.startswith(key):
            return meth(strn[len(key):])
    return strn

def resolve_attrs(attrs):
    return {key: resolve(attr) for key, attr in attrs.items()}

def resolve_dataset(dset):
    return dset[()]

def resolve_group(grp):
    out = {key: resolve(item) for key, item in grp.items()}
    out.update(resolve_attrs(grp.attrs))
    return out

resmeths = {
    str: resolve_str,
    _h5py.AttributeManager: resolve_attrs,
    _h5py.Dataset: resolve_dataset,
    _h5py.Group: resolve_group,
    }

def resolve(obj):
    for key, meth in resmeths.items():
        if isinstance(obj, key):
            return meth(obj)
    return obj


def process_query(strn):
    split = strn.split('/')
    if len(split) > 1:
        for sub in split:
            yield from process_query(sub)
    elif isreg(strn):
        yield Reg(strn)
    elif isfnmatch(strn):
        yield FnMatch(strn)
    else:
        yield strn

def record_manifest_sub(h5grp, manifest, prename, name):
    try:
        h5grp = h5grp[name]
    except KeyError:
        return
    if not (isgrp := isinstance(h5grp, _h5py.Group)):
        name = '#' + name
    fullname = f"{prename}/{name}"
    manifest.append(fullname)
    manifest.extend((f"{fullname}.{attname}" for attname in h5grp.attrs))
    if isgrp:
        for name in h5grp:
            record_manifest_sub(h5grp, manifest, fullname, name)

def record_manifest(h5grp, manifest = None):
    manifest = _deque() if manifest is None else manifest
    manifest.append('/')
    manifest.extend((f"/.{attname}" for attname in h5grp.attrs))
    for i, name in enumerate(h5grp):
        record_manifest_sub(h5grp, manifest, '', name)
        if not i % 1000:
            print(i, name)


@_classtools.Operable
class _Reader(_ABC):

    __slots__ = (
        '_h5man', '_manifest', '_base', '_isunique', '_getmeths',
        '_basedict', '_basehash',
        )

    @property
    def base(self):
        return self._base

    @property
    def manifest(self):
        try:
            return self._manifest
        except AttributeError:
            manifest = self._manifest = sorted(self.get_manifest())
            return manifest

    @_abstractmethod
    def get_manifest(self):
        '''Should return a list of internal h5 paths.'''
        raise TypeError("Abstract method!")

    @property
    def basekeys(self):
        try:
            return self._basekeys
        except AttributeError:
            basekeys = self._basekeys = sorted(self.get_basekeys())
            return basekeys

    def get_basekeys(self):
        manifest = self.manifest
        if (base := self.base) is None:
            return manifest
        return ['/'.join(path.split('/')[:base+1]) for path in manifest]

    @property
    def basedict(self):
        try:
            return self._basedict
        except AttributeError:
            basedict = self._basedict = dict(zip(self.basekeys, self.manifest))
            return basedict

    @property
    def basehash(self):
        try:
            return self._basehash
        except AttributeError:
            basehash = self._basehash = _makehash.quick_hash(self.basekeys)
            return basehash

    @property
    def isunique(self):
        try:
            return self._isunique
        except AttributeError:
            if self.base is None:
                isunique = True
            else:
                isunique = len(set(self.basekeys)) == len(self)
            self._isunique = isunique
            return isunique

    @property
    def h5man(self):
        try:
            return self._h5man
        except AttributeError:
            h5man = self._h5man = self.get_h5man()
            return h5man

    @_abstractmethod
    def get_h5man(self):
        '''Should return an H5Manager object.'''
        raise TypeError("Abstract method!")

    @property
    def getmeths(self):
        try:
            return self._getmeths
        except AttributeError:
            getmeths = self._getmeths = _TypeMap({
                tuple: self.getitem_tuple,
                _Reader: self.getitem_mask,
                str: self.getitem_str,
                _Collection: self.getitem_collection,
                int: self.getitem_int,
                slice: self.getitem_slice,
                object: self.getitem_bad,
                })
            return getmeths

    def getitem_bad(self, key):
        raise TypeError(type(arg))

    def getitem_tuple(self, arg):
        raise Exception("Getting from Reader with tuple not yet supported.")

    def getitem_str(self, key):
        if key in self.manifest:
            return self.getitem_path(key)
        return Pattern(self, key)

    def getitem_pattern(self, key):
        return Pattern(self, key)

    def getitem_slice(self, key):
        return Slice(self, key)

    def getitem_collection(self, coll):
        manifest = self.manifest
        selection = [key for key in coll if key in manifest]
        if len(selection) < len(coll):
            raise KeyError
        if isinstance(self, Selection):
            return Selection(self.reader, selection)
        return Selection(self, selection)

    def getitem_path(self, key, *, h5file = None):
        if h5file is None:
            with self.h5man as h5file:
                return self.getitem_path(key, h5file = h5file)
        key = key.replace('#', '').replace('.', '/.')
        if '.' in key:
            key, attrkey = (
                _os.path.dirname(key), _os.path.basename(key).strip('.')
                )
            raw = h5file[key].attrs[attrkey]
        else:
            raw = h5file[key]
        return resolve(raw)

    def getitem_int(self, index):
        return self.getitem_path(self.manifest[index])

    def getitem_mask(self, arg):
        return Mask(self, arg)

    def __getitem__(self, arg):
        return self.getmeths[type(arg)](arg)

    def read(self):
        if not self.isunique:
            raise ValueError("Cannot read from reader with non-unique basekeys")
        manifest = self.manifest
        with self.h5man as h5file:
            results = (
                self.getitem_path(path, h5file = h5file)
                    for path in self.manifest
                )
            return dict(zip(self.basekeys, results))

    @classmethod
    def operate(cls, *args, typ = None, **kwargs):
        return Transform(*args, **kwargs)

    def __contains__(self, key):
        return key in self.manifest

    def __iter__(self):
        return iter(self.read().values())

    def __len__(self):
        return len(self.manifest)

    def __repr__(self):
        return f"{type(self).__name__}({self.h5man.h5filename})"

    def __hash__(self):
        try:
            return self._hashint
        except AttributeError:
            hashint = self._hashint = _reseed.randint(repr(self))
            return hashint


class Reader(_Reader):

    __slots__ = ('name', 'path')

    def __init__(self, name, path, base = None):
        self.name, self.path = name, path
        self._base = base

    def get_h5man(self):
         return _disk.H5Manager(self.name, self.path, mode = 'r')

    def get_manifest(self):
        manfilepath = _os.path.join(self.path, self.name + '.pkl')
        try:
            with open(manfilepath, mode = 'rb') as file:
                manifest = _pickle.loads(file.read())
        except FileNotFoundError:
            manifest = _deque()
            with self.h5man as h5file:
                record_manifest(h5file, manifest)
            with open(manfilepath, mode = 'wb') as file:
                file.write(_pickle.dumps(manifest))
        return manifest


class _Derived(_Reader):

    __slots__ = ('_source', '_reader', "_incisor")

    def __init__(self, source, incisor):
        self._source = source
        if isinstance(source, _Derived):
            self._reader = source.reader
        else:
            self._reader = source
        self._incisor = incisor

    @property
    def base(self):
        return self.reader.base

    @property
    def name(self):
        return self.reader.name

    @property
    def path(self):
        return self.reader.path

    @property
    def source(self):
        return self._source

    @property
    def reader(self):
        return self._reader

    @property
    def incisor(self):
        return self._incisor

    def get_h5man(self):
        return self.reader.h5man

    def getitem_path(self, key, *, h5file = None):
        return self.reader.getitem_path(key, h5file = h5file)

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.reader)}, {self.incisor})"

# class Readlet(_Derived):
    


class Pattern(_Derived):

    def get_manifest(self):
        return _fnmatch.filter(self.source.manifest, self.incisor)


class Slice(_Derived):

    def get_manifest(self):
        return self.source.manifest[self.incisor]


class Selection(_Derived):

    def get_manifest(self):
        return self.incisor


class Mask(_Derived):

    def get_manifest(self):
        return (
            entry
            for entry, mask in zip(self.source.manifest, self.incisor)
            if mask
            )


class Source:
    def __hash__(self):
        return 0
    def __repr__(self):
        return 'SOURCE'
SOURCE = Source()

class Transform(_Reader):

    __slots__ = (
        '_sources', '_operands', '_length', '_basekeys',
        '_singlesource', '_operator', '_alloperands',
        )

    def __init__(self, operator, *args, **kwargs):
        global SOURCE
        sources = []
        operands = []
        for arg in args:
            if isinstance(arg, _Reader):
                sources.append(arg)
                operands.append(SOURCE)
            else:
                operands.append(arg)
        if not len(sources):
            raise ValueError("No sources!")
        if not (singlesource := len(sources) == 1):
            if len(set(source.h5man.h5filename for source in sources)) != 1:
                raise ValueError("Incongruous sources.")
            if not all(source.isunique for source in sources):
                raise ValueError("Sources must all have unambiguous basekeys.")
            if not len(set(source.basehash for source in sources)):
                raise ValueError("Sources must have matching basekeys.")
        self._alloperands = args
        self._sources, self._operands = sources, operands
        self._singlesource = singlesource
        self._operator = _partial(operator, **kwargs) if kwargs else operator
        self._base = sources[0].base

    @property
    def alloperands(self):
        return self._alloperands

    @property
    def sources(self):
        return self._sources

    @property
    def source(self):
        return self.sources[0]

    @property
    def singlesource(self):
        return self._singlesource

    @property
    def operands(self):
        return self._operands

    @property
    def operator(self):
        return self._operator

    def get_h5man(self):
        return self.sources[0].h5man

    def get_manifest(self):
        sources = self.sources
        if self.singlesource:
            return self.source.manifest
        else:
            return zip(*(source.manifest for source in sources))

    def get_basekeys(self):
        sources = self.sources
        if self.singlesource:
            return self.source.basekeys
        return sorted(set.intersection(
            *(set(source.basekeys) for source in sources)
            ))

    def getitem_path(self, keys, h5file = None):
        if h5file is None:
            with self.h5man as h5file:
                return self.getitem_path(*keys, h5file = h5file)
        global SOURCE
        keys = iter((keys,) if self.singlesource else keys)
        sources = iter(self.sources)
        return self.operator(*(
            (
                next(sources).getitem_path(next(keys), h5file = h5file)
                if op is SOURCE
                else op
            ) for op in self.operands
            ))

    def __repr__(self):
        return f"{type(self).__name__}({self.operator}, {self.alloperands})"


###############################################################################
###############################################################################