###############################################################################
''''''
###############################################################################


from functools import partial as _partial
import fnmatch as _fnmatch
import itertools as _itertools

from . import _utilities

from .base import _Reader


_FrozenOrderedMap = _utilities.misc.FrozenOrderedMap


class _Derived(_Reader):

#     __slots__ = ('_source', '_reader')

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
        try:
            return self._reader
        except AttributeError:
            reader = self._reader = self.source.reader
            return reader

    def operate(self, *args, **kwargs):
        return type(self.reader).operate(*args, **kwargs)

    def get_h5man(self):
        return self.reader.h5man

    def get_getmeths(self):
        return self.reader.get_getmeths()

    def retrieve(self, key, *, h5file = None):
        return self.reader.retrieve(key, h5file = h5file)


class _Incision(_Derived):

#     __slots__ = ('_incisor',)

    def __init__(self, source, incisor):
        if isinstance(incisor, _Reader):
            if incisor.reader is not source.reader:
                raise ValueError(
                    "Incisor reader and source reader must be identical."
                    )
        self._source = source
        self._incisor = incisor
        self.register_argskwargs(source, incisor)

    def get_basekeydict(self):
        manifest = self.manifest
        srcdict = self.source.basekeydict
        return _FrozenOrderedMap(zip(
            manifest,
            map(srcdict.__getitem__, manifest)
            ))

    def get_basekeys(self):
        return type(self.reader).get_basekeys(self)

    @property
    def incisor(self):
        return self._incisor

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.reader)}, {self.incisor})"

# class Readlet(_Derived):
    


class Pattern(_Incision):

    def get_manifest(self):
        return tuple(_fnmatch.filter(self.source.manifest, self.incisor))


class Slice(_Incision):

    def get_manifest(self):
        return tuple(self.source.manifest)[self.incisor]


class Selection(_Incision):

    def get_basekeys(self):
        incisor = self.incisor
        if isinstance(incisor, _Reader):
            with self.h5man as h5file:
                incisor = frozenset(_itertools.compress(
                    incisor.basekeydict.values(),
                    incisor._read(h5file)
                    ))
        return frozenset.intersection(incisor, self.source.basekeys)

    def get_manifest(self):
        srcbkd = self.source.basekeydict
        return tuple(_itertools.compress(
            srcbkd,
            map(self.__contains__, srcbkd.values()),
            ))

class _MultiDerived(_Derived):

#     __slots__ = ('_sources')

    def __init__(self, *sources):
        if not all(isinstance(source, _Reader) for source in sources):
            raise ValueError("All sources must be _Reader instances.")
        if len(frozenset(source.reader for source in sources)) != 1:
            raise ValueError("Cannot combine different reader objects.")
#         if len(frozenset(source.basehash for source in sources)) != 1:
#             raise ValueError("Sources must share identical basekeys.")
        self._sources = sources
        self._source = sources[0]
        self.register_argskwargs(*sources)
    
    @property
    def sources(self):
        return self._sources


class SetOp(_MultiDerived):

#     __slots__ = ('_setop',)

    SETOPS = dict(
        union = frozenset.union,
        intersection = frozenset.intersection,
        difference = frozenset.difference,
        symmetric_difference = frozenset.symmetric_difference
        )

    def __init__(self, setop, *args):
        if isinstance(setop, str):
            setop = self.SETOPS[setop]
        self._setop = setop
        self.register_argskwargs(setop)
        super().__init__(*args)

    @property
    def setop(self):
        return self._setop

    def get_basekeys(self):
        if len(sources := self.sources) == 1:
            return sources[0].basekeys
        return self._setop(*(source.basekeys for source in sources))

    def get_basekeydict(self):
        return _FrozenOrderedMap(
            _itertools.chain.from_iterable((
                (mk, bk) for mk, bk in src.basekeydict.items()
                    if bk in self.basekeys
                ) for src in self.sources)
            )

    def get_manifest(self):
        return tuple(self.basekeydict)

    def __repr__(self):
        return f"{type(self).__name__}({self.setop}({self.sources}))"


class Transform(_MultiDerived):

#     __slots__ = (
#         '_sources', '_operands', '_length', '_basekeys',
#         '_operator',
#         )
    _setop = frozenset.intersection

    def __init__(self, operator, *operands, **kwargs):
        operator = _partial(operator, **kwargs) if kwargs else operator
        self._operands = operands
        self._operator = operator
        self.register_argskwargs(operator)
        super().__init__(*(op for op in operands if isinstance(op, _Reader)))

    @property
    def operands(self):
        return self._operands

    @property
    def operator(self):
        return self._operator

    def get_basekeys(self):
        return self.sources[0].basekeys

    def get_manifest(self):
        sources = self.sources
        if len(set(src.basehash for src in sources)) != 1:
            raise ValueError("Transform sources must have identical bases.")
        return tuple(zip(*(src.manifest for src in sources)))

    def get_basekeydict(self):
        return _FrozenOrderedMap(
            (mks, self.sources[0].basekeydict[mks[0]])
                for mks in self.manifest
            )

    def _retrieve(self, key, *, h5file):
        keys = iter(keys)
        return self.operator(*(
            op._retrieve(next(keys)) if isinstance(op, _Reader) else op
                for op in self.operands
            ))

    def _read(self, h5file):
        return map(self.operator, *(
            oper._read(h5file) if isinstance(oper, _Reader)
                else _itertools.repeat(oper)
                    for oper in self.operands
            ))

    def __repr__(self):
        return f"{type(self).__name__}({self.operator}, {self.operands})"


###############################################################################
###############################################################################
