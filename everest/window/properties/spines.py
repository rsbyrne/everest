from ._base import _Vanishable, _Colourable, _Fadable

class _SpineController(_Vanishable, _Colourable, _Fadable):
    def __init__(self, mplax, sides, **kwargs):
        self._sides = sides
        super().__init__(mplax, **kwargs)
    @property
    def spines(self):
        return tuple(self.mplax.spines[k] for k in self._sides)
    def _set_visible(self, value):
        for spine in self.spines:
            spine.set_visible(value)
    def _set_alpha(self, value):
        for spine in self.spines:
            spine.set_alpha(value)
    def _set_spinecolour(self, value):
        for spine in self.mplax.spines.values():
            spine.set_color(value)
    def _set_colour(self, value):
        self._set_spinecolour(value)
    def update(self):
        super().update()
        self._set_colour(self.colour)
        self._set_visible(self.visible)
        self._set_alpha(self.alpha)

class Spines(_SpineController):
    def __init__(self,
            mplax,
            dims = ('x', 'y'),
            dimsubs = None,
            subs = None,
            **kwargs,
            ):
        subs = dict() if subs is None else subs
        if dimsubs is None:
            dimsubs = tuple(dict() for dim in dims)
        subs.update({
            dim : SpineParallels(mplax, dim, subs = dsubs)
                for dim, dsubs in zip(dims, dimsubs)
            })
        super().__init__(
            mplax,
            tuple(mplax.spines.keys()),
            subs = subs,
            **kwargs
            )
        self._title = ''
        self._titledict = dict()
    def _set_titlecolour(self, value):
        self.titledict = dict(color = value)
    def _set_colour(self, value):
        super()._set_colour(value)
        self._set_titlecolour(value)
    def _set_title(self, value):
        self.mplax.set_title(value)
        self.mplax.title.set(**self.titledict)
    def update(self):
        super().update()
        self._set_title(self.title)
    def swap(self):
        for sub in self._subs.values():
            sub.swap()
    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, val):
        self._title = val
        self.update()
    @property
    def titledict(self):
        return self._titledict
    @titledict.setter
    def titledict(self, value):
        if value is None:
            self._titledict.clear()
        else:
            self._titledict.update(value)

class SpineParallels(_SpineController):
    _directions = dict(
        x = ('bottom', 'top'),
        y = ('left', 'right'),
        z = ('front', 'back'),
        )
    def __init__(self,
            mplax,
            dim, # 'x', 'y', 'z'
            subs = None,
            **kwargs,
            ):
        subs = dict() if subs is None else subs
        super().__init__(
            mplax,
            self._directions[dim],
            subs = subs,
            **kwargs
            )
        self.dim = dim
        self._label = ''
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
    def _set_colour(self, value):
        super()._set_colour(value)
        self.mplaxAxis.label.set_color(value)
    def _set_visible(self, value):
        super()._set_visible(value)
        visible = self.visible
        mplaxAxis = self.mplaxAxis
        mplaxAxis.label.set_visible(visible)
        for tic in mplaxAxis.get_major_ticks():
            tic.set_visible(visible)
        for tic in mplaxAxis.get_minor_ticks():
            tic.set_visible(visible)
    def update(self):
        super().update()
        self._set_label(self.label)
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

# class Spine(_SpineController):
#     def __init__(self,
#             mplax,
#             side,
#             **kwargs,
#             ):
#         super().__init__(
#             mplax,
#             (side,),
#             **kwargs
#             )
#     @property
#     def spine(self):
#         return self.mplax