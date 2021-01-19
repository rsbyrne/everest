from ._base import _Vanishable, _Colourable
from .spines import Spines
from .grid import Grid
from .ticks import Ticks

class _PropsController(_Vanishable, _Colourable):
    pass

class Props(_PropsController):
    def __init__(self,
            mplax,
            dims = ('x', 'y'),
            subs = None,
            colour = 'black',
            visible = True,
            ):
        subs = dict() if subs is None else subs
        grid = Grid(
            mplax,
            dims = dims,
            colour = 'grey',
            alpha = 0.5,
            )
        ticks = Ticks(
            mplax,
            dims = dims,
            )
        spines = Spines(
            mplax,
            dims = dims,
            subs = dict(ticks = ticks),
            dimsubs = tuple(dict(ticks = ticks[dim]) for dim in dims),
            )
        subs.update(dict(ticks = ticks, spines = spines, grid = grid))
        super().__init__(
            mplax,
            subs = subs,
            colour = colour,
            visible = visible,
            )