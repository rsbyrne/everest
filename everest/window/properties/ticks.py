# from matplotlib.ticker import FixedLocator, FixedFormatter

from ._base import _Vanishable, _Colourable

class _TickController(_Vanishable, _Colourable):
    pass

class Ticks(_TickController):
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
            sub = TickParallels(mplax, dim)
            self._add_sub(sub, dim)

class TickParallels(_TickController):
    _statures = ('major', 'minor')
    def __init__(self,
            mplax,
            dim, # x, y, z
            **kwargs,
            ):
        super().__init__(
            mplax,
            **kwargs
            )
        for stature in self._statures:
            sub = TickSubs(mplax, dim, stature)
            self._add_sub(sub, stature)

class TickSubs(_TickController):
    def __init__(self,
            mplax,
            dim, # x, y, z
            stature, # major, minor
            **kwargs,
            ):
        super().__init__(
            mplax,
            **kwargs
            )
        self.dim = dim
        self.stature = stature
        self._minor = stature == 'minor'
        self._values = []
        self._labels = []
        self._rotation = 0
    def _set_labels(self, labels, *args, **kwargs):
        getattr(self.mplax, f'set_{self.dim}ticklabels')(
            labels,
            *args,
            minor = self._minor,
            rotation = self.rotation,
            **kwargs
            )
    def _set_values(self, values, *args, **kwargs):
        getattr(self.mplax, f'set_{self.dim}ticks')(
            values,
            *args,
            minor = self._minor,
            **kwargs
            )
    def _set_colour(self, value, **kwargs):
        self.mplax.tick_params(
            axis = self.dim,
            which = self.stature,
            color = value,
            labelcolor = value,
            **kwargs,
            )
    def update(self):
        super().update()
        self._set_colour(self.colour)
        if self.visible:
            self._set_values(self.values)
            self._set_labels(self.labels)
        else:
            self._set_values([])
            self._set_labels([])
    def set_values_labels(self, values, labels):
        self._values[:] = values
        self._labels[:] = labels
        self.update()
    @property
    def values(self):
        return self._values
    @values.setter
    def values(self, vals):
        self._values[:] = vals
        self.update()
    @property
    def labels(self):
        return self._labels
    @labels.setter
    def labels(self, vals):
        self._labels[:] = vals
        self.update()
    @property
    def rotation(self):
        return self._rotation
    @rotation.setter
    def rotation(self, val):
        self._rotation = val
        self.update()

    # @property
    # def mplaxAxis(self):
    #     return getattr(self.mplax, f'{self.dim}axis')
    # def _set_values(self, values, *args, **kwargs):
    #     getattr(self.mplaxAxis, f'set_{self.stature}_locator')(
    #         *args,
    #         **kwargs
    #         )

# class TickObject(_TickController):
#     def __init__(self,
#             mplax,
#             dim,
#             stature,
#             objType, # 'value', 'label'
#             ):

#####################
 
# from matplotlib.ticker import FixedLocator, FixedFormatter
