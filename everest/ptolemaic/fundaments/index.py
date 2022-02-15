###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc
import types as _types

from everest.utilities import caching as _caching

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.chora import (
    Choric as _Choric,
    Sampleable as _Sampleable,
    Null as _Null,
    )

from everest.ptolemaic.fundaments.fundament import Fundament as _Fundament
from everest.ptolemaic.fundaments.predicate import Predicate as _Predicate


def get_index_iterable(func, /):
    def index_iterable(it, /):
        for i, val in enumerate(it):
            if func(val):
                return i
        raise ValueError(val)
    return index_iterable


class Index(_Fundament, _Choric, metaclass=_Essence):


    SUBCLASSES = ('Arbitrary', 'Slyce')

    memberspace = object

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.Arbitrary(*args, **kwargs)

    @property
    @_abc.abstractmethod
    def indexdict(self, /) -> _types.MappingProxyType:
        raise NotImplementedError

    @property
    def index(self, /):
        return self.indexdict.__getitem__

    def __incise_iter__(self, /):
        return iter(self.indexdict)

    def __incise_contains__(self, /):
        return self.indexdict.__contains__

    def __incise_length__(self, /):
        return len(self.indexdict)

    class __choret__(_Sampleable):

        def slyce_predicate(self, incisor: _Predicate, /):
            return (bound := self.bound).Slyce.Predicated(bound, incisor)

        def slyce_callable(self, incisor: _collabc.Callable, /):
            return self.slyce_predicate(_Predicate(incisor))

        def retrieve_index(self, incisor: 'owner.memberspace', /):
            return self.bound.index(incisor)


    class Arbitrary(metaclass=_Sprite):

        content: tuple

        @classmethod
        def __class_call__(cls, content):
            return super().__class_call__(tuple(content))

        @property
        @_caching.soft_cache()
        def indexdict(self, /):
            return _types.MappingProxyType(dict(zip(
                content := self.content, range(len(content))
                )))
            # return _types.MappingProxyType(dict(zip(*map(
            #     reversed, (content := self.content, range(len(content)))
            #     ))))


    class Slyce(metaclass=_Essence):

        SUBCLASSES = ('Predicated',)


        class Predicated(metaclass=_Sprite):

            source: 'Index'
            predicate: _Predicate

            @property
            @_caching.soft_cache()
            def indexdict(self, /):
                return _types.MappingProxyType({
                    key: val for key, val in self.source.indexdict.items()
                    if self.predicate(key)
                    })

#     class __choret__(metaclass=_Essence):

#         def slyce_predicate(self, incisor: _Null, /):
#             raise NotImplementedError


###############################################################################
###############################################################################
