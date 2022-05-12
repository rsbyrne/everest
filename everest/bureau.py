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


_CURRENTFOCUS = None


def get_current_session():
    return _CURRENTFOCUS.session

def get_current_bureau():
    return _CURRENTFOCUS.bureau

def request_tab(requester, /):
    return _CURRENTFOCUS.request_tab(requester)

def request_tray(requester, /):
    return _CURRENTFOCUS.request_tray(requester)

def request_drawer(requester, /):
    return _CURRENTFOCUS.request_drawer(requester)

def get_taphonomy():
    return get_session().taphonomy


class OpenStorer:

    __slots__ = ('__weakref__', 'storer')

    def __init__(self, storer, /):
        object.__setattr__(self, 'storer', storer)

    def __getattr__(self, name, /):
        return getattr(object.__getattribute__(self, 'storer'), name)

    def __setattr__(self, name, val, /):
        return setattr(object.__getattribute__(self, 'storer'), name, val)

    def __delattr__(self, name, val, /):
        return delattr(object.__getattribute__(self, 'storer'), name)

    def __repr__(self, /):
        return (
            f"<"
            f"{type(self).__qualname__} {id(self)} "
            f"of {object.__getattribute__(self, 'storer')}"
            f">"
            )


class Storer(_SimpleNamespace):

    __slots__ = ('__weakref__',)

    def __init__(self, /):
        super().__init__()

    def __repr__(self, /):
        return (
            f"<"
            f"{type(self).__qualname__} "
            f"{id(self)}"
            f">"
            )


class MultiStorer(_weakref.WeakKeyDictionary):

    def __init__(self, /):
        super().__init__()

    def __getitem__(self, requester, /):
        try:
            storer = super().__getitem__(requester)
        except KeyError:
            storer = Storer()
            super().__setitem__(requester, storer)
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


class _FocusMeta_(type):

    @property
    def SESSIONS(cls, /):
        return tuple(cls._SESSIONS)

    @property
    def scratch(cls, /):
        return cls._scratch


class _Focus_(metaclass=_FocusMeta_):

    __slots__ = ('__weakref__', '_session')

    _SESSIONS = _deque([None,])

    _tabs = MultiStorer()
    _stuff = _deque()

    def __new__(cls, session=None, /):
        if session is not None:
            cls._SESSIONS.append(session)
        obj = super().__new__(cls)
        obj._session = cls.SESSIONS[-1]
        global _CURRENTFOCUS
        if _CURRENTFOCUS is not None:
            ref = _weakref.ref(_CURRENTFOCUS)
            del _CURRENTFOCUS
            if ref() is not None:
                raise RuntimeError
        _CURRENTFOCUS = obj

    @classmethod
    def revert_to_previous_session(cls, /):
        _ = cls._SESSIONS.pop()
        cls()

    @property
    def session(self, /):
        return self._session

    @property
    def bureau(self, /):
        return self.session.bureau

    @property
    def tabs(self, /):
        return type(self)._tabs

    def request_tab(self, requester, /):
        obj = self.tabs[requester]
        self._stuff.append(obj)
        return obj

    def request_tray(self, requester, /):
        obj = self.session.trays[requester]
        self._stuff.append(obj)
        return obj

    def request_drawer(self, requester, /):
        obj = self.bureau.drawers[requester]
        self._stuff.append(obj)
        return obj

    def __repr__(self, /):
        return f"<_Focus_ {id(self)} of {self.session}>"

    def __del__(self, /):
        self._tabs.clear()
        self._stuff.clear()


class Session:

    __slots__ = ('__weakref__', '_bureau', '_trays')

    def __init__(self, bureau, /):
        self._bureau = bureau
        self._trays = MultiStorer()

    @property
    def bureau(self, /):
        return self._bureau

    @property
    def trays(self, /):
        return self._trays

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

    def __del__(self, /):
        self._trays.clear()


class Bureau:

    __slots__ = (
        '__weakref__',
        '_drawers', '_name', '_taphonomy', '_currentsession',
        )

    def __init__(self, name: str, /):
        self._name = name
        self._drawers = MultiStorer()
        self._taphonomy = _Taphonomy()
        self._currentsession = None

    @property
    def name(self, /):
        return self._name

    @property
    def drawers(self, /):
        return self._drawers

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

    def __del__(self, /):
        self._drawers.clear()


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