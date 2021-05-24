###############################################################################
''''''
###############################################################################

from PIL import Image as _Image

from functools import partial as _partial

def from_file(path, *args, **kwargs):
    return _Image.open(path, *args, **kwargs)

def concat(*images, horiz = True):
    keys = 'width', 'height'
    longkey, shortkey = keys if horiz else keys[::-1]
    dims = [
        max(getattr(im, shortkey) for im in images),
        sum(getattr(im, longkey) for im in images),
        ]
    if horiz:
        dims.reverse()
    out = _Image.new('RGB', dims)
    pos = 0
    for im in images:
        dims = [0, pos]
        if horiz:
            dims.reverse()
        out.paste(im, dims)
        pos += getattr(im, longkey)
    return out

concat_horiz = _partial(concat, horiz = True)
concat_vert = _partial(concat, horiz = False)

###############################################################################
###############################################################################
