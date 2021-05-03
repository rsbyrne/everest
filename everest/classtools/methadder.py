###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC
from functools import partial as _partial

class ApplyDecorator:
    __slots__ = ('dec', 'func', 'partial',)
    def __init__(self, dec, *args, func = None, **kwargs):
        self.dec = _partial(dec, *args, **kwargs) if args or kwargs else dec
        if func is None:
            self.partial = True
        else:
            self.partial = False
            # if not isinstance(func, ApplyDecorator):
            #     func = staticmethod(func)
            self.func = func
    def __call__(self, func):
        if self.partial:
            return type(self)(self.dec, func = func)
        raise TypeError(f"Cannot call non-partial {type(self)} object.")
    def resolve(self):
        if self.partial:
            raise TypeError(f"Cannot resolve partial {type(self)} object.")
        func = self.func
        if isinstance(func, ApplyDecorator):
            func = func.resolve()
        return self.dec(func)


def __subclasshook__(compclass, cls, C):
    if cls is compclass:
        return cls.check_sub(C)
    return NotImplemented

class MethAdder(_ABC):
    @classmethod
    def meths_to_add(cls):
        for name in dir(cls):
            if name not in MethAdder.__dict__:
                if name not in cls.__abstractmethods__:
                    yield name
            # if name[:2] == '__' and name[-2:] == '__':
            #     continue

    @classmethod
    def check_sub(cls, C):
        if all(
                any(name in B.__dict__ for B in C.__mro__)
                    for name in cls.meths_to_add()
                ):
            return True
        return NotImplemented
    def __init_subclass__(cls, **kwargs):
        if '__subclasshook__' not in cls.__dict__:
            addmeth = classmethod(_partial(__subclasshook__, cls))
            setattr(cls, '__subclasshook__', addmeth)
        super().__init_subclass__(**kwargs)
    def __new__(cls, ACls):
        missingmeths = set(
            name for name in cls.__abstractmethods__
                if not hasattr(ACls, name)
            )
        if missingmeths:
            raise TypeError(f"Missing methods: {missingmeths}")
        for name in cls.meths_to_add():
            if not hasattr(ACls, name):
                att = getattr(cls, name)
                if isinstance(att, ApplyDecorator):
                    setattr(ACls, name, att.resolve())
                else:
                    setattr(ACls, name, att)
        return ACls

###############################################################################
###############################################################################
