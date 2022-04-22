###############################################################################
''''''
###############################################################################


import weakref as _weakref
from types import (
    MappingProxyType as _MappingProxyType,
    SimpleNamespace as _SimpleNamespace,
    )
import time as _time

from everest.utilities import reseed as _reseed


class BureauMeta(type):

    @property
    def current(cls, /):
        return cls._current

    @current.setter
    def current(cls, val, /):
        cls._current = val

    @property
    def session(cls, /):
        return cls.current.session


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
        return f"{object.__getattribute__(self, 'drawer')}.opened"


class Drawer(_SimpleNamespace):

    opened = property(OpenDrawer)


class Drawers(_weakref.WeakKeyDictionary):

    __slots__ = ('_data',)

    def __init__(self, /):
        self._data = _weakref.WeakKeyDictionary()

    @property
    def data(self, /):
        return _MappingProxyType(self._data)

    def __getitem__(self, name, /):
        try:
            drawer = self._data[name]
        except KeyError:
            drawer = self._data[name] = Drawer()
        return drawer.opened


class Session:

    __slots__ = ('_active', '_hashint', '_bureau', '_data')

    def __init__(self, bureau, /):
        self._active = True
        self._hashint = _reseed.rdigits(16)
        self._bureau = bureau
        self._data = _weakref.WeakKeyDictionary()

    def __hash__(self, /):
        return self._hashint

    @property
    def active(self, /):
        return self._active

    @property
    def data(self, /):
        return _MappingProxyType(self._data)

    def __getitem__(self, name, /):
        try:
            drawer = self._data[name]
        except KeyError as exc:
            drawer = self._data[name] = self._bureau.drawers[name]
        return drawer

    @property
    def bureau(self, /):
        return self._bureau

    def close(self, /):
        if not self.active:
            raise RuntimeError("Cannot close already-closed session.")
        self._active = False
        self._data.clear()
        del self._bureau

    def __repr__(self, /):
        return f"<Session[{hash(self)}]" + ('' if self.active else '(Closed)')


class Bureau(metaclass=BureauMeta):

    __slots__ = (
        '__weakref__',
        '_state', '_former', '_drawers', '_session',
        '_name',
        )

    def __init__(self, name, /):
        self._name = name
        self._state = False
        self._drawers = Drawers()

    @property
    def name(self, /):
        return self._name

    @property
    def state(self, /):
        return self._state

    @state.setter
    def state(self, val: int, /):
        '''0: Ready, 1: Dormant, 2: Active'''
        self._state = int(val)

    @property
    def ready(self, /):
        return self.state == 0

    @property
    def dormant(self, /):
        return self.state == 1

    @property
    def active(self, /):
        return self.state == 2

    @property
    def drawers(self, /):
        return self._drawers

    @property
    def session(self, /):
        return self._session

    @session.deleter
    def session(self, /):
        # self.close_drawers()
        self._session.close()
        del self._session

    def activate(self, /):
        if not self.ready:
            raise RuntimeError("Cannot enter previously entered bureau.")
        self._activate()

    def _activate(self, /):
        try:
            former = self._former = Bureau.current
        except AttributeError:
            pass
        else:
            former.suspend()
        Bureau.current = self
        assert not hasattr(self, '_session')
        self._session = Session(self)
        self.state = 2  # Active

    def __enter__(self, /):
        self.activate()
        return self

    def suspend(self, /):
        if not self.active:
            raise RuntimeError("Cannot suspend inactive bureau.")
        del self.session
        self.state = 1  # Dormant

    def revive(self, /):
        if not self.dormant:
            raise RuntimeError("Cannot suspend non-dormant bureau.")
        assert not hasattr(self, '_session')
        self._session = Session(self)
        self.state = 2  # Active

    def deactivate(self, /):
        if not self.active:
            raise RuntimeError("Cannot deactivate inactive bureau.")
        self._deactivate()

    def _deactivate(self, /):
        try:
            former = Bureau.current = self._former
        except AttributeError:
            pass
        else:
            former.revive()
        del self.session
        self.state = 0

    def __exit__(self, /, *_):
        self.deactivate()

    def __del__(self, /):
        if self.active:
            self._deactivate()

    def __repr__(self, /):
        return f"Bureau({self.name})"


GLOBALBUREAU = Bureau('GLOBAL')
GLOBALBUREAU.activate()


def open_drawer(requester, /):
    return Bureau.session[requester]


###############################################################################
###############################################################################
