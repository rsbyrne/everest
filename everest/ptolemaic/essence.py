###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import itertools as _itertools
import more_itertools as _mitertools
import inspect as _inspect
import operator as _operator
import pickle as _pickle
# import typing as _typing
from collections import abc as _collabc

from everest import utilities as _utilities
from everest.utilities import caching as _caching

from everest.ptolemaic.pleroma import Pleroma as _Pleroma


def ordered_set(itr):
    return tuple(_mitertools.unique_everseen(itr))


def pass_fn(arg, /):
    return arg


class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

    ### Methods relating to the metaclass itself:

    @classmethod
    def _pleroma_init__(meta, /):
        pass

    ### Methods relating to the Incision Protocol for classes:

    def __instancecheck__(cls, arg, /):
        return cls._ptolemaic_isinstance__(arg)

    def __contains__(cls, arg, /):
        return cls._ptolemaic_contains__(arg)

    def __getitem__(cls, arg, /):
        return cls._ptolemaic_getitem__(arg)

    def _class_chora_passthrough(cls, arg, /):
        return arg

    def _class_defer_chora_methods(cls, /):

        chcls = type(cls.clschora)
        prefixes = chcls.PREFIXES
        defkws = chcls._get_defkws((f"cls.class_{st}" for st in prefixes))

        for prefix in prefixes:
            methname = f"class_{prefix}"
            if not hasattr(cls, methname):
                setattr(cls, methname, cls._class_chora_passthrough)

        exec('\n'.join((
            f"@classmethod",
            f"def _ptolemaic_getitem__(cls, arg, /):"
            f"    return cls.clschora.__getitem__(arg, {defkws})"
            )))
        cls._ptolemaic_getitem__ = eval('_ptolemaic_getitem__')

        for name in chcls.chorameths:
            new = f"class_{name}"
            exec('\n'.join((
                f"@classmethod",
                f"@_functools.wraps(chcls.{name})",
                f"def {new}(cls, /, *args):",
                f"    return cls.clschora.{name}(*args, {defkws})",
                )))
            setattr(cls, new, eval(new))

    ### Defining the mandatory basetype for instances of this metaclass:

    @classmethod
    def get_basetyp(meta, /):
        try:
            return Shade
        except NameError:
            return type(meta).get_basetyp(meta)

    ### Creating the object that is the class itself:

    @classmethod
    def __prepare__(meta, name, bases, /, *args, **kwargs):
        return dict()

    @classmethod
    def process_bases(meta, bases):
        '''Inserts the metaclass's mandatory basetype if necessary.'''
        basetyp = meta.BaseTyp
        if tuple(filter(basetyp.__subclasscheck__, bases)):
            return bases
        return (*bases, basetyp)

    def __new__(meta, name, bases, namespace, /, *args, **kwargs):
        bases = meta.process_bases(bases)
        namespace['__slots__'] = ()
        return super().__new__(meta, name, bases, namespace, *args, **kwargs)

    ### Implementing mergetuples and mergedicts:

    @staticmethod
    def _gather_names(bases, name, methcall, /):
        return ordered_set(_itertools.chain.from_iterable(
            methcall(getattr(base, name))
            for base in bases if hasattr(base, name)
            ))

    def _merge_names(cls, name, /, *, mergetyp=tuple, itermeth='__iter__'):
        methcall = _operator.methodcaller(itermeth)
        merged = []
        merged.extend(cls._gather_names(cls.__bases__, name, methcall))
        if name in cls.__dict__:
            merged.extend(ordered_set(methcall(getattr(cls, name))))
        merged = ordered_set(merged)
        setattr(cls, name, mergetyp(merged))

    def _merge_names_all(cls, overname, /, **kwargs):
        cls._merge_names(overname)
        for name in getattr(cls, overname):
            cls._merge_names(name, **kwargs)

    ### Implementing mroclasses:

    def _add_mroclass(cls, name: str, /):
        adjname = f'_mroclassbase_{name}__'
        fusename = f'_mroclassfused_{name}__'
        if name in cls.__dict__:
            setattr(cls, adjname, cls.__dict__[name])
        inhclasses = []
        for mcls in cls.__mro__:
            searchname = adjname if isinstance(mcls, Essence) else name
            if searchname in mcls.__dict__:
                inhcls = mcls.__dict__[searchname]
                if not inhcls in inhclasses:
                    inhclasses.append(inhcls)
        inhclasses = tuple(inhclasses)
        mroclass = type(name, inhclasses, {})
        setattr(cls, fusename, mroclass)
        setattr(cls, name, mroclass)

    def _add_mroclasses(cls, /):
        for name in cls._ptolemaic_mroclasses__:
            cls._add_mroclass(name)

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(cls, '__annotations__'):
            cls.__annotations__ = dict()
        cls._merge_names('_ptolemaic_mergetuples_')
        cls._merge_names('_ptolemaic_mergedicts__')
        cls._merge_names_all(
            '_ptolemaic_mergetuples__'
            )
        cls._merge_names_all(
            '_ptolemaic_mergedicts__',
            mergetyp=_utilities.FrozenMap,
            itermeth='items',
            )
        cls._add_mroclasses()
        try:
            cls.clschora = cls._get_clschora()
        except NotImplementedError:
            pass
        else:
            cls._class_defer_chora_methods()

    ### What happens when the class is called:

    def construct(cls, /):
        raise NotImplementedError

    @property
    def __call__(cls, /):
        return cls.construct

    ### Methods relating to serialising and unserialising classes:

    @property
    @_caching.soft_cache()
    def epitaph(cls, /):
        return type(cls).taphonomy(cls.get_epitaph())

    ### Defining aliases and representations for classes:

    def __repr__(cls, /):
        return cls.__class_repr__()

    @property
    def _ptolemaic_class__(cls, /):
        return cls

    @property
    def metacls(cls, /):
        return type(cls._ptolemaic_class__)

    @property
    def taphonomy(cls, /):
        return cls.metacls.taphonomy

    @property
    def hashcode(cls, /):
        return cls.epitaph.hashcode

    @property
    def hashint(cls, /):
        return cls.epitaph.hashint

    @property
    def hashID(cls, /):
        return cls.epitaph.hashID


class Shade(metaclass=Essence):

    __slots__ = ()

    _ptolemaic_mergetuples__ = (
        '_ptolemaic_mroclasses__',
        )
    _ptolemaic_mergedicts__ = ()
    _ptolemaic_mroclasses__ = ()

    @classmethod
    def __class_init__(cls, /):
        pass

    ### Customisable methods relating to the Incision Protocol:

    @classmethod
    def _ptolemaic_isinstance__(cls, arg, /):
        '''Returns `False` as `Essence` types cannot be instantiated.'''
        return False

#         @classmethod
#         def _ptolemaic_issubclass__(cls, arg, /):
#             return _abc.ABCMeta.__subclasscheck__(cls, arg)

    @classmethod
    def _ptolemaic_contains__(cls, arg, /):
        raise NotImplementedError

    @classmethod
    def _ptolemaic_getitem__(cls, arg, /):
        raise NotImplementedError

    @classmethod
    def _get_clschora(cls, /) -> 'Chora':
        raise NotImplementedError

    @classmethod
    def __contains__(cls, arg, /):
        return cls.clschora.__contains__(arg)

    ### Supporting serialisation:

    @classmethod
    def get_epitaph(cls, /):
        return type(cls).taphonomy.encode_content(cls)

    ### Legibility methods:

    @classmethod
    def __class_repr__(cls, /):
        return cls.__qualname__


###############################################################################
###############################################################################
