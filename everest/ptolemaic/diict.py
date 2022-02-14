###############################################################################
''''''
###############################################################################


import types as _types

from everest.ptolemaic.sprite import Sprite as _Sprite


class Diict(metaclass=_Sprite):

    content: dict = {}

    for name in (
            '__getitem__', '__len__', '__iter__', '__contains__',
            'keys', 'values', 'items',
            ):
        exec('\n'.join((
            f'@property',
            f'def {name}(self, /):',
            f'    return self.content.{name}',
            )))
    del name

    @classmethod
    def __class_call__(cls, arg=_types.MappingProxyType({}), /, **kwargs):
        return super().__class_call__(
            _types.MappingProxyType(dict(arg) | kwargs)
            )

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


class Kwargs(Diict):

    @classmethod
    def __class_call__(cls, /, arg=_types.MappingProxyType({}), **kwargs):
        out = super().__class_call__(arg, **kwargs)
        if not all(map(str.__instancecheck__, out)):
            raise TypeError("All keys of Kwargs must be str type.")
        return out


###############################################################################
###############################################################################
