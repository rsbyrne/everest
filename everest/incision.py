###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import deque as _deque
from collections import abc as _collabc
import inspect as _inspect
import collections as _collections

from everest.utilities import (
    Null as _Null, FrozenNamespace as _FrozenNamespace
    )

from everest.exceptions import (
    IncisionException,
    IncisorTypeException,
    )


class Degenerate(metaclass=_abc.ABCMeta):

    __slots__ = ('subject', 'incisor')

    def __init__(self, subject, incisor, /):
        self.subject, self.incisor = subject, incisor

    def __repr__(self, /):
        return f"{type(self).__name__}({self.subject}, {self.incisor})"


class Empty(metaclass=_abc.ABCMeta):

    __slots__ = ('subject',)

    def __init__(self, subject, /):
        self.subject, self.incisor = subject

    def __repr__(self, /):
        return f"{type(self).__name__}({self.subject})"


HANDLERMETHS = (
    '__incise__',
    '__incise_trivial__', '__incise_slyce__', '__incise_retrieve__',
    '__incise_degenerate__', '__incise_empty__', '__incise_fail__',
    )


class IncisionHandler(metaclass=_abc.ABCMeta):

    __slots__ = ()

    def __incise_trivial__(self, /):
        return self

    def __incise_slyce__(self, incisor, /):
        return incisor

    def __incise_retrieve__(self, incisor, /):
        return incisor

    def __incise_degenerate__(self, incisor, /):
        return Degenerate(self, incisor)

    def __incise_empty__(self, /):
        return Empty(self)

    def __incise_fail__(self, incisor, message=None, /):
        if isinstance(message, Exception):
            raise IncisorTypeException(incisor, self) from message
        raise IncisorTypeException(incisor, self, message)


COLLECTIONLIKEMETHS = ('__contains__', '__len__', '__iter__', '__includes__')
INCISABLEMETHS = (
    '__incise__', '__chain_incise__', '__getitem__',
    *HANDLERMETHS, *COLLECTIONLIKEMETHS
    )


class Incisable(IncisionHandler):

    __slots__ = ()

    @_abc.abstractmethod
    def __contains__(self, arg, /):
        raise NotImplementedError

    # @_abc.abstractmethod
    def __len__(self, /):
        raise NotImplementedError

    def __iter__(self, /):
        raise NotImplementedError

    @_abc.abstractmethod
    def __includes__(self, /):
        raise NotImplementedError

    @_abc.abstractmethod
    def __incise__(self, arg, /, *, caller):
        raise NotImplementedError

    @property
    def __incision_chain__(self, /):
        return IncisionChain

    def __chain_incise__(self, caller, arg, /):
        if isinstance(caller, tuple):
            caller = self.__incision_chain__(self, *caller)
        else:
            caller = self.__incision_chain__(self, caller)
        return self.__incise__(arg, caller=caller)

    def __getitem__(self, arg, /):
        return self.__incise__(arg, caller=self)


class IncisionChain(Incisable):

    __slots__ = (
        'incisables', '_incise_meth', '_retrievemeths', '_slycemeths',
        '_degenretrievemeths', 'last',
        )

    def __init__(self, /, *incisables, **methods):
        super().__init__()
        if methods:
            incisables = (_FrozenNamespace(**methods), *incisables)
        self.incisables = incisables
        self.last = incisables[-1]

    @property
    def __incise__(self, /):
        try:
            return self._incise_meth
        except AttributeError:
            for inc in self.incisables:
                try:
                    meth = inc.__incise__
                except AttributeError:
                    continue
                break
            else:
                meth = self.__incise_fail__
            self._incise_meth = meth
            return meth

    @property
    def slycemeths(self, /):
        try:
            return self._slycemeths
        except AttributeError:
            out = _deque()
            for obj in self.incisables:
                try:
                    meth = obj.__incise_slyce__
                except AttributeError:
                    continue
                out.append(meth)
            out = self._slycemeths = tuple(out)
            return out

    def __incise_slyce__(self, incisor, /):
        for meth in self.slycemeths:
            incisor = meth(incisor)
        return incisor

    @property
    def retrievemeths(self, /):
        try:
            return self._retrievemeths
        except AttributeError:
            out = _deque()
            for obj in self.incisables:
                try:
                    meth = obj.__incise_retrieve__
                except AttributeError:
                    continue
                out.append(meth)
            out = self._retrievemeths = tuple(out)
            return out

    def __incise_retrieve__(self, incisor, /):
        for meth in self.retrievemeths:
            incisor = meth(incisor)
        return incisor

    def __incise_degenerate__(self, incisor, /):
        return self.last.__incise_degenerate__(
            self.__incise_retrieve__(incisor)
            )

    for methname in (
            '__incise_trivial__', '__incise_empty__', '__incise_fail__',
            *COLLECTIONLIKEMETHS,
            ):
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self.last.{methname}",
            )))
    del methname

    def __repr__(self, /):
        return f"{type(self)}{self.incisables}"


class DeferIncisable(Incisable):

    __slots__ = ()

    @property
    @_abc.abstractmethod
    def __incision_manager__(self, /) -> Incisable:
        raise NotImplementedError

    for methname in INCISABLEMETHS:
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    try:",
            f"        return self.__incision_manager__.{methname}",
            f"    except AttributeError:",
            f"        raise NotImplementedError",
            )))
    del methname


class ChainIncisable(Incisable):

    __slots__ = ()

    @property
    @_abc.abstractmethod
    def __incision_manager__(self, /) -> Incisable:
        raise NotImplementedError

    for methname in COLLECTIONLIKEMETHS:
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    try:",
            f"        return self.__incision_manager__.{methname}",
            f"    except AttributeError:",
            f"        raise NotImplementedError",
            )))
    del methname

    def __incise__(self, incisor, /, *, caller):
        return self.__incision_manager__.__chain_incise__(caller, incisor)

    def __chain_incise__(self, caller, incisor, /):
        if isinstance(caller, tuple):
            caller = (self, *caller)
        else:
            caller = (self, caller)
        return self.__incision_manager__.__chain_incise__(caller, incisor)


class Degenerator(ChainIncisable):

    __slots__ = ('subject',)

    def __init__(self, subject, /):
        self.subject = subject

    @property
    def __incision_manager__(self, /):
        return self.subject

    @property
    def __incise_trivial__(self, /):
        return self.subject.__incise_trivial__

    @property
    def __incise_retrieve__(self, /):
        return self.subject.__incise_degenerate__

    def __repr__(self, /):
        return f"{type(self).__name__}({self.subject})"


###############################################################################
###############################################################################


# class IncisionProtocol(_Protocol):

#     # Mandatory:
#     INCISE = ('__incise__', True)
#     TRIVIAL = ('__incise_trivial__', True)
#     SLYCE = ('__incise_slyce__', True)
#     RETRIEVE = ('__incise_retrieve__', True)
#     FAIL = ('__incise_fail__', True)
#     DEGENERATE = ('__incise_degenerate__', True)
#     EMPTY = ('__incise_empty__', True)

#     # Optional:

#     CONTAINS = ('__incise_contains__', False)
#     INCLUDES = ('__incise_includes__', False)
#     LENGTH = ('__incise_length__', False)
#     ITER = ('__incise_iter__', False)
#     INDEX = ('__incise_index__', False)
#     DEFER = ('__incision_manager__', False)

#     def exc(self, obj, /):
#         return IncisionProtocolException(self, obj)
