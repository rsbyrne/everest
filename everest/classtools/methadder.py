###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC
from functools import partial as _partial

class ApplyDecorator:
    __slots__ = 'dec', 'func'
    def __init__(self, dec, func):
        self.dec, self.func = dec, func
    def __iter__(self):
        yield self.dec
        yield self.func
def applydecorator(dec):
    part = _partial(ApplyDecorator, dec)
    return part

class MethAdder(_ABC):
    @classmethod
    def meths_to_add(cls):
        for name in dir(cls):
            if name in MethAdder.__dict__:
                continue
            if name[:2] == '__' and name[-2:] == '__':
                continue
            yield name
    @classmethod
    def check_sub(cls, C):
        if all(
                any(name in B.__dict__ for B in C.__mro__)
                    for name in cls.meths_to_add()
                ):
            return True
        return NotImplemented
    def __new__(cls, ACls):
        for name in cls.meths_to_add():
            if not hasattr(ACls, name):
                att = getattr(cls, name)
                if isinstance(att, ApplyDecorator):
                    dec, func = att
                    setattr(ACls, name, dec(func))
                else:
                    setattr(ACls, name, att)
        return ACls

###############################################################################
###############################################################################
