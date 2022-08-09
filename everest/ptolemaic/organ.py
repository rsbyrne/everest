###############################################################################
''''''
###############################################################################


from functools import partial as _partial

from . import ptolemaic as _ptolemaic
from .comp import Comp as _Comp


class Organ(_Comp):

    def _kindlike_getter(self, name, obj, /):
        callble = obj.__mro_getattr__(name)
        bound = self._get_callble_bound(name, callble, obj)
        out = callble.__instantiate__(tuple(bound.arguments.values()))
        obj._register_innerobj(name, out)
        return out

    def _functionlike_getter(self, name, obj, /):
        out = super()._functionlike_getter(name, obj)
        obj._register_innerobj(name, out)
        return out

    def _get_getter_(self, obj, name, /):
        if isinstance(obj, _ptolemaic.Kind):
            return _partial(self._kindlike_getter, name)
        return super()._get_getter_(obj, name)


###############################################################################
###############################################################################
