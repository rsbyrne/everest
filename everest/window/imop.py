###############################################################################
''''''
###############################################################################

from PIL import Image as _PILImage

from .image import Image as _Image

class ImOp(_Image):
    ...

class Concat(ImOp):
    __slots__ = ('horiz', 'terms',)
    def __init__(self, *terms, horiz = True, **kwargs):
        self.horiz = horiz
        self.terms = terms
        super().__init__(*terms, **kwargs)
    def get_pilimg(self):
        images = tuple(im.pilimg for im in self.terms)
            # (im.pilimg if hasattr(im, 'pilimg') else im) for im in self.terms
            # )
        horiz = self.horiz
        keys = 'width', 'height'
        longkey, shortkey = keys if horiz else keys[::-1]
        dims = [
            max(getattr(im, shortkey) for im in images),
            sum(getattr(im, longkey) for im in images),
            ]
        if horiz:
            dims.reverse()
        out = _PILImage.new('RGB', dims, **self.pilkwargs)
        pos = 0
        for im in images:
            dims = [0, pos]
            if horiz:
                dims.reverse()
            out.paste(im, dims)
            pos += getattr(im, longkey)
        return out

def hstack(*terms, **kwargs):
    return Concat(*terms, **kwargs)
def vstack(*terms, **kwargs):
    return Concat(*terms, horiz = False, **kwargs)

###############################################################################
###############################################################################
