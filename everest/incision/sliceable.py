###############################################################################
''''''
###############################################################################


import itertools as _itertools

from . import _utilities

from .chora import Chora as _Chora


class Sliceable(_Chora):

    @classmethod
    def _cls_extra_init_(cls, /):
        super()._cls_extra_init_()
        cls.slcmeths = dict(reversed(tuple(cls.slice_methods())))

    @classmethod
    def slice_methods(cls, /):
        yield (False, False, False), cls.incise_trivial

    def incise_slice(self, slc, /, *, context):
        return self.incise_slyce(
            _utilities.misc.slyce(slc),
            context=context,
            )

    def incise_slyce(self, slc, /, *, context):
        try:
            slcmeth = self.slcmeths[slc.hasargs]
        except KeyError:
            raise ValueError(" ".join((
                f"Object of type {type(self)}",
                "cannot be sliced with slice of",
                "start={0}, stop={1}, step={2}".format(*slc.args),
                )))
        return slcmeth(self, *slc, context=context)

    @classmethod
    def incision_methods(cls, /):
        yield slice, cls.incise_slice
        yield _utilities.misc.Slyce, cls.incise_slyce
        yield from super().incision_methods()


###############################################################################
###############################################################################
