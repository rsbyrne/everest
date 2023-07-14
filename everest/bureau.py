###############################################################################
''''''
###############################################################################


import weakref as _weakref
from types import (
    MappingProxyType as _MappingProxyType,
    SimpleNamespace as _SimpleNamespace,
    )
from collections import deque as _deque

from everest.epitaph import Taphonomy as _Taphonomy
from everest.utilities import pretty as _pretty


class OpenStorer:

    __slots__ = ('__weakref__', 'storer')

    def __init__(self, storer, /):
        super().__init__()
        self.storer = _weakref.proxy(storer)

    for methname in (
            '__getitem__', '__iter__', '__len__',
            '__contains__', 'keys', 'items', 'values',
            'get', '__eq__', '__ne__',
            '__setitem__', '__delitem__',
            'pop', 'popitem', 'clear', 'update', 'setdefault',
            ):
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self.storer.{methname}",
            )))
    del methname

    def __repr__(self, /):
        return (
            f"<"
            f"{type(self).__qualname__} {id(self)} "
            f"of {self.storer}"
            f">"
            )

    def _repr_pretty_(self, p, cycle, /):
        return _pretty.pretty_dict(self, p, cycle, root=repr(self))


class Storer(dict):

    def __init__(self, /):
        super().__init__()

    def __repr__(self, /):
        return (
            f"<"
            f"{type(self).__qualname__} "
            f"{id(self)}"
            f">"
            )

    def _repr_pretty_(self, p, cycle, /):
        return _pretty.pretty_dict(self, p, cycle, root=repr(self))


class Cabinet(_weakref.WeakKeyDictionary):

    def __init__(self, /):
        super().__init__()

    def __getitem__(self, requester, /):
        try:
            storer = super().__getitem__(requester)
        except KeyError:
            storer = Storer()
            super().__setitem__(requester, storer)
        assert requester in self, (requester, tuple(self))
        return OpenStorer(storer)

    for methname in ('__setitem__', 'setdefault', 'update'):
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    raise AttributeError",
            )))
    del methname

    def __repr__(self, /):
        return (
            f"<"
            f"{type(self).__qualname__} "
            f"{id(self)}"
            f">"
            )

    def _repr_pretty_(self, p, cycle, /):
        return _pretty.pretty_dict(self, p, cycle, root=repr(self))


class _FocusMeta_(type):

    @property
    def SESSIONS(cls, /):
        return tuple(cls._SESSIONS)

    @property
    def scratch(cls, /):
        return cls._scratch


class FocusProxy:

    def __getattribute__(self, name, /):
        return getattr(_Focus_._instance, name)

    @property
    def __setattr__(self, /):
        raise AttributeError

    @property
    def __delattr__(self, /):
        raise AttributeError


FOCUS = FocusProxy()


class _Focus_(metaclass=_FocusMeta_):

    __slots__ = ('__weakref__', 'session')

    _SESSIONS = _deque([None,])
    _sessionopenstorers = _weakref.WeakKeyDictionary()
    _bureauopenstorers = _weakref.WeakKeyDictionary()

    def __new__(cls, session=None, /):
        sessions = cls._SESSIONS
        if session is not None:
            sessions.append(session)
        obj = super().__new__(cls)
        obj.session = sessions[-1]
        try:
            currentfocus = cls._instance
        except AttributeError:
            pass
        else:
            ref = _weakref.ref(currentfocus)
            del cls._instance, currentfocus
            if ref() is not None:
                raise RuntimeError
        cls._instance = obj

    @classmethod
    def revert_to_previous_session(cls, /):
        _ = cls._SESSIONS.pop()
        cls()

    @property
    def bureau(self, /):
        return self.session.bureau

    def request_session_storer(self, requester, /):
        out = self._sessionopenstorers[requester] = self.session[requester]
        return out

    def request_bureau_storer(self, requester, /):
        out = self._bureauopenstorers[requester] = self.bureau[requester]
        return out

    def __repr__(self, /):
        return f"<_Focus_ {id(self)} of {self.session}>"

    def __del__(self, /):
        self._sessionopenstorers.clear()
        self._bureauopenstorers.clear()


class Session(Cabinet):

    def __init__(self, bureau, /):
        super().__init__()
        self.bureau = bureau

    @property
    def entered(self, /):
        return _Focus_.SESSIONS[-1] is self

    def __enter__(self, /):
        if self.entered:
            raise RuntimeError("Cannot enter already entered session.")
        _Focus_(self)
        return self

    def __exit__(self, /, *_):
        if not self.entered:
            raise RuntimeError("Cannot exit non-entered session.")
        _Focus_.revert_to_previous_session()

    def __hash__(self, /):
        return id(self)

    def __repr__(self, /):
        return f"<Session {hash(self)} of {self.bureau}>"

    def _repr_pretty_(self, p, cycle, /):
        return _pretty.pretty_dict(self, p, cycle, root=repr(self))


class Bureau(Cabinet):

    __slots__ = (
        '_name', '_taphonomy', '_currentsession',
        )

    def __init__(self, name: str, /):
        super().__init__()
        self._name = name
        self._taphonomy = _Taphonomy()
        self._currentsession = None

    @property
    def name(self, /):
        return self._name

    @property
    def taphonomy(self, /):
        return self._taphonomy

    @property
    def currentsession(self, /):
        return self._currentsession

    @property
    def entered(self, /):
        return self._currentsession is not None

    def __enter__(self, /):
        if self.entered:
            raise RuntimeError("Cannot enter already entered session.")
        session = self._currentsession = Session(self)
        session.__enter__()
        return self

    def __exit__(self, /, *_):
        if not self.entered:
            raise RuntimeError("Cannot exit non-entered session.")
        session = self._currentsession
        session.__exit__()
        self._currentsession = None

    def __repr__(self, /):
        return f"Bureau({self.name})"

    def _repr_pretty_(self, p, cycle, /):
        return _pretty.pretty_dict(self, p, cycle, root=repr(self))


_GLOBALBUREAU = Bureau('GLOBAL').__enter__()


def get_globalbureau():
    return _GLOBALBUREAU

def get_globalsession():
    return _GLOBALBUREAU.currentsession


###############################################################################
###############################################################################


#     @property
#     def state(self, /):
#         return self._state

#     @state.setter
#     def state(self, val: int, /):
#         '''0: Ready, 1: Active, 2: Dormant, 3: Retired'''
#         self._state = int(val)

#     @property
#     def ready(self, /):
#         return self.state == 0

#     @property
#     def active(self, /):
#         return self.state == 1

#     @property
#     def dormant(self, /):
#         return self.state == 2

#     @property
#     def retired(self, /):
#         return self.state == 3

#     def activate(self, /):
#         if not self.ready:
#             raise RuntimeError("Cannot enter previously entered bureau.")
#         global ACTIVESESSION
#         former = self._former = ACTIVESESSION
#         if isinstance(former, State):
#             former.suspend()
#         ACTIVESESSION = self
#         self.state = 1  # Active

#     def suspend(self, /):
#         if not self.active:
#             raise RuntimeError("Cannot suspend inactive bureau.")
#         self.state = 2  # Dormant

#     def revive(self, /):
#         if not self.dormant:
#             raise RuntimeError("Cannot suspend non-dormant bureau.")
#         self.state = 1  # Active

#     def deactivate(self, /):
#         if not self.active:
#             raise RuntimeError("Cannot deactivate inactive bureau.")
#         self.state = 3  # Retired