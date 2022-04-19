###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc
import types as _types

from everest.utilities import (
    caching as _caching,
    pretty as _pretty,
    )

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite

from .chora import (
    Choric as _Choric,
    Sampleable as _Sampleable,
    Null as _Null,
    )
from .fundament import Fundament as _Fundament
from .predicate import Predicate as _Predicate


def get_index_iterable(func, /):
    def index_iterable(it, /):
        for i, val in enumerate(it):
            if func(val):
                return i
        raise ValueError(val)
    return index_iterable


class Index(_Fundament):


    MROCLASSES = ('Form', 'Arbitrary', 'Slyce')

    memberspace = object

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.register(cls.Form)

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.Arbitrary(*args, **kwargs)


    class Form(_Choric):

        @_abc.abstractmethod
        def __incise_retrieve__(self, /):
            raise NotImplementedError

        @_abc.abstractmethod
        def __incise_contains__(self, /):
            raise NotImplementedError

        @_abc.abstractmethod
        def __incise_length__(self, /):
            raise NotImplementedError

        @_abc.abstractmethod
        def __incise_iter__(self, /):
            raise NotImplementedError

        @property
        @_abc.abstractmethod
        def arrayquery(self, /):
            raise NotImplementedError


        class __choret__(_Sampleable):

            def slyce_predicate(self, incisor: _Predicate, /):
                return (bound := self.bound).Slyce.Predicated(bound, incisor)

            def slyce_callable(self, incisor: _collabc.Callable, /):
                return self.slyce_predicate(_Predicate(incisor))

            def retrieve_member(self, incisor: 'owner.owner.memberspace', /):
                return incisor


    class Arbitrary(metaclass=_Sprite):

        OVERCLASSES = ('Form',)

        content: tuple

        @classmethod
        def __class_call__(cls, content):
            return super().__class_call__(tuple(content))

        @_caching.soft_cache()
        def asdict(self, /):
            return _types.MappingProxyType(dict(zip(
                content := self.content, range(len(content))
                )))

        @property
        def __incise_retrieve__(self, /):
            return self.asdict().__getitem__

        @property
        def __incise_contains__(self, /):
            return self.asdict().__contains__

        def __incise_length__(self, /):
            return len(self.asdict())

        def __incise_iter__(self, /):
            return iter(self.asdict())

        @property
        def arrayquery(self, /):
            return self.content

        def _repr_pretty_(self, p, cycle, root=None):
            if root is None:
                root = self._ptolemaic_class__.__qualname__
            _pretty.pretty(self.content, p, cycle, root=root)


    class Slyce(metaclass=_Essence):

        OVERCLASSES = ('Form',)


    class Predicated(metaclass=_Sprite):

        OVERCLASSES = ('Slyce',)

        source: 'Index'
        predicate: _Predicate

        @_caching.soft_cache()
        def asdict(self, /):
            return _types.MappingProxyType({
                key: val for key, val in self.source.asdict().items()
                if self.predicate(key)
                })

        @property
        @_caching.soft_cache()
        def content(self, /):
            return tuple(self.asdict().values())

        @property
        def __incise_retrieve__(self, /):
            return self.asdict().__getitem__

        @property
        def __incise_contains__(self, /):
            return self.asdict().__contains__

        def __incise_length__(self, /):
            return len(self.asdict())

        def __incise_iter__(self, /):
            return iter(self.asdict())

        @property
        def arrayquery(self, /):
            return self.content


###############################################################################
###############################################################################
