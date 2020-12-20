# from matplotlib.ticker import FixedLocator, FixedFormatter

from ._base import _Vanishable

class _TickController(_Vanishable):
    pass

class Ticks(_TickController):
    def __init__(self,
            mplax,
            dims = ('x', 'y'),
            ):
        super().__init__(**{
            dim : TickParallels(mplax, dim)
                for dim in dims
            })
        self.update()

class TickParallels(_TickController):
    def __init__(self,
            mplax,
            dim, # x, y, z
            statures = ('major', 'minor'),
            ):
        super().__init__(**{
            stature : TickSubs(mplax, dim, stature)
                for stature in statures
            })

class TickSubs(_TickController):
    def __init__(self,
            mplax,
            dim, # x, y, z
            stature, # major, minor
            ):
        super().__init__()
        self.mplax = mplax
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
    def update(self):
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
