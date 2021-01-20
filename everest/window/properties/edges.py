from ._base import _Vanishable, _Colourable, _Fadable

class _EdgeController(_Vanishable, _Colourable, _Fadable):
    _directions = dict(
        x = ('bottom', 'top'),
        y = ('left', 'right'),
        z = ('front', 'back'),
        )

class Edges(_EdgeController):
    def __init__(self,
            mplax,
            dims = ('x', 'y'),
            **kwargs,
            ):
        super().__init__(
            mplax,
            **kwargs
            )
        for dim in dims:
            sub = EdgeParallels(mplax, dim)
            self._add_sub(sub, dim)
        self._title = ''
        self._titledict = dict()
    def _set_titlecolour(self, value):
        self.titledict = dict(color = value)
    def _set_colour(self, value):
        self._set_titlecolour(value)
    def _set_title(self, title, **kwargs):
        self.mplax.set_title(title)
        self.mplax.title.set(**kwargs)
    def update(self):
        super().update()
        self._set_colour(self.colour)
        self._set_title(self.title, **self.titledict)
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

class EdgeParallels(_EdgeController):
    _whichs = ('primary', 'secondary')
    def __init__(self,
            mplax,
            dim, # 'x', 'y', 'z'
            swapped = False,
            **kwargs,
            ):
        super().__init__(
            mplax,
            **kwargs
            )
        for which in self._whichs:
            sub = Edge(mplax, dim, which, swapped)
            self._add_sub(sub, which)
        self._swapped = swapped
        self.dim = dim
        self._label = ''
#         self._lims = None
#         self._scale = 'linear'
#         self._margin = 0.
    @property
    def side(self):
        return self['primary'].side
    @property
    def swapped(self):
        return self._swapped
    @swapped.setter
    def swapped(self, value):
        if value != self.swapped:
            self.swap()
    def swap(self):
        self._swapped = not self.swapped
        self['primary']._swapped = self.swapped
        self['secondary']._swapped = self.swapped
        self.update()
    @property
    def mplaxAxis(self):
        return getattr(self.mplax, f'{self.dim}axis')
    def _set_label(self, *args, **kwargs):
        getattr(self.mplax, f'set_{self.dim}label')(*args, **kwargs)
    def _set_side(self, side):
        try:
            getattr(self.mplaxAxis, f'tick_{side}')()
            self.mplaxAxis.set_label_position(side)
        except AttributeError: # we assume it's 3d
            pass
    def update(self):
        super().update()
        self._set_label(self.label)
        self._set_side(self.side)
    @property
    def label(self):
        return self._label
    @label.setter
    def label(self, val):
        self._label = val
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

class Edge(_EdgeController):
    def __init__(self,
            mplax,
            dim, # 'x', 'y', 'z'
            which, # ('primary', 'secondary')
            swapped = False,
            **kwargs
            ):
        self.dim = dim
        self._swapped = swapped
        self._which = which
        self._primary = which == 'primary'
        super().__init__(
            mplax,
            **kwargs
            )
    @property
    def isprimary(self):
        return self._primary
    @property
    def mplaxAxis(self):
        return getattr(self.mplax, f'{self.dim}axis')
    @property
    def side(self):
        return self._directions[self.dim][
            dict(primary = 0, secondary = 1)[self._which] ^ self.swapped
            ]
    @property
    def swapped(self):
        return self._swapped
    @property
    def mplspine(self):
        return self.mplax.spines[self.side]
    def _set_visible(self, value):
        self.mplspine.set_visible(value)
        if self.isprimary:
            mplaxAxis = self.mplaxAxis
            mplaxAxis.label.set_visible(value)
            for tic in mplaxAxis.get_major_ticks():
                tic.set_visible(value)
            for tic in mplaxAxis.get_minor_ticks():
                tic.set_visible(value)
    def _set_alpha(self, value):
        self.mplspine.set_alpha(value)
    def _set_colour(self, value):
        self.mplspine.set_color(value)
        if self.isprimary:
            self.mplaxAxis.label.set_color(value)
    def update(self):
        super().update()
        self._set_visible(self.visible)
        self._set_alpha(self.alpha)
        self._set_colour(self.colour)

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