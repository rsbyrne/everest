###############################################################################
''''''
###############################################################################


import types as _types

from everest.utilities import classtools as _classtools

from everest.ptolemaic.sprite import Sprite as _Sprite


@_classtools.add_defer_meths('content', like=dict)
class Diict(metaclass=_Sprite):

    content: dict = {}

    @classmethod
    def __class_call__(cls, arg=None, /, **kwargs):
        if arg is None:
            arg = kwargs
        elif kwargs:
            raise ValueError(
                f"Cannot pass both args and kwargs "
                f"to {self._ptolemaic_class__}"
                )
        return super().__class_call__(_types.MappingProxyType(dict(arg)))

    def get_epitaph(self, /):
        ptolcls = self._ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(
            ptolcls, dict(self.content)
            )

    def __repr__(self, /):
        valpairs = ', '.join(map(':'.join, zip(
            map(repr, content := self.content),
            map(repr, content.values()),
            )))
        return f"<{self._ptolemaic_class__}{{{valpairs}}}>"

    def _repr_pretty_(self, p, cycle):
        root = ':'.join((
            self._ptolemaic_class__.__name__,
            str(id(self)),
            ))
        if cycle:
            p.text(root + '{...}')
        elif not (kwargs := self.content):
            p.text(root + '()')
        else:
            with p.group(4, root + '(', ')'):
                kwargit = iter(kwargs.items())
                p.breakable()
                key, val = next(kwargit)
                p.pretty(key)
                p.text(' : ')
                p.pretty(val)
                for key, val in kwargit:
                    p.text(',')
                    p.breakable()
                    p.pretty(key)
                    p.text(' : ')
                    p.pretty(val)
                p.breakable()


###############################################################################
###############################################################################
