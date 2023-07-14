###############################################################################
''''''
###############################################################################


import abc as _abc


class ProxyAbstract(_abc.ABC):

    __slots__ = ()

    @classmethod
    def __subclasshook__(cls, other, /):
        if cls is ProxyAbstract:
            if isinstance(other, type):
                if hasattr(other, 'unproxy'):
                    return True
        return NotImplemented

    @classmethod
    def unproxy_arg(cls, arg, /):
        return arg.unproxy() if isinstance(arg, ProxyAbstract) else arg

    @classmethod
    def unproxy_argskwargs(cls, args, kwargs, /):
        func = cls.unproxy_arg
        return (
            tuple(map(func, args)),
            dict(zip(kwargs, map(func, kwargs.values()))),
            )





###############################################################################
###############################################################################
