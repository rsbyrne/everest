import weakref
from functools import reduce
import operator

class _PropertyController:
    def __init__(self, mplax):
        self.mplax = mplax
        self._masters = list()
        self._subs = dict()
    def _add_sub(self, sub, name):
        self._subs[name] = sub
        setattr(self, name, sub)
        sub._masters.append(weakref.ref(self))
    @property
    def masters(self):
        outs = []
        for ref in self._masters:
            out = ref()
            if not out is None:
                outs.append(out)
        return tuple(outs)
    def update(self):
        for sub in self._subs.values():
            sub.update()
    def __getitem__(self, key):
        return self._subs[key]

class _Vanishable(_PropertyController):
    def __init__(self, mplax, visible = None, **kwargs):
        super().__init__(mplax, **kwargs)
        self._visible = visible
    @property
    def masterVisible(self):
        for m in self.masters:
            if isinstance(m, _Vanishable):
                v = m.visible
                if not v is None:
                    return v
        return None
    @property
    def visible(self):
        if self._visible is None:
            mv = self.masterVisible
            if mv is None:
                raise ValueError(None)
            return mv
        return self._visible
    @visible.setter
    def visible(self, value):
        self._visible = None if value is None else bool(value)
        self.update()
    def toggle(self):
        self.visible = not self.visible

class _Fadable(_PropertyController):
    def __init__(self, mplax, alpha = 1., **kwargs):
        super().__init__(mplax, **kwargs)
        self._alpha = alpha
    @property
    def masterAlpha(self):
        return reduce(
            operator.mul,
            (1, *(m.alpha for m in self.masters if isinstance(m, _Fadable)))
            )
    @property
    def alpha(self):
        return self._alpha * self.masterAlpha
    @alpha.setter
    def alpha(self, value):
        self._alpha = float(value)
        self.update()

class _Colourable(_PropertyController):
    def __init__(self, mplax, colour = None, **kwargs):
        super().__init__(mplax, **kwargs)
        self._colour = colour
    @property
    def masterColour(self):
        masters = self.masters
        if len(masters):
            for m in masters[::-1]:
                if isinstance(m, _Colourable):
                    c = m.colour
                    if not c is None:
                        return c
        return None
    @property
    def colour(self):
        if self._colour is None:
            c = self.masterColour
        else:
            c = self._colour
        if c is None:
            raise ValueError(None)
        return c
    @colour.setter
    def colour(self, value):
        self._colour = value
        self.update()

#         if self._colourMaster == self._defaultcolour:
#             return self._colour
#         else:
#             return self._colourMaster