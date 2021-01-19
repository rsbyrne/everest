from ._base import _Fadable, _Vanishable, _Colourable

class _GridController(_Fadable, _Vanishable, _Colourable):
    _defaultcolour = 'grey'

class Grid(_GridController):
    def __init__(self,
            mplax,
            dims = ('x', 'y'),
            dimsubs = None,
            **subs,
            ):
        if dimsubs is None:
            dimsubs = tuple(dict() for dim in dims)
        subs.update({
            dim : GridParallels(mplax, dim, **dimsub)
                for dim, dimsub in zip(dims, dimsubs)
            })
        super().__init__(**subs)
        self.update()

class GridParallels(_GridController):
    def __init__(self,
            mplax,
            dim, # x, y, z
            statures = ('major', 'minor'),
            **subs,
            ):
        subs.update({
            stature : GridSubs(mplax, dim, stature)
                for stature in statures
            })
        super().__init__(**subs)

class GridSubs(_GridController):
    def __init__(self,
            mplax,
            dim, # x, y, z
            stature, # major, minor
            **subs,
            ):
        super().__init__(**subs)
        self.mplax = mplax
        self.dim = dim
        self.stature = stature
    def update(self):
        alpha = self.alpha if self.visible else 0.
        self.mplax.grid(
            b = True,
            axis = self.dim,
            which = self.stature,
            alpha = alpha,
            color = self.colour,
            )
