###############################################################################
''''''
###############################################################################


import collections as _collections
from collections import abc as _collabc
import itertools as _itertools
import functools as _functools

from everest.utilities import TypeMap as _TypeMap
from everest.utilities import caching as _caching
from everest.ptolemaic.aspect import Aspect as _Aspect
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic


def not_none(a, b):
    return b if a is None else a


overprint = _functools.partial(_itertools.starmap, not_none)


def passfn(obj, arg, /):
    return arg


class DEFAULTCALLER:

    @classmethod
    def retrieve(cls, retriever, /):
        return retriever

    @classmethod
    def incise(cls, incisor, /):
        return incisor


class Chora(_Ptolemaic):
    '''
    The Chora is Everest's abstract master representation
    of the concept of space.
    Objects may be said to 'contain space'
    if they have a Chora instance as an attribute
    and defer their __getitem__ and __contains__ methods towards it.
    '''

    def _retrieve_trivial_(self, incisor, /):
        '''Returns the element if this chora contains it.'''
        if self.__contains__(incisor):
            return incisor
        raise KeyError(f"Element {incisor} not in {self}.")

    def _retrieve_none_(self, incisor: type(None), /):
        '''Returns what the user has asked for: nothing!'''
        return None

    def _incise_tuple_(self, incisor: tuple, /):
        '''Captures the special behaviour implied by `self[a,b,c...]`'''
        raise TypeError("Tuple slicing not supported.")

    def _incise_trivial_(self, incisor: type(Ellipsis) = None, /):
        '''Captures the special behaviour implied by `self[...]`.'''
        return self

    @staticmethod
    def _generic_retrieve(meth, chora, incisor, caller, /):
        return caller.retrieve(meth(chora, incisor))

    @staticmethod
    def _generic_incise(meth, chora, incisor, caller, /):
        return caller.incise(meth(chora, incisor))

    @classmethod
    def _wrap_methods(cls, /):
        for attr in dir(cls):
            for prefix in ('_incise_', '_retrieve_'):
                if attr.startswith(prefix):
                    newmeth = _functools.partial(
                        getattr(cls, f"_generic_{prefix.strip('_')}"),
                        getattr(cls, attr),
                        )
                    setattr(cls, attr.strip('_'), newmeth)
                    break

    @classmethod
    def _incision_methods(cls, /):
        '''Returns acceptable incisor types and their associated getmeths.'''
        return
        yield

    @classmethod
    def _priority_incision_methods(cls, /):
        '''Returns like `.incision_methods` but takes priority.'''
        yield tuple, cls.incise_tuple
        yield type(Ellipsis), cls.incise_trivial

    @classmethod
    def _retrieval_methods(cls, /):
        '''Returns acceptable retriever types and their associated getmeths.'''
        yield object, cls.retrieve_trivial

    @classmethod
    def _priority_retrieval_methods(cls, /):
        '''Returns like `.retrieval_methods` but takes priority.'''
        yield type(None), cls.retrieve_none

    @classmethod
    def _get_incision_meths(cls, /) -> _TypeMap:
        return _TypeMap(_itertools.chain(
            cls._priority_incision_methods(),
            cls._incision_methods()
            ))

    @classmethod
    def _get_retrieval_meths(cls, /) -> _TypeMap:
        return _TypeMap(_itertools.chain(
            cls._priority_retrieval_methods(),
            cls._retrieval_methods()
            ))

    @classmethod
    def _get_getmeths(cls, /) -> callable:
        retmeths = cls.retmeths = cls._get_retrieval_meths()
        incmeths = cls.incmeths = cls._get_incision_meths()
        getmeths = cls.getmeths = _collections.ChainMap(retmeths, incmeths)
        return getmeths.__getitem__

    @classmethod
    def _get_getitem(cls, /):

        def __getitem__(
                chora, incisor, /, *,
                caller=DEFAULTCALLER, getmeths=cls._get_getmeths(),
                ):
            try:
                meth = getmeths(type(incisor))
            except Exception as exc:
                raise TypeError from exc
            return meth(chora, incisor, caller)

        return __getitem__

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls._wrap_methods()
        cls.__getitem__ = cls._get_getitem()

    def __getitem__(self, arg, /):
        '''Placeholder for dynamically generated __getitem__.'''
        raise NotImplementedError

    def __contains__(self, arg, /):
        return False

    def new_self(self, *args, cls=None, **kwargs):
        return (type(self) if cls is None else cls)(
            *overprint(_itertools.zip_longest(self.args, args)),
            **(self.kwargs | kwargs),
            )


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

    def retrieve(self, retriever, /):
        raise NotImplementedError

    def incise(self, incisor, /):
        raise NotImplementedError

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
        return self.chora.__getitem__(arg, caller=self)

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
