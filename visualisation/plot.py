from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from ..disk import tempname
from ._fig import Fig

def scatter(*args, figkwargs = {}, subplotkwargs = {}, **kwargs):
    plot = Plot(
        figkwargs = figkwargs,
        subplotkwargs = subplotkwargs,
        )
    collection = plot[0][0].scatter(*args, **kwargs)
    return plot

class Plot(Fig):

    def __init__(self,
            name = None,
            shape = (1, 1),
            share = (False, False),
            size = (3, 3), # inches
            dpi = 100, # pixels per inch
            facecolour = 'white',
            edgecolour = 'black',
            fig_kws = {},
            # subplots_kws = {},
            # subplot_kws = {},
            # gridspec_kws = {},
            **kwargs
            ):

        fig = Figure(
            figsize = size,
            dpi = dpi,
            facecolor = facecolour,
            edgecolor = edgecolour,
            **{**kwargs, **fig_kws}
            )

        # axes = fig.subplots(
        #     nrows = nrows,
        #     ncols = ncols,
        #     sharex = share[0],
        #     sharey = share[1],
        #     squeeze = False,
        #     subplot_kw = subplot_kws,
        #     gridspec_kw = gridspec_kws,
        #     **{**kwargs, **subplots_kws})

        # axList = [item for sublist in axes for item in sublist]
        #
        # self.axes = axes
        # self.axList = axList

        nrows, ncols = shape
        axes = [[None for col in range(ncols)] for row in range(nrows)]

        self.shape = shape
        self.nrows, self.ncols = nrows, ncols
        self.axes = axes

        self._updateFns = []
        self.fig = fig

        self._update_axeslist()

        super().__init__()

    def _update_axeslist(self):
        self.axesList = [item for sublist in self.axes for item in sublist]

    def add_subplot(self,
            place = (0, 0),
            projection = 'rectilinear',
            share = (None, None),
            name = None,
            **kwargs
            ):

        if name is None:
            name = tempname()

        index = self._calc_index(place)
        if not self.axesList[index] is None:
            raise Exception("Already a subplot at those coordinates.")

        ax = self.fig.add_subplot(
            self.nrows,
            self.ncols,
            index + 1,
            projection = projection,
            label = name,
            sharex = share[0],
            sharey = share[1],
            **kwargs
            )

        self.axes[place[0]][place[1]] = ax
        self._update_axeslist()

        return ax

    def add_rectilinear(self,
            place = (0, 0), # (x, y) coords of subplot on plot
            title = 'mysubplot', # the title to be printed on the subplot
            position = None, # [left, bottom, width, height]
            margins = (0., 0.), # (xmargin, ymargin)
            lims = ((0., 1.), (0., 1.)), # ((float, float), (float, float))
            scales = ('linear', 'linear'), # (xaxis, yaxis)
            labels = ('x', 'y'), # (xaxis, yaxis)
            grid = True,
            ticks = (
                [i / 10. for i in range(0, 11, 2)],
                [i / 10. for i in range(0, 11, 2)],
                ), # (ticks, ticks) OR ((ticks, labels), (ticks, labels))
            share = (None, None), # (sharex, sharey)
            name = None, # provide a name to the Python object
            zorder = 0., # determines what overlaps what
            **kwargs # all other kwargs passed to axes constructor
            ):

        ax = self.add_subplot(
            place = place,
            projection = 'rectilinear',
            share = share,
            zorder = zorder,
            name = name,
            **kwargs
            )

        ax.set_xscale(scales[0])
        ax.set_yscale(scales[1])

        if all([lim is None for lim in lims[0]]):
            ax.set_xlim(auto = True)
        else:
            ax.set_xlim(*lims[0])
        if all([lim is None for lim in lims[1]]):
            ax.set_ylim(auto = True)
        else:
            ax.set_ylim(*lims[1])

        ax.set_xticks([])
        ax.set_xticklabels([])
        ax.set_yticks([])
        ax.set_yticklabels([])
        procTicks = []
        ticklabels = []
        for tick in ticks:
            if type(tick) is tuple:
                ticklabels.append(tick[1])
                procTicks.append(tick[0])
            else:
                ticklabels.append([str(val) for val in tick])
                procTicks.append(tick)
        ticks = procTicks
        ax.set_xticks(ticks[0])
        ax.set_xticklabels(ticklabels[0])
        ax.set_yticks(ticks[1])
        ax.set_yticklabels(ticklabels[1])

        if grid:
            if type(grid) is float:
                alpha = grid
            else:
                alpha = 0.2
            ax.grid(which = 'major', alpha = alpha)

        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1])

        ax.set_xmargin(margins[0])
        ax.set_ymargin(margins[1])

        ax.set_title(title)

        return ax

    def _calc_index(self, place):
        rowNo, colNo = place
        if colNo >= self.shape[0] or rowNo >= self.shape[1]:
            raise ValueError("Prescribed row and col do not exist.")
        return (self.ncols * rowNo + colNo)

    def __getitem__(self, arg):
        if type(arg) is int:
            return self.axGrid[arg]
        elif type(arg) is tuple:
            return self.axGrid[arg[0], arg[1]]
        elif type(arg) is str:
            raise TypeError("Accessing axes by name is not yet supported.")

    def _update(self):
        for fn in self._updateFns:
            fn()

    def _save(self, filepath):
        self.fig.savefig(filepath)

    def _show(self):
        FigureCanvas(self.fig)
        return self.fig
