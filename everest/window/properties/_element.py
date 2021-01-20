import weakref

from .exceptions import MissingAsset
from ._base import _Vanishable, _Colourable, _Fadable

class _MplElement(_Vanishable, _Colourable, _Fadable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mplprops = dict()
    @property
    def mplelement(self):
        return self._get_mplelement()
    def _get_mplelement(self):
        raise MissingAsset
    def update(self):
        super().update()
        self._set_visible(self.visible)
        self._set_alpha(self.alpha)
        self._set_colour(self.colour)
        self.mplelement.set(**self.mplprops)
    def _set_visible(self, value):
        self.mplelement.set_visible(value)
    def _set_alpha(self, value):
        self.mplelement.set_alpha(value)
    def _set_colour(self, value):
        self.mplelement.set_color(value)
    @property
    def mplprops(self):
        return self._mplprops
    @mplprops.setter
    def mplprops(self, value):
        if value is None:
            self._mplprops.clear()
        else:
            self._mplprops.update(value)

class _MplText(_MplElement):
    def __init__(self, text = '', **kwargs):
        super().__init__(**kwargs)
        self._text = text
    @property
    def mpltext(self):
        return self.mplelement
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, value):
        self._text = value
        self.update()
    def update(self):
        super().update()
        mpltext = self.mpltext
        mpltext.set_text(self.text)
