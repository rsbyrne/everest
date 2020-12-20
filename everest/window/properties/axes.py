from ._base import _Vanishable

class _AxisController(_Vanishable):
    pass

class Axes(_AxisController):
    def __init__(self,
            mplax,
            dims = ('x', 'y'),
            ):
        super().__init__(**{
            dim : Axis(mplax, dim)
                for dim in dims
            })
        self.mplax = mplax
        self._title = ''
        self.update()
    def swap(self):
        for sub in self._subs.values():
            sub.swap()
    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, val):
        self._title = val
        self.mplax.set_title(val)

class Axis(_AxisController):
    _directions = dict(
        x = ('bottom', 'top'),
        y = ('left', 'right'),
        z = ('front', 'back'),
        )
    def __init__(self,
            mplax,
            dim, # 'x', 'y', 'z'
            ):
        super().__init__()
        self.dim = dim
        self.mplax = mplax
        self._label = ''
        self._sides = self._directions[dim]
        self._side = self._sides[0]
        self._lims = None
        self._scale = 'linear'
        self._margin = 0.
    @property
    def mplaxAxis(self):
        return getattr(self.mplax, f'{self.dim}axis')
    def _set_label(self, *args, **kwargs):
        getattr(self.mplax, f'set_{self.dim}label')(*args, **kwargs)
    def _set_side(self, side):
        if not side in self._sides:
            raise ValueError
        getattr(self.mplaxAxis, f'tick_{side}')()
        self.mplaxAxis.set_label_position(side)
    def update(self):
        self._set_label(self.label)
        visible = self.visible
        mplaxAxis = self.mplaxAxis
        mplaxAxis.label.set_visible(visible)
        for tic in mplaxAxis.get_major_ticks():
            tic.set_visible(visible)
        for tic in mplaxAxis.get_minor_ticks():
            tic.set_visible(visible)
        side = self.side
        try:
            self._set_side(side)
        except AttributeError: # we assume it's 3d
            pass
    @property
    def label(self):
        return self._label
    @label.setter
    def label(self, val):
        self._label = val
        self.update()
    @property
    def side(self):
        return self._side
    @side.setter
    def side(self, val):
        if not val in self._sides:
            raise ValueError
        if not val == self._side:
            self.swap()
    def swap(self):
        if self._side == self._sides[0]:
            self._side = self._sides[1]
        else:
            self._side = self._sides[0]
        self.update()
    @property
    def lims(self):
        return self._lims
    @lims.setter
    def lims(self, val):
        self._lims = val
        getattr(self.mplax, f'set_{self.dim}lim')(val)
    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self, val):
        self._scale = val
        getattr(self.mplax, f'set_{self.dim}scale')(val)
    @property
    def margin(self):
        return self._margin
    @margin.setter
    def margin(self, val):
        self._margin = val
        getattr(self.mplax, f'set_{self.dim}margin')(val)
