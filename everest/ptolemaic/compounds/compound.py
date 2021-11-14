###############################################################################
''''''
###############################################################################


from everest.ptolemaic.sprites.sprite import Sprite as _Sprite
from everest.ptolemaic.sprites.resourcers import Resourcer as _Resourcer


class Compound(_Sprite):

    _ptolemaic_knowntypes__ = (_Sprite,)

    conversions = {
        _Resourcer.can_convert: _Resourcer,
        }

    class Registrar:

        def process_param(self, arg, /):
            for key, val in Compound.conversions.items():
                if key(arg):
                    return val(arg)
            return arg

        def __call__(self, /, *args, **kwargs):
            proc = self.process_param
            super().__call__(
                *map(proc, args),
                **dict(zip(kwargs, map(proc, kwargs.values()))),
                )


###############################################################################
###############################################################################
