###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC
from dataclasses import dataclass as _dataclass
from types import FunctionType as _FunctionType
from functools import partial as _partial, wraps as _wraps


class ApplyDecorator:
    __slots__ = ('dec', 'func', 'partial',)
    def __init__(self, dec, *args, func = None, **kwargs):
        self.dec = _partial(dec, *args, **kwargs) if args or kwargs else dec
        if func is None:
            self.partial = True
        else:
            self.partial = False
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


@_dataclass
class ForceMethod:
    func: _FunctionType


def __subclasshook__(compclass, cls, C):
    if cls is compclass:
        return cls.check_sub(C)
    return NotImplemented

class MethAdder(_ABC):
    decorate = ApplyDecorator
    forcemethod = ForceMethod
    @classmethod
    def hidden_names(cls):
        return
        yield # pylint: disable=W0101
    @classmethod
    def meths_to_add(cls):
        forbidden = (
            *MethAdder.__dict__.keys(),
            *cls.__abstractmethods__,
            *set(cls.hidden_names())
            )
        return (name for name in dir(cls) if not name in forbidden)
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
            att = getattr(cls, name)
            if forcemeth := isinstance(att, ForceMethod):
                att = att.func
            if hasattr(ACls, name) and not forcemeth:
                continue
            if isinstance(att, ApplyDecorator):
                att = att.resolve()
            setattr(ACls, name, att)
        return ACls

###############################################################################
###############################################################################
