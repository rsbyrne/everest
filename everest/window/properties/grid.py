from ._base import _Fadable, _Vanishable, _Colourable

class _GridController(_Fadable, _Vanishable, _Colourable):
    ...

class Grid(_GridController):
    def __init__(self,
            mplax,
            dims = ('x', 'y'),
            dimsubs = None,
            subs = None,
            alpha = 0.5,
            **kwargs,
            ):
        subs = dict() if subs is None else subs
        if dimsubs is None:
            dimsubs = tuple(dict() for dim in dims)
        subs.update({
            dim : GridParallels(mplax, dim, subs = dsubs)
                for dim, dsubs in zip(dims, dimsubs)
            })
        super().__init__(
            mplax,
            subs = subs,
            alpha = alpha,
            **kwargs
            )

class GridParallels(_GridController):
    def __init__(self,
            mplax,
            dim, # x, y, z
            statures = ('major', 'minor'),
            subs = None,
            **kwargs,
            ):
        subs = dict() if subs is None else subs
        subs.update({
            stature : GridSubs(mplax, dim, stature)
                for stature in statures
            })
        super().__init__(
            mplax,
            subs = subs,
            **kwargs
            )

class GridSubs(_GridController):
    def __init__(self,
            mplax,
            dim, # x, y, z
            stature, # major, minor
            subs = None,
            alpha = None,
            **kwargs,
            ):
        alpha = dict(major = 1, minor = 0.5)[stature] if alpha is None else alpha
        subs = dict() if subs is None else subs
        super().__init__(
            mplax,
            subs = subs,
            alpha = alpha,
            **kwargs
            )
        self.dim = dim
        self.stature = stature
    def update(self):
        super().update()
        self.mplax.grid(
            b = True,
            axis = self.dim,
            which = self.stature,
            alpha = self.alpha if self.visible else 0.,
            color = self.colour,
            )
