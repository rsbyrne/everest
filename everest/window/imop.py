###############################################################################
''''''
###############################################################################

from PIL import Image as _PILImage

from .image import Image as _Image

class ImOp(_Image):
    ...

def rescale_width(image, targetwidth, **kwargs):
    width, height = image.width, image.height
    if width == targetwidth:
        return image
    scalefactor = targetwidth / width
    newlength = round(scalefactor * height)
    return image.resize((targetwidth, newlength), **kwargs)
def rescale_height(image, targetheight, **kwargs):
    width, height = image.width, image.height
    if height == targetheight:
        return image
    scalefactor = targetheight / height
    newlength = round(scalefactor * width)
    return image.resize((newlength, targetheight), **kwargs)

class Concat(ImOp):
    __slots__ = ('horiz', 'terms',)
    def __init__(self, *terms, horiz = True, **kwargs):
        self.horiz = horiz
        self.terms = terms
        super().__init__(*terms, **kwargs)
    def get_pilimg(self):
        images = tuple(im.pilimg for im in self.terms)
        horiz = self.horiz
        longkey, shortkey = \
            ('width', 'height') if horiz else ('height', 'width')
        shortlen = min(getattr(im, shortkey) for im in images)
        targetlength = min(getattr(im, shortkey) for im in images)
        rescaler = rescale_height if horiz else rescale_width
        images = tuple(rescaler(im, targetlength) for im in images)
        assert len(set(getattr(im, shortkey) for im in images)) == 1
        longlen = sum(getattr(im, longkey) for im in images)
        outdims = (longlen, shortlen) if horiz else (shortlen, longlen)
        out = _PILImage.new('RGB', outdims, **self.pilkwargs)
        pos = 0
        for image in images:
            pastedims =  (pos, 0) if horiz else (0, pos)
            out.paste(image, pastedims)
            pos += getattr(image, longkey)
        return out

def hstack(*terms, **kwargs):
    return Concat(*terms, **kwargs)
def vstack(*terms, **kwargs):
    return Concat(*terms, horiz = False, **kwargs)

###############################################################################
###############################################################################
