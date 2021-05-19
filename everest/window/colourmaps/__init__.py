from matplotlib.pyplot import get_cmap as mpl_get_cmap

from . import turbo

cmaps = dict(
    Turbo = turbo.cmap
    )

def get_cmap(key):
    try:
        return mpl_get_cmap(key)
    except ValueError:
        return cmaps[key]