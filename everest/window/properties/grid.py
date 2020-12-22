from ._base import _Fadable, _Vanishable

class _GridController(_Fadable, _Vanishable):
    pass

class Grid(_GridController):
    def __init__(self,
            mplax,
            dims = ('x', 'y'),
            ):
        super().__init__(**{
            dim : GridParallels(mplax, dim)
                for dim in dims
            })
        self.update()

class GridParallels(_GridController):
    def __init__(self,
            mplax,
            dim, # x, y, z
            statures = ('major', 'minor')
            ):
        super().__init__(**{
            stature : GridSubs(mplax, dim, stature)
                for stature in statures
            })

class GridSubs(_GridController):
    def __init__(self,
            mplax,
            dim, # x, y, z
            stature, # major, minor
            ):
        super().__init__()
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
            )

#
# class Axis:
#     _dims = {
#         0: 'x',
#         1: 'y',
#         2: 'z',
#         }
#     _allvocab = dict(
#         x = dict(
#             sides = ('left', 'right')
#             ),
#         y = dict(
#             sides = ('bottom', 'top')
#             ),
#         z = dict(
#             sides = 'front'
#             )
#         )
#     def __init__(self,
#             ax,
#             dim,
#             ):
#         if not dim in self_.dims.values():
#             dim = self._dims[dim]
#         self.dim = dim
#         self.ax = ax
#         self.mplax = ax.ax
#
#     self.visible = True
#     self.side = self.vocab['sides'][0]
#
#     self.tickValsMajor = []
#     self.tickValsMinor = []
#     self.tickValsMajorVisible = True
#     self.tickValsMinorVisible = True
#
#     self.tickLabelsMajor = []
#     self.tickLabelsMinor = []
#     self.tickLabelsMajorVisible = []
#     self.tickLabelsMinorVisible = []
#
#     @property
#     def _vocab(self):
#         return self._allvocab[self.dim]
