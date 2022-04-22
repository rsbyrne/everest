###############################################################################
''''''
###############################################################################


import weakref as _weakref
from types import MappingProxyType as _MappingProxyType


class BureauMeta(type):

    @property
    def current(cls, /):
        return cls._current

    @current.setter
    def current(cls, val, /):
        cls._current = val


class Drawer:
    ...


class OpenDrawer:

    __slots__ = ('__weakref__', '_drawer')

    def __init__(self, drawer, /):
        self._drawer = drawer

    for methname in (
            '__getitem__', '__setitem__', '__delitem__', '__repr__'
            ):
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self._drawer.{methname}",
            )))


class Bureau(metaclass=BureauMeta):

    __slots__ = (
        '__weakref__',
        '_state', '_former', '_opendrawers', '_drawers'
        )

    def __init__(self, /):
        self._state = False
        self._opendrawers = _weakref.WeakKeyDictionary()
        self._drawers = _weakref.WeakKeyDictionary()

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
    def opendrawers(self, /):
        return _MappingProxyType(self._opendrawers)

    @property
    def drawers(self, /):
        return _MappingProxyType(self._drawers)

    def activate(self, /):
        if not self.ready:
            raise RuntimeError("Cannot enter previously entered bureau.")
        try:
            former = self._former = Bureau.current
        except AttributeError:
            pass
        else:
            former.suspend()
        Bureau.current = self
        self.state = 2  # Active

    def __enter__(self, /):
        self.activate()
        return self

    def suspend(self, /):
        if not self.active:
            raise RuntimeError("Cannot suspend inactive bureau.")
        self.close_drawers()
        self.state = 1  # Dormant

    def revive(self, /):
        if not self.dormant:
            raise RuntimeError("Cannot suspend non-dormant bureau.")
        self.state = 2  # Active

    def open_drawer(self, requester, /):
        if not self.active:
            raise RuntimeError("Cannot open drawer of inactive bureau.")
        opendrawers = self._opendrawers
        try:
            opendrawer = opendrawers[requester]
        except KeyError:
            drawers = self._drawers
            try:
                drawer = drawers[requester]
            except KeyError:
                drawer = drawers[requester] = Drawer()
            opendrawer = opendrawers[requester] = OpenDrawer(drawer)
        return _weakref.proxy(opendrawer)

    def close_drawers(self, /):
        if not self.active:
            raise RuntimeError(
                "Cannot purge opened drawers of inactive bureau."
                )
        self._opendrawers.clear()

    def deactivate(self, /):
        if not self.active:
            raise RuntimeError("Cannot deactivate inactive bureau.")
        try:
            former = Bureau.current = self._former
        except AttributeError:
            pass
        else:
            former.revive()
        self.close_drawers()
        self.state = 0

    def __exit__(self, /, *_):
        self.deactivate()


GLOBALBUREAU = Bureau()
GLOBALBUREAU.activate()


def open_drawer(requester, /):
    return Bureau.current.open_drawer(requester)


###############################################################################
###############################################################################
