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


def get_session():
    return _CURRENTFOCUS.session

def get_bureau():
    return get_session().bureau

def get_drawer(requester, /):
    return _CURRENTFOCUS.get_drawer(requester)

def get_taphonomy():
    return get_session().taphonomy


class OpenDrawer:

    __slots__ = ('__weakref__', 'drawer')

    def __init__(self, drawer, /):
        object.__setattr__(self, 'drawer', drawer)

    def __getattr__(self, name, /):
        return getattr(object.__getattribute__(self, 'drawer'), name)

    def __setattr__(self, name, val, /):
        return setattr(object.__getattribute__(self, 'drawer'), name, val)

    def __delattr__(self, name, val, /):
        return delattr(object.__getattribute__(self, 'drawer'), name)

    def __repr__(self, /):
        return (
            f"<"
            f"{type(self).__qualname__} {id(self)} "
            f"of {object.__getattribute__(self, 'drawer')}"
            f">"
            )


class Drawer(_SimpleNamespace):

    __slots__ = ('__weakref__', '_cabinet', '_owner')

    def __init__(self, cabinet, owner, /):
        self._cabinet = _weakref.ref(cabinet)
        self._owner = _weakref.ref(owner)

    @property
    def cabinet(self, /):
        return self._cabinet()

    @property
    def owner(self, /):
        return self._owner()

    def open_(self, /):
        return OpenDrawer(self)

    def __repr__(self, /):
        return (
            f"<"
            f"{type(self).__qualname__} "
            f"{id(self)} of {self.cabinet} "
            f"owned by {self.owner}"
            f">"
            )


class Cabinet:

    __slots__ = ('__weakref__', '_host', '_data',)

    def __init__(self, host, /):
        self._host = _weakref.ref(host)
        self._data = _weakref.WeakKeyDictionary()

    @property
    def host(self, /):
        return self._host()

    @property
    def data(self, /):
        return _MappingProxyType(self._data)

    def new(self, requester, /):
        return Drawer(self, requester)

    def __getitem__(self, requester, /):
        try:
            drawer = self._data[requester]
        except KeyError:
            drawer = self._data[requester] = self.new(requester)
        return drawer.open_()

    def __repr__(self, /):
        return (
            f"<"
            f"{type(self).__qualname__} "
            f"{id(self)} of {self.host} "
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

    __slots__ = ('__weakref__', '_session', '_opendrawers')

    _SESSIONS = _deque([None,])

    def __new__(cls, session=None, /):
        if session is not None:
            cls._SESSIONS.append(session)
        obj = super().__new__(cls)
        obj._session = cls.SESSIONS[-1]
        obj._opendrawers = _weakref.WeakKeyDictionary()
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
    def opendrawers(self, /):
        return _MappingProxyType(self._opendrawers)

    def get_drawer(self, requester, /):
        opendrawer = self._opendrawers[requester] = \
            self.session.bureau.cabinet[requester]
        return opendrawer

    def __repr__(self, /):
        return f"<_Focus_ {id(self)} of {self.session}>"


class Session:

    __slots__ = ('__weakref__', '_bureau')

    def __init__(self, bureau, /):
        self._bureau = bureau

    @property
    def bureau(self, /):
        return self._bureau

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


class Bureau:

    __slots__ = (
        '__weakref__',
        '_cabinet', '_name', '_taphonomy', '_currentsession',
        )

    def __init__(self, name: str, /):
        self._name = name
        self._cabinet = Cabinet(self)
        self._taphonomy = _Taphonomy()
        self._currentsession = None

    @property
    def name(self, /):
        return self._name

    @property
    def cabinet(self, /):
        return self._cabinet

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