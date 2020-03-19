from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from ._fig import Fig

def scatter(*args, figkwargs = {}, subplotkwargs = {}, **kwargs):
    plot = Plot(
        figkwargs = figkwargs,
        subplotkwargs = subplotkwargs,
        **kwargs
        )
    collection = plot[0][0].scatter(*args)
    return plot

class Plot(Fig):

    def __init__(self,
            name = None,
            figsize = (3, 3), # inches
            dpi = 100, # pixels per inch
            facecolour = 'white',
            edgecolour = 'black',
            rows = 1,
            cols = 1,
            figkwargs = {},
            subplotkwargs = {},
            **kwargs
            ):

        fig = Figure(
            figsize = figsize,
            dpi = dpi,
            facecolor = facecolour,
            edgecolor = edgecolour,
            **{**kwargs, **figkwargs}
            )

        if type(rows) is int:
            rowNo = rows
        elif type(rows) is tuple:
            rowNo = len(rows)
        if type(cols) is int:
            colNo = cols
        elif type(cols) is tuple:
            colNo = len(cols)

        axes = fig.subplots(rowNo, colNo, **{**kwargs, **subplotkwargs})

        if rowNo > 1 and colNo > 1:
            axGrid = axes
        else:
            axGrid = [[None for col in range(colNo)] for row in range(rowNo)]
            if not type(axes) is list:
                axGrid[0][0] = axes
            elif colNo > 1 and rowNo == 1:
                for i in range(colNo):
                    axGrid[0][i] = axes[i]
            elif rowNo > 1 and colNo == 1:
                for i in range(rowNo):
                    axGrid[i][0] = axes[i]
            else:
                axGrid = axes
        axList = [item for sublist in axGrid for item in sublist]

        self._updateFns = []

        self.fig = fig
        self.axes = axes
        self.axList = axList
        self.axGrid = axGrid

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
