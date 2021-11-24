###############################################################################
''''''
###############################################################################


import abc as _abc
import collections as _collections
from collections import abc as _collabc
import itertools as _itertools
import functools as _functools
import types as _types
import inspect as _inspect

from everest.utilities import (
    TypeMap as _TypeMap, MultiTypeMap as _MultiTypeMap
    )
from everest.utilities import caching as _caching
from everest.ptolemaic.aspect import Aspect as _Aspect
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic


def not_none(a, b):
    return b if a is None else a


overprint = _functools.partial(_itertools.starmap, not_none)


def passfn(arg, /):
    return arg


class Chora(_Ptolemaic):
    '''
    The Chora is Everest's abstract master representation
    of the concept of space.
    '''

    _ptolemaic_mergetuples__ = ('PREFIXES',)

    PREFIXES = ('trivial', 'retrieve', 'incise')

    def _trivial_(self, incisor: type(Ellipsis) = None, /):
        '''Captures the special behaviour implied by `self[...]`.'''
        return self

    def _retrieve_none_(self, retriever: type(None), /):
        '''Returns what the user has asked for: nothing!'''
        return None

    def _retrieve_contains_(self, retriever: object, /) -> type(None):
        '''Returns the element if this chora contains it.'''
        raise KeyError(f"Element {retriever} not in {repr(self)}.")

    @classmethod
    def _get_chora_rawmeths(cls, /):
        prefixes = cls.PREFIXES
        out = dict()
        for attr in dir(cls):
            for prefix in prefixes:
                if attr.startswith(f"_{prefix}_"):
                    out[attr] = getattr(cls, attr)
                    break
        return out

    @classmethod
    def _get_defkws(cls, tovals=None, /):
        if tovals is None:
            tovals = _itertools.repeat('passfn')
        return ', '.join(map(
            '='.join,
            zip(cls.PREFIXES, tovals)
            ))

    @classmethod
    def _wrap_chora_meth(cls, name, meth, /):

        prefix = name.split('_')[0]
        defkws = cls._get_defkws()
        params = tuple(_inspect.signature(meth).parameters.values())[1:]
        argstrn = ', '.join(
            param.name for param in params if param.kind.value == 0
            )

        exec('\n'.join((
            f"@_functools.wraps(meth)",
            f"def {name}(self, /, {argstrn}, meth=meth, {defkws}):",
            f"    return {prefix}(meth(self, {argstrn}))",
            )))

        wrapper = eval(name)
        wrapper.raw = meth

        return wrapper

    @classmethod
    def _get_chora_meths(cls, /):
        return {
            (name := methname.strip('_')):
                cls._wrap_chora_meth(name, meth)
            for methname, meth in cls.chorarawmeths.items()
            }

    @classmethod
    def _yield_getmeths(cls, /):
        for meth in cls.chorameths.values():
            hint = tuple(
                val for key, val in meth.__annotations__.items()
                if key != 'return'
                )
            yield hint, meth

    @classmethod
    def _get_getmeths(cls, /):
        return _MultiTypeMap(cls._yield_getmeths())

    @classmethod
    def _get_getitem(cls, /):
        defkws = cls._get_defkws()
        passkws = cls._get_defkws(cls.PREFIXES)
        exec('\n'.join((
            f"def __getitem__(self, /, *args, {defkws}):",
            f"    return self.getmeths[tuple(map(type, args))](",
            f"        self, *args, {passkws}",
            f"        )",
            )))
        return eval('__getitem__')

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.chorarawmeths = cls._get_chora_rawmeths()
        chorameths = cls.chorameths = cls._get_chora_meths()
        for name, meth in chorameths.items():
            setattr(cls, name, meth)
        cls.getmeths = cls._get_getmeths()
        cls.primetype = cls._retrieve_contains_.__annotations__['return']
        cls.__getitem__ = cls._get_getitem()

    def __getitem__(self, arg, /):
        '''Placeholder for dynamically generated __getitem__.'''
        raise TypeError

    def __contains__(self, arg, /):
        if isinstance(arg, self.primetype):
            try:
                val = self._retrieve_contains_(arg)
                return True
            except KeyError:
                return False

#     def new_self(self, *args, cls=None, **kwargs):
#         return (type(self) if cls is None else cls)(
#             *overprint(_itertools.zip_longest(self.args, args)),
#             **(self.kwargs | kwargs),
#             )


class Sliceable(Chora):

    def _incise_slice_(self, incisor: slice, /):
        slcargs = (incisor.start, incisor.stop, incisor.step)
        meth = self.slcmeths[tuple(map(type, slcargs))].raw
        return meth(self, *slcargs)

    def _incise_slice_trivial_(self,
            start: type(None), stop: type(None), step: type(None), /
            ):
        '''Captures the special behaviour implied by `self[:]`.'''
        return self


class ChoraDeferrer:

    __slots__ = ('methname',)

    def __set_name__(self, owner, methname, /):
        self.methname = methname

    def __get__(self, obj, objtype=None, /):
        meth = getattr(obj.chora, self.methname)
        return _functools.partial(meth, caller=obj)


class Incisable(_Aspect):
    '''
    Incisable objects are said to 'contain space'
    because they own a Chora instance
    and point their __getitem__ and __contains__ methods to it.
    '''

    _req_slots__ = ('chora',)

    Chora = Chora

    @classmethod
    def _defer_chora_methods(cls, /):
        for attr in dir(cls.Chora):
            for prefix in ('incise_', 'retrieve_'):
                if attr.startswith(prefix):
                    setattr(cls, attr, ChoraDeferrer())
                    break

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls._defer_chora_methods()

    def _make_chora_(self, /):
        return self.Chora()

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chora = self._make_chora_()

    def __getitem__(self, arg, /):
        return self.chora.__getitem__(arg, caller=self.__getattr__)

    def __contains__(self, arg, /):
        return self.chora.__contains__(arg)


###############################################################################


# from everest.ptolemaic.compound import Compound
# from everest.ptolemaic.sprite import Sprite


# class MyChora(Sprite, Chora):

#     _req_slots__ = ('length',)

#     def __init__(self, length: int = 0, /):
#         self.length = int(length)
#         super().__init__()

#     def __contains__(self, arg, /):
#         if isinstance(arg, int):
#             return 0 <= arg <= self.length


# class MyIncisable(Incisable, Compound):

#     _req_slots__ = ('content',)

#     Chora = MyChora

#     def retrieve(self, retriever, /):
#         return self.content[retriever]

#     def incise(self, incisor, /):
#         return self.content[incisor]

#     def __init__(self, content, /):
#         self.content = content
#         super().__init__()

#     def _make_chora_(self, /):
#         return self.Chora(len(self.content))


###############################################################################
