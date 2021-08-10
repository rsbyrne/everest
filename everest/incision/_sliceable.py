###############################################################################
''''''
###############################################################################


from . import _utilities

from ._incisable import Incisable as _Incisable


_slyce = _utilities.misc.slyce
_TypeMap = _utilities.misc.TypeMap


class Sliceable(_Incisable):

    @classmethod
    def _cls_extra_init_(cls, /):
        super()._cls_extra_init_()
        Incisor = cls.Incisor
        slcmeths = []
        for name in ('start', 'stop', 'step'):
            get_meths = getattr(cls, f"slice_{name}_methods")
            meths = _TypeMap(get_meths())
            setattr(cls, f"slc{name}meths", meths)
            slcmeths.append(meths)
        cls.slcmeths = tuple(slcmeths)

    @classmethod
    def slice_start_methods(cls, /):
        return iter(())

    @classmethod
    def slice_stop_methods(cls, /):
        return iter(())

    @classmethod
    def slice_step_methods(cls, /):
        return iter(())

    def incise_slyce(self, incisor: _slyce, /):
        for slcarg, slcmeths in zip(incisor.args, self.slcmeths):
            if slcarg is not None:
                self = slcmeths[type(slcarg)](self, slcarg)
        return self

    def incise_slice(self, incisor: slice, /):
        return self.incise_slyce(_slyce(incisor))

    @classmethod
    def priority_incision_methods(cls, /):
        yield slice, cls.incise_slice
        yield _utilities.misc.Slyce, cls.incise_slyce
        yield from super().priority_incision_methods()


###############################################################################
###############################################################################
